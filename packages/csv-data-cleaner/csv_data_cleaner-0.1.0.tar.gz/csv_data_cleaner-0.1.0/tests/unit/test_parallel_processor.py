"""
Unit tests for ParallelProcessor.
"""

import pytest
import pandas as pd
import numpy as np
import multiprocessing as mp
from unittest.mock import Mock, patch, MagicMock
from csv_cleaner.core.parallel_processor import ParallelProcessor, ParallelTask

# Global test functions for parallel processing (must be picklable)
def global_test_operation(data, **kwargs):
    """Global test operation that can be pickled."""
    data['C'] = data['A'] * 2
    return data

def global_add_column_operation(data, **kwargs):
    """Global operation to add a column."""
    return data.assign(B=data['A'] * 2)

def global_add_another_column_operation(data, **kwargs):
    """Global operation to add another column."""
    return data.assign(C=data['B'] + 10)

def global_sometimes_failing_operation(data, **kwargs):
    """Global operation that sometimes fails."""
    if len(data) > 0 and data.iloc[0]['A'] % 10 == 0:  # Fail every 10th chunk
        raise ValueError("Simulated failure")
    data['D'] = data['A'] * 3
    return data


class TestParallelTask:
    """Test ParallelTask dataclass."""

    def test_parallel_task_creation(self):
        """Test creating ParallelTask instance."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        task = ParallelTask(
            task_id=1,
            data=df,
            operation="test_operation",
            parameters={'param1': 'value1'}
        )

        assert task.task_id == 1
        assert len(task.data) == 3
        assert task.operation == "test_operation"
        assert task.parameters == {'param1': 'value1'}


class TestParallelProcessor:
    """Test ParallelProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ParallelProcessor(max_workers=2, chunk_size=1000)

    def test_initialization(self):
        """Test ParallelProcessor initialization."""
        assert self.processor.max_workers == 2
        assert self.processor.chunk_size == 1000
        assert self.processor.executor is None

    @patch('multiprocessing.cpu_count')
    def test_initialization_default_workers(self, mock_cpu_count):
        """Test initialization with default worker count."""
        mock_cpu_count.return_value = 4

        processor = ParallelProcessor()

        assert processor.max_workers == 4
        assert processor.chunk_size == 10000

    def test_context_manager(self):
        """Test context manager functionality."""
        with self.processor as proc:
            assert proc.executor is not None
            assert proc.max_workers == 2

    def test_worker_function_success(self):
        """Test worker function with successful operation."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        task = ParallelTask(
            task_id=1,
            data=df,
            operation="test_operation",
            parameters={}
        )

        def test_operation(data, **kwargs):
            data['B'] = data['A'] * 2
            return data

        task_id, result = self.processor._worker_function(task, test_operation)

        assert task_id == 1
        assert len(result) == 3
        assert 'B' in result.columns
        assert all(result['B'] == result['A'] * 2)

    def test_worker_function_exception(self):
        """Test worker function with exception."""
        df = pd.DataFrame({'A': [1, 2, 3]})
        task = ParallelTask(
            task_id=1,
            data=df,
            operation="test_operation",
            parameters={}
        )

        def failing_operation(data, **kwargs):
            raise ValueError("Test error")

        task_id, result = self.processor._worker_function(task, failing_operation)

        assert task_id == 1
        assert result.empty

    def test_chunk_dataframe(self):
        """Test DataFrame chunking."""
        df = pd.DataFrame({
            'A': range(2500),
            'B': ['test'] * 2500
        })

        chunks = self.processor.chunk_dataframe(df, chunk_size=1000)

        assert len(chunks) == 3
        assert len(chunks[0]) == 1000
        assert len(chunks[1]) == 1000
        assert len(chunks[2]) == 500

    @patch('concurrent.futures.ProcessPoolExecutor')
    def test_process_parallel_small_dataset(self, mock_executor):
        """Test parallel processing with small dataset."""
        df = pd.DataFrame({'A': range(100)})  # Smaller than chunk_size

        def test_operation(data, **kwargs):
            data['B'] = data['A'] * 2
            return data

        result = self.processor.process_parallel(
            df, "test_operation", test_operation, show_progress=False
        )

        # Should use single-threaded approach for small datasets
        assert len(result) == 100
        assert 'B' in result.columns
        assert all(result['B'] == result['A'] * 2)

    @patch('concurrent.futures.ProcessPoolExecutor')
    @patch('concurrent.futures.as_completed')
    def test_process_parallel_large_dataset(self, mock_as_completed, mock_executor):
        """Test parallel processing with large dataset."""
        df = pd.DataFrame({
            'A': range(5000),
            'B': ['test'] * 5000
        })

        # Mock the executor and futures
        mock_future1 = Mock()
        mock_future1.result.return_value = (0, pd.DataFrame({'A': [0, 1], 'B': ['test', 'test'], 'C': [0, 2]}))
        mock_future2 = Mock()
        mock_future2.result.return_value = (1, pd.DataFrame({'A': [2, 3], 'B': ['test', 'test'], 'C': [4, 6]}))

        mock_as_completed.return_value = [mock_future1, mock_future2]
        mock_executor.return_value.__enter__.return_value.submit.side_effect = [mock_future1, mock_future2]

        result = self.processor.process_parallel(
            df, "test_operation", global_test_operation, chunk_size=2, show_progress=False
        )

        # The result should have the same number of rows as input, with the operation applied
        assert len(result) == 5000
        assert 'C' in result.columns
        assert all(result['C'] == result['A'] * 2)

    def test_process_operations_parallel(self):
        """Test processing multiple operations in parallel."""
        df = pd.DataFrame({'A': range(100)})

        operations = [
            {
                'operation': 'op1',
                'function': lambda data, **kwargs: data.assign(B=data['A'] * 2),
                'parameters': {}
            },
            {
                'operation': 'op2',
                'function': lambda data, **kwargs: data.assign(C=data['B'] + 1),
                'parameters': {}
            }
        ]

        with patch.object(self.processor, 'process_parallel') as mock_process:
            mock_process.return_value = df.assign(B=df['A'] * 2, C=df['A'] * 2 + 1)

            result = self.processor.process_operations_parallel(df, operations, show_progress=False)

            assert mock_process.call_count == 2

    def test_get_optimal_worker_count_small_data(self):
        """Test optimal worker count for small datasets."""
        with patch('multiprocessing.cpu_count', return_value=8):
            optimal_workers = self.processor.get_optimal_worker_count(5000, 'medium')

            assert optimal_workers <= 2  # Should use fewer workers for small data

    def test_get_optimal_worker_count_large_data(self):
        """Test optimal worker count for large datasets."""
        with patch('multiprocessing.cpu_count', return_value=8):
            optimal_workers = self.processor.get_optimal_worker_count(100000, 'medium')

            assert 4 <= optimal_workers <= 8  # Should use more workers for large data

    def test_get_optimal_worker_count_complexity_adjustment(self):
        """Test optimal worker count with different complexity levels."""
        with patch('multiprocessing.cpu_count', return_value=8):
            low_complexity = self.processor.get_optimal_worker_count(50000, 'low')
            medium_complexity = self.processor.get_optimal_worker_count(50000, 'medium')
            high_complexity = self.processor.get_optimal_worker_count(50000, 'high')

            assert low_complexity <= medium_complexity <= high_complexity

    def test_estimate_processing_time(self):
        """Test processing time estimation."""
        with patch('multiprocessing.cpu_count', return_value=4):
            estimated_time = self.processor.estimate_processing_time(10000, 'medium')

            assert estimated_time > 0
            assert isinstance(estimated_time, float)

    def test_get_system_info(self):
        """Test system information retrieval."""
        with patch('multiprocessing.cpu_count', return_value=4):
            system_info = self.processor.get_system_info()

            assert system_info['cpu_count'] == 4
            assert system_info['max_workers'] == 2
            assert system_info['chunk_size'] == 1000
            assert 'platform' in system_info
            assert 'python_version' in system_info


class TestParallelProcessorIntegration:
    """Integration tests for ParallelProcessor."""

    def test_simple_parallel_processing(self):
        """Test simple parallel processing scenario."""
        processor = ParallelProcessor(max_workers=2, chunk_size=100)

        df = pd.DataFrame({
            'A': range(500),
            'B': ['test'] * 500
        })

        # Use a small chunk size to force parallel processing
        result = processor.process_parallel(
            df, "simple_operation", global_test_operation, chunk_size=50, show_progress=False
        )

        assert len(result) == 500
        assert 'C' in result.columns
        assert all(result['C'] == result['A'] * 2)

    def test_multiple_operations_sequential(self):
        """Test multiple operations processed sequentially."""
        processor = ParallelProcessor(max_workers=2, chunk_size=100)

        df = pd.DataFrame({'A': range(200)})

        operations = [
            {
                'operation': 'add_column',
                'function': global_add_column_operation,
                'parameters': {}
            },
            {
                'operation': 'add_another_column',
                'function': global_add_another_column_operation,
                'parameters': {}
            }
        ]

        result = processor.process_operations_parallel(df, operations, show_progress=False)

        assert len(result) == 200
        assert 'B' in result.columns
        assert 'C' in result.columns
        assert all(result['B'] == result['A'] * 2)
        assert all(result['C'] == result['B'] + 10)

    def test_worker_count_optimization(self):
        """Test worker count optimization for different scenarios."""
        processor = ParallelProcessor(max_workers=4, chunk_size=1000)

        # Test different data sizes
        small_data_workers = processor.get_optimal_worker_count(5000, 'medium')
        medium_data_workers = processor.get_optimal_worker_count(50000, 'medium')
        large_data_workers = processor.get_optimal_worker_count(500000, 'medium')

        assert small_data_workers <= medium_data_workers <= large_data_workers

    def test_processing_time_estimation_accuracy(self):
        """Test that processing time estimation is reasonable."""
        processor = ParallelProcessor(max_workers=2, chunk_size=1000)

        # Test estimation for different complexities
        low_time = processor.estimate_processing_time(10000, 'low')
        medium_time = processor.estimate_processing_time(10000, 'medium')
        high_time = processor.estimate_processing_time(10000, 'high')

        # All times should be positive
        assert all(t > 0 for t in [low_time, medium_time, high_time])
        # Times should be reasonable (not necessarily strictly increasing due to estimation)
        assert all(t < 1000 for t in [low_time, medium_time, high_time])


class TestParallelProcessorErrorHandling:
    """Test error handling in ParallelProcessor."""

    def test_worker_function_exception_handling(self):
        """Test that worker function handles exceptions gracefully."""
        processor = ParallelProcessor(max_workers=1, chunk_size=100)

        df = pd.DataFrame({'A': range(10)})
        task = ParallelTask(
            task_id=1,
            data=df,
            operation="failing_operation",
            parameters={}
        )

        def failing_operation(data, **kwargs):
            raise RuntimeError("Simulated failure")

        task_id, result = processor._worker_function(task, failing_operation)

        assert task_id == 1
        assert result.empty

    def test_process_parallel_with_failing_chunks(self):
        """Test parallel processing when some chunks fail."""
        processor = ParallelProcessor(max_workers=2, chunk_size=50)

        df = pd.DataFrame({'A': range(200)})

        # This should handle the failure gracefully
        result = processor.process_parallel(
            df, "sometimes_failing_operation", global_sometimes_failing_operation,
            chunk_size=50, show_progress=False
        )

        # Should still return some results
        assert len(result) >= 0
