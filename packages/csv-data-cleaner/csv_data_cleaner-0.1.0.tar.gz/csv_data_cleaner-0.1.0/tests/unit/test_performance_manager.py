"""
Unit tests for PerformanceManager.
"""

import pytest
import pandas as pd
import numpy as np
import time
from unittest.mock import Mock, patch
from csv_cleaner.core.performance_manager import PerformanceManager, PerformanceMetrics


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass."""

    def test_performance_metrics_creation(self):
        """Test creating PerformanceMetrics instance."""
        metrics = PerformanceMetrics(
            start_time=100.0,
            end_time=110.0,
            memory_peak=1024 * 1024,  # 1MB
            memory_avg=512 * 1024,    # 0.5MB
            chunks_processed=5,
            rows_processed=1000,
            operations_performed=['test_op']
        )

        assert metrics.duration == 10.0
        assert metrics.rows_per_second == 100.0
        assert metrics.memory_usage_mb == 1.0

    def test_performance_metrics_zero_duration(self):
        """Test PerformanceMetrics with zero duration."""
        metrics = PerformanceMetrics(
            start_time=100.0,
            end_time=100.0,
            memory_peak=1024 * 1024,
            memory_avg=512 * 1024,
            chunks_processed=0,
            rows_processed=0,
            operations_performed=[]
        )

        assert metrics.duration == 0.0
        assert metrics.rows_per_second == 0.0


class TestPerformanceManager:
    """Test PerformanceManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.performance_manager = PerformanceManager(max_memory_gb=1.0, chunk_size=1000)

    def test_initialization(self):
        """Test PerformanceManager initialization."""
        assert self.performance_manager.max_memory_gb == 1.0
        assert self.performance_manager.max_memory_bytes == 1024 * 1024 * 1024
        assert self.performance_manager.chunk_size == 1000
        assert len(self.performance_manager.metrics_history) == 0

    def test_start_operation(self):
        """Test starting an operation."""
        self.performance_manager.start_operation("test_operation")

        assert self.performance_manager._current_operation == "test_operation"
        assert self.performance_manager._start_time is not None
        assert len(self.performance_manager._memory_samples) == 0

    def test_end_operation(self):
        """Test ending an operation."""
        self.performance_manager.start_operation("test_operation")
        time.sleep(0.1)  # Small delay to ensure measurable duration

        metrics = self.performance_manager.end_operation(
            chunks_processed=2,
            rows_processed=500,
            operations_performed=['test_op']
        )

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.chunks_processed == 2
        assert metrics.rows_processed == 500
        assert metrics.operations_performed == ['test_op']
        assert metrics.duration > 0
        assert len(self.performance_manager.metrics_history) == 1

    def test_end_operation_without_start(self):
        """Test ending operation without starting it."""
        with pytest.raises(ValueError, match="No operation started"):
            self.performance_manager.end_operation()

    @patch('psutil.Process')
    def test_sample_memory(self, mock_process):
        """Test memory sampling."""
        mock_process.return_value.memory_info.return_value.rss = 1024 * 1024  # 1MB

        memory_bytes = self.performance_manager.sample_memory()

        assert memory_bytes == 1024 * 1024
        assert len(self.performance_manager._memory_samples) == 1

    @patch('psutil.Process')
    def test_check_memory_limit_within_bounds(self, mock_process):
        """Test memory limit check when within bounds."""
        mock_process.return_value.memory_info.return_value.rss = 512 * 1024 * 1024  # 0.5GB

        result = self.performance_manager.check_memory_limit()

        assert result is True

    @patch('psutil.Process')
    def test_check_memory_limit_exceeded(self, mock_process):
        """Test memory limit check when exceeded."""
        mock_process.return_value.memory_info.return_value.rss = 2 * 1024 * 1024 * 1024  # 2GB

        result = self.performance_manager.check_memory_limit()

        assert result is False

    @patch('gc.collect')
    def test_force_garbage_collection(self, mock_gc):
        """Test forced garbage collection."""
        mock_gc.return_value = 10

        self.performance_manager.force_garbage_collection()

        mock_gc.assert_called_once()

    def test_memory_monitoring_context_manager(self):
        """Test memory monitoring context manager."""
        with patch.object(self.performance_manager, 'sample_memory') as mock_sample:
            with self.performance_manager.memory_monitoring():
                pass

            assert mock_sample.call_count == 2  # Called at start and end

    def test_chunk_dataframe(self):
        """Test DataFrame chunking."""
        # Create test DataFrame
        df = pd.DataFrame({
            'A': range(2500),
            'B': ['test'] * 2500
        })

        chunks = list(self.performance_manager.chunk_dataframe(df, chunk_size=1000))

        assert len(chunks) == 3
        assert len(chunks[0]) == 1000
        assert len(chunks[1]) == 1000
        assert len(chunks[2]) == 500

    def test_process_in_chunks(self):
        """Test processing DataFrame in chunks."""
        # Create test DataFrame
        df = pd.DataFrame({
            'A': range(2500),
            'B': ['test'] * 2500
        })

        def test_operation(chunk_df):
            # Simple operation that adds a new column
            chunk_df['C'] = chunk_df['A'] * 2
            return chunk_df

        with patch.object(self.performance_manager, 'check_memory_limit', return_value=True):
            with patch.object(self.performance_manager, 'force_garbage_collection'):
                result = self.performance_manager.process_in_chunks(
                    df, test_operation, chunk_size=1000, show_progress=False
                )

        assert len(result) == 2500
        assert 'C' in result.columns
        assert all(result['C'] == result['A'] * 2)

    def test_process_in_chunks_memory_limit_exceeded(self):
        """Test chunked processing with memory limit exceeded."""
        df = pd.DataFrame({'A': range(100)})

        def test_operation(chunk_df):
            return chunk_df

        with patch.object(self.performance_manager, 'check_memory_limit', return_value=False):
            with pytest.raises(MemoryError, match="Memory limit exceeded"):
                self.performance_manager.process_in_chunks(df, test_operation)

    def test_get_performance_summary_empty(self):
        """Test performance summary with no history."""
        summary = self.performance_manager.get_performance_summary()

        assert summary['message'] == "No performance data available"

    def test_get_performance_summary_with_data(self):
        """Test performance summary with metrics history."""
        # Add some test metrics
        self.performance_manager.metrics_history = [
            PerformanceMetrics(
                start_time=100.0,
                end_time=110.0,
                memory_peak=1024 * 1024,
                memory_avg=512 * 1024,
                chunks_processed=2,
                rows_processed=1000,
                operations_performed=['test_op']
            ),
            PerformanceMetrics(
                start_time=110.0,
                end_time=115.0,
                memory_peak=2048 * 1024,
                memory_avg=1024 * 1024,
                chunks_processed=1,
                rows_processed=500,
                operations_performed=['test_op2']
            )
        ]

        summary = self.performance_manager.get_performance_summary()

        assert summary['total_operations'] == 2
        assert summary['total_duration_seconds'] == 15.0
        assert summary['total_rows_processed'] == 1500
        assert summary['average_memory_mb'] == 1.5
        assert summary['peak_memory_mb'] == 2.0

    def test_optimize_chunk_size(self):
        """Test chunk size optimization."""
        # Create test DataFrame with known memory characteristics
        df = pd.DataFrame({
            'A': range(1000),
            'B': ['test'] * 1000,
            'C': [1.5] * 1000
        })

        optimal_size = self.performance_manager.optimize_chunk_size(df, target_memory_mb=1.0)

        assert 100 <= optimal_size <= 50000  # Within reasonable bounds

    def test_clear_history(self):
        """Test clearing performance metrics history."""
        # Add some test metrics
        self.performance_manager.metrics_history = [
            PerformanceMetrics(
                start_time=100.0,
                end_time=110.0,
                memory_peak=1024 * 1024,
                memory_avg=512 * 1024,
                chunks_processed=1,
                rows_processed=100,
                operations_performed=['test_op']
            )
        ]

        self.performance_manager.clear_history()

        assert len(self.performance_manager.metrics_history) == 0


class TestPerformanceManagerIntegration:
    """Integration tests for PerformanceManager."""

    def test_full_operation_cycle(self):
        """Test complete operation cycle with real data."""
        performance_manager = PerformanceManager(max_memory_gb=1.0, chunk_size=500)

        # Create test DataFrame
        df = pd.DataFrame({
            'A': range(2000),
            'B': ['test'] * 2000,
            'C': np.random.randn(2000)
        })

        def complex_operation(chunk_df):
            # Simulate complex operation
            chunk_df['D'] = chunk_df['A'] + chunk_df['C']
            chunk_df['E'] = chunk_df['B'].str.upper()
            return chunk_df

        # Process in chunks (this will handle its own operation tracking)
        with patch.object(performance_manager, 'check_memory_limit', return_value=True):
            with patch.object(performance_manager, 'force_garbage_collection'):
                result = performance_manager.process_in_chunks(
                    df, complex_operation, chunk_size=500, show_progress=False
                )

        # Get metrics from the last operation in history
        metrics = performance_manager.metrics_history[-1] if performance_manager.metrics_history else None

        # Verify results
        assert len(result) == 2000
        assert 'D' in result.columns
        assert 'E' in result.columns
        assert metrics.chunks_processed == 4
        assert metrics.rows_processed == 2000
        assert metrics.duration > 0
        assert metrics.memory_usage_mb > 0
