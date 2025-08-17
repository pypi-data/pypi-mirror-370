"""
Parallel processor for CSV Data Cleaner.
Handles parallel processing of data using multiprocessing.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Tuple
import time
import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParallelTask:
    """Represents a task for parallel processing."""

    task_id: int
    data: pd.DataFrame
    operation: str
    parameters: Dict[str, Any]


class ParallelProcessor:
    """Manages parallel processing of data operations."""

    def __init__(self, max_workers: Optional[int] = None, chunk_size: int = 10000):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker processes (defaults to CPU count).
            chunk_size: Size of chunks for parallel processing.
        """
        self.max_workers = max_workers or min(
            mp.cpu_count(), 8
        )  # Limit to 8 workers max
        self.chunk_size = chunk_size
        self.executor = None

        logger.info(f"Initialized ParallelProcessor with {self.max_workers} workers")

    def __enter__(self):
        """Context manager entry."""
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.executor:
            self.executor.shutdown(wait=True)

    def _worker_function(
        self, task: ParallelTask, operation_func: Callable
    ) -> Tuple[int, pd.DataFrame]:
        """Worker function for parallel processing.

        Args:
            task: Task to process.
            operation_func: Function to apply to the data.

        Returns:
            Tuple of (task_id, processed_dataframe).
        """
        try:
            # Apply operation to the chunk
            result = operation_func(task.data, **task.parameters)
            return task.task_id, result
        except Exception as e:
            logger.error(f"Error in worker {task.task_id}: {str(e)}")
            # Return empty DataFrame on error
            return task.task_id, pd.DataFrame()

    def chunk_dataframe(
        self, df: pd.DataFrame, chunk_size: Optional[int] = None
    ) -> List[pd.DataFrame]:
        """Split DataFrame into chunks for parallel processing.

        Args:
            df: DataFrame to chunk.
            chunk_size: Size of each chunk.

        Returns:
            List of DataFrame chunks.
        """
        chunk_size = chunk_size or self.chunk_size
        chunks = []

        for start_idx in range(0, len(df), chunk_size):
            end_idx = min(start_idx + chunk_size, len(df))
            chunk = df.iloc[start_idx:end_idx].copy()
            chunks.append(chunk)

        logger.info(
            f"Split DataFrame into {len(chunks)} chunks of ~{chunk_size} rows each"
        )
        return chunks

    def process_parallel(
        self,
        df: pd.DataFrame,
        operation: str,
        operation_func: Callable,
        parameters: Optional[Dict[str, Any]] = None,
        chunk_size: Optional[int] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """Process DataFrame in parallel.

        Args:
            df: DataFrame to process.
            operation: Name of the operation.
            operation_func: Function to apply to each chunk.
            parameters: Parameters to pass to the operation function.
            chunk_size: Size of chunks for processing.
            show_progress: Whether to show progress information.

        Returns:
            Processed DataFrame.
        """
        if len(df) < self.chunk_size:
            logger.info(
                "DataFrame too small for parallel processing, using single-threaded approach"
            )
            return operation_func(df, **(parameters or {}))

        chunk_size = chunk_size or self.chunk_size
        parameters = parameters or {}

        # Split data into chunks
        chunks = self.chunk_dataframe(df, chunk_size)

        # Create tasks
        tasks = [
            ParallelTask(i, chunk, operation, parameters)
            for i, chunk in enumerate(chunks)
        ]

        logger.info(
            f"Starting parallel processing of {len(tasks)} chunks with {self.max_workers} workers"
        )
        start_time = time.time()

        # Process chunks in parallel
        results = []
        completed_tasks = 0

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._worker_function, task, operation_func): task
                for task in tasks
            }

            # Collect results as they complete
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    task_id, result = future.result()
                    results.append((task_id, result))
                    completed_tasks += 1

                    if show_progress:
                        progress = (completed_tasks / len(tasks)) * 100
                        logger.info(
                            f"Progress: {progress:.1f}% ({completed_tasks}/{len(tasks)} chunks)"
                        )

                except Exception as e:
                    logger.error(f"Task {task.task_id} failed: {str(e)}")
                    # Add empty DataFrame for failed task
                    results.append((task.task_id, pd.DataFrame()))

        # Sort results by task ID to maintain order
        results.sort(key=lambda x: x[0])
        processed_chunks = [result for _, result in results]

        # Combine results
        if processed_chunks:
            final_result = pd.concat(processed_chunks, ignore_index=True)
            processing_time = time.time() - start_time

            logger.info(f"Parallel processing completed in {processing_time:.2f}s")
            logger.info(f"Processed {len(final_result)} rows from {len(chunks)} chunks")

            return final_result
        else:
            logger.warning("No chunks were processed successfully")
            return pd.DataFrame()

    def process_operations_parallel(
        self,
        df: pd.DataFrame,
        operations: List[Dict[str, Any]],
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """Process multiple operations in parallel.

        Args:
            df: DataFrame to process.
            operations: List of operation dictionaries with 'operation' and 'parameters' keys.
            show_progress: Whether to show progress information.

        Returns:
            DataFrame after all operations.
        """
        if not operations:
            return df

        current_df = df

        for i, op_config in enumerate(operations):
            operation_name = op_config.get("operation")
            parameters = op_config.get("parameters", {})
            operation_func = op_config.get("function")

            if not operation_func:
                logger.warning(f"No function provided for operation: {operation_name}")
                continue

            logger.info(
                f"Processing operation {i+1}/{len(operations)}: {operation_name}"
            )

            current_df = self.process_parallel(
                current_df,
                operation_name,
                operation_func,
                parameters,
                show_progress=show_progress,
            )

            if current_df.empty:
                logger.error(f"Operation {operation_name} failed, stopping processing")
                break

        return current_df

    def get_optimal_worker_count(
        self, data_size: int, operation_complexity: str = "medium"
    ) -> int:
        """Get optimal number of workers based on data size and operation complexity.

        Args:
            data_size: Number of rows in the dataset.
            operation_complexity: Complexity of the operation ('low', 'medium', 'high').

        Returns:
            Optimal number of workers.
        """
        cpu_count = mp.cpu_count()

        # Base worker count on CPU cores
        base_workers = cpu_count

        # Adjust based on data size
        if data_size < 10000:
            # Small datasets: use fewer workers to avoid overhead
            optimal_workers = max(1, min(2, base_workers))
        elif data_size < 100000:
            # Medium datasets: use moderate number of workers
            optimal_workers = max(2, min(4, base_workers))
        else:
            # Large datasets: use more workers
            optimal_workers = max(4, min(8, base_workers))

        # Adjust based on operation complexity
        complexity_multipliers = {
            "low": 0.5,  # Simple operations: fewer workers
            "medium": 1.0,  # Standard operations: normal workers
            "high": 1.5,  # Complex operations: more workers
        }

        multiplier = complexity_multipliers.get(operation_complexity, 1.0)
        optimal_workers = int(optimal_workers * multiplier)

        # Ensure reasonable bounds
        optimal_workers = max(1, min(optimal_workers, cpu_count))

        logger.info(
            f"Optimal worker count: {optimal_workers} (data_size={data_size}, complexity={operation_complexity})"
        )
        return optimal_workers

    def estimate_processing_time(
        self, data_size: int, operation_complexity: str = "medium"
    ) -> float:
        """Estimate processing time for parallel operations.

        Args:
            data_size: Number of rows in the dataset.
            operation_complexity: Complexity of the operation.

        Returns:
            Estimated processing time in seconds.
        """
        # Base processing rates (rows per second per worker)
        base_rates = {
            "low": 10000,  # Simple operations
            "medium": 5000,  # Standard operations
            "high": 1000,  # Complex operations
        }

        base_rate = base_rates.get(operation_complexity, 5000)
        worker_count = self.get_optimal_worker_count(data_size, operation_complexity)

        # Estimate time with parallel processing
        estimated_time = data_size / (base_rate * worker_count)

        # Add overhead for parallel processing
        overhead_multiplier = 1.2  # 20% overhead
        estimated_time *= overhead_multiplier

        logger.info(
            f"Estimated processing time: {estimated_time:.2f}s for {data_size} rows"
        )
        return estimated_time

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for parallel processing.

        Returns:
            Dictionary with system information.
        """
        return {
            "cpu_count": mp.cpu_count(),
            "max_workers": self.max_workers,
            "chunk_size": self.chunk_size,
            "platform": os.name,
            "python_version": f"{mp.sys.version_info.major}.{mp.sys.version_info.minor}",
        }
