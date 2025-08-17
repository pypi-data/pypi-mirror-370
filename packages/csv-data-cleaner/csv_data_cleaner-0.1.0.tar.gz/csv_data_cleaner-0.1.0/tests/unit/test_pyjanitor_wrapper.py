"""
TEST SUITE: csv_cleaner.wrappers.pyjanitor_wrapper
PURPOSE: Test PyJanitor-based data cleaning operations
SCOPE: PyJanitorWrapper class, all supported operations, import handling, error handling, performance timing
DEPENDENCIES: pandas, pyjanitor library, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from csv_cleaner.wrappers.pyjanitor_wrapper import PyJanitorWrapper, PYJANITOR_AVAILABLE


class TestPyJanitorWrapper:
    """Test cases for PyJanitorWrapper class."""

    def test_initialization_with_pyjanitor_available(self, mock_pyjanitor):
        """TEST: should_initialize_successfully_when_pyjanitor_is_available"""
        # ARRANGE: Mock pyjanitor as available
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            # ACT: Initialize PyJanitorWrapper
            wrapper = PyJanitorWrapper()

            # ASSERT: Verify wrapper is initialized
            assert wrapper is not None, "Expected PyJanitorWrapper to be initialized successfully"
            assert isinstance(wrapper, PyJanitorWrapper), "Expected PyJanitorWrapper instance"

    def test_initialization_without_pyjanitor(self):
        """TEST: should_raise_importerror_when_pyjanitor_is_not_available"""
        # ARRANGE: Mock pyjanitor as unavailable
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', False):
            # ACT & ASSERT: Verify ImportError is raised
            with pytest.raises(ImportError, match="PyJanitor is not available"):
                PyJanitorWrapper()

    def test_can_handle_pyjanitor_operations(self, mock_pyjanitor):
        """TEST: should_return_true_for_supported_pyjanitor_operations"""
        # ARRANGE: PyJanitorWrapper and supported operations
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            supported_operations = [
                'clean_names', 'remove_empty', 'fill_empty', 'remove_duplicates',
                'handle_missing', 'remove_constant_columns', 'remove_columns_with_nulls', 'coalesce_columns'
            ]

            # ACT & ASSERT: Verify all supported operations return True
            for operation in supported_operations:
                result = wrapper.can_handle(operation)
                assert result is True, f"Expected can_handle('{operation}') to return True, got {result}"

    def test_can_handle_unsupported_operations(self, mock_pyjanitor):
        """TEST: should_return_false_for_unsupported_operations"""
        # ARRANGE: PyJanitorWrapper and unsupported operations
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            unsupported_operations = ['invalid_operation', 'unknown_method', 'test_function']

            # ACT & ASSERT: Verify unsupported operations return False
            for operation in unsupported_operations:
                result = wrapper.can_handle(operation)
                assert result is False, f"Expected can_handle('{operation}') to return False, got {result}"

    def test_get_supported_operations(self, mock_pyjanitor):
        """TEST: should_return_list_of_all_supported_operations"""
        # ARRANGE: PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            expected_operations = [
                'clean_names', 'remove_empty', 'fill_empty', 'remove_duplicates',
                'handle_missing', 'remove_constant_columns', 'remove_columns_with_nulls', 'coalesce_columns'
            ]

            # ACT: Get supported operations
            result = wrapper.get_supported_operations()

            # ASSERT: Verify all expected operations are returned
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            assert len(result) == len(expected_operations), f"Expected {len(expected_operations)} operations, got {len(result)}"
            for operation in expected_operations:
                assert operation in result, f"Expected '{operation}' to be in supported operations"

    def test_execute_clean_names(self, text_data_df, mock_pyjanitor):
        """TEST: should_execute_clean_names_operation"""
        # ARRANGE: DataFrame with dirty column names and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor clean_names method to return a modified DataFrame
            mock_pyjanitor.clean_names.return_value = text_data_df.copy()

            # ACT: Execute clean_names operation
            result = wrapper.execute('clean_names', text_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(text_data_df), f"Expected same number of rows, got {len(result)} != {len(text_data_df)}"
            # Verify pyjanitor.clean_names was called
            mock_pyjanitor.clean_names.assert_called_once()

    def test_execute_remove_empty(self, missing_data_df, mock_pyjanitor):
        """TEST: should_execute_remove_empty_operation"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor remove_empty method
            mock_pyjanitor.remove_empty.return_value = missing_data_df.dropna()

            # ACT: Execute remove_empty operation
            result = wrapper.execute('remove_empty', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.remove_empty was called (called twice: once for rows, once for columns)
            assert mock_pyjanitor.remove_empty.call_count == 2, "Expected remove_empty to be called twice"

    def test_execute_fill_empty(self, missing_data_df, mock_pyjanitor):
        """TEST: should_execute_fill_empty_operation"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor fill_empty method
            mock_pyjanitor.fill_empty.return_value = missing_data_df.fillna('FILLED')

            # ACT: Execute fill_empty operation
            result = wrapper.execute('fill_empty', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify pyjanitor.fill_empty was called
            mock_pyjanitor.fill_empty.assert_called_once()

    def test_execute_remove_duplicates(self, basic_df, mock_pyjanitor):
        """TEST: should_execute_remove_duplicates_operation"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Add duplicates to the DataFrame
            df_with_duplicates = pd.concat([basic_df, basic_df.iloc[:2]])

            # ACT: Execute remove_duplicates operation
            result = wrapper.execute('remove_duplicates', df_with_duplicates)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify that duplicates were removed (should have fewer rows than input)
            assert len(result) < len(df_with_duplicates), "Expected duplicates to be removed"
            # Verify the result is the same as pandas drop_duplicates
            expected_result = df_with_duplicates.drop_duplicates()
            assert result.equals(expected_result), "Expected result to match pandas drop_duplicates"

    def test_execute_handle_missing(self, missing_data_df, mock_pyjanitor):
        """TEST: should_execute_handle_missing_operation"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor handle_missing method
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                expected_result = missing_data_df.ffill()
            expected_result = expected_result.infer_objects(copy=False)
            mock_pyjanitor.handle_missing.return_value = expected_result

            # ACT: Execute handle_missing operation
            result = wrapper.execute('handle_missing', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # The result should be the same as the mock return value
            assert result.equals(expected_result), "Expected result to match mock return value"
            # Verify pyjanitor.handle_missing was called
            mock_pyjanitor.handle_missing.assert_called_once()

    def test_execute_remove_constant_columns(self, basic_df, mock_pyjanitor):
        """TEST: should_execute_remove_constant_columns_operation"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor remove_constant_columns method
            mock_pyjanitor.remove_constant_columns.return_value = basic_df.drop(columns=['active'])

            # ACT: Execute remove_constant_columns operation
            result = wrapper.execute('remove_constant_columns', basic_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.remove_constant_columns was called
            mock_pyjanitor.remove_constant_columns.assert_called_once()

    def test_execute_remove_columns_with_nulls(self, missing_data_df, mock_pyjanitor):
        """TEST: should_execute_remove_columns_with_nulls_operation"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor remove_columns_with_nulls method
            mock_pyjanitor.remove_columns_with_nulls.return_value = missing_data_df.dropna(axis=1)

            # ACT: Execute remove_columns_with_nulls operation
            result = wrapper.execute('remove_columns_with_nulls', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.remove_columns_with_nulls was called
            mock_pyjanitor.remove_columns_with_nulls.assert_called_once()

    def test_execute_coalesce_columns(self, basic_df, mock_pyjanitor):
        """TEST: should_execute_coalesce_columns_operation"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock the pyjanitor coalesce_columns method
            mock_pyjanitor.coalesce_columns.return_value = basic_df.copy()

            # ACT: Execute coalesce_columns operation
            result = wrapper.execute('coalesce_columns', basic_df, columns=['name', 'city'])

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(basic_df), f"Expected same number of rows, got {len(result)} != {len(basic_df)}"
            # Verify pyjanitor.coalesce_columns was called
            mock_pyjanitor.coalesce_columns.assert_called_once()

    def test_execute_with_additional_kwargs(self, basic_df, mock_pyjanitor):
        """TEST: should_pass_additional_kwargs_to_pyjanitor_functions"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            additional_kwargs = {'subset': ['name', 'age'], 'keep': 'first'}
            # Add duplicates to the DataFrame
            df_with_duplicates = pd.concat([basic_df, basic_df.iloc[:2]])

            # ACT: Execute operation with additional kwargs
            result = wrapper.execute('remove_duplicates', df_with_duplicates, **additional_kwargs)

            # ASSERT: Verify kwargs were passed to pandas function
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify the result is the same as pandas drop_duplicates with kwargs
            expected_result = df_with_duplicates.drop_duplicates(**additional_kwargs)
            assert result.equals(expected_result), "Expected result to match pandas drop_duplicates with kwargs"

    def test_execute_invalid_operation(self, basic_df, mock_pyjanitor):
        """TEST: should_raise_valueerror_when_operation_is_not_supported"""
        # ARRANGE: PyJanitorWrapper and invalid operation
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            invalid_operation = 'invalid_operation'

            # ACT & ASSERT: Verify ValueError is raised
            with pytest.raises(ValueError, match=f"Operation '{invalid_operation}' not supported"):
                wrapper.execute(invalid_operation, basic_df)

    def test_execute_with_empty_dataframe(self, edge_case_dfs, mock_pyjanitor):
        """TEST: should_handle_empty_dataframe_gracefully"""
        # ARRANGE: Empty DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            empty_df = edge_case_dfs['empty']
            mock_pyjanitor.clean_names.return_value = empty_df

            # ACT: Execute operation on empty DataFrame
            result = wrapper.execute('clean_names', empty_df)

            # ASSERT: Verify operation handles empty DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from clean_names"
            assert len(result) == 0, "Expected empty DataFrame from clean_names"

    def test_execute_with_single_row(self, edge_case_dfs, mock_pyjanitor):
        """TEST: should_handle_single_row_dataframe"""
        # ARRANGE: Single row DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            single_row_df = edge_case_dfs['single_row']
            mock_pyjanitor.clean_names.return_value = single_row_df

            # ACT: Execute operation on single row DataFrame
            result = wrapper.execute('clean_names', single_row_df)

            # ASSERT: Verify operation handles single row DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from clean_names"
            assert len(result) == 1, "Expected single row from clean_names"

    def test_execute_with_large_dataframe(self, large_df, mock_pyjanitor):
        """TEST: should_handle_large_dataframe_efficiently"""
        # ARRANGE: Large DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            mock_pyjanitor.clean_names.return_value = large_df

            # ACT: Execute operation on large DataFrame
            result = wrapper.execute('clean_names', large_df)

            # ASSERT: Verify operation handles large DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from clean_names"
            assert len(result) == len(large_df), f"Expected same number of rows, got {len(result)} != {len(large_df)}"

    def test_performance_timing(self, basic_df, mock_pyjanitor):
        """TEST: should_log_execution_time_for_operations"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            mock_pyjanitor.clean_names.return_value = basic_df

            # ACT: Execute operation and capture logs
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger
                result = wrapper.execute('clean_names', basic_df)

            # ASSERT: Verify timing is logged
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Check that info and completion logs were called
            assert mock_logger.info.called, "Expected timing information to be logged"

    def test_error_handling_pyjanitor_function_failure(self, basic_df, mock_pyjanitor):
        """TEST: should_handle_pyjanitor_function_failures_gracefully"""
        # ARRANGE: PyJanitorWrapper with failing pyjanitor function
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Make pyjanitor.clean_names raise an exception
            mock_pyjanitor.clean_names.side_effect = Exception("PyJanitor function failed")

            # ACT & ASSERT: Verify exception is re-raised
            with pytest.raises(Exception, match="PyJanitor function failed"):
                wrapper.execute('clean_names', basic_df)

    def test_error_handling_dataframe_not_provided(self, mock_pyjanitor):
        """TEST: should_raise_typeerror_when_dataframe_is_not_provided"""
        # ARRANGE: PyJanitorWrapper without DataFrame
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()

            # ACT & ASSERT: Verify TypeError is raised
            with pytest.raises(TypeError):
                wrapper.execute('clean_names', None)

    def test_clean_names_with_custom_case(self, text_data_df, mock_pyjanitor):
        """TEST: should_handle_custom_case_parameter_in_clean_names"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            mock_pyjanitor.clean_names.return_value = text_data_df.copy()

            # ACT: Execute clean_names with custom case
            result = wrapper.execute('clean_names', text_data_df, case='snake')

            # ASSERT: Verify operation executed with custom parameters
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.clean_names was called with case_type parameter (converted from case)
            mock_pyjanitor.clean_names.assert_called_once()
            call_args = mock_pyjanitor.clean_names.call_args
            assert 'case_type' in call_args[1], "Expected case_type parameter to be passed"
            assert call_args[1]['case_type'] == 'snake', "Expected case_type to be 'snake'"

    def test_fill_empty_with_custom_value(self, missing_data_df, mock_pyjanitor):
        """TEST: should_handle_custom_value_parameter_in_fill_empty"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            custom_value = 'CUSTOM_FILL'
            mock_pyjanitor.fill_empty.return_value = missing_data_df.fillna(custom_value)

            # ACT: Execute fill_empty with custom value
            result = wrapper.execute('fill_empty', missing_data_df, value=custom_value)

            # ASSERT: Verify operation executed with custom parameters
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.fill_empty was called with value parameter
            mock_pyjanitor.fill_empty.assert_called_once()
            call_args = mock_pyjanitor.fill_empty.call_args
            assert 'value' in call_args[1], "Expected value parameter to be passed"

    def test_handle_missing_with_custom_strategy(self, missing_data_df, mock_pyjanitor):
        """TEST: should_handle_custom_strategy_parameter_in_handle_missing"""
        # ARRANGE: DataFrame with missing data and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            custom_strategy = 'drop'
            mock_pyjanitor.handle_missing.return_value = missing_data_df.dropna()

            # ACT: Execute handle_missing with custom strategy
            result = wrapper.execute('handle_missing', missing_data_df, strategy=custom_strategy)

            # ASSERT: Verify operation executed with custom parameters
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify pyjanitor.handle_missing was called with strategy parameter
            mock_pyjanitor.handle_missing.assert_called_once()
            call_args = mock_pyjanitor.handle_missing.call_args
            assert 'strategy' in call_args[1], "Expected strategy parameter to be passed"

    def test_multiple_operations_sequence(self, basic_df, mock_pyjanitor):
        """TEST: should_execute_multiple_operations_in_sequence"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            operations = ['clean_names', 'remove_duplicates', 'handle_missing']

            # Mock all operations to return the DataFrame
            for operation in operations:
                getattr(mock_pyjanitor, operation).return_value = basic_df.copy()

            # ACT: Execute multiple operations in sequence
            results = []
            for operation in operations:
                result = wrapper.execute(operation, basic_df)
                results.append(result)

            # ASSERT: Verify all operations executed successfully
            assert len(results) == len(operations), f"Expected {len(operations)} results, got {len(results)}"
            for result in results:
                assert isinstance(result, pd.DataFrame), "Expected DataFrame from each operation"
                assert len(result) == len(basic_df), "Expected same number of rows from each operation"

    def test_operation_with_dataframe_method_chaining(self, basic_df, mock_pyjanitor):
        """TEST: should_support_dataframe_method_chaining"""
        # ARRANGE: DataFrame and PyJanitorWrapper
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            wrapper = PyJanitorWrapper()
            # Mock pyjanitor methods to return modified DataFrames
            mock_pyjanitor.clean_names.return_value = basic_df.copy()
            mock_pyjanitor.remove_duplicates.return_value = basic_df.drop_duplicates()

            # ACT: Execute operations in sequence
            result1 = wrapper.execute('clean_names', basic_df)
            result2 = wrapper.execute('remove_duplicates', result1)

            # ASSERT: Verify method chaining works
            assert isinstance(result1, pd.DataFrame), "Expected DataFrame from first operation"
            assert isinstance(result2, pd.DataFrame), "Expected DataFrame from second operation"
            assert len(result2) <= len(result1), "Expected fewer or equal rows after removing duplicates"
