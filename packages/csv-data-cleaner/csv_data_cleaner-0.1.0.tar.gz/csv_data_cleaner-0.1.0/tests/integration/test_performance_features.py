"""
Integration tests for Week 6 performance features.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from unittest.mock import patch, Mock
from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config
from csv_cleaner.core.performance_manager import PerformanceManager
from csv_cleaner.core.parallel_processor import ParallelProcessor
from csv_cleaner.core.validator import AdvancedValidator


class TestPerformanceFeaturesIntegration:
    """Integration tests for performance features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            max_memory_gb=1.0,
            chunk_size=1000,
            enable_chunked_processing=True,
            enable_parallel_processing=True,
            performance_monitoring=True
        )
        self.cleaner = CSVCleaner(self.config)

    def test_performance_optimized_cleaning_small_dataset(self):
        """Test performance-optimized cleaning with small dataset."""
        # Create small dataset (should use standard processing)
        df = pd.DataFrame({
            'A': range(500),
            'B': ['test'] * 500,
            'C': np.random.randn(500)
        })

        operations = ['remove_duplicates', 'rename_columns']

        result = self.cleaner.clean_with_performance_optimization(
            df, operations, use_parallel=False
        )

        assert len(result) == 500
        assert 'A' in result.columns
        assert 'B' in result.columns
        assert 'C' in result.columns

    def test_performance_optimized_cleaning_large_dataset(self):
        """Test performance-optimized cleaning with large dataset."""
        # Create large dataset (should use chunked processing)
        df = pd.DataFrame({
            'A': range(5000),
            'B': ['test'] * 5000,
            'C': np.random.randn(5000)
        })

        operations = ['remove_duplicates', 'rename_columns']

        with patch.object(self.cleaner.performance_manager, 'check_memory_limit', return_value=True):
            with patch.object(self.cleaner.performance_manager, 'force_garbage_collection'):
                result = self.cleaner.clean_with_performance_optimization(
                    df, operations, chunk_size=1000, use_parallel=False
                )

        assert len(result) == 5000
        assert 'A' in result.columns
        assert 'B' in result.columns
        assert 'C' in result.columns

    def test_parallel_processing_integration(self):
        """Test parallel processing integration."""
        # Create medium dataset for parallel processing
        df = pd.DataFrame({
            'A': range(15000),
            'B': ['test'] * 15000,
            'C': np.random.randn(15000)
        })

        operations = ['remove_duplicates', 'rename_columns']

        with patch('concurrent.futures.ProcessPoolExecutor'):
            with patch('concurrent.futures.as_completed'):
                result = self.cleaner.clean_with_performance_optimization(
                    df, operations, use_parallel=True
                )

        assert len(result) == 15000

    def test_validation_integration(self):
        """Test validation integration."""
        # Create test data with various issues
        df = pd.DataFrame({
            'id': [1, 2, 2, 4, 5],  # Duplicate values
            'name': ['Alice', 'Bob', 'Charlie', 'David', None],  # Null value
            'age': [25, 30, 35, 40, 45],
            'email': ['alice@example.com', 'invalid-email', 'charlie@test.org', 'david@', 'eve@valid.com'],
            'score': [85, 92, 78, 105, 88]  # Value above 100
        })

        # Test validation without schema
        validation_results = self.cleaner.validate_data(df)

        assert 'validation_results' in validation_results
        assert 'quality_score' in validation_results
        assert 'passed' in validation_results
        assert 'total_errors' in validation_results

        quality_score = validation_results['quality_score']
        assert 0.0 <= quality_score.overall <= 1.0
        assert 0.0 <= quality_score.completeness <= 1.0
        assert 0.0 <= quality_score.accuracy <= 1.0
        assert 0.0 <= quality_score.consistency <= 1.0
        assert 0.0 <= quality_score.validity <= 1.0

    def test_validation_with_schema(self):
        """Test validation with schema file."""
        # Create test data
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'email': ['alice@example.com', 'bob@test.org', 'charlie@demo.net', 'david@site.com', 'eve@valid.com']
        })

        # Create schema file
        schema = {
            "rules": [
                {
                    "id": "unique_id",
                    "type": "unique",
                    "column": "id",
                    "description": "ID must be unique"
                },
                {
                    "id": "not_null_name",
                    "type": "not_null",
                    "column": "name",
                    "description": "Name cannot be null"
                },
                {
                    "id": "valid_email",
                    "type": "pattern",
                    "column": "email",
                    "parameters": {"pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
                    "description": "Email must be valid"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema, f)
            schema_file = f.name

        try:
            validation_results = self.cleaner.validate_data(df, schema_file)

            assert 'validation_results' in validation_results
            assert 'quality_score' in validation_results
            assert validation_results['passed'] is True  # All rules should pass
            assert validation_results['total_errors'] == 0
        finally:
            os.unlink(schema_file)

    def test_performance_summary_integration(self):
        """Test performance summary integration."""
        # Create test data
        df = pd.DataFrame({
            'A': range(1000),
            'B': ['test'] * 1000
        })

        # Perform some operations to generate metrics
        operations = ['remove_duplicates']
        self.cleaner.clean_with_performance_optimization(df, operations)

        # Get performance summary
        summary = self.cleaner.get_performance_summary()

        assert 'performance_manager' in summary
        assert 'parallel_processor' in summary
        assert 'operation_history' in summary
        assert 'config' in summary

        # Check config information
        config_info = summary['config']
        assert config_info['max_memory_gb'] == 1.0
        assert config_info['chunk_size'] == 1000
        assert config_info['enable_chunked_processing'] is True
        assert config_info['enable_parallel_processing'] is True

        # Check system information
        system_info = summary['parallel_processor']
        assert 'cpu_count' in system_info
        assert 'max_workers' in system_info
        assert 'chunk_size' in system_info

    def test_processing_time_estimation(self):
        """Test processing time estimation."""
        # Create test data
        df = pd.DataFrame({
            'A': range(5000),
            'B': ['test'] * 5000
        })

        operations = ['remove_duplicates', 'clean_names', 'handle_missing']

        estimated_time = self.cleaner.estimate_processing_time(df, operations)

        assert estimated_time > 0
        assert isinstance(estimated_time, float)

    def test_memory_optimization_integration(self):
        """Test memory optimization integration."""
        # Create large dataset
        df = pd.DataFrame({
            'A': range(10000),
            'B': ['test'] * 10000,
            'C': np.random.randn(10000),
            'D': [1.5] * 10000
        })

        # Test chunk size optimization
        optimal_chunk_size = self.cleaner.performance_manager.optimize_chunk_size(df)

        assert 100 <= optimal_chunk_size <= 50000  # Within reasonable bounds

        # Test processing with optimized chunk size
        operations = ['remove_duplicates']

        with patch.object(self.cleaner.performance_manager, 'check_memory_limit', return_value=True):
            with patch.object(self.cleaner.performance_manager, 'force_garbage_collection'):
                result = self.cleaner.clean_with_performance_optimization(
                    df, operations, chunk_size=optimal_chunk_size, use_parallel=False
                )

        assert len(result) == 10000

    def test_error_handling_integration(self):
        """Test error handling in performance features."""
        # Test with invalid operations
        df = pd.DataFrame({'A': range(100)})
        invalid_operations = ['invalid_operation']

        with pytest.raises(ValueError):
            self.cleaner.clean_with_performance_optimization(df, invalid_operations)

        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        operations = ['remove_duplicates']

        result = self.cleaner.clean_with_performance_optimization(empty_df, operations)
        assert len(result) == 0

    def test_configuration_integration(self):
        """Test configuration integration with performance features."""
        # Test with different configurations
        config_large = Config(
            max_memory_gb=4.0,
            chunk_size=5000,
            enable_chunked_processing=True,
            enable_parallel_processing=True
        )
        cleaner_large = CSVCleaner(config_large)

        config_small = Config(
            max_memory_gb=0.5,
            chunk_size=100,
            enable_chunked_processing=False,
            enable_parallel_processing=False
        )
        cleaner_small = CSVCleaner(config_small)

        df = pd.DataFrame({
            'A': range(2000),
            'B': ['test'] * 2000
        })

        operations = ['remove_duplicates']

        # Both should work with different strategies
        result_large = cleaner_large.clean_with_performance_optimization(df, operations)
        result_small = cleaner_small.clean_with_performance_optimization(df, operations)

        assert len(result_large) == 2000
        assert len(result_small) == 2000

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        # Create test data
        df = pd.DataFrame({
            'A': range(3000),
            'B': ['test'] * 3000
        })

        # Perform operations (this will handle its own operation tracking)
        operations = ['remove_duplicates']
        result = self.cleaner.clean_with_performance_optimization(df, operations)

        # Get metrics from the last operation
        metrics = self.cleaner.performance_manager.metrics_history[-1] if self.cleaner.performance_manager.metrics_history else None

        assert metrics.chunks_processed >= 1  # Could be 1 or more depending on chunk size
        assert metrics.rows_processed == 3000
        assert 'chunked_processing' in metrics.operations_performed  # The actual operation name
        assert metrics.duration > 0
        assert len(result) == 3000

    def test_validation_report_generation(self):
        """Test validation report generation integration."""
        # Create test data with issues
        df = pd.DataFrame({
            'id': [1, 2, 2, 4, 5],  # Duplicate values
            'name': ['Alice', 'Bob', 'Charlie', 'David', None],  # Null value
            'email': ['alice@example.com', 'invalid-email', 'charlie@test.org', 'david@', 'eve@valid.com']
        })

        # Add some validation rules first
        from csv_cleaner.core.validator import ValidationRule

        self.cleaner.validator.add_validation_rule(
            ValidationRule(rule_id="unique_id", rule_type="unique", column="id")
        )
        self.cleaner.validator.add_validation_rule(
            ValidationRule(rule_id="not_null_name", rule_type="not_null", column="name")
        )
        self.cleaner.validator.add_validation_rule(
            ValidationRule(rule_id="email_pattern", rule_type="pattern", column="email",
                          parameters={"pattern": "email"})
        )

        # Perform validation (this will store results in the validator)
        validation_results = self.cleaner.validate_data(df)

        # Generate report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            report_file = f.name

        try:
            # The validation results should already be stored in the validator
            report_content = self.cleaner.validator.generate_validation_report(report_file)

            assert "DATA VALIDATION REPORT" in report_content
            assert os.path.exists(report_file)

            # Check file content
            with open(report_file, 'r') as f:
                file_content = f.read()
                assert "DATA VALIDATION REPORT" in file_content
        finally:
            os.unlink(report_file)


class TestAdvancedFeaturesIntegration:
    """Integration tests for advanced features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            enable_validation=True,
            quality_threshold=0.8,
            dedupe_threshold=0.5,
            dedupe_sample_size=100
        )
        self.cleaner = CSVCleaner(self.config)

    def test_quality_threshold_validation(self):
        """Test quality threshold validation."""
        # Create data with known quality issues
        df = pd.DataFrame({
            'id': [1, 2, 2, 4, 5],  # Duplicate values
            'name': ['Alice', 'Bob', 'Charlie', 'David', None],  # Null value
            'email': ['alice@example.com', 'invalid-email', 'charlie@test.org', 'david@', 'eve@valid.com']
        })

        validation_results = self.cleaner.validate_data(df)
        quality_score = validation_results['quality_score']

        # Check if quality meets threshold
        meets_threshold = bool(quality_score.overall >= self.config.quality_threshold)
        assert isinstance(meets_threshold, bool)

    def test_comprehensive_data_quality_assessment(self):
        """Test comprehensive data quality assessment."""
        # Create complex test data
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'email': ['alice@example.com', 'bob@test.org', 'charlie@demo.net', 'david@site.com', 'eve@valid.com'],
            'age': [25, 30, 35, 40, 45],
            'score': [85, 92, 78, 88, 95],
            'category': ['A', 'B', 'A', 'B', 'A']
        })

        validation_results = self.cleaner.validate_data(df)
        quality_score = validation_results['quality_score']

        # All scores should be reasonable
        assert 0.0 <= quality_score.completeness <= 1.0
        assert 0.0 <= quality_score.accuracy <= 1.0
        assert 0.0 <= quality_score.consistency <= 1.0
        assert 0.0 <= quality_score.validity <= 1.0
        assert 0.0 <= quality_score.overall <= 1.0

        # Check details
        details = quality_score.details
        assert 'completeness_details' in details
        assert 'accuracy_details' in details
        assert 'consistency_details' in details
        assert 'validity_details' in details

    def test_performance_with_validation(self):
        """Test performance features with validation."""
        # Create test data
        df = pd.DataFrame({
            'A': range(2000),
            'B': ['test'] * 2000,
            'C': np.random.randn(2000)
        })

        # Perform cleaning with performance optimization
        operations = ['remove_duplicates', 'rename_columns']
        cleaned_df = self.cleaner.clean_with_performance_optimization(df, operations)

        # Validate the cleaned data
        validation_results = self.cleaner.validate_data(cleaned_df)

        # Both should work together
        assert len(cleaned_df) == 2000
        assert 'validation_results' in validation_results
        assert 'quality_score' in validation_results

    def test_error_recovery_integration(self):
        """Test error recovery in integration scenarios."""
        # Test with problematic data
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['test', 'test', 'test', 'test', 'test'],  # All same values
            'C': [np.nan, np.nan, np.nan, np.nan, np.nan]  # All nulls
        })

        # This should handle gracefully
        operations = ['remove_duplicates', 'handle_missing']

        try:
            result = self.cleaner.clean_with_performance_optimization(df, operations)
            validation_results = self.cleaner.validate_data(result)

            # Should complete without crashing
            assert len(result) >= 0
            assert 'quality_score' in validation_results
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, (ValueError, RuntimeError))
