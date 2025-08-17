"""
TEST SUITE: csv_cleaner.wrappers.pandas_wrapper
PURPOSE: Test pandas-based data cleaning operations including text cleaning, type conversion, date handling, and column operations
SCOPE: PandasWrapper class, all supported operations, error handling, performance timing
DEPENDENCIES: pandas, numpy, re module, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import re

from csv_cleaner.wrappers.pandas_wrapper import PandasWrapper


class TestPandasWrapper:
    """Test cases for PandasWrapper class."""

    def test_can_handle_supported_operations(self):
        """TEST: should_return_true_when_operation_is_supported"""
        # ARRANGE: PandasWrapper and supported operations
        wrapper = PandasWrapper()
        supported_operations = [
            'remove_duplicates', 'drop_missing', 'fill_missing', 'convert_types',
            'rename_columns', 'clean_text', 'drop_columns', 'select_columns', 'fix_dates'
        ]

        # ACT & ASSERT: Verify all supported operations return True
        for operation in supported_operations:
            result = wrapper.can_handle(operation)
            assert result is True, f"Expected can_handle('{operation}') to return True, got {result}"

    def test_can_handle_unsupported_operations(self):
        """TEST: should_return_false_when_operation_is_not_supported"""
        # ARRANGE: PandasWrapper and unsupported operations
        wrapper = PandasWrapper()
        unsupported_operations = ['invalid_operation', 'unknown_method', 'test_function']

        # ACT & ASSERT: Verify unsupported operations return False
        for operation in unsupported_operations:
            result = wrapper.can_handle(operation)
            assert result is False, f"Expected can_handle('{operation}') to return False, got {result}"

    def test_get_supported_operations(self):
        """TEST: should_return_list_of_all_supported_operations"""
        # ARRANGE: PandasWrapper
        wrapper = PandasWrapper()
        expected_operations = [
            'remove_duplicates', 'drop_missing', 'fill_missing', 'convert_types',
            'rename_columns', 'clean_text', 'drop_columns', 'select_columns', 'fix_dates'
        ]

        # ACT: Get supported operations
        result = wrapper.get_supported_operations()

        # ASSERT: Verify all expected operations are returned
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) == len(expected_operations), f"Expected {len(expected_operations)} operations, got {len(result)}"
        for operation in expected_operations:
            assert operation in result, f"Expected '{operation}' to be in supported operations"

    def test_execute_remove_duplicates_basic(self, basic_df):
        """TEST: should_remove_duplicate_rows_when_duplicates_exist"""
        # ARRANGE: DataFrame with duplicates and PandasWrapper
        df_with_duplicates = pd.concat([basic_df, basic_df.iloc[0:2]])  # Add duplicates
        wrapper = PandasWrapper()
        original_rows = len(df_with_duplicates)

        # ACT: Execute remove_duplicates
        result = wrapper.execute('remove_duplicates', df_with_duplicates)

        # ASSERT: Verify duplicates are removed
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result) < original_rows, f"Expected fewer rows after removing duplicates, got {len(result)} >= {original_rows}"
        assert len(result) == len(basic_df), f"Expected {len(basic_df)} rows, got {len(result)}"

    def test_execute_remove_duplicates_no_duplicates(self, basic_df):
        """TEST: should_return_same_dataframe_when_no_duplicates_exist"""
        # ARRANGE: DataFrame without duplicates and PandasWrapper
        wrapper = PandasWrapper()
        original_rows = len(basic_df)

        # ACT: Execute remove_duplicates
        result = wrapper.execute('remove_duplicates', basic_df)

        # ASSERT: Verify DataFrame is unchanged
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result) == original_rows, f"Expected {original_rows} rows, got {len(result)}"
        pd.testing.assert_frame_equal(result, basic_df)

    def test_execute_drop_missing_basic(self, missing_data_df):
        """TEST: should_drop_rows_with_missing_values"""
        # ARRANGE: DataFrame with missing values and PandasWrapper
        wrapper = PandasWrapper()
        original_rows = len(missing_data_df)

        # ACT: Execute drop_missing
        result = wrapper.execute('drop_missing', missing_data_df)

        # ASSERT: Verify missing values are dropped
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result) < original_rows, f"Expected fewer rows after dropping missing values, got {len(result)} >= {original_rows}"
        assert result.isnull().sum().sum() == 0, "Expected no missing values in result"

    def test_execute_drop_missing_subset(self, missing_data_df):
        """TEST: should_drop_missing_values_only_in_specified_columns"""
        # ARRANGE: DataFrame with missing values and PandasWrapper
        wrapper = PandasWrapper()
        subset_columns = ['name', 'age']

        # ACT: Execute drop_missing with subset
        result = wrapper.execute('drop_missing', missing_data_df, subset=subset_columns)

        # ASSERT: Verify only specified columns are considered
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        # Check that specified columns have no missing values
        for col in subset_columns:
            assert result[col].isnull().sum() == 0, f"Expected no missing values in column '{col}'"

    def test_execute_fill_missing_basic(self, missing_data_df):
        """TEST: should_fill_missing_values_with_specified_value"""
        # ARRANGE: DataFrame with missing values and PandasWrapper
        wrapper = PandasWrapper()
        fill_value = 'UNKNOWN'

        # ACT: Execute fill_missing
        result = wrapper.execute('fill_missing', missing_data_df, value=fill_value)

        # ASSERT: Verify missing values are filled
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
        # Check that string columns have the fill value
        string_columns = result.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in missing_data_df.columns:
                assert fill_value in result[col].values, f"Expected '{fill_value}' in column '{col}'"

    def test_execute_fill_missing_method(self, missing_data_df):
        """TEST: should_fill_missing_values_using_specified_method"""
        # ARRANGE: DataFrame with missing values and PandasWrapper
        wrapper = PandasWrapper()

        # ACT: Execute fill_missing with method
        result = wrapper.execute('fill_missing', missing_data_df, method='ffill')

        # ASSERT: Verify missing values are filled using method
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"

    def test_execute_convert_types_basic(self, basic_df):
        """TEST: should_convert_column_types_as_specified"""
        # ARRANGE: DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        type_mapping = {'age': 'float64', 'salary': 'int64'}

        # ACT: Execute convert_types
        result = wrapper.execute('convert_types', basic_df, dtype_mapping=type_mapping)

        # ASSERT: Verify types are converted
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert result['age'].dtype == 'float64', f"Expected age column to be float64, got {result['age'].dtype}"
        assert result['salary'].dtype == 'int64', f"Expected salary column to be int64, got {result['salary'].dtype}"

    def test_execute_convert_types_auto(self, basic_df):
        """TEST: should_auto_convert_types_when_no_mapping_provided"""
        # ARRANGE: DataFrame with mixed types and PandasWrapper
        mixed_df = basic_df.copy()
        mixed_df['numeric_string'] = ['1', '2', '3', '4', '5']
        wrapper = PandasWrapper()

        # ACT: Execute convert_types with auto detection
        result = wrapper.execute('convert_types', mixed_df, dtype_mapping={'numeric_string': 'int64'})

        # ASSERT: Verify automatic type conversion
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        # Check that numeric strings are converted to numeric
        assert pd.api.types.is_numeric_dtype(result['numeric_string']), "Expected numeric_string to be converted to numeric type"

    def test_execute_rename_columns_basic(self, basic_df):
        """TEST: should_rename_columns_as_specified"""
        # ARRANGE: DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        rename_mapping = {'name': 'full_name', 'age': 'years_old', 'city': 'location'}

        # ACT: Execute rename_columns
        result = wrapper.execute('rename_columns', basic_df, column_mapping=rename_mapping)

        # ASSERT: Verify columns are renamed
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        for old_name, new_name in rename_mapping.items():
            assert new_name in result.columns, f"Expected column '{new_name}' to exist"
            assert old_name not in result.columns, f"Expected column '{old_name}' to be renamed"

    def test_execute_clean_text_basic(self, text_data_df):
        """TEST: should_clean_text_columns_basic_operations"""
        # ARRANGE: DataFrame with dirty text and PandasWrapper
        wrapper = PandasWrapper()
        text_columns = ['dirty_text', 'names']

        # ACT: Execute clean_text
        result = wrapper.execute('clean_text', text_data_df, columns=text_columns)

        # ASSERT: Verify text is cleaned
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        # Check that whitespace is trimmed
        for col in text_columns:
            if col in result.columns:
                # Check that leading/trailing whitespace is removed
                for value in result[col].dropna():
                    assert value == value.strip(), f"Expected whitespace to be trimmed in column '{col}'"

    def test_execute_clean_text_advanced(self, text_data_df):
        """TEST: should_clean_text_with_advanced_operations"""
        # ARRANGE: DataFrame with dirty text and PandasWrapper
        wrapper = PandasWrapper()
        text_columns = ['dirty_text']

        # ACT: Execute clean_text with advanced options
        result = wrapper.execute('clean_text', text_data_df, columns=text_columns,
                               lowercase=True, remove_special_chars=True)

        # ASSERT: Verify advanced text cleaning
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        if 'dirty_text' in result.columns:
            # Check that text is lowercased
            for value in result['dirty_text'].dropna():
                assert value == value.lower(), f"Expected text to be lowercased, got '{value}'"

    def test_execute_drop_columns_basic(self, basic_df):
        """TEST: should_drop_specified_columns"""
        # ARRANGE: DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        columns_to_drop = ['age', 'salary']

        # ACT: Execute drop_columns
        result = wrapper.execute('drop_columns', basic_df, columns=columns_to_drop)

        # ASSERT: Verify columns are dropped
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        for col in columns_to_drop:
            assert col not in result.columns, f"Expected column '{col}' to be dropped"
        # Check that other columns remain
        remaining_columns = ['name', 'city', 'active']
        for col in remaining_columns:
            assert col in result.columns, f"Expected column '{col}' to remain"

    def test_execute_select_columns_basic(self, basic_df):
        """TEST: should_select_only_specified_columns"""
        # ARRANGE: DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        columns_to_select = ['name', 'age']

        # ACT: Execute select_columns
        result = wrapper.execute('select_columns', basic_df, columns=columns_to_select)

        # ASSERT: Verify only specified columns are selected
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        assert len(result.columns) == len(columns_to_select), f"Expected {len(columns_to_select)} columns, got {len(result.columns)}"
        for col in columns_to_select:
            assert col in result.columns, f"Expected column '{col}' to be selected"

    def test_execute_fix_dates_basic(self, date_data_df):
        """TEST: should_convert_date_strings_to_datetime"""
        # ARRANGE: DataFrame with date strings and PandasWrapper
        wrapper = PandasWrapper()
        date_columns = ['iso_dates', 'slash_dates']

        # ACT: Execute fix_dates
        result = wrapper.execute('fix_dates', date_data_df, columns=date_columns)

        # ASSERT: Verify dates are converted
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        for col in date_columns:
            if col in result.columns:
                assert pd.api.types.is_datetime64_any_dtype(result[col]), f"Expected column '{col}' to be datetime type"

    def test_execute_fix_dates_with_format(self, date_data_df):
        """TEST: should_convert_dates_with_specified_format"""
        # ARRANGE: DataFrame with date strings and PandasWrapper
        wrapper = PandasWrapper()
        date_columns = ['dot_dates']

        # ACT: Execute fix_dates with format
        result = wrapper.execute('fix_dates', date_data_df, columns=date_columns, date_format='%d.%m.%Y')

        # ASSERT: Verify dates are converted with format
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        if 'dot_dates' in result.columns:
            assert pd.api.types.is_datetime64_any_dtype(result['dot_dates']), "Expected dot_dates to be datetime type"

    def test_execute_invalid_operation(self, basic_df):
        """TEST: should_raise_valueerror_when_operation_is_not_supported"""
        # ARRANGE: PandasWrapper and invalid operation
        wrapper = PandasWrapper()
        invalid_operation = 'invalid_operation'

        # ACT & ASSERT: Verify ValueError is raised
        with pytest.raises(ValueError, match=f"Operation '{invalid_operation}' not supported"):
            wrapper.execute(invalid_operation, basic_df)

    def test_execute_with_empty_dataframe(self, edge_case_dfs):
        """TEST: should_handle_empty_dataframe_gracefully"""
        # ARRANGE: Empty DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        empty_df = edge_case_dfs['empty']

        # ACT: Execute operations on empty DataFrame
        result_remove = wrapper.execute('remove_duplicates', empty_df)
        result_drop = wrapper.execute('drop_missing', empty_df)
        result_fill = wrapper.execute('fill_missing', empty_df)

        # ASSERT: Verify operations handle empty DataFrame
        assert isinstance(result_remove, pd.DataFrame), "Expected DataFrame from remove_duplicates"
        assert isinstance(result_drop, pd.DataFrame), "Expected DataFrame from drop_missing"
        assert isinstance(result_fill, pd.DataFrame), "Expected DataFrame from fill_missing"
        assert len(result_remove) == 0, "Expected empty DataFrame from remove_duplicates"
        assert len(result_drop) == 0, "Expected empty DataFrame from drop_missing"
        assert len(result_fill) == 0, "Expected empty DataFrame from fill_missing"

    def test_execute_with_single_row(self, edge_case_dfs):
        """TEST: should_handle_single_row_dataframe"""
        # ARRANGE: Single row DataFrame and PandasWrapper
        wrapper = PandasWrapper()
        single_row_df = edge_case_dfs['single_row']

        # ACT: Execute operations on single row DataFrame
        result_remove = wrapper.execute('remove_duplicates', single_row_df)
        result_drop = wrapper.execute('drop_missing', single_row_df)

        # ASSERT: Verify operations handle single row DataFrame
        assert isinstance(result_remove, pd.DataFrame), "Expected DataFrame from remove_duplicates"
        assert isinstance(result_drop, pd.DataFrame), "Expected DataFrame from drop_missing"
        assert len(result_remove) == 1, "Expected single row from remove_duplicates"
        assert len(result_drop) == 1, "Expected single row from drop_missing"

    def test_execute_with_all_nulls(self, edge_case_dfs):
        """TEST: should_handle_dataframe_with_all_null_values"""
        # ARRANGE: DataFrame with all nulls and PandasWrapper
        wrapper = PandasWrapper()
        all_nulls_df = edge_case_dfs['all_nulls']

        # ACT: Execute operations on all nulls DataFrame
        result_drop = wrapper.execute('drop_missing', all_nulls_df)
        result_fill = wrapper.execute('fill_missing', all_nulls_df, value='FILLED')

        # ASSERT: Verify operations handle all nulls DataFrame
        assert isinstance(result_drop, pd.DataFrame), "Expected DataFrame from drop_missing"
        assert isinstance(result_fill, pd.DataFrame), "Expected DataFrame from fill_missing"
        assert len(result_drop) == 0, "Expected empty DataFrame from drop_missing with all nulls"
        assert len(result_fill) == len(all_nulls_df), "Expected same number of rows from fill_missing"

    def test_performance_timing(self, large_df):
        """TEST: should_log_execution_time_for_operations"""
        # ARRANGE: Large DataFrame and PandasWrapper
        wrapper = PandasWrapper()

        # ACT: Execute operation and capture logs
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            result = wrapper.execute('remove_duplicates', large_df)

        # ASSERT: Verify timing is logged
        assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
        # Check that info and completion logs were called
        assert mock_logger.info.called, "Expected timing information to be logged"

    def test_error_handling_dataframe_not_provided(self):
        """TEST: should_raise_attributeerror_when_dataframe_is_not_provided"""
        # ARRANGE: PandasWrapper without DataFrame
        wrapper = PandasWrapper()

        # ACT & ASSERT: Verify AttributeError is raised
        with pytest.raises(AttributeError):
            wrapper.execute('remove_duplicates', None)

    def test_error_handling_invalid_kwargs(self, basic_df):
        """TEST: should_handle_invalid_kwargs_gracefully"""
        # ARRANGE: PandasWrapper with invalid kwargs
        wrapper = PandasWrapper()

        # ACT & ASSERT: Verify operations handle invalid kwargs
        # This should not raise an error but handle gracefully
        result = wrapper.execute('remove_duplicates', basic_df, invalid_param='test')
        assert isinstance(result, pd.DataFrame), "Expected DataFrame even with invalid kwargs"
