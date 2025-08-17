"""
Pytest configuration and common fixtures for CSV Data Cleaner tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from csv_cleaner.core.config import Config, ConfigurationManager

# Import wrapper fixtures
from .fixtures.wrapper_fixtures import (
    basic_df, missing_data_df, large_df, complex_df, edge_case_dfs,
    text_data_df, date_data_df, mock_missingno, mock_pyjanitor,
    mock_feature_engine, mock_matplotlib, mock_seaborn, mock_plotly,
    temp_visualization_dir, sample_config
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        'default_encoding': 'utf-8',
        'max_memory_usage': 1024 * 1024 * 1024,
        'chunk_size': 10000,
        'parallel_processing': True,
        'max_workers': 4,
        'ai_enabled': False,
        'default_llm_provider': 'openai',
        'ai_api_keys': {},
        'ai_cost_limit': 10.0,
        'backup_enabled': True,
        'backup_suffix': '.backup',
        'output_format': 'csv',
        'log_level': 'INFO',
        'log_file': None,
        'default_operations': ['remove_duplicates', 'clean_names', 'handle_missing']
    }


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        'Name': ['John', 'Jane', 'Bob', 'Alice'],
        'Age': [25, 30, 35, 28],
        'City': ['NYC', 'LA', 'Chicago', 'Boston'],
        'Salary': [50000, 60000, 70000, 55000]
    })


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock configuration file path."""
    return os.path.join(temp_dir, 'test_config.yaml')


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'CSV_CLEANER_DEFAULT_ENCODING': 'latin-1',
        'CSV_CLEANER_CHUNK_SIZE': '5000',
        'CSV_CLEANER_MAX_WORKERS': '8',
        'CSV_CLEANER_AI_ENABLED': 'true',
        'CSV_CLEANER_DEFAULT_LLM_PROVIDER': 'anthropic',
        'CSV_CLEANER_AI_COST_LIMIT': '20.0',
        'CSV_CLEANER_LOG_LEVEL': 'DEBUG',
        'CSV_CLEANER_LOG_FILE': '/tmp/test.log',
        'CSV_CLEANER_OPENAI_API_KEY': 'test-openai-key',
        'CSV_CLEANER_ANTHROPIC_API_KEY': 'test-anthropic-key'
    }
    return env_vars


@pytest.fixture
def invalid_yaml_content():
    """Invalid YAML content for testing error handling."""
    return """
    default_encoding: utf-8
    max_memory_usage: invalid_value
    chunk_size:
        - invalid
        - list
    parallel_processing: not_a_boolean
    """


# AI-specific test fixtures
@pytest.fixture
def ai_config():
    """AI-enabled configuration for testing."""
    config = Config()
    config.ai_enabled = True
    config.default_llm_provider = 'openai'
    config.ai_api_keys = {
        'openai': 'test-openai-key',
        'anthropic': 'test-anthropic-key'
    }
    config.ai_cost_limit = 10.0
    config.ai_logging_enabled = True
    config.ai_log_file = '/tmp/test_ai.log'
    return config


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    from csv_cleaner.core.llm_providers import LLMResponse
    return LLMResponse(
        content='{"suggestions": [{"operation": "remove_duplicates", "library": "pandas", "parameters": {}, "confidence": 0.9, "reasoning": "Test", "estimated_impact": "Test", "priority": 1}]}',
        model="gpt-3.5-turbo",
        tokens_used=100,
        cost_usd=0.002,
        response_time_seconds=1.5,
        success=True
    )


@pytest.fixture
def mock_llm_response_failure():
    """Mock LLM response for testing failures."""
    from csv_cleaner.core.llm_providers import LLMResponse
    return LLMResponse(
        content="",
        model="gpt-3.5-turbo",
        tokens_used=0,
        cost_usd=0.0,
        response_time_seconds=0.5,
        success=False,
        error_message="API rate limit exceeded"
    )


@pytest.fixture
def sample_cleaning_suggestion():
    """Sample cleaning suggestion for testing."""
    from csv_cleaner.core.ai_agent import CleaningSuggestion
    return CleaningSuggestion(
        operation="remove_duplicates",
        library="pandas",
        parameters={"keep": "first"},
        confidence=0.9,
        reasoning="Remove duplicate rows to improve data quality",
        estimated_impact="Will remove 5% of duplicate rows",
        priority=1
    )


@pytest.fixture
def sample_data_profile():
    """Sample data profile for testing."""
    from csv_cleaner.core.ai_agent import DataProfile
    return DataProfile(
        row_count=1000,
        column_count=10,
        missing_percentage=5.5,
        duplicate_percentage=2.1,
        data_types={'col1': 'object', 'col2': 'int64'},
        memory_usage_mb=15.5,
        has_text_columns=True,
        has_numeric_columns=True,
        has_date_columns=False,
        has_categorical_columns=True,
        quality_score=0.85
    )


@pytest.fixture
def complex_test_df():
    """Complex test DataFrame with various data types and issues."""
    return pd.DataFrame({
        'Name': ['John', 'Jane', 'Bob', 'Alice', 'John', None],
        'Age': [25, 30, 35, 28, 25, 40],
        'City': ['NYC', 'LA', 'Chicago', 'Boston', 'NYC', 'Miami'],
        'Salary': [50000, 60000, 70000, 55000, 50000, 80000],
        'Email': ['john@email.com', 'jane@email.com', 'bob@email.com', 'alice@email.com', 'john@email.com', 'mike@email.com'],
        'JoinDate': pd.to_datetime(['2020-01-01', '2021-03-15', '2019-11-20', '2022-06-10', '2020-01-01', '2023-01-01']),
        'Category': pd.Categorical(['A', 'B', 'A', 'C', 'A', 'B']),
        'Score': [85.5, 92.3, 78.9, 88.1, 85.5, 95.0]
    })


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_response.usage.total_tokens = 100
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Test response"
    mock_response.usage.input_tokens = 50
    mock_response.usage.output_tokens = 100
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_local_model():
    """Mock local LLM model for testing."""
    mock_model = MagicMock()
    mock_response = {'choices': [{'text': 'Test response'}]}
    mock_model.return_value = mock_response
    return mock_model
