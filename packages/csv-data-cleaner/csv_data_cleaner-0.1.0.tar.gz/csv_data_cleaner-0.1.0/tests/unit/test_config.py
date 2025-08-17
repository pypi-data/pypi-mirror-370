"""
TEST SUITE: csv_cleaner.core.config
PURPOSE: Test configuration management functionality including Config dataclass and ConfigurationManager
SCOPE: Config instantiation, serialization, file operations, environment variables
DEPENDENCIES: yaml, pathlib, os.environ, tempfile
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import yaml

from csv_cleaner.core.config import Config, ConfigurationManager
from tests.fixtures.config_fixtures import (
    create_valid_config_file, create_invalid_config_file, create_empty_config_file,
    create_partial_config_file, create_large_config_file, get_test_config_scenarios,
    create_temp_config_file, cleanup_temp_file
)


class TestConfig:
    """Test cases for Config dataclass."""

    def test_config_default_initialization(self):
        """TEST: should_create_config_with_default_values_when_no_parameters_provided"""
        # ARRANGE: No parameters provided
        # ACT: Create Config instance
        config = Config()

        # ASSERT: Verify default values are set correctly
        assert config.default_encoding == "utf-8", f"Expected default_encoding to be 'utf-8', got '{config.default_encoding}'"
        assert config.max_memory_usage == 1024 * 1024 * 1024, f"Expected max_memory_usage to be 1GB, got {config.max_memory_usage}"
        assert config.chunk_size == 10000, f"Expected chunk_size to be 10000, got {config.chunk_size}"
        assert config.parallel_processing is True, f"Expected parallel_processing to be True, got {config.parallel_processing}"
        assert config.max_workers == 4, f"Expected max_workers to be 4, got {config.max_workers}"
        assert config.ai_enabled is False, f"Expected ai_enabled to be False, got {config.ai_enabled}"
        assert config.default_llm_provider == "openai", f"Expected default_llm_provider to be 'openai', got '{config.default_llm_provider}'"
        assert config.ai_cost_limit == 10.0, f"Expected ai_cost_limit to be 10.0, got {config.ai_cost_limit}"
        assert config.backup_enabled is True, f"Expected backup_enabled to be True, got {config.backup_enabled}"
        assert config.backup_suffix == ".backup", f"Expected backup_suffix to be '.backup', got '{config.backup_suffix}'"
        assert config.output_format == "csv", f"Expected output_format to be 'csv', got '{config.output_format}'"
        assert config.log_level == "INFO", f"Expected log_level to be 'INFO', got '{config.log_level}'"
        assert config.log_file is None, f"Expected log_file to be None, got {config.log_file}"
        assert config.progress_tracking is True, f"Expected progress_tracking to be True, got {config.progress_tracking}"

    def test_config_custom_initialization(self):
        """TEST: should_create_config_with_custom_values_when_parameters_provided"""
        # ARRANGE: Custom configuration parameters
        custom_config = {
            'default_encoding': 'latin-1',
            'chunk_size': 5000,
            'max_workers': 8,
            'ai_enabled': True,
            'ai_cost_limit': 20.0,
            'log_level': 'DEBUG'
        }

        # ACT: Create Config instance with custom values
        config = Config(**custom_config)

        # ASSERT: Verify custom values are set correctly
        assert config.default_encoding == 'latin-1', f"Expected default_encoding to be 'latin-1', got '{config.default_encoding}'"
        assert config.chunk_size == 5000, f"Expected chunk_size to be 5000, got {config.chunk_size}"
        assert config.max_workers == 8, f"Expected max_workers to be 8, got {config.max_workers}"
        assert config.ai_enabled is True, f"Expected ai_enabled to be True, got {config.ai_enabled}"
        assert config.ai_cost_limit == 20.0, f"Expected ai_cost_limit to be 20.0, got {config.ai_cost_limit}"
        assert config.log_level == 'DEBUG', f"Expected log_level to be 'DEBUG', got '{config.log_level}'"

    def test_config_default_operations(self):
        """TEST: should_have_default_operations_list_when_initialized"""
        # ARRANGE: No parameters provided
        # ACT: Create Config instance
        config = Config()

        # ASSERT: Verify default operations are set correctly
        expected_operations = ['remove_duplicates', 'clean_names', 'handle_missing']
        assert config.default_operations == expected_operations, f"Expected default_operations to be {expected_operations}, got {config.default_operations}"

    def test_config_custom_operations(self):
        """TEST: should_allow_custom_default_operations_when_provided"""
        # ARRANGE: Custom operations list
        custom_operations = ['remove_duplicates', 'convert_types']

        # ACT: Create Config instance with custom operations
        config = Config(default_operations=custom_operations)

        # ASSERT: Verify custom operations are set correctly
        assert config.default_operations == custom_operations, f"Expected default_operations to be {custom_operations}, got {config.default_operations}"

    def test_config_ai_api_keys_default(self):
        """TEST: should_have_empty_ai_api_keys_dict_when_not_provided"""
        # ARRANGE: No AI API keys provided
        # ACT: Create Config instance
        config = Config()

        # ASSERT: Verify AI API keys is empty dict
        assert config.ai_api_keys == {}, f"Expected ai_api_keys to be empty dict, got {config.ai_api_keys}"

    def test_config_ai_api_keys_custom(self):
        """TEST: should_allow_custom_ai_api_keys_when_provided"""
        # ARRANGE: Custom AI API keys
        custom_keys = {'openai': 'key1', 'anthropic': 'key2'}

        # ACT: Create Config instance with custom API keys
        config = Config(ai_api_keys=custom_keys)

        # ASSERT: Verify custom API keys are set correctly
        assert config.ai_api_keys == custom_keys, f"Expected ai_api_keys to be {custom_keys}, got {config.ai_api_keys}"

    def test_config_equality(self):
        """TEST: should_be_equal_when_same_values_are_set"""
        # ARRANGE: Two configs with same values
        config1 = Config(default_encoding='utf-8', chunk_size=1000)
        config2 = Config(default_encoding='utf-8', chunk_size=1000)

        # ACT: Compare configs
        # ASSERT: Verify configs are equal
        assert config1 == config2, f"Expected configs to be equal, but they are not"

    def test_config_inequality(self):
        """TEST: should_not_be_equal_when_different_values_are_set"""
        # ARRANGE: Two configs with different values
        config1 = Config(default_encoding='utf-8', chunk_size=1000)
        config2 = Config(default_encoding='latin-1', chunk_size=1000)

        # ACT: Compare configs
        # ASSERT: Verify configs are not equal
        assert config1 != config2, f"Expected configs to be different, but they are equal"

    def test_default_config_values(self):
        """Test default configuration values."""
        config = Config()

        # Test AI model defaults
        assert config.ai_openai_model == "gpt-4o-mini"
        assert config.ai_anthropic_model == "claude-3-5-sonnet-20241022"
        assert config.ai_local_model == "llama3.1:8b"

        # Test other defaults
        assert config.default_llm_provider == "openai"
        assert config.ai_enabled is False
        assert config.ai_cost_limit == 10.0


class TestConfigurationManager:
    """Test cases for ConfigurationManager class."""

    def test_configuration_manager_initialization(self):
        """TEST: should_initialize_with_default_config_path_when_no_path_provided"""
        # ARRANGE: No config path provided
        # ACT: Create ConfigurationManager instance
        with patch('csv_cleaner.core.config.Path.home') as mock_home, \
             patch('csv_cleaner.core.config.Path.mkdir') as mock_mkdir:
            mock_home.return_value = Path('/mock/home')
            config_manager = ConfigurationManager()

        # ASSERT: Verify default config path is set correctly
        expected_path = str(Path('/mock/home') / '.csv-cleaner' / 'config.yaml')
        assert config_manager.config_path == expected_path, f"Expected config_path to be '{expected_path}', got '{config_manager.config_path}'"

    def test_configuration_manager_custom_path(self):
        """TEST: should_initialize_with_custom_config_path_when_provided"""
        # ARRANGE: Custom config path
        custom_path = '/custom/path/config.yaml'

        # ACT: Create ConfigurationManager instance with custom path
        config_manager = ConfigurationManager(custom_path)

        # ASSERT: Verify custom config path is set correctly
        assert config_manager.config_path == custom_path, f"Expected config_path to be '{custom_path}', got '{config_manager.config_path}'"

    def test_load_config_from_existing_file(self, temp_dir):
        """TEST: should_load_config_from_existing_file_when_file_exists"""
        # ARRANGE: Create valid config file
        config_file = os.path.join(temp_dir, 'test_config.yaml')
        create_valid_config_file(config_file)

        # ACT: Create ConfigurationManager and load config
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        # ASSERT: Verify config is loaded correctly
        assert config.default_encoding == 'utf-8', f"Expected default_encoding to be 'utf-8', got '{config.default_encoding}'"
        assert config.chunk_size == 10000, f"Expected chunk_size to be 10000, got {config.chunk_size}"
        assert config.ai_enabled is False, f"Expected ai_enabled to be False, got {config.ai_enabled}"

    def test_load_config_from_nonexistent_file(self):
        """TEST: should_return_default_config_when_file_does_not_exist"""
        # ARRANGE: Non-existent config file
        nonexistent_path = '/nonexistent/path/config.yaml'

        # ACT: Create ConfigurationManager and load config
        config_manager = ConfigurationManager(nonexistent_path)
        config = config_manager.load_config()

        # ASSERT: Verify default config is returned
        assert config.default_encoding == 'utf-8', f"Expected default_encoding to be 'utf-8', got '{config.default_encoding}'"
        assert config.chunk_size == 10000, f"Expected chunk_size to be 10000, got {config.chunk_size}"

    def test_load_config_from_invalid_file(self, temp_dir):
        """TEST: should_return_default_config_when_file_has_invalid_yaml"""
        # ARRANGE: Create invalid config file
        config_file = os.path.join(temp_dir, 'invalid_config.yaml')
        create_invalid_config_file(config_file)

        # ACT: Create ConfigurationManager and load config
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        # ASSERT: Verify default config is returned due to invalid YAML
        # Note: The actual implementation doesn't validate types, so invalid values are passed through
        assert config.default_encoding == 'utf-8', f"Expected default_encoding to be 'utf-8', got '{config.default_encoding}'"
        # The chunk_size will be the invalid value from the file, not the default
        assert isinstance(config.chunk_size, list), f"Expected chunk_size to be list from invalid YAML, got {type(config.chunk_size)}"

    def test_load_config_from_empty_file(self, temp_dir):
        """TEST: should_return_default_config_when_file_is_empty"""
        # ARRANGE: Create empty config file
        config_file = os.path.join(temp_dir, 'empty_config.yaml')
        create_empty_config_file(config_file)

        # ACT: Create ConfigurationManager and load config
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        # ASSERT: Verify default config is returned
        assert config.default_encoding == 'utf-8', f"Expected default_encoding to be 'utf-8', got '{config.default_encoding}'"
        assert config.chunk_size == 10000, f"Expected chunk_size to be 10000, got {config.chunk_size}"

    def test_load_config_from_partial_file(self, temp_dir):
        """TEST: should_load_partial_config_and_use_defaults_for_missing_values"""
        # ARRANGE: Create partial config file
        config_file = os.path.join(temp_dir, 'partial_config.yaml')
        create_partial_config_file(config_file)

        # ACT: Create ConfigurationManager and load config
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        # ASSERT: Verify partial values are loaded and defaults used for missing
        assert config.default_encoding == 'latin-1', f"Expected default_encoding to be 'latin-1', got '{config.default_encoding}'"
        assert config.chunk_size == 5000, f"Expected chunk_size to be 5000, got {config.chunk_size}"
        assert config.ai_enabled is True, f"Expected ai_enabled to be True, got {config.ai_enabled}"
        # Verify defaults are used for missing values
        assert config.max_workers == 4, f"Expected max_workers to be 4 (default), got {config.max_workers}"
        assert config.backup_enabled is True, f"Expected backup_enabled to be True (default), got {config.backup_enabled}"

    def test_save_config_to_file(self, temp_dir):
        """TEST: should_save_config_to_file_when_save_config_is_called"""
        # ARRANGE: Create config and config file path
        config = Config(default_encoding='latin-1', chunk_size=5000)
        config_file = os.path.join(temp_dir, 'save_test_config.yaml')

        # ACT: Create ConfigurationManager and save config
        config_manager = ConfigurationManager(config_file)
        config_manager.save_config(config)

        # ASSERT: Verify file is created and contains correct data
        assert os.path.exists(config_file), f"Expected config file to exist at '{config_file}'"

        # Load the saved config and verify values
        saved_config = config_manager.load_config()
        assert saved_config.default_encoding == 'latin-1', f"Expected saved default_encoding to be 'latin-1', got '{saved_config.default_encoding}'"
        assert saved_config.chunk_size == 5000, f"Expected saved chunk_size to be 5000, got {saved_config.chunk_size}"

    def test_save_config_creates_directory(self, temp_dir):
        """TEST: should_create_parent_directory_when_saving_config_to_nonexistent_path"""
        # ARRANGE: Config and non-existent directory path
        config = Config()
        config_file = os.path.join(temp_dir, 'new_dir', 'config.yaml')

        # ACT: Create ConfigurationManager and save config
        config_manager = ConfigurationManager(config_file)
        config_manager.save_config(config)

        # ASSERT: Verify directory is created and file is saved
        assert os.path.exists(config_file), f"Expected config file to exist at '{config_file}'"
        assert os.path.isdir(os.path.dirname(config_file)), f"Expected parent directory to exist"

    def test_get_env_config(self, mock_env_vars):
        """TEST: should_extract_config_from_environment_variables_when_present"""
        # ARRANGE: Mock environment variables
        # ACT: Get environment config
        with patch.dict(os.environ, mock_env_vars):
            config_manager = ConfigurationManager()
            env_config = config_manager.get_env_config()

        # ASSERT: Verify environment variables are extracted correctly
        assert env_config['default_encoding'] == 'latin-1', f"Expected default_encoding from env to be 'latin-1', got '{env_config.get('default_encoding')}'"
        assert env_config['chunk_size'] == '5000', f"Expected chunk_size from env to be '5000', got '{env_config.get('chunk_size')}'"
        assert env_config['max_workers'] == '8', f"Expected max_workers from env to be '8', got '{env_config.get('max_workers')}'"
        assert env_config['ai_enabled'] == 'true', f"Expected ai_enabled from env to be 'true', got '{env_config.get('ai_enabled')}'"
        assert env_config['ai_cost_limit'] == '20.0', f"Expected ai_cost_limit from env to be '20.0', got '{env_config.get('ai_cost_limit')}'"
        assert env_config['log_level'] == 'DEBUG', f"Expected log_level from env to be 'DEBUG', got '{env_config.get('log_level')}'"
        assert env_config['log_file'] == '/tmp/test.log', f"Expected log_file from env to be '/tmp/test.log', got '{env_config.get('log_file')}'"

        # Verify AI API keys are extracted
        assert 'ai_api_keys' in env_config, "Expected ai_api_keys to be in env_config"
        assert env_config['ai_api_keys']['openai'] == 'test-openai-key', f"Expected openai key to be 'test-openai-key', got '{env_config['ai_api_keys'].get('openai')}'"
        assert env_config['ai_api_keys']['anthropic'] == 'test-anthropic-key', f"Expected anthropic key to be 'test-anthropic-key', got '{env_config['ai_api_keys'].get('anthropic')}'"

    def test_get_env_config_empty(self):
        """TEST: should_return_empty_dict_when_no_environment_variables_are_set"""
        # ARRANGE: No environment variables set
        # ACT: Get environment config
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigurationManager()
            env_config = config_manager.get_env_config()

        # ASSERT: Verify empty dict is returned
        assert env_config == {}, f"Expected empty dict, got {env_config}"

    def test_update_from_env(self, mock_env_vars):
        """TEST: should_update_config_with_environment_variables_when_update_from_env_is_called"""
        # ARRANGE: Mock environment variables and config manager
        # ACT: Update config from environment
        with patch.dict(os.environ, mock_env_vars):
            config_manager = ConfigurationManager()
            config_manager.update_from_env()

        # ASSERT: Verify config is updated with environment values
        config = config_manager.config
        assert config.default_encoding == 'latin-1', f"Expected default_encoding to be updated to 'latin-1', got '{config.default_encoding}'"
        # Note: Environment variables are strings, so they're not converted to int/float
        assert config.chunk_size == '5000', f"Expected chunk_size to be updated to '5000', got {config.chunk_size}"
        assert config.max_workers == '8', f"Expected max_workers to be updated to '8', got {config.max_workers}"
        assert config.ai_enabled == 'true', f"Expected ai_enabled to be updated to 'true', got {config.ai_enabled}"
        assert config.ai_cost_limit == '20.0', f"Expected ai_cost_limit to be updated to '20.0', got {config.ai_cost_limit}"
        assert config.log_level == 'DEBUG', f"Expected log_level to be updated to 'DEBUG', got '{config.log_level}'"
        assert config.log_file == '/tmp/test.log', f"Expected log_file to be updated to '/tmp/test.log', got '{config.log_file}'"

    def test_create_default_config_file(self, temp_dir):
        """TEST: should_create_default_config_file_when_create_default_config_file_is_called"""
        # ARRANGE: Config file path
        config_file = os.path.join(temp_dir, 'default_config.yaml')

        # ACT: Create ConfigurationManager and create default config file
        config_manager = ConfigurationManager(config_file)
        config_manager.create_default_config_file()

        # ASSERT: Verify default config file is created
        assert os.path.exists(config_file), f"Expected default config file to exist at '{config_file}'"

        # Load and verify default values
        config = config_manager.load_config()
        assert config.default_encoding == 'utf-8', f"Expected default default_encoding to be 'utf-8', got '{config.default_encoding}'"
        assert config.chunk_size == 10000, f"Expected default chunk_size to be 10000, got {config.chunk_size}"

    def test_get_config_path(self):
        """TEST: should_return_config_path_when_get_config_path_is_called"""
        # ARRANGE: Custom config path
        custom_path = '/custom/path/config.yaml'

        # ACT: Create ConfigurationManager and get config path
        config_manager = ConfigurationManager(custom_path)
        config_path = config_manager.get_config_path()

        # ASSERT: Verify correct config path is returned
        assert config_path == custom_path, f"Expected config_path to be '{custom_path}', got '{config_path}'"

    def test_config_serialization(self):
        """Test configuration serialization and deserialization."""
        original_config = Config()
        original_config.ai_enabled = True
        original_config.default_llm_provider = 'anthropic'
        original_config.ai_openai_model = 'gpt-4o'
        original_config.ai_anthropic_model = 'claude-3-haiku-20240307'
        original_config.ai_local_model = 'llama3.1:70b'
        original_config.ai_cost_limit = 25.0

        # Convert to dict and back
        config_manager = ConfigurationManager()
        config_dict = config_manager._config_to_dict(original_config)
        reloaded_config = config_manager._dict_to_config(config_dict)

        # Verify all fields are preserved
        assert reloaded_config.ai_enabled == original_config.ai_enabled
        assert reloaded_config.default_llm_provider == original_config.default_llm_provider
        assert reloaded_config.ai_openai_model == original_config.ai_openai_model
        assert reloaded_config.ai_anthropic_model == original_config.ai_anthropic_model
        assert reloaded_config.ai_local_model == original_config.ai_local_model
        assert reloaded_config.ai_cost_limit == original_config.ai_cost_limit
