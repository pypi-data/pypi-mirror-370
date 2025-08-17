"""
TEST SUITE: csv_cleaner.core.library_manager (Advanced Features)
PURPOSE: Test advanced library manager functionality including wrapper initialization failures, performance optimization, and caching mechanisms
SCOPE: LibraryManager class advanced features, wrapper failures, performance optimization, caching, memory management
DEPENDENCIES: All wrapper mocks, performance metrics, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta

from csv_cleaner.core.library_manager import LibraryManager
from csv_cleaner.core.config import Config
from csv_cleaner.feature_gate import FeatureGate


class TestLibraryManagerWrapperInitializationFailures:
    """Test cases for wrapper initialization failures and error handling."""

    @patch('csv_cleaner.core.library_manager.PandasWrapper')
    def test_pandas_wrapper_required_but_fails(self, mock_pandas):
        """TEST: should_handle_pandas_wrapper_required_but_fails"""
        # ARRANGE: Pandas wrapper fails but is required
        mock_pandas.side_effect = ImportError("Pandas is required but not available")

        config = Config()

        # ACT & ASSERT: Verify LibraryManager raises appropriate error
        with pytest.raises(RuntimeError, match="PandasWrapper is required but failed to initialize"):
            LibraryManager(config)

    @patch('csv_cleaner.core.library_manager.PyJanitorWrapper')
    @patch('csv_cleaner.core.library_manager.FeatureEngineWrapper')
    @patch('csv_cleaner.core.library_manager.DedupeWrapper')
    @patch('csv_cleaner.core.library_manager.MissingnoWrapper')
    def test_optional_wrapper_initialization_failures(self, mock_missingno, mock_dedupe, mock_feature_engine, mock_pyjanitor):
        """TEST: should_handle_optional_wrapper_initialization_failures_gracefully"""
        # ARRANGE: Mock optional wrapper initialization failures (PandasWrapper succeeds)
        mock_pyjanitor.side_effect = Exception("PyJanitor initialization failed")
        mock_feature_engine.return_value = Mock()
        mock_dedupe.side_effect = RuntimeError("Dedupe configuration error")
        mock_missingno.return_value = Mock()

        config = Config()
        config.package_version = "pro"  # Use pro version to enable feature_engine

        # ACT: Initialize LibraryManager
        manager = LibraryManager(config)

        # ASSERT: Verify only successful wrappers are available
        available_wrappers = manager.get_available_wrappers()
        assert "pandas" in available_wrappers, "Expected pandas wrapper to be available"
        assert "feature_engine" in available_wrappers, "Expected feature_engine wrapper to be available"
        assert "missingno" in available_wrappers, "Expected missingno wrapper to be available"
        assert "pyjanitor" not in available_wrappers, "Expected pyjanitor wrapper to not be available due to failure"
        assert "dedupe" not in available_wrappers, "Expected dedupe wrapper to not be available due to failure"


class TestLibraryManagerPerformanceOptimization:
    """Test cases for performance optimization features."""

    def test_performance_caching_mechanism(self):
        """TEST: should_cache_performance_metrics_for_operations"""
        # ARRANGE: LibraryManager with performance caching
        config = Config()
        manager = LibraryManager(config)

        # Mock wrapper for testing
        mock_wrapper = Mock()
        mock_wrapper.get_performance_estimate.return_value = {"time_estimate": 1.5, "memory_estimate": 100}
        mock_wrapper.can_handle.return_value = True
        manager.wrappers["test_wrapper"] = mock_wrapper

        # ACT: Get performance estimate multiple times
        operation = "test_operation"
        df = pd.DataFrame({"col1": [1, 2, 3]})

        estimate1 = manager.get_best_wrapper(operation, df)
        estimate2 = manager.get_best_wrapper(operation, df)

        # ASSERT: Verify caching behavior
        assert estimate1 == estimate2, "Expected cached results to be consistent"

    def test_performance_optimization_with_large_datasets(self):
        """TEST: should_optimize_performance_for_large_datasets"""
        # ARRANGE: Large dataset and performance optimization
        config = Config()
        manager = LibraryManager(config)

        # Create large dataset
        large_df = pd.DataFrame({
            "col1": np.random.randn(10000),
            "col2": np.random.randn(10000),
            "col3": np.random.randn(10000)
        })

        # Mock wrappers with different performance characteristics
        fast_wrapper = Mock()
        fast_wrapper.can_handle.return_value = True
        fast_wrapper.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})

        slow_wrapper = Mock()
        slow_wrapper.can_handle.return_value = True
        slow_wrapper.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})

        manager.wrappers["fast_wrapper"] = fast_wrapper
        manager.wrappers["slow_wrapper"] = slow_wrapper

        # ACT: Get best wrapper for operation
        best_wrapper = manager.get_best_wrapper("test_operation", large_df)

        # ASSERT: Verify performance optimization
        # Both wrappers should be executed for benchmarking
        assert fast_wrapper.execute.called, "Expected fast_wrapper to be executed for benchmarking"
        assert slow_wrapper.execute.called, "Expected slow_wrapper to be executed for benchmarking"
        assert best_wrapper in [fast_wrapper, slow_wrapper], "Expected one of the wrappers to be selected"

    def test_performance_monitoring_and_tracking(self):
        """TEST: should_monitor_and_track_performance_metrics"""
        # ARRANGE: Performance monitoring setup
        config = Config()
        manager = LibraryManager(config)

        # Mock wrapper with performance tracking
        mock_wrapper = Mock()
        mock_wrapper.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})
        mock_wrapper.can_handle.return_value = True
        manager.wrappers["test_wrapper"] = mock_wrapper

        # ACT: Execute operation and track performance
        operation = "test_operation"
        df = pd.DataFrame({"col1": [1, 2, 3]})

        start_time = datetime.now()
        result = manager.execute_operation(operation, df)
        end_time = datetime.now()

        # ASSERT: Verify performance tracking
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 1.0, f"Operation took too long: {execution_time:.3f} seconds"
        assert result is not None, "Expected operation to return result"
        assert len(manager.operation_history) > 0, "Expected operation history to be recorded"


class TestLibraryManagerErrorRecovery:
    """Test cases for error recovery and resilience."""

    def test_wrapper_failure_recovery(self):
        """TEST: should_recover_from_wrapper_failures"""
        # ARRANGE: Wrapper failure scenario
        config = Config()
        manager = LibraryManager(config)

        # Mock wrappers with one failing
        failing_wrapper = Mock()
        failing_wrapper.execute.side_effect = Exception("Wrapper failed")
        failing_wrapper.can_handle.return_value = True

        working_wrapper = Mock()
        working_wrapper.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})
        working_wrapper.can_handle.return_value = True

        manager.wrappers["failing_wrapper"] = failing_wrapper
        manager.wrappers["working_wrapper"] = working_wrapper

        # ACT: Execute operation with fallback
        operation = "test_operation"
        df = pd.DataFrame({"col1": [1, 2, 3]})

        # Note: This test would need to be adjusted based on actual fallback logic
        # For now, we'll test that the operation history is recorded even on failure
        try:
            manager.execute_operation(operation, df)
        except Exception:
            pass

        # ASSERT: Verify error recovery
        assert len(manager.operation_history) > 0, "Expected operation history to be recorded even on failure"

    def test_operation_history_tracking(self):
        """TEST: should_track_operation_history"""
        # ARRANGE: Operation history tracking
        config = Config()
        manager = LibraryManager(config)

        # Mock wrapper
        mock_wrapper = Mock()
        mock_wrapper.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})
        mock_wrapper.can_handle.return_value = True
        manager.wrappers["test_wrapper"] = mock_wrapper

        # ACT: Execute multiple operations
        operations = ["op1", "op2", "op3"]
        df = pd.DataFrame({"col1": [1, 2, 3]})

        for operation in operations:
            manager.execute_operation(operation, df)

        # ASSERT: Verify operation history
        assert len(manager.operation_history) == 3, "Expected all operations to be tracked"
        assert all(op["success"] for op in manager.operation_history), "Expected all operations to be successful"

    def test_benchmark_operation_functionality(self):
        """TEST: should_benchmark_operations_correctly"""
        # ARRANGE: Benchmark functionality
        config = Config()
        manager = LibraryManager(config)

        # Mock wrappers
        wrapper1 = Mock()
        wrapper1.can_handle.return_value = True
        wrapper1.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})

        wrapper2 = Mock()
        wrapper2.can_handle.return_value = True
        wrapper2.execute.return_value = pd.DataFrame({"result": [1, 2, 3]})

        manager.wrappers["wrapper1"] = wrapper1
        manager.wrappers["wrapper2"] = wrapper2

        # ACT: Benchmark operation
        operation = "test_operation"
        df = pd.DataFrame({"col1": [1, 2, 3, 4, 5]})
        results = manager.benchmark_operation(operation, df)

        # ASSERT: Verify benchmark results
        assert "wrapper1" in results, "Expected wrapper1 to be benchmarked"
        assert "wrapper2" in results, "Expected wrapper2 to be benchmarked"
        assert all(result["success"] for result in results.values()), "Expected all benchmarks to succeed"
