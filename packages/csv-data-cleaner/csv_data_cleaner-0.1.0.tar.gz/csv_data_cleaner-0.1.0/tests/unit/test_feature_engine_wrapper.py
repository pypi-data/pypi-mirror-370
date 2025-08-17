"""
TEST SUITE: csv_cleaner.wrappers.feature_engine_wrapper
PURPOSE: Test advanced data transformation and feature engineering operations using feature-engine library
SCOPE: FeatureEngineWrapper class, all supported operations, import handling, error handling, performance timing
DEPENDENCIES: pandas, feature-engine library, scikit-learn, numpy, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from csv_cleaner.wrappers.feature_engine_wrapper import FeatureEngineWrapper, FEATURE_ENGINE_AVAILABLE


class TestFeatureEngineWrapper:
    """Test cases for FeatureEngineWrapper class."""

    def test_initialization_with_feature_engine_available(self, mock_feature_engine):
        """TEST: should_initialize_successfully_when_feature_engine_is_available"""
        # ARRANGE: Mock feature-engine as available
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            # ACT: Initialize FeatureEngineWrapper
            wrapper = FeatureEngineWrapper()

            # ASSERT: Verify wrapper is initialized
            assert wrapper is not None, "Expected FeatureEngineWrapper to be initialized successfully"
            assert isinstance(wrapper, FeatureEngineWrapper), "Expected FeatureEngineWrapper instance"

    def test_initialization_without_feature_engine(self):
        """TEST: should_raise_importerror_when_feature_engine_is_not_available"""
        # ARRANGE: Mock feature-engine as unavailable
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', False):
            # ACT & ASSERT: Verify ImportError is raised
            with pytest.raises(ImportError, match="Feature-Engine is not available"):
                FeatureEngineWrapper()

    def test_can_handle_feature_engine_operations(self, mock_feature_engine):
        """TEST: should_return_true_for_supported_feature_engine_operations"""
        # ARRANGE: FeatureEngineWrapper and supported operations
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            supported_operations = [
                'advanced_imputation', 'categorical_encoding', 'outlier_detection',
                'variable_selection', 'data_transformation', 'missing_indicator'
            ]

            # ACT & ASSERT: Verify all supported operations return True
            for operation in supported_operations:
                result = wrapper.can_handle(operation)
                assert result is True, f"Expected can_handle('{operation}') to return True, got {result}"

    def test_can_handle_unsupported_operations(self, mock_feature_engine):
        """TEST: should_return_false_for_unsupported_operations"""
        # ARRANGE: FeatureEngineWrapper and unsupported operations
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            unsupported_operations = ['invalid_operation', 'unknown_method', 'test_function']

            # ACT & ASSERT: Verify unsupported operations return False
            for operation in unsupported_operations:
                result = wrapper.can_handle(operation)
                assert result is False, f"Expected can_handle('{operation}') to return False, got {result}"

    def test_get_supported_operations(self, mock_feature_engine):
        """TEST: should_return_list_of_all_supported_operations"""
        # ARRANGE: FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            expected_operations = [
                'advanced_imputation', 'categorical_encoding', 'outlier_detection',
                'variable_selection', 'data_transformation', 'missing_indicator'
            ]

            # ACT: Get supported operations
            result = wrapper.get_supported_operations()

            # ASSERT: Verify all expected operations are returned
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            assert len(result) == len(expected_operations), f"Expected {len(expected_operations)} operations, got {len(result)}"
            for operation in expected_operations:
                assert operation in result, f"Expected '{operation}' to be in supported operations"

    def test_execute_advanced_imputation(self, missing_data_df, mock_feature_engine):
        """TEST: should_execute_advanced_imputation_operation"""
        # ARRANGE: DataFrame with missing data and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine imputer
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = missing_data_df.fillna(0)
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            # ACT: Execute advanced_imputation operation
            result = wrapper.execute('advanced_imputation', missing_data_df, method='mean')

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify feature-engine imputer was created and used
            mock_feature_engine.MeanMedianImputer.assert_called_once()

    def test_execute_categorical_encoding(self, basic_df, mock_feature_engine):
        """TEST: should_execute_categorical_encoding_operation"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine encoder
            mock_encoder = Mock()
            mock_encoder.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.OneHotEncoder.return_value = mock_encoder

            # ACT: Execute categorical_encoding operation
            result = wrapper.execute('categorical_encoding', basic_df, method='onehot')

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(basic_df), f"Expected same number of rows, got {len(result)} != {len(basic_df)}"
            # Verify feature-engine encoder was created and used
            mock_feature_engine.OneHotEncoder.assert_called_once()

    def test_execute_outlier_detection(self, basic_df, mock_feature_engine):
        """TEST: should_execute_outlier_detection_operation"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine outlier detector
            mock_detector = Mock()
            mock_detector.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.OutlierTrimmer.return_value = mock_detector

            # ACT: Execute outlier_detection operation
            result = wrapper.execute('outlier_detection', basic_df, method='iqr')

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(basic_df), f"Expected same number of rows, got {len(result)} != {len(basic_df)}"
            # Verify feature-engine detector was created and used
            mock_feature_engine.OutlierTrimmer.assert_called_once()

    def test_execute_variable_selection(self, basic_df, mock_feature_engine):
        """TEST: should_execute_variable_selection_operation"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine selector
            mock_selector = Mock()
            mock_selector.fit_transform.return_value = basic_df.drop(columns=['active'])
            mock_feature_engine.DropConstantFeatures.return_value = mock_selector

            # ACT: Execute variable_selection operation
            result = wrapper.execute('variable_selection', basic_df, method='constant')

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Verify feature-engine selector was created and used
            mock_feature_engine.DropConstantFeatures.assert_called_once()

    def test_execute_data_transformation(self, basic_df, mock_feature_engine):
        """TEST: should_execute_data_transformation_operation"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine transformer
            mock_transformer = Mock()
            mock_transformer.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.LogTransformer.return_value = mock_transformer

            # ACT: Execute data_transformation operation
            result = wrapper.execute('data_transformation', basic_df, method='log')

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(basic_df), f"Expected same number of rows, got {len(result)} != {len(basic_df)}"
            # Verify feature-engine transformer was created and used
            mock_feature_engine.LogTransformer.assert_called_once()

    def test_execute_missing_indicator(self, missing_data_df, mock_feature_engine):
        """TEST: should_execute_missing_indicator_operation"""
        # ARRANGE: DataFrame with missing data and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine missing indicator
            mock_indicator = Mock()
            mock_indicator.fit_transform.return_value = missing_data_df.copy()
            mock_feature_engine.AddMissingIndicator.return_value = mock_indicator

            # ACT: Execute missing_indicator operation
            result = wrapper.execute('missing_indicator', missing_data_df)

            # ASSERT: Verify operation executed and returned DataFrame
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            assert len(result) == len(missing_data_df), f"Expected same number of rows, got {len(result)} != {len(missing_data_df)}"
            # Verify feature-engine indicator was created and used
            mock_feature_engine.AddMissingIndicator.assert_called_once()

    def test_execute_with_additional_kwargs(self, basic_df, mock_feature_engine):
        """TEST: should_pass_additional_kwargs_to_feature_engine_functions"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            additional_kwargs = {'variables': ['age', 'salary'], 'threshold': 0.1}
            # Mock the feature-engine encoder
            mock_encoder = Mock()
            mock_encoder.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.OneHotEncoder.return_value = mock_encoder

            # ACT: Execute operation with additional kwargs
            result = wrapper.execute('categorical_encoding', basic_df, method='onehot', **additional_kwargs)

            # ASSERT: Verify kwargs were passed to feature-engine function
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Check that feature-engine.OneHotEncoder was called with kwargs
            mock_feature_engine.OneHotEncoder.assert_called_once()
            call_args = mock_feature_engine.OneHotEncoder.call_args
            assert call_args is not None, "Expected feature-engine.OneHotEncoder to be called"

    def test_execute_invalid_operation(self, basic_df, mock_feature_engine):
        """TEST: should_raise_valueerror_when_operation_is_not_supported"""
        # ARRANGE: FeatureEngineWrapper and invalid operation
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            invalid_operation = 'invalid_operation'

            # ACT & ASSERT: Verify ValueError is raised
            with pytest.raises(ValueError, match=f"Operation '{invalid_operation}' not supported"):
                wrapper.execute(invalid_operation, basic_df)

    def test_execute_with_empty_dataframe(self, edge_case_dfs, mock_feature_engine):
        """TEST: should_handle_empty_dataframe_gracefully"""
        # ARRANGE: Empty DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            empty_df = edge_case_dfs['empty']
            # Mock the feature-engine imputer
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = empty_df
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            # ACT: Execute operation on empty DataFrame
            result = wrapper.execute('advanced_imputation', empty_df)

            # ASSERT: Verify operation handles empty DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from advanced_imputation"
            assert len(result) == 0, "Expected empty DataFrame from advanced_imputation"

    def test_execute_with_single_row(self, edge_case_dfs, mock_feature_engine):
        """TEST: should_handle_single_row_dataframe"""
        # ARRANGE: Single row DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            single_row_df = edge_case_dfs['single_row']
            # Mock the feature-engine imputer
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = single_row_df
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            # ACT: Execute operation on single row DataFrame
            result = wrapper.execute('advanced_imputation', single_row_df)

            # ASSERT: Verify operation handles single row DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from advanced_imputation"
            assert len(result) == 1, "Expected single row from advanced_imputation"

    def test_execute_with_large_dataframe(self, large_df, mock_feature_engine):
        """TEST: should_handle_large_dataframe_efficiently"""
        # ARRANGE: Large DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine imputer
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = large_df
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            # ACT: Execute operation on large DataFrame
            result = wrapper.execute('advanced_imputation', large_df)

            # ASSERT: Verify operation handles large DataFrame
            assert isinstance(result, pd.DataFrame), "Expected DataFrame from advanced_imputation"
            assert len(result) == len(large_df), f"Expected same number of rows, got {len(result)} != {len(large_df)}"

    def test_performance_timing(self, basic_df, mock_feature_engine):
        """TEST: should_log_execution_time_for_operations"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock the feature-engine imputer
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = basic_df
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            # ACT: Execute operation and capture logs
            with patch('csv_cleaner.wrappers.feature_engine_wrapper.logger') as mock_logger:
                result = wrapper.execute('advanced_imputation', basic_df)

            # ASSERT: Verify timing is logged
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
            # Check that info and completion logs were called
            assert mock_logger.info.called, "Expected timing information to be logged"

    def test_error_handling_feature_engine_function_failure(self, basic_df, mock_feature_engine):
        """TEST: should_handle_feature_engine_function_failures_gracefully"""
        # ARRANGE: FeatureEngineWrapper with failing feature-engine function
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Make feature-engine.MeanMedianImputer raise an exception
            mock_feature_engine.MeanMedianImputer.side_effect = Exception("Feature-engine function failed")

            # ACT & ASSERT: Verify exception is re-raised
            with pytest.raises(Exception, match="Feature-engine function failed"):
                wrapper.execute('advanced_imputation', basic_df)

    def test_error_handling_dataframe_not_provided(self, mock_feature_engine):
        """TEST: should_raise_typeerror_when_dataframe_is_not_provided"""
        # ARRANGE: FeatureEngineWrapper without DataFrame
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()

            # ACT & ASSERT: Verify TypeError is raised
            with pytest.raises(TypeError):
                wrapper.execute('advanced_imputation', None)

    def test_advanced_imputation_with_different_methods(self, missing_data_df, mock_feature_engine):
        """TEST: should_handle_different_imputation_methods"""
        # ARRANGE: DataFrame with missing data and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            methods = ['mean', 'median', 'random', 'end_tail']

            for method in methods:
                # Mock the appropriate feature-engine imputer
                mock_imputer = Mock()
                mock_imputer.fit_transform.return_value = missing_data_df.fillna(0)

                if method == 'mean':
                    mock_feature_engine.MeanMedianImputer.return_value = mock_imputer
                elif method == 'median':
                    mock_feature_engine.MeanMedianImputer.return_value = mock_imputer
                elif method == 'random':
                    mock_feature_engine.RandomSampleImputer.return_value = mock_imputer
                elif method == 'end_tail':
                    mock_feature_engine.EndTailImputer.return_value = mock_imputer

                # ACT: Execute advanced_imputation with different method
                result = wrapper.execute('advanced_imputation', missing_data_df, method=method)

                # ASSERT: Verify operation executed successfully
                assert isinstance(result, pd.DataFrame), f"Expected DataFrame for method '{method}'"
                assert len(result) == len(missing_data_df), f"Expected same number of rows for method '{method}'"

    def test_categorical_encoding_with_different_methods(self, basic_df, mock_feature_engine):
        """TEST: should_handle_different_encoding_methods"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            methods = ['onehot', 'ordinal', 'mean', 'rare']

            for method in methods:
                # Mock the appropriate feature-engine encoder
                mock_encoder = Mock()
                mock_encoder.fit_transform.return_value = basic_df.copy()

                if method == 'onehot':
                    mock_feature_engine.OneHotEncoder.return_value = mock_encoder
                elif method == 'ordinal':
                    mock_feature_engine.OrdinalEncoder.return_value = mock_encoder
                elif method == 'mean':
                    mock_feature_engine.MeanEncoder.return_value = mock_encoder
                elif method == 'rare':
                    mock_feature_engine.RareLabelEncoder.return_value = mock_encoder

                # ACT: Execute categorical_encoding with different method
                if method == 'mean':
                    # Mean encoding requires a target variable
                    result = wrapper.execute('categorical_encoding', basic_df, method=method, target_variable='active')
                else:
                    result = wrapper.execute('categorical_encoding', basic_df, method=method)

                # ASSERT: Verify operation executed successfully
                assert isinstance(result, pd.DataFrame), f"Expected DataFrame for method '{method}'"
                assert len(result) == len(basic_df), f"Expected same number of rows for method '{method}'"

    def test_outlier_detection_with_different_methods(self, basic_df, mock_feature_engine):
        """TEST: should_handle_different_outlier_detection_methods"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            methods = ['iqr', 'winsorize']

            for method in methods:
                # Mock the appropriate feature-engine detector
                mock_detector = Mock()
                mock_detector.fit_transform.return_value = basic_df.copy()

                if method == 'iqr':
                    mock_feature_engine.OutlierTrimmer.return_value = mock_detector
                elif method == 'winsorize':
                    mock_feature_engine.Winsorizer.return_value = mock_detector

                # ACT: Execute outlier_detection with different method
                result = wrapper.execute('outlier_detection', basic_df, method=method)

                # ASSERT: Verify operation executed successfully
                assert isinstance(result, pd.DataFrame), f"Expected DataFrame for method '{method}'"
                assert len(result) == len(basic_df), f"Expected same number of rows for method '{method}'"

    def test_variable_selection_with_different_methods(self, basic_df, mock_feature_engine):
        """TEST: should_handle_different_variable_selection_methods"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            methods = ['constant', 'correlated', 'duplicate']

            for method in methods:
                # Mock the appropriate feature-engine selector
                mock_selector = Mock()
                mock_selector.fit_transform.return_value = basic_df.drop(columns=['active'])

                if method == 'constant':
                    mock_feature_engine.DropConstantFeatures.return_value = mock_selector
                elif method == 'correlated':
                    mock_feature_engine.DropCorrelatedFeatures.return_value = mock_selector
                elif method == 'duplicate':
                    mock_feature_engine.DropDuplicateFeatures.return_value = mock_selector

                # ACT: Execute variable_selection with different method
                result = wrapper.execute('variable_selection', basic_df, method=method)

                # ASSERT: Verify operation executed successfully
                assert isinstance(result, pd.DataFrame), f"Expected DataFrame for method '{method}'"

    def test_data_transformation_with_different_methods(self, basic_df, mock_feature_engine):
        """TEST: should_handle_different_data_transformation_methods"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            methods = ['log', 'power']

            for method in methods:
                # Mock the appropriate feature-engine transformer
                mock_transformer = Mock()
                mock_transformer.fit_transform.return_value = basic_df.copy()

                if method == 'log':
                    mock_feature_engine.LogTransformer.return_value = mock_transformer
                elif method == 'power':
                    mock_feature_engine.PowerTransformer.return_value = mock_transformer

                # ACT: Execute data_transformation with different method
                result = wrapper.execute('data_transformation', basic_df, method=method)

                # ASSERT: Verify operation executed successfully
                assert isinstance(result, pd.DataFrame), f"Expected DataFrame for method '{method}'"
                assert len(result) == len(basic_df), f"Expected same number of rows for method '{method}'"

    def test_multiple_operations_sequence(self, basic_df, mock_feature_engine):
        """TEST: should_execute_multiple_operations_in_sequence"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            operations = ['advanced_imputation', 'categorical_encoding', 'outlier_detection']

            # Mock all operations to return the DataFrame
            for operation in operations:
                if operation == 'advanced_imputation':
                    mock_imputer = Mock()
                    mock_imputer.fit_transform.return_value = basic_df.copy()
                    mock_feature_engine.MeanMedianImputer.return_value = mock_imputer
                elif operation == 'categorical_encoding':
                    mock_encoder = Mock()
                    mock_encoder.fit_transform.return_value = basic_df.copy()
                    mock_feature_engine.OneHotEncoder.return_value = mock_encoder
                elif operation == 'outlier_detection':
                    mock_detector = Mock()
                    mock_detector.fit_transform.return_value = basic_df.copy()
                    mock_feature_engine.OutlierTrimmer.return_value = mock_detector

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

    def test_operation_with_dataframe_method_chaining(self, basic_df, mock_feature_engine):
        """TEST: should_support_dataframe_method_chaining"""
        # ARRANGE: DataFrame and FeatureEngineWrapper
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            wrapper = FeatureEngineWrapper()
            # Mock feature-engine methods to return modified DataFrames
            mock_imputer = Mock()
            mock_imputer.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.MeanMedianImputer.return_value = mock_imputer

            mock_encoder = Mock()
            mock_encoder.fit_transform.return_value = basic_df.copy()
            mock_feature_engine.OneHotEncoder.return_value = mock_encoder

            # ACT: Execute operations in sequence
            result1 = wrapper.execute('advanced_imputation', basic_df)
            result2 = wrapper.execute('categorical_encoding', result1)

            # ASSERT: Verify method chaining works
            assert isinstance(result1, pd.DataFrame), "Expected DataFrame from first operation"
            assert isinstance(result2, pd.DataFrame), "Expected DataFrame from second operation"
            assert len(result2) == len(result1), "Expected same number of rows after encoding"
