"""
Test fixtures for configuration testing.
"""

import yaml
import tempfile
import os
from pathlib import Path


def create_valid_config_file(file_path: str) -> None:
    """Create a valid configuration file for testing.

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
        'output_format': 'csv',
        'log_level': 'INFO',
        'log_file': '/tmp/test.log',
        'default_operations': ['remove_duplicates', 'clean_names', 'handle_missing']
    }

    with open(file_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2)


def create_invalid_config_file(file_path: str) -> None:
    """Create an invalid configuration file for testing error handling.

    Args:
        file_path: Path to create the invalid config file.
    """
    invalid_content = """
    default_encoding: utf-8
    max_memory_usage: invalid_value
    chunk_size:
        - invalid
        - list
    parallel_processing: not_a_boolean
    ai_enabled: maybe
    """

    with open(file_path, 'w') as f:
        f.write(invalid_content)


def create_empty_config_file(file_path: str) -> None:
    """Create an empty configuration file for testing.

    Args:
        file_path: Path to create the empty config file.
    """
    with open(file_path, 'w') as f:
        f.write('')


def create_partial_config_file(file_path: str) -> None:
    """Create a partial configuration file with only some settings.

    Args:
        file_path: Path to create the partial config file.
    """
    partial_config = {
        'default_encoding': 'latin-1',
        'chunk_size': 5000,
        'ai_enabled': True
    }

    with open(file_path, 'w') as f:
        yaml.dump(partial_config, f, default_flow_style=False, indent=2)


def create_large_config_file(file_path: str) -> None:
    """Create a large configuration file for testing performance.

    Args:
        file_path: Path to create the large config file.
    """
    # Create a large config with many operations
    large_config = {
        'default_encoding': 'utf-8',
        'max_memory_usage': 2048 * 1024 * 1024,
        'chunk_size': 20000,
        'parallel_processing': True,
        'max_workers': 8,
        'ai_enabled': True,
        'default_llm_provider': 'anthropic',
        'ai_api_keys': {
            'openai': 'key1',
            'anthropic': 'key2',
            'ollama': 'key3'
        },
        'ai_cost_limit': 50.0,
        'backup_enabled': True,
        'backup_suffix': '.backup',
        'output_format': 'csv',
        'log_level': 'DEBUG',
        'log_file': '/var/log/csv-cleaner.log',
        'default_operations': [
            'remove_duplicates', 'clean_names', 'handle_missing',
            'convert_types', 'rename_columns', 'drop_missing',
            'fill_missing', 'clean_text', 'fix_dates'
        ]
    }

    with open(file_path, 'w') as f:
        yaml.dump(large_config, f, default_flow_style=False, indent=2)


def get_test_config_scenarios():
    """Get various test configuration scenarios.

    Returns:
        Dictionary of test scenario names and their config data.
    """
    return {
        'minimal': {
            'default_encoding': 'utf-8',
            'chunk_size': 1000
        },
        'ai_enabled': {
            'default_encoding': 'utf-8',
            'ai_enabled': True,
            'default_llm_provider': 'openai',
            'ai_api_keys': {'openai': 'test-key'},
            'ai_cost_limit': 5.0
        },
        'high_performance': {
            'default_encoding': 'utf-8',
            'max_memory_usage': 4096 * 1024 * 1024,
            'chunk_size': 50000,
            'parallel_processing': True,
            'max_workers': 16
        },
        'debug_mode': {
            'default_encoding': 'utf-8',
            'log_level': 'DEBUG',
            'log_file': '/tmp/debug.log',
            'progress_tracking': True
        },
        'custom_operations': {
            'default_encoding': 'utf-8',
            'default_operations': ['remove_duplicates', 'convert_types']
        }
    }


def create_temp_config_file(config_data: dict) -> str:
    """Create a temporary configuration file with given data.

    Args:
        config_data: Configuration data to write to file.

    Returns:
        Path to the created temporary file.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2)
        return f.name


def cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file.

    Args:
        file_path: Path to the file to remove.
    """
    try:
        os.unlink(file_path)
    except OSError:
        pass  # File might already be deleted
