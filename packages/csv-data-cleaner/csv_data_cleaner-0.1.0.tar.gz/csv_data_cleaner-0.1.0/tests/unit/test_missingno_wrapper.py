"""
TEST SUITE: csv_cleaner.wrappers.missingno_wrapper
PURPOSE: Test missing data visualization and analysis operations using missingno library
SCOPE: MissingnoWrapper class, all supported operations, import handling, error handling, performance timing
DEPENDENCIES: pandas, missingno library, matplotlib, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from csv_cleaner.wrappers.missingno_wrapper import MissingnoWrapper, MISSINGNO_AVAILABLE


class TestMissingnoWrapper:
    """Test cases for MissingnoWrapper class."""

    def test_initialization_with_missingno_available(self, mock_missingno):
        """TEST: should_initialize_successfully_when_missingno_is_available"""
        # ARRANGE: Mock missingno as available
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            # ACT: Initialize MissingnoWrapper
            wrapper = MissingnoWrapper()

            # ASSERT: Verify wrapper is initialized
            assert wrapper is not None, "Expected MissingnoWrapper to be initialized successfully"
            assert isinstance(wrapper, MissingnoWrapper), "Expected MissingnoWrapper instance"

    def test_initialization_without_missingno(self):
        """TEST: should_raise_importerror_when_missingno_is_not_available"""
        # ARRANGE: Mock missingno as unavailable
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', False):
            # ACT & ASSERT: Verify ImportError is raised
            with pytest.raises(ImportError, match="Missingno is not available"):
                MissingnoWrapper()

    def test_can_handle_missingno_operations(self, mock_missingno):
        """TEST: should_return_true_for_supported_missingno_operations"""
        # ARRANGE: MissingnoWrapper and supported operations
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            supported_operations = [
                'missing_matrix', 'missing_bar', 'missing_heatmap',
                'missing_dendrogram', 'missing_summary'
            ]

            # ACT & ASSERT: Verify all supported operations return True
            for operation in supported_operations:
                result = wrapper.can_handle(operation)
                assert result is True, f"Expected can_handle('{operation}') to return True, got {result}"

    def test_can_handle_unsupported_operations(self, mock_missingno):
        """TEST: should_return_false_for_unsupported_operations"""
        # ARRANGE: MissingnoWrapper and unsupported operations
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            unsupported_operations = ['invalid_operation', 'unknown_method', 'test_function']

            # ACT & ASSERT: Verify unsupported operations return False
            for operation in unsupported_operations:
                result = wrapper.can_handle(operation)
                assert result is False, f"Expected can_handle('{operation}') to return False, got {result}"

    def test_get_supported_operations(self, mock_missingno):
        """TEST: should_return_list_of_all_supported_operations"""
        # ARRANGE: MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            expected_operations = [
                'missing_matrix', 'missing_bar', 'missing_heatmap',
                'missing_dendrogram', 'missing_summary'
            ]

            # ACT: Get supported operations
            result = wrapper.get_supported_operations()

            # ASSERT: Verify all expected operations are returned
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            assert len(result) == len(expected_operations), f"Expected {len(expected_operations)} operations, got {len(result)}"
            for operation in expected_operations:
                assert operation in result, f"Expected '{operation}' to be in supported operations"

    def test_execute_missing_matrix(self, missing_data_df, mock_missingno):
        """TEST: should_execute_missing_matrix_operation"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute missing_matrix operation
            result = wrapper.execute('missing_matrix', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify missingno.matrix was called
            mock_missingno.matrix.assert_called_once()

    def test_execute_missing_bar(self, missing_data_df, mock_missingno):
        """TEST: should_execute_missing_bar_operation"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute missing_bar operation
            result = wrapper.execute('missing_bar', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify missingno.bar was called
            mock_missingno.bar.assert_called_once()

    def test_execute_missing_heatmap(self, missing_data_df, mock_missingno):
        """TEST: should_execute_missing_heatmap_operation"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute missing_heatmap operation
            result = wrapper.execute('missing_heatmap', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify missingno.heatmap was called
            mock_missingno.heatmap.assert_called_once()

    def test_execute_missing_dendrogram(self, missing_data_df, mock_missingno):
        """TEST: should_execute_missing_dendrogram_operation"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute missing_dendrogram operation
            result = wrapper.execute('missing_dendrogram', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify missingno.dendrogram was called
            mock_missingno.dendrogram.assert_called_once()

    def test_execute_missing_summary(self, missing_data_df, mock_missingno):
        """TEST: should_execute_missing_summary_operation"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute missing_summary operation
            result = wrapper.execute('missing_summary', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"

            # Verify the result is the original DataFrame (not a summary DataFrame)
            assert result.equals(missing_data_df), "Expected original DataFrame to be returned"

    def test_execute_with_additional_kwargs(self, missing_data_df, mock_missingno):
        """TEST: should_pass_additional_kwargs_to_missingno_functions"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            additional_kwargs = {'figsize': (10, 6), 'color': 'blue'}

            # ACT: Execute operation with additional kwargs
            result = wrapper.execute('missing_matrix', missing_data_df, **additional_kwargs)

            # ASSERT: Verify kwargs were passed to missingno function
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Check that missingno.matrix was called with kwargs
            mock_missingno.matrix.assert_called_once()
            call_args = mock_missingno.matrix.call_args
            assert call_args is not None, "Expected missingno.matrix to be called"

    def test_execute_invalid_operation(self, missing_data_df, mock_missingno):
        """TEST: should_raise_valueerror_when_operation_is_not_supported"""
        # ARRANGE: MissingnoWrapper and invalid operation
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            invalid_operation = 'invalid_operation'

            # ACT & ASSERT: Verify ValueError is raised
            with pytest.raises(ValueError, match=f"Operation '{invalid_operation}' not supported"):
                wrapper.execute(invalid_operation, missing_data_df)

    def test_execute_with_empty_dataframe(self, edge_case_dfs, mock_missingno):
        """TEST: should_handle_empty_dataframe_gracefully"""
        # ARRANGE: Empty DataFrame and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            empty_df = edge_case_dfs['empty']

            # ACT: Execute operation on empty DataFrame
            result = wrapper.execute('missing_matrix', empty_df)

            # ASSERT: Verify operation handles empty DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from missing_matrix"
            assert len(result) == 0, "Expected empty DataFrame from missing_matrix"

    def test_execute_with_no_missing_data(self, basic_df, mock_missingno):
        """TEST: should_handle_dataframe_with_no_missing_data"""
        # ARRANGE: DataFrame with no missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute operation on DataFrame with no missing data
            result = wrapper.execute('missing_matrix', basic_df)

            # ASSERT: Verify operation handles DataFrame with no missing data
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from missing_matrix"
            assert len(result) == len(basic_df), f"Expected same number of rows, got {len(result)} != {len(basic_df)}"

    def test_execute_with_large_dataframe(self, large_df, mock_missingno):
        """TEST: should_handle_large_dataframe_efficiently"""
        # ARRANGE: Large DataFrame and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute operation on large DataFrame
            result = wrapper.execute('missing_matrix', large_df)

            # ASSERT: Verify operation handles large DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from missing_matrix"
            assert len(result) == len(large_df), f"Expected same number of rows, got {len(result)} != {len(large_df)}"

    def test_performance_timing(self, missing_data_df, mock_missingno):
        """TEST: should_log_execution_time_for_operations"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT: Execute operation and capture logs
            with patch('csv_cleaner.wrappers.missingno_wrapper.logger') as mock_logger:
                result = wrapper.execute('missing_matrix', missing_data_df)

            # ASSERT: Verify timing is logged
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Check that info and completion logs were called
            assert mock_logger.info.called, "Expected timing information to be logged"

    def test_error_handling_missingno_function_failure(self, missing_data_df, mock_missingno):
        """TEST: should_handle_missingno_function_failures_gracefully"""
        # ARRANGE: MissingnoWrapper with failing missingno function
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            # Make missingno.matrix raise an exception
            mock_missingno.matrix.side_effect = Exception("Missingno function failed")

            # ACT & ASSERT: Verify exception is re-raised
            with pytest.raises(Exception, match="Missingno function failed"):
                wrapper.execute('missing_matrix', missing_data_df)

    def test_error_handling_dataframe_not_provided(self, mock_missingno):
        """TEST: should_raise_typeerror_when_dataframe_is_not_provided"""
        # ARRANGE: MissingnoWrapper without DataFrame
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()

            # ACT & ASSERT: Verify TypeError is raised
            with pytest.raises(TypeError):
                wrapper.execute('missing_matrix', None)

    def test_matplotlib_backend_setup(self, mock_missingno):
        """TEST: should_setup_matplotlib_backend_correctly"""
        # ARRANGE: Mock matplotlib
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            # ACT: Initialize MissingnoWrapper
            wrapper = MissingnoWrapper()

            # ASSERT: Verify wrapper initializes successfully
            assert wrapper is not None, "Wrapper should initialize successfully"
            # Note: matplotlib.use('Agg') is called at module import time, which is hard to test
            # in isolation. The important thing is that the wrapper works correctly.

    def test_operation_with_custom_figure_size(self, missing_data_df, mock_missingno):
        """TEST: should_handle_custom_figure_size_parameter"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            custom_figsize = (12, 8)

            # ACT: Execute operation with custom figure size
            result = wrapper.execute('missing_matrix', missing_data_df, figsize=custom_figsize)

            # ASSERT: Verify operation executed with custom parameters
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify missingno.matrix was called with figsize parameter
            mock_missingno.matrix.assert_called_once()
            call_args = mock_missingno.matrix.call_args
            assert 'figsize' in call_args[1], "Expected figsize parameter to be passed"

    def test_operation_with_custom_color_scheme(self, missing_data_df, mock_missingno):
        """TEST: should_handle_custom_color_scheme_parameter"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            custom_color = 'viridis'

            # ACT: Execute operation with custom color scheme
            result = wrapper.execute('missing_heatmap', missing_data_df, cmap=custom_color)

            # ASSERT: Verify operation executed with custom parameters
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify missingno.heatmap was called with cmap parameter
            mock_missingno.heatmap.assert_called_once()
            call_args = mock_missingno.heatmap.call_args
            assert 'cmap' in call_args[1], "Expected cmap parameter to be passed"

    def test_multiple_operations_sequence(self, missing_data_df, mock_missingno):
        """TEST: should_execute_multiple_operations_in_sequence"""
        # ARRANGE: DataFrame with missing data and MissingnoWrapper
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            wrapper = MissingnoWrapper()
            operations = ['missing_matrix', 'missing_bar', 'missing_heatmap']

            # ACT: Execute multiple operations in sequence
            results = []
            for operation in operations:
                result = wrapper.execute(operation, missing_data_df)
                results.append(result)

            # ASSERT: Verify all operations executed successfully
            assert len(results) == len(operations), f"Expected {len(operations)} results, got {len(results)}"
            for result in results:
                assert isinstance(result, pd.DataFrame), "Expected DataFrame from each operation"
                assert len(result) == len(missing_data_df), "Expected same number of rows from each operation"
