"""
Test fixtures for CLI testing.
"""

import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from unittest.mock import Mock, patch, MagicMock
import click
from click.testing import CliRunner

from csv_cleaner.core.config import Config
from csv_cleaner.core.file_operations import FileOperations
from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.visualization_manager import VisualizationManager


def create_mock_click_context():
    """Create a mock Click context for testing.

    Returns:
        Mock Click context object.
    """
    context = Mock()
    context.obj = {}
    context.params = {}
    context.command = Mock()
    context.command.name = "test_command"
    return context


def create_mock_click_runner():
    """Create a Click test runner for CLI testing.

    Returns:
        CliRunner instance for testing.
    """
    return CliRunner()


def create_mock_csv_cleaner():
    """Create a mock CSVCleaner instance.

    Returns:
        Mock CSVCleaner object.
    """
    cleaner = Mock(spec=CSVCleaner)

    # Mock clean_file method
    cleaner.clean_file.return_value = {
        'success': True,
        'input_rows': 100,
        'input_columns': 5,
        'output_rows': 95,
        'output_columns': 4,
        'rows_removed': 5,
        'columns_removed': 1,
        'total_execution_time': 2.5,
        'backup_created': True,
        'backup_path': '/tmp/backup.csv',
        'operations_performed': ['remove_duplicates', 'drop_missing']
    }

    # Mock get_supported_operations method
    cleaner.get_supported_operations.return_value = [
        'remove_duplicates', 'drop_missing', 'fill_missing',
        'remove_outliers', 'normalize_columns'
    ]

    # Mock file_operations
    cleaner.file_operations = Mock()

    # Create a proper mock DataFrame with required attributes
    mock_df = Mock()
    mock_df.__len__ = Mock(return_value=5)  # len(df) returns 5
    mock_df.columns = ['col1', 'col2', 'col3']
    mock_df.isna.return_value.sum.return_value.sum.return_value = 2  # Missing values
    mock_df.duplicated.return_value.sum.return_value = 1  # Duplicate rows
    mock_df.nunique.return_value = 4  # Unique values per column

    # Mock column access for df[column]
    def mock_getitem(column):
        mock_column = Mock()
        mock_column.isna.return_value.sum.return_value = 1  # 1 null value per column
        mock_column.nunique.return_value = 4  # 4 unique values per column
        return mock_column

    mock_df.__getitem__ = Mock(side_effect=mock_getitem)

    cleaner.file_operations.read_csv.return_value = mock_df
    cleaner.file_operations.write_csv.return_value = None

    # Mock library_manager
    cleaner.library_manager = Mock()
    cleaner.library_manager.get_wrapper_info.return_value = {
        'pandas': {
            'class': 'PandasWrapper',
            'supported_operations': ['remove_duplicates', 'drop_missing']
        },
        'pyjanitor': {
            'class': 'PyJanitorWrapper',
            'supported_operations': ['fill_missing', 'remove_outliers']
        }
    }

    # Mock validator
    cleaner.validator = Mock()
    cleaner.validator.generate_smart_validation_rules.return_value = []
    cleaner.validator.generate_validation_report.return_value = "Mock validation report"

    # Mock validate_data method
    mock_quality_score = Mock()
    mock_quality_score.overall = 0.85
    mock_quality_score.completeness = 0.90
    mock_quality_score.accuracy = 0.80
    mock_quality_score.consistency = 0.88
    mock_quality_score.validity = 0.92

    mock_validation_result = Mock()
    mock_validation_result.passed = True

    cleaner.validate_data.return_value = {
        'quality_score': mock_quality_score,
        'validation_results': [mock_validation_result],
        'total_errors': 0
    }

    # Mock get_performance_summary method
    cleaner.get_performance_summary.return_value = {
        'total_operations': 10,
        'success_rate': 0.9,
        'average_execution_time': 1.5
    }

    return cleaner


def create_mock_file_operations():
    """Create a mock FileOperations instance.

    Returns:
        Mock FileOperations object.
    """
    file_ops = Mock(spec=FileOperations)

    # Mock read_csv method
    file_ops.read_csv.return_value = Mock()  # Mock DataFrame

    # Mock validate_file method
    file_ops.validate_file.return_value = {
        'exists': True,
        'file_path': '/test/file.csv',
        'is_csv': True,
        'encoding': 'utf-8',
        'estimated_rows': 100,
        'estimated_columns': 5,
        'errors': []
    }

    # Mock get_file_info method
    file_ops.get_file_info.return_value = {
        'file_path': '/test/file.csv',
        'file_name': 'file.csv',
        'file_extension': '.csv',
        'parent_directory': '/test',
        'exists': True,
        'size_bytes': 1024,
        'size_mb': 0.001,
        'created_time': 1640995200,
        'modified_time': 1640995200,
        'is_compressed': False,
        'compression_type': None
    }

    # Mock create_backup method
    file_ops.create_backup.return_value = '/test/file.backup_1640995200.csv'

    return file_ops


def create_mock_visualization_manager():
    """Create a mock VisualizationManager instance.

    Returns:
        Mock VisualizationManager object.
    """
    viz_manager = Mock(spec=VisualizationManager)

    # Mock visualization methods
    viz_manager.create_data_quality_heatmap.return_value = '/test/heatmap.png'
    viz_manager.create_correlation_matrix.return_value = '/test/correlation.png'
    viz_manager.create_distribution_plots.return_value = '/test/distribution.png'
    viz_manager.create_summary_report.return_value = '/test/report.html'

    # Mock _generate_summary_statistics method
    viz_manager._generate_summary_statistics.return_value = {
        'total_rows': 100,
        'total_columns': 5,
        'missing_values': 10,
        'duplicate_rows': 5,
        'data_types': {'object': 2, 'int64': 2, 'float64': 1}
    }

    return viz_manager


def create_mock_configuration_manager():
    """Create a mock ConfigurationManager instance.

    Returns:
        Mock ConfigurationManager object.
    """
    config_manager = Mock()

    # Mock load_config method
    config_manager.load_config.return_value = Config()

    # Mock save_config method
    config_manager.save_config.return_value = None

    # Mock config_path property
    config_manager.config_path = '/test/config.yaml'

    return config_manager


def create_test_csv_file(file_path: str, rows: int = 10) -> None:
    """Create a test CSV file for CLI testing.

    Args:
        file_path: Path to create the CSV file.
        rows: Number of rows to generate.
    """
    import pandas as pd

    data = {
        'Name': [f'User_{i}' for i in range(rows)],
        'Age': [20 + i for i in range(rows)],
        'City': [f'City_{i % 3}' for i in range(rows)],
        'Salary': [30000 + i * 1000 for i in range(rows)],
        'Department': [f'Dept_{i % 2}' for i in range(rows)]
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def create_test_config_file(file_path: str) -> None:
    """Create a test configuration file for CLI testing.

    Args:
        file_path: Path to create the config file.
    """
    config_data = {
        'default_encoding': 'utf-8',
        'max_memory_usage': 1024 * 1024 * 1024,
        'chunk_size': 10000,
        'parallel_processing': True,
        'max_workers': 4,
        'ai_enabled': False,
        'default_llm_provider': 'openai',
        'ai_api_keys': {
            'openai': 'test-key-1',
            'anthropic': 'test-key-2'
        },
        'ai_cost_limit': 10.0,
        'backup_enabled': True,
        'backup_suffix': '.backup',
        'log_level': 'INFO',
        'output_format': 'csv',
        'default_operations': ['remove_duplicates', 'drop_missing']
    }

    with open(file_path, 'w') as f:
        import yaml
        yaml.dump(config_data, f)


def create_invalid_csv_file(file_path: str) -> None:
    """Create an invalid CSV file for error testing.

    Args:
        file_path: Path to create the invalid file.
    """
    with open(file_path, 'w') as f:
        f.write("This is not a valid CSV file\n")
        f.write("It has no commas or proper structure\n")


def create_corrupted_csv_file(file_path: str) -> None:
    """Create a corrupted CSV file for error testing.

    Args:
        file_path: Path to create the corrupted file.
    """
    with open(file_path, 'w') as f:
        f.write("Name,Age,City\n")
        f.write("John,25,NYC\n")
        f.write("Jane,30,LA\n")
        f.write("Bob,35,Chicago\n")
        f.write("Alice,28,Boston\n")
        f.write("Invalid,row,with,too,many,columns\n")


def create_large_csv_file(file_path: str, rows: int = 1000) -> None:
    """Create a large CSV file for performance testing.

    Args:
        file_path: Path to create the large file.
        rows: Number of rows to generate.
    """
    import pandas as pd
    import numpy as np

    np.random.seed(42)

    data = {
        'ID': range(1, rows + 1),
        'Name': [f'User_{i}' for i in range(1, rows + 1)],
        'Age': np.random.randint(18, 80, rows),
        'Salary': np.random.randint(30000, 150000, rows),
        'Department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR'], rows),
        'City': np.random.choice(['NYC', 'LA', 'Chicago', 'Boston'], rows),
        'Score': np.random.uniform(0, 100, rows),
        'Active': np.random.choice([True, False], rows)
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def mock_click_echo(output_capture: List[str]):
    """Create a mock for click.echo that captures output.

    Args:
        output_capture: List to capture output strings.

    Returns:
        Mock function that captures click.echo calls.
    """
    def mock_echo(message, *args, **kwargs):
        output_capture.append(str(message))

    return mock_echo


def mock_click_prompt(responses: List[str]):
    """Create a mock for click.prompt that returns predefined responses.

    Args:
        responses: List of responses to return in sequence.

    Returns:
        Mock function that returns predefined responses.
    """
    response_index = [0]  # Use list to make it mutable in closure

    def mock_prompt(message, *args, **kwargs):
        if response_index[0] < len(responses):
            response = responses[response_index[0]]
            response_index[0] += 1
            return response
        else:
            raise click.Abort("No more responses available")

    return mock_prompt


def mock_click_confirm(responses: List[bool]):
    """Create a mock for click.confirm that returns predefined responses.

    Args:
        responses: List of boolean responses to return in sequence.

    Returns:
        Mock function that returns predefined responses.
    """
    response_index = [0]  # Use list to make it mutable in closure

    def mock_confirm(message, *args, **kwargs):
        if response_index[0] < len(responses):
            response = responses[response_index[0]]
            response_index[0] += 1
            return response
        else:
            raise click.Abort("No more responses available")

    return mock_confirm


def mock_click_progressbar():
    """Create a mock for click.progressbar.

    Returns:
        Mock progress bar context manager.
    """
    progress_bar = Mock()
    progress_bar.update = Mock()

    class MockProgressBar:
        def __enter__(self):
            return progress_bar

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    return MockProgressBar()


def create_cli_test_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get various CLI test scenarios.

    Returns:
        Dictionary of test scenario names and their configuration.
    """
    return {
        'basic_clean': {
            'input_file': 'test_input.csv',
            'output_file': 'test_output.csv',
            'operations': 'remove_duplicates,drop_missing',
            'description': 'Basic CSV cleaning workflow'
        },
        'interactive_mode': {
            'input_file': 'test_input.csv',
            'output_file': 'test_output.csv',
            'operations': None,
            'user_responses': ['remove_duplicates,drop_missing', True],
            'description': 'Interactive mode with user input'
        },
        'file_validation': {
            'input_file': 'test_input.csv',
            'output_file': None,
            'operations': None,
            'description': 'File validation command'
        },
        'config_management': {
            'action': 'show',
            'key': None,
            'value': None,
            'description': 'Configuration management'
        },
        'visualization': {
            'input_file': 'test_input.csv',
            'viz_type': 'heatmap',
            'output': 'test_heatmap.png',
            'description': 'Data visualization command'
        },
        'report_generation': {
            'input_file': 'test_input.csv',
            'output': 'test_report.html',
            'format': 'html',
            'description': 'Report generation command'
        },
        'error_handling': {
            'input_file': 'nonexistent.csv',
            'output_file': 'test_output.csv',
            'operations': 'remove_duplicates',
            'description': 'Error handling for invalid files'
        },
        'large_file_processing': {
            'input_file': 'large_input.csv',
            'output_file': 'large_output.csv',
            'operations': 'remove_duplicates',
            'description': 'Large file processing'
        }
    }


def create_error_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get various error scenarios for CLI testing.

    Returns:
        Dictionary of error scenario names and their configuration.
    """
    return {
        'file_not_found': {
            'input_file': '/nonexistent/path/file.csv',
            'expected_error': 'File not found',
            'description': 'Non-existent input file'
        },
        'invalid_operations': {
            'operations': 'invalid_operation,another_invalid',
            'expected_error': 'Invalid operation',
            'description': 'Invalid cleaning operations'
        },
        'permission_error': {
            'input_file': '/root/protected/file.csv',
            'expected_error': 'Permission denied',
            'description': 'File permission issues'
        },
        'invalid_config': {
            'config_file': 'invalid_config.yaml',
            'expected_error': 'Invalid configuration',
            'description': 'Invalid configuration file'
        },
        'user_cancellation': {
            'user_responses': [False],  # User cancels operation
            'expected_error': 'Operation cancelled',
            'description': 'User cancels interactive operation'
        },
        'encoding_error': {
            'input_file': 'corrupted_encoding.csv',
            'expected_error': 'Encoding error',
            'description': 'File encoding issues'
        },
        'memory_error': {
            'input_file': 'extremely_large.csv',
            'expected_error': 'Memory error',
            'description': 'Memory exhaustion scenarios'
        },
        'timeout_error': {
            'input_file': 'slow_processing.csv',
            'expected_error': 'Timeout error',
            'description': 'Processing timeout scenarios'
        }
    }


def cleanup_test_files(file_paths: List[str]) -> None:
    """Clean up test files.

    Args:
        file_paths: List of file paths to remove.
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # File might already be deleted


def create_cli_output_validator():
    """Create a CLI output validator utility.

    Returns:
        Function to validate CLI output patterns.
    """
    def validate_output(output: str, expected_patterns: List[str]) -> bool:
        """Validate CLI output against expected patterns.

        Args:
            output: CLI output string to validate.
            expected_patterns: List of patterns that should be present.

        Returns:
            True if all patterns are found, False otherwise.
        """
        for pattern in expected_patterns:
            if pattern not in output:
                return False
        return True

    return validate_output


def create_performance_monitor():
    """Create a performance monitoring utility for CLI tests.

    Returns:
        Function to monitor CLI command performance.
    """
    import time

    def monitor_performance(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Monitor performance of a CLI command.

        Args:
            func: Function to monitor.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Dictionary with performance metrics.
        """
        start_time = time.time()
        start_memory = 0  # Could add memory monitoring here

        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        execution_time = end_time - start_time

        return {
            'success': success,
            'execution_time': execution_time,
            'result': result,
            'error': error if not success else None
        }

    return monitor_performance
