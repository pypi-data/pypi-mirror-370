"""
TEST SUITE: ai_utils.py
PURPOSE: Test AI utilities for prompt engineering and response parsing
SCOPE: PromptEngineer and ResponseParser classes with all methods
DEPENDENCIES: None (pure utility functions, no external dependencies)
"""

import pytest
import json
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from csv_cleaner.core.ai_utils import PromptEngineer, ResponseParser


class TestPromptEngineer:
    """Test PromptEngineer class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.prompt_engineer = PromptEngineer()

    def test_initialization(self):
        """Test PromptEngineer initialization and base prompt loading."""
        # Test that base prompts are loaded
        assert hasattr(self.prompt_engineer, 'base_prompts')
        assert isinstance(self.prompt_engineer.base_prompts, dict)

        # Test that all expected prompt types are available
        expected_prompts = [
            'data_analysis', 'library_selection', 'parameter_optimization', 'explanation'
        ]
        for prompt_type in expected_prompts:
            assert prompt_type in self.prompt_engineer.base_prompts
            assert isinstance(self.prompt_engineer.base_prompts[prompt_type], str)
            assert len(self.prompt_engineer.base_prompts[prompt_type]) > 0

    def test_create_data_analysis_prompt_valid_input(self):
        """Test data analysis prompt creation with valid input."""
        profile = {
            'row_count': 1000,
            'column_count': 10,
            'missing_percentage': 5.5,
            'duplicate_percentage': 2.1,
            'data_types': {'col1': 'object', 'col2': 'int64'},
            'memory_usage_mb': 15.5,
            'has_text_columns': True,
            'has_numeric_columns': True,
            'has_date_columns': False,
            'has_categorical_columns': True,
            'quality_score': 0.85
        }
        available_operations = ['remove_duplicates', 'clean_names', 'handle_missing']

        prompt = self.prompt_engineer.create_data_analysis_prompt(profile, available_operations)

        # Test that prompt contains all expected elements
        assert '1000' in prompt  # row_count
        assert '10' in prompt    # column_count
        assert '5.5' in prompt   # missing_percentage
        assert '2.1' in prompt   # duplicate_percentage
        assert 'object' in prompt  # data_types
        assert 'int64' in prompt   # data_types
        assert '15.5' in prompt  # memory_usage_mb
        assert 'True' in prompt  # has_text_columns
        assert 'False' in prompt # has_date_columns
        assert '0.85' in prompt  # quality_score
        assert 'remove_duplicates' in prompt  # available_operations
        assert 'clean_names' in prompt        # available_operations
        assert 'handle_missing' in prompt     # available_operations

    def test_create_data_analysis_prompt_missing_fields(self):
        """Test data analysis prompt creation with missing profile fields."""
        profile = {
            'row_count': 500,
            'column_count': 5
            # Missing other fields
        }
        available_operations = ['remove_duplicates']

        prompt = self.prompt_engineer.create_data_analysis_prompt(profile, available_operations)

        # Test that default values are used for missing fields
        assert '500' in prompt  # row_count
        assert '5' in prompt    # column_count
        assert '0.0' in prompt  # missing_percentage (default)
        assert '0.0' in prompt  # duplicate_percentage (default)
        assert '{}' in prompt   # data_types (default)
        assert '0.0' in prompt  # memory_usage_mb (default)
        assert 'False' in prompt # has_text_columns (default)
        assert 'False' in prompt # has_numeric_columns (default)
        assert 'False' in prompt # has_date_columns (default)
        assert 'False' in prompt # has_categorical_columns (default)
        assert '0.0' in prompt  # quality_score (default)

    def test_create_data_analysis_prompt_empty_operations(self):
        """Test data analysis prompt creation with empty operations list."""
        profile = {
            'row_count': 100,
            'column_count': 3,
            'missing_percentage': 0.0,
            'duplicate_percentage': 0.0,
            'data_types': {},
            'memory_usage_mb': 1.0,
            'has_text_columns': False,
            'has_numeric_columns': True,
            'has_date_columns': False,
            'has_categorical_columns': False,
            'quality_score': 1.0
        }
        available_operations = []

        prompt = self.prompt_engineer.create_data_analysis_prompt(profile, available_operations)

        # Test that prompt is still generated correctly
        assert '100' in prompt  # row_count
        assert '3' in prompt    # column_count
        assert '[]' in prompt   # empty operations list

    def test_create_library_selection_prompt_valid_input(self):
        """Test library selection prompt creation with valid input."""
        operation = 'remove_duplicates'
        profile = {
            'row_count': 5000,
            'column_count': 15,
            'data_types': {'id': 'int64', 'name': 'object', 'date': 'datetime64[ns]'},
            'missing_percentage': 3.2
        }
        available_libraries = ['pandas', 'pyjanitor', 'dedupe']

        prompt = self.prompt_engineer.create_library_selection_prompt(operation, profile, available_libraries)

        # Test that prompt contains all expected elements
        assert 'remove_duplicates' in prompt  # operation
        assert '5000' in prompt  # row_count
        assert '15' in prompt    # column_count
        assert 'int64' in prompt # data_types
        assert 'object' in prompt # data_types
        assert 'datetime64' in prompt # data_types
        assert '3.2' in prompt   # missing_percentage
        assert 'pandas' in prompt # available_libraries
        assert 'pyjanitor' in prompt # available_libraries
        assert 'dedupe' in prompt # available_libraries

    def test_create_library_selection_prompt_missing_profile_fields(self):
        """Test library selection prompt creation with missing profile fields."""
        operation = 'clean_names'
        profile = {
            'row_count': 100
            # Missing other fields
        }
        available_libraries = ['pandas']

        prompt = self.prompt_engineer.create_library_selection_prompt(operation, profile, available_libraries)

        # Test that default values are used for missing fields
        assert 'clean_names' in prompt  # operation
        assert '100' in prompt  # row_count
        assert '0' in prompt    # column_count (default)
        assert '{}' in prompt   # data_types (default)
        assert '0.0' in prompt  # missing_percentage (default)
        assert 'pandas' in prompt # available_libraries

    def test_create_parameter_optimization_prompt_valid_input(self):
        """Test parameter optimization prompt creation with valid input."""
        operation = 'handle_missing'
        library = 'pandas'
        profile = {
            'row_count': 2000,
            'column_count': 8,
            'missing_percentage': 12.5,
            'data_types': {'col1': 'object', 'col2': 'float64'}
        }
        current_parameters = {
            'method': 'drop',
            'threshold': 0.5
        }

        prompt = self.prompt_engineer.create_parameter_optimization_prompt(
            operation, library, profile, current_parameters
        )

        # Test that prompt contains all expected elements
        assert 'handle_missing' in prompt  # operation
        assert 'pandas' in prompt  # library
        assert '2000' in prompt  # row_count
        assert '8' in prompt    # column_count
        assert '12.5' in prompt # missing_percentage
        assert 'object' in prompt # data_types
        assert 'float64' in prompt # data_types
        assert 'drop' in prompt  # current_parameters
        assert '0.5' in prompt   # current_parameters

    def test_create_parameter_optimization_prompt_empty_parameters(self):
        """Test parameter optimization prompt creation with empty current parameters."""
        operation = 'remove_duplicates'
        library = 'pyjanitor'
        profile = {
            'row_count': 1000,
            'column_count': 5,
            'missing_percentage': 0.0,
            'data_types': {}
        }
        current_parameters = {}

        prompt = self.prompt_engineer.create_parameter_optimization_prompt(
            operation, library, profile, current_parameters
        )

        # Test that prompt is still generated correctly
        assert 'remove_duplicates' in prompt  # operation
        assert 'pyjanitor' in prompt  # library
        assert '1000' in prompt  # row_count
        assert '{}' in prompt   # empty current_parameters

    def test_create_explanation_prompt_valid_input(self):
        """Test explanation prompt creation with valid input."""
        operation = 'clean_names'
        library = 'pyjanitor'
        parameters = {
            'case': 'snake',
            'remove_special': True
        }
        profile = {
            'row_count': 500,
            'column_count': 10,
            'missing_percentage': 2.0
        }

        prompt = self.prompt_engineer.create_explanation_prompt(operation, library, parameters, profile)

        # Test that prompt contains all expected elements
        assert 'clean_names' in prompt  # operation
        assert 'pyjanitor' in prompt  # library
        assert 'snake' in prompt  # parameters
        assert 'True' in prompt   # parameters
        assert '500' in prompt  # row_count
        assert '10' in prompt   # column_count
        assert '2.0' in prompt  # missing_percentage

    def test_create_explanation_prompt_complex_parameters(self):
        """Test explanation prompt creation with complex parameter structures."""
        operation = 'handle_missing'
        library = 'pandas'
        parameters = {
            'method': 'interpolate',
            'options': {
                'method': 'linear',
                'limit': 5
            },
            'columns': ['col1', 'col2']
        }
        profile = {
            'row_count': 1000,
            'column_count': 5,
            'missing_percentage': 8.5
        }

        prompt = self.prompt_engineer.create_explanation_prompt(operation, library, parameters, profile)

        # Test that prompt contains all expected elements
        assert 'handle_missing' in prompt  # operation
        assert 'pandas' in prompt  # library
        assert 'interpolate' in prompt  # parameters
        assert 'linear' in prompt  # parameters
        assert '5' in prompt  # parameters
        assert 'col1' in prompt  # parameters
        assert 'col2' in prompt  # parameters
        assert '1000' in prompt  # row_count
        assert '8.5' in prompt  # missing_percentage


class TestResponseParser:
    """Test ResponseParser class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.response_parser = ResponseParser()

    def test_parse_suggestions_response_valid_simple(self):
        """Test parsing valid simple suggestions response."""
        json_response = '{"suggestions": [{"operation": "remove_duplicates", "library": "pandas", "parameters": {}, "confidence": 0.9, "reasoning": "Test", "estimated_impact": "Test", "priority": 1}]}'

        result = self.response_parser.parse_suggestions_response(json_response)

        assert len(result) == 1
        assert result[0]['operation'] == "remove_duplicates"
        assert result[0]['library'] == "pandas"
        assert result[0]['confidence'] == 0.9

    def test_parse_suggestions_response_valid_complex(self):
        """Test parsing valid complex suggestions response."""
        json_response = '''
        {
            "suggestions": [
                {
                    "operation": "remove_duplicates",
                    "library": "pandas",
                    "confidence": 0.9,
                    "parameters": {"keep": "first"},
                    "reasoning": "Remove duplicates",
                    "estimated_impact": "Clean data"
                },
                {
                    "operation": "clean_names",
                    "library": "pyjanitor",
                    "confidence": 0.8,
                    "parameters": {"case": "snake"},
                    "reasoning": "Standardize names",
                    "estimated_impact": "Improve consistency"
                }
            ]
        }
        '''

        result = self.response_parser.parse_suggestions_response(json_response)

        assert len(result) == 2
        assert result[0]['operation'] == 'remove_duplicates'
        assert result[1]['operation'] == 'clean_names'
        assert result[0]['library'] == 'pandas'
        assert result[1]['library'] == 'pyjanitor'

    def test_parse_suggestions_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        invalid_json = '{"suggestions": [{"operation": "test", "unclosed": }]}'

        result = self.response_parser.parse_suggestions_response(invalid_json)

        assert result == []

    def test_parse_suggestions_response_empty_string(self):
        """Test parsing empty string response."""
        empty_response = ''

        result = self.response_parser.parse_suggestions_response(empty_response)

        assert result == []

    def test_parse_suggestions_response_no_suggestions_key(self):
        """Test parsing response without suggestions key."""
        json_response = '{"other_data": "value"}'

        result = self.response_parser.parse_suggestions_response(json_response)

        assert result == []

    def test_parse_suggestions_response_invalid_suggestion_format(self):
        """Test parsing response with invalid suggestion format."""
        json_response = '{"suggestions": [{"operation": "test"}]}'  # Missing required fields

        result = self.response_parser.parse_suggestions_response(json_response)

        assert result == []

    def test_parse_suggestions_response_with_code_blocks(self):
        """Test parsing response with JSON in code blocks."""
        json_response = '''
        Here is my analysis:
        ```json
        {
            "suggestions": [
                {
                    "operation": "remove_duplicates",
                    "library": "pandas",
                    "parameters": {},
                    "confidence": 0.9,
                    "reasoning": "Test",
                    "estimated_impact": "Test"
                }
            ]
        }
        ```
        '''

        result = self.response_parser.parse_suggestions_response(json_response)

        assert len(result) == 1
        assert result[0]['operation'] == "remove_duplicates"

    def test_parse_library_selection_response_valid(self):
        """Test parsing valid library selection response."""
        json_response = '{"recommended_library": "pandas", "confidence": 0.9, "reasoning": "Best for this task", "alternative_libraries": ["pyjanitor", "dedupe"]}'

        result = self.response_parser.parse_library_selection_response(json_response)

        assert result['recommended_library'] == "pandas"
        assert result['confidence'] == 0.9
        assert result['reasoning'] == "Best for this task"
        assert result['alternative_libraries'] == ["pyjanitor", "dedupe"]

    def test_parse_library_selection_response_invalid_json(self):
        """Test parsing invalid library selection response."""
        invalid_json = '{"recommended_library": "pandas", "unclosed": }'

        result = self.response_parser.parse_library_selection_response(invalid_json)

        assert result['recommended_library'] is None
        assert result['confidence'] == 0.0

    def test_parse_library_selection_response_empty_string(self):
        """Test parsing empty library selection response."""
        empty_response = ''

        result = self.response_parser.parse_library_selection_response(empty_response)

        assert result['recommended_library'] is None
        assert result['confidence'] == 0.0

    def test_parse_parameter_optimization_response_valid(self):
        """Test parsing valid parameter optimization response."""
        json_response = '{"optimized_parameters": {"method": "drop", "threshold": 0.5}, "confidence": 0.8, "reasoning": "Optimal for this dataset", "expected_improvement": "Better performance"}'

        result = self.response_parser.parse_parameter_optimization_response(json_response)

        assert result['optimized_parameters'] == {"method": "drop", "threshold": 0.5}
        assert result['confidence'] == 0.8
        assert result['reasoning'] == "Optimal for this dataset"
        assert result['expected_improvement'] == "Better performance"

    def test_parse_parameter_optimization_response_invalid_json(self):
        """Test parsing invalid parameter optimization response."""
        invalid_json = '{"optimized_parameters": {}, "unclosed": }'

        result = self.response_parser.parse_parameter_optimization_response(invalid_json)

        assert result['optimized_parameters'] == {}
        assert result['confidence'] == 0.0

    def test_extract_json_from_code_blocks(self):
        """Test extracting JSON from code blocks."""
        text_with_code_blocks = '''
        Here is the analysis:
        ```json
        {"key": "value"}
        ```
        '''

        json_str = self.response_parser._extract_json(text_with_code_blocks)

        assert json_str == '{"key": "value"}'

    def test_extract_json_from_plain_text(self):
        """Test extracting JSON from plain text."""
        text_with_json = 'Here is the data: {"key": "value"} and more text'

        json_str = self.response_parser._extract_json(text_with_json)

        # The regex should find the JSON object
        assert json_str is not None
        assert "key" in json_str
        assert "value" in json_str

    def test_extract_json_not_found(self):
        """Test extracting JSON when not found."""
        text_without_json = 'This text contains no JSON data'

        json_str = self.response_parser._extract_json(text_without_json)

        assert json_str is None

    def test_validate_suggestion_valid(self):
        """Test validating valid suggestion."""
        suggestion = {
            'operation': 'remove_duplicates',
            'library': 'pandas',
            'parameters': {},
            'confidence': 0.9,
            'reasoning': 'Test'
        }

        result = self.response_parser._validate_suggestion(suggestion)

        assert result is True

    def test_validate_suggestion_missing_fields(self):
        """Test validating suggestion with missing fields."""
        suggestion = {
            'operation': 'remove_duplicates',
            'library': 'pandas'
            # Missing required fields
        }

        result = self.response_parser._validate_suggestion(suggestion)

        assert result is False
