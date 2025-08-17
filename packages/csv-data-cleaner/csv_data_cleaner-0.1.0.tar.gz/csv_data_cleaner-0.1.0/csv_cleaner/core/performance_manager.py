"""
Performance manager for CSV Data Cleaner.
Handles chunked processing, memory monitoring, and performance optimization.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Generator
import time
import logging
import psutil
import gc
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""

    start_time: float
    end_time: float
    memory_peak: float
    memory_avg: float
    chunks_processed: int
    rows_processed: int
    operations_performed: List[str]

    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        return self.end_time - self.start_time

    @property
    def rows_per_second(self) -> float:
        """Get processing speed in rows per second."""
        return self.rows_processed / self.duration if self.duration > 0 else 0

    @property
    def memory_usage_mb(self) -> float:
        """Get memory usage in MB."""
        return self.memory_peak / (1024 * 1024)


class PerformanceManager:
    """Manages performance optimization and monitoring for CSV operations."""

    def __init__(self, max_memory_gb: float = 2.0, chunk_size: int = 10000):
        """Initialize performance manager.

        Args:
            max_memory_gb: Maximum memory usage in GB.
            chunk_size: Default chunk size for processing.
        """
        self.max_memory_gb = max_memory_gb
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.chunk_size = chunk_size
        self.metrics_history: List[PerformanceMetrics] = []

        # Performance monitoring
        self._start_time = None
        self._memory_samples: List[float] = []
        self._current_operation = None

    def start_operation(self, operation_name: str) -> None:
        """Start monitoring a new operation.

        Args:
            operation_name: Name of the operation being monitored.
        """
        self._current_operation = operation_name
        self._start_time = time.time()
        self._memory_samples = []
        logger.info(f"Starting operation: {operation_name}")

    def end_operation(
        self,
        chunks_processed: int = 0,
        rows_processed: int = 0,
        operations_performed: Optional[List[str]] = None,
    ) -> PerformanceMetrics:
        """End operation monitoring and return metrics.

        Args:
            chunks_processed: Number of chunks processed.
            rows_processed: Number of rows processed.
            operations_performed: List of operations performed.

        Returns:
            Performance metrics for the operation.
        """
        if self._start_time is None:
            raise ValueError("No operation started. Call start_operation() first.")

        end_time = time.time()
        memory_peak = max(self._memory_samples) if self._memory_samples else 0
        memory_avg = (
            sum(self._memory_samples) / len(self._memory_samples)
            if self._memory_samples
            else 0
        )

        metrics = PerformanceMetrics(
            start_time=self._start_time,
            end_time=end_time,
            memory_peak=memory_peak,
            memory_avg=memory_avg,
            chunks_processed=chunks_processed,
            rows_processed=rows_processed,
            operations_performed=operations_performed or [],
        )

        self.metrics_history.append(metrics)

        logger.info(f"Operation completed: {self._current_operation}")
        logger.info(
            f"Duration: {metrics.duration:.2f}s, Rows/sec: {metrics.rows_per_second:.0f}"
        )
        logger.info(f"Memory peak: {metrics.memory_usage_mb:.1f}MB")

        # Reset monitoring state
        self._start_time = None
        self._memory_samples = []
        self._current_operation = None

        return metrics

    def sample_memory(self) -> float:
        """Sample current memory usage.

        Returns:
            Current memory usage in bytes.
        """
        process = psutil.Process()
        memory_bytes = process.memory_info().rss
        self._memory_samples.append(memory_bytes)
        return memory_bytes

    def check_memory_limit(self) -> bool:
        """Check if current memory usage is within limits.

        Returns:
            True if memory usage is within limits, False otherwise.
        """
        current_memory = self.sample_memory()
        if current_memory > self.max_memory_bytes:
            logger.warning(
                f"Memory usage ({current_memory / (1024**3):.2f}GB) exceeds limit ({self.max_memory_gb}GB)"
            )
            return False
        return True

    def force_garbage_collection(self) -> None:
        """Force garbage collection to free memory."""
        collected = gc.collect()
        logger.debug(f"Garbage collection freed {collected} objects")

    @contextmanager
    def memory_monitoring(self):
        """Context manager for memory monitoring."""
        try:
            self.sample_memory()
            yield
        finally:
            self.sample_memory()

    def chunk_dataframe(
        self, df: pd.DataFrame, chunk_size: Optional[int] = None
    ) -> Generator[pd.DataFrame, None, None]:
        """Split DataFrame into chunks for processing.

        Args:
            df: DataFrame to chunk.
            chunk_size: Size of each chunk (uses default if None).

        Yields:
            DataFrame chunks.
        """
        chunk_size = chunk_size or self.chunk_size
        total_rows = len(df)

        logger.info(
            f"Chunking DataFrame: {total_rows} rows, {chunk_size} rows per chunk"
        )

        for start_idx in range(0, total_rows, chunk_size):
            end_idx = min(start_idx + chunk_size, total_rows)
            chunk = df.iloc[start_idx:end_idx].copy()

            logger.debug(
                f"Processing chunk {start_idx//chunk_size + 1}: rows {start_idx}-{end_idx-1}"
            )
            yield chunk

    def process_in_chunks(
        self,
        df: pd.DataFrame,
        operation: Callable[[pd.DataFrame], pd.DataFrame],
        chunk_size: Optional[int] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """Process DataFrame in chunks with memory monitoring.

        Args:
            df: DataFrame to process.
            operation: Function to apply to each chunk.
            chunk_size: Size of each chunk.
            show_progress: Whether to show progress information.

        Returns:
            Processed DataFrame.
        """
        chunk_size = chunk_size or self.chunk_size
        total_rows = len(df)
        processed_chunks = []
        chunks_processed = 0
        rows_processed = 0

        self.start_operation("chunked_processing")

        try:
            for chunk in self.chunk_dataframe(df, chunk_size):
                # Check memory before processing
                if not self.check_memory_limit():
                    self.force_garbage_collection()
                    if not self.check_memory_limit():
                        raise MemoryError(
                            "Memory limit exceeded even after garbage collection"
                        )

                # Process chunk
                with self.memory_monitoring():
                    processed_chunk = operation(chunk)
                    processed_chunks.append(processed_chunk)

                chunks_processed += 1
                rows_processed += len(chunk)

                if show_progress:
                    progress = (rows_processed / total_rows) * 100
                    logger.info(
                        f"Progress: {progress:.1f}% ({rows_processed}/{total_rows} rows)"
                    )

                # Periodic garbage collection
                if chunks_processed % 5 == 0:
                    self.force_garbage_collection()

        except Exception as e:
            logger.error(f"Error during chunked processing: {str(e)}")
            raise

        finally:
            self.end_operation(
                chunks_processed, rows_processed, ["chunked_processing"]
            )

        # Combine processed chunks
        if processed_chunks:
            result = pd.concat(processed_chunks, ignore_index=True)
            logger.info(f"Chunked processing completed: {len(result)} rows processed")
            return result
        else:
            logger.warning("No chunks were processed successfully")
            return pd.DataFrame()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from all operations.

        Returns:
            Dictionary with performance summary statistics.
        """
        if not self.metrics_history:
            return {"message": "No performance data available"}

        total_operations = len(self.metrics_history)
        total_duration = sum(m.duration for m in self.metrics_history)
        total_rows = sum(m.rows_processed for m in self.metrics_history)
        avg_memory = (
            sum(m.memory_usage_mb for m in self.metrics_history) / total_operations
        )
        max_memory = max(m.memory_usage_mb for m in self.metrics_history)

        return {
            "total_operations": total_operations,
            "total_duration_seconds": total_duration,
            "total_rows_processed": total_rows,
            "average_memory_mb": avg_memory,
            "peak_memory_mb": max_memory,
            "average_rows_per_second": total_rows / total_duration
            if total_duration > 0
            else 0,
            "operations": [m.operations_performed for m in self.metrics_history],
        }

    def optimize_chunk_size(
        self, df: pd.DataFrame, target_memory_mb: float = 500
    ) -> int:
        """Optimize chunk size based on DataFrame characteristics and memory constraints.

        Args:
            df: DataFrame to analyze.
            target_memory_mb: Target memory usage per chunk in MB.

        Returns:
            Optimized chunk size.
        """
        # Estimate memory usage per row
        sample_size = min(1000, len(df))
        if sample_size == 0:
            # Handle empty DataFrame
            return 1000  # Default chunk size for empty DataFrames

        sample = df.head(sample_size)
        sample_memory = sample.memory_usage(deep=True).sum()
        memory_per_row = sample_memory / sample_size if sample_size > 0 else 0

        # Calculate optimal chunk size
        target_memory_bytes = target_memory_mb * 1024 * 1024
        optimal_chunk_size = int(target_memory_bytes / memory_per_row)

        # Ensure reasonable bounds
        optimal_chunk_size = max(100, min(optimal_chunk_size, 50000))

        logger.info(f"Optimized chunk size: {optimal_chunk_size} rows")
        logger.info(
            f"Estimated memory per chunk: {optimal_chunk_size * memory_per_row / (1024*1024):.1f}MB"
        )

        return optimal_chunk_size

    def clear_history(self) -> None:
        """Clear performance metrics history."""
        self.metrics_history.clear()
        logger.info("Performance metrics history cleared")
