"""
TEST SUITE: csv_cleaner.wrappers.base
PURPOSE: Test base wrapper functionality including abstract methods, operation validation, and performance estimation
SCOPE: BaseWrapper abstract class, operation validation, performance estimation, error handling
DEPENDENCIES: pandas, abc, unittest.mock
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from abc import ABC

from csv_cleaner.wrappers.base import BaseWrapper


class MockWrapper(BaseWrapper):
    """Mock wrapper for testing BaseWrapper functionality."""

    def can_handle(self, operation: str) -> bool:
        """Mock implementation of can_handle."""
        supported_operations = ['remove_duplicates', 'drop_missing', 'fill_missing']
        return operation in supported_operations

    def _execute_operation(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Mock implementation of _execute_operation."""
        # Mock different operations
        if operation == 'remove_duplicates':
            return df.drop_duplicates(**kwargs)
        elif operation == 'drop_missing':
            return df.dropna(**kwargs)
        elif operation == 'fill_missing':
            return df.fillna(**kwargs)
        else:
            return df

    def get_supported_operations(self) -> list:
        """Mock implementation of get_supported_operations."""
        return ['remove_duplicates', 'drop_missing', 'fill_missing']


class TestBaseWrapper:
    """Test cases for BaseWrapper abstract class."""

    def test_base_wrapper_is_abstract(self):
        """TEST: should_be_abstract_class_and_require_implementation_of_abstract_methods"""
        # ARRANGE: BaseWrapper class
        # ACT & ASSERT: Verify BaseWrapper is abstract and cannot be instantiated directly
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseWrapper()

    def test_mock_wrapper_instantiation(self):
        """TEST: should_instantiate_successfully_when_all_abstract_methods_are_implemented"""
        # ARRANGE: MockWrapper with all abstract methods implemented
        # ACT: Create MockWrapper instance
        wrapper = MockWrapper()

        # ASSERT: Verify wrapper is instantiated successfully
        assert wrapper is not None, "Expected MockWrapper to be instantiated successfully"
        assert isinstance(wrapper, BaseWrapper), "Expected MockWrapper to be instance of BaseWrapper"

    def test_can_handle_supported_operation(self):
        """TEST: should_return_true_when_operation_is_supported"""
        # ARRANGE: MockWrapper and supported operation
        wrapper = MockWrapper()
        supported_operation = 'remove_duplicates'

        # ACT: Check if operation is supported
        result = wrapper.can_handle(supported_operation)

        # ASSERT: Verify operation is supported
        assert result is True, f"Expected can_handle('{supported_operation}') to return True, got {result}"

    def test_can_handle_unsupported_operation(self):
        """TEST: should_return_false_when_operation_is_not_supported"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'

        # ACT: Check if operation is supported
        result = wrapper.can_handle(unsupported_operation)

        # ASSERT: Verify operation is not supported
        assert result is False, f"Expected can_handle('{unsupported_operation}') to return False, got {result}"

    def test_execute_supported_operation(self, sample_df):
        """TEST: should_execute_supported_operation_successfully"""
        # ARRANGE: MockWrapper and supported operation
        wrapper = MockWrapper()
        operation = 'remove_duplicates'
        original_rows = len(sample_df)

        # ACT: Execute operation
        result = wrapper.execute(operation, sample_df)

        # ASSERT: Verify operation executed successfully
        assert isinstance(result, pd.DataFrame), f"Expected result to be DataFrame, got {type(result)}"
        assert len(result) <= original_rows, f"Expected result rows ({len(result)}) to be <= original rows ({original_rows})"

    def test_execute_unsupported_operation(self, sample_df):
        """TEST: should_raise_valueerror_when_executing_unsupported_operation"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'

        # ACT & ASSERT: Verify ValueError is raised
        with pytest.raises(ValueError, match=f"Operation '{unsupported_operation}' not supported"):
            wrapper.execute(unsupported_operation, sample_df)

    def test_get_supported_operations(self):
        """TEST: should_return_list_of_supported_operations"""
        # ARRANGE: MockWrapper
        wrapper = MockWrapper()
        expected_operations = ['remove_duplicates', 'drop_missing', 'fill_missing']

        # ACT: Get supported operations
        operations = wrapper.get_supported_operations()

        # ASSERT: Verify correct operations are returned
        assert isinstance(operations, list), f"Expected operations to be list, got {type(operations)}"
        assert operations == expected_operations, f"Expected operations to be {expected_operations}, got {operations}"

    def test_get_operation_info_supported_operation(self):
        """TEST: should_return_operation_info_for_supported_operation"""
        # ARRANGE: MockWrapper and supported operation
        wrapper = MockWrapper()
        operation = 'remove_duplicates'

        # ACT: Get operation info
        info = wrapper.get_operation_info(operation)

        # ASSERT: Verify operation info is returned correctly
        assert info is not None, f"Expected operation info to not be None for '{operation}'"
        assert 'name' in info, f"Expected 'name' key in operation info, got {info.keys()}"
        assert 'description' in info, f"Expected 'description' key in operation info, got {info.keys()}"
        assert 'parameters' in info, f"Expected 'parameters' key in operation info, got {info.keys()}"
        assert 'wrapper' in info, f"Expected 'wrapper' key in operation info, got {info.keys()}"
        assert info['name'] == operation, f"Expected operation name to be '{operation}', got '{info['name']}'"
        assert info['wrapper'] == 'MockWrapper', f"Expected wrapper name to be 'MockWrapper', got '{info['wrapper']}'"

    def test_get_operation_info_unsupported_operation(self):
        """TEST: should_return_none_for_unsupported_operation"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'

        # ACT: Get operation info
        info = wrapper.get_operation_info(unsupported_operation)

        # ASSERT: Verify None is returned for unsupported operation
        assert info is None, f"Expected operation info to be None for '{unsupported_operation}', got {info}"

    def test_validate_operation_supported(self):
        """TEST: should_not_raise_error_when_validating_supported_operation"""
        # ARRANGE: MockWrapper and supported operation
        wrapper = MockWrapper()
        supported_operation = 'remove_duplicates'

        # ACT & ASSERT: Verify no error is raised for supported operation
        try:
            wrapper.validate_operation(supported_operation)
        except ValueError:
            pytest.fail(f"Expected validate_operation('{supported_operation}') to not raise ValueError")

    def test_validate_operation_unsupported(self):
        """TEST: should_raise_valueerror_when_validating_unsupported_operation"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'

        # ACT & ASSERT: Verify ValueError is raised with correct message
        with pytest.raises(ValueError, match=f"Operation '{unsupported_operation}' not supported by MockWrapper"):
            wrapper.validate_operation(unsupported_operation)

    def test_get_performance_estimate_supported_operation(self, sample_df):
        """TEST: should_return_performance_estimate_for_supported_operation"""
        # ARRANGE: MockWrapper and supported operation
        wrapper = MockWrapper()
        operation = 'remove_duplicates'

        # ACT: Get performance estimate
        estimate = wrapper.get_performance_estimate(operation, sample_df)

        # ASSERT: Verify performance estimate is returned
        assert isinstance(estimate, dict), f"Expected estimate to be dict, got {type(estimate)}"
        assert 'time_estimate' in estimate, f"Expected 'time_estimate' key in estimate, got {estimate.keys()}"
        assert 'memory_estimate' in estimate, f"Expected 'memory_estimate' key in estimate, got {estimate.keys()}"
        assert 'complexity' in estimate, f"Expected 'complexity' key in estimate, got {estimate.keys()}"
        assert estimate['complexity'] == 'O(n log n)', f"Expected complexity to be 'O(n log n)', got '{estimate['complexity']}'"

    def test_get_performance_estimate_unsupported_operation(self, sample_df):
        """TEST: should_return_error_for_unsupported_operation_performance_estimate"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'

        # ACT: Get performance estimate
        estimate = wrapper.get_performance_estimate(unsupported_operation, sample_df)

        # ASSERT: Verify error is returned for unsupported operation
        assert isinstance(estimate, dict), f"Expected estimate to be dict, got {type(estimate)}"
        assert 'error' in estimate, f"Expected 'error' key in estimate, got {estimate.keys()}"
        assert estimate['error'] == f'Operation {unsupported_operation} not supported', f"Expected error message to match, got '{estimate['error']}'"

    def test_get_performance_estimate_empty_dataframe(self):
        """TEST: should_handle_empty_dataframe_in_performance_estimate"""
        # ARRANGE: MockWrapper, supported operation, and empty DataFrame
        wrapper = MockWrapper()
        operation = 'remove_duplicates'
        empty_df = pd.DataFrame()

        # ACT: Get performance estimate
        estimate = wrapper.get_performance_estimate(operation, empty_df)

        # ASSERT: Verify performance estimate handles empty DataFrame
        assert isinstance(estimate, dict), f"Expected estimate to be dict, got {type(estimate)}"
        assert 'time_estimate' in estimate, f"Expected 'time_estimate' key in estimate, got {estimate.keys()}"
        assert 'memory_estimate' in estimate, f"Expected 'memory_estimate' key in estimate, got {estimate.keys()}"

    def test_get_performance_estimate_large_dataframe(self):
        """TEST: should_handle_large_dataframe_in_performance_estimate"""
        # ARRANGE: MockWrapper, supported operation, and large DataFrame
        wrapper = MockWrapper()
        operation = 'remove_duplicates'
        large_df = pd.DataFrame({
            'A': range(10000),
            'B': range(10000),
            'C': range(10000)
        })

        # ACT: Get performance estimate
        estimate = wrapper.get_performance_estimate(operation, large_df)

        # ASSERT: Verify performance estimate handles large DataFrame
        assert isinstance(estimate, dict), f"Expected estimate to be dict, got {type(estimate)}"
        assert 'time_estimate' in estimate, f"Expected 'time_estimate' key in estimate, got {estimate.keys()}"
        assert 'memory_estimate' in estimate, f"Expected 'memory_estimate' key in estimate, got {estimate.keys()}"
        assert 'complexity' in estimate, f"Expected 'complexity' key in estimate, got {estimate.keys()}"

    def test_operation_descriptions(self):
        """TEST: should_return_correct_descriptions_for_known_operations"""
        # ARRANGE: MockWrapper and known operations
        wrapper = MockWrapper()
        known_operations = {
            'remove_duplicates': 'Remove duplicate rows from the DataFrame',
            'drop_missing': 'Remove rows with missing values',
            'fill_missing': 'Fill missing values with specified strategy',
            'convert_types': 'Convert data types of columns',
            'rename_columns': 'Rename DataFrame columns',
            'clean_names': 'Clean column names (remove special chars, normalize)',
            'remove_empty': 'Remove empty rows and columns',
            'handle_missing': 'Handle missing values with various strategies'
        }

        # ACT & ASSERT: Verify descriptions for known operations
        for operation, expected_description in known_operations.items():
            info = wrapper.get_operation_info(operation)
            if info:  # Only check if operation is supported
                actual_description = info['description']
                assert actual_description == expected_description, f"Expected description for '{operation}' to be '{expected_description}', got '{actual_description}'"

    def test_operation_parameters(self):
        """TEST: should_return_correct_parameters_for_known_operations"""
        # ARRANGE: MockWrapper and known operations with parameters
        wrapper = MockWrapper()
        operation = 'remove_duplicates'

        # ACT: Get operation info
        info = wrapper.get_operation_info(operation)

        # ASSERT: Verify parameters are returned correctly
        assert info is not None, f"Expected operation info to not be None for '{operation}'"
        parameters = info['parameters']
        assert isinstance(parameters, dict), f"Expected parameters to be dict, got {type(parameters)}"
        assert 'subset' in parameters, f"Expected 'subset' parameter for '{operation}', got {parameters.keys()}"
        assert 'keep' in parameters, f"Expected 'keep' parameter for '{operation}', got {parameters.keys()}"

    def test_execute_with_kwargs(self, sample_df):
        """TEST: should_execute_operation_with_additional_kwargs"""
        # ARRANGE: MockWrapper, operation, and kwargs
        wrapper = MockWrapper()
        operation = 'remove_duplicates'
        kwargs = {'subset': ['Name'], 'keep': 'first'}

        # ACT: Execute operation with kwargs
        result = wrapper.execute(operation, sample_df, **kwargs)

        # ASSERT: Verify operation executed with kwargs
        assert isinstance(result, pd.DataFrame), f"Expected result to be DataFrame, got {type(result)}"
        assert len(result) <= len(sample_df), f"Expected result rows ({len(result)}) to be <= original rows ({len(sample_df)})"

    def test_execute_with_empty_kwargs(self, sample_df):
        """TEST: should_execute_operation_with_empty_kwargs"""
        # ARRANGE: MockWrapper, operation, and empty kwargs
        wrapper = MockWrapper()
        operation = 'remove_duplicates'

        # ACT: Execute operation with empty kwargs
        result = wrapper.execute(operation, sample_df)

        # ASSERT: Verify operation executed successfully
        assert isinstance(result, pd.DataFrame), f"Expected result to be DataFrame, got {type(result)}"

    def test_get_supported_operations_empty_list(self):
        """TEST: should_handle_wrapper_with_no_supported_operations"""
        # ARRANGE: Mock wrapper with no supported operations
        class EmptyWrapper(BaseWrapper):
            def can_handle(self, operation: str) -> bool:
                return False

            def _execute_operation(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
                raise ValueError(f"Operation '{operation}' not supported")

            def get_supported_operations(self) -> list:
                return []

        wrapper = EmptyWrapper()

        # ACT: Get supported operations
        operations = wrapper.get_supported_operations()

        # ASSERT: Verify empty list is returned
        assert operations == [], f"Expected empty list for wrapper with no operations, got {operations}"

    def test_validate_operation_error_message_includes_supported_operations(self):
        """TEST: should_include_supported_operations_in_error_message"""
        # ARRANGE: MockWrapper and unsupported operation
        wrapper = MockWrapper()
        unsupported_operation = 'invalid_operation'
        supported_operations = ['remove_duplicates', 'drop_missing', 'fill_missing']

        # ACT & ASSERT: Verify error message includes supported operations
        with pytest.raises(ValueError) as exc_info:
            wrapper.validate_operation(unsupported_operation)

        error_message = str(exc_info.value)
        assert "MockWrapper" in error_message, f"Expected error message to include 'MockWrapper', got '{error_message}'"
        assert "Supported operations" in error_message, f"Expected error message to include 'Supported operations', got '{error_message}'"

        # Check that all supported operations are mentioned
        for operation in supported_operations:
            assert operation in error_message, f"Expected error message to include '{operation}', got '{error_message}'"
