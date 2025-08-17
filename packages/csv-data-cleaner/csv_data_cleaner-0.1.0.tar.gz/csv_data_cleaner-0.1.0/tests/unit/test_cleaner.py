"""
Unit tests for CSVCleaner class.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config


class TestCSVCleaner:
    """Test cases for CSVCleaner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.cleaner = CSVCleaner(self.config)

        # Create test data
        self.test_data = pd.DataFrame({
            'Name': ['John', 'Jane', 'John', 'Bob', 'Alice'],
            'Age': [25, 30, 25, 35, None],
            'City': ['NYC', 'LA', 'NYC', 'Chicago', 'Boston'],
            'Salary': [50000, 60000, 50000, 70000, 55000]
        })

    def test_cleaner_initialization(self):
        """Test CSVCleaner initialization."""
        assert self.cleaner is not None
        assert self.cleaner.config is not None
        assert self.cleaner.library_manager is not None
        assert self.cleaner.file_operations is not None

    def test_validate_operations_valid(self):
        """Test operation validation with valid operations."""
        operations = ['remove_duplicates', 'drop_missing']
        valid_ops = self.cleaner.validate_operations(operations)
        assert len(valid_ops) == 2
        assert 'remove_duplicates' in valid_ops
        assert 'drop_missing' in valid_ops

    def test_validate_operations_invalid(self):
        """Test operation validation with invalid operations."""
        operations = ['invalid_operation', 'remove_duplicates']
        valid_ops = self.cleaner.validate_operations(operations)
        assert len(valid_ops) == 1
        assert 'remove_duplicates' in valid_ops

    def test_validate_operations_empty(self):
        """Test operation validation with empty list."""
        with pytest.raises(ValueError, match="No operations specified"):
            self.cleaner.validate_operations([])

    def test_validate_operations_none_valid(self):
        """Test operation validation with no valid operations."""
        with pytest.raises(ValueError, match="No valid operations found"):
            self.cleaner.validate_operations(['invalid_op1', 'invalid_op2'])

    def test_clean_dataframe_remove_duplicates(self):
        """Test DataFrame cleaning with remove_duplicates operation."""
        operations = ['remove_duplicates']
        result = self.cleaner.clean_dataframe(self.test_data, operations)

        assert len(result) == 4  # Should remove one duplicate row
        assert len(result.columns) == 4  # Same number of columns

    def test_clean_dataframe_empty(self):
        """Test DataFrame cleaning with empty DataFrame."""
        empty_df = pd.DataFrame()
        operations = ['remove_duplicates']

        # The cleaner should handle empty DataFrames gracefully
        result = self.cleaner.clean_dataframe(empty_df, operations)
        assert result.empty

    def test_get_supported_operations(self):
        """Test getting supported operations."""
        operations = self.cleaner.get_supported_operations()
        assert isinstance(operations, list)
        assert len(operations) > 0
        assert 'remove_duplicates' in operations

    def test_get_operation_info(self):
        """Test getting operation information."""
        info = self.cleaner.get_operation_info('remove_duplicates')
        assert info is not None
        assert 'name' in info
        assert 'description' in info

    def test_get_operation_info_invalid(self):
        """Test getting operation information for invalid operation."""
        info = self.cleaner.get_operation_info('invalid_operation')
        assert info is None

    def test_get_operations_summary_empty(self):
        """Test getting operations summary when no operations performed."""
        summary = self.cleaner.get_operations_summary()
        assert summary['total_operations'] == 0
        assert summary['operations'] == []

    def test_reset_session(self):
        """Test resetting the cleaning session."""
        # Perform some operations to populate history
        self.cleaner.clean_dataframe(self.test_data, ['remove_duplicates'])

        # Reset session
        self.cleaner.reset_session()

        # Check that history is cleared
        summary = self.cleaner.get_operations_summary()
        assert summary['total_operations'] == 0

    def test_clean_file_basic(self):
        """Test basic file cleaning functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_file = f.name

        try:
            output_file = input_file.replace('.csv', '_cleaned.csv')
            operations = ['remove_duplicates']

            summary = self.cleaner.clean_file(input_file, output_file, operations)

            assert summary['success'] is True
            assert summary['input_rows'] == 5
            assert summary['output_rows'] == 4
            assert summary['rows_removed'] == 1
            assert Path(output_file).exists()

            # Clean up
            os.unlink(output_file)

        finally:
            os.unlink(input_file)

    def test_clean_file_input_not_found(self):
        """Test file cleaning with non-existent input file."""
        with pytest.raises(FileNotFoundError):
            self.cleaner.clean_file('nonexistent.csv', 'output.csv')

    def test_clean_file_default_operations(self):
        """Test file cleaning with default operations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.test_data.to_csv(f.name, index=False)
            input_file = f.name

        try:
            output_file = input_file.replace('.csv', '_cleaned.csv')

            summary = self.cleaner.clean_file(input_file, output_file)

            assert summary['success'] is True
            assert Path(output_file).exists()

            # Clean up
            os.unlink(output_file)

        finally:
            os.unlink(input_file)
