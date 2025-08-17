"""
Unit tests for AdvancedValidator.
"""

import pytest
import pandas as pd
import numpy as np
import json
import tempfile
import os
from unittest.mock import Mock, patch
from csv_cleaner.core.validator import (
    AdvancedValidator, ValidationRule, ValidationResult, QualityScore
)


class TestValidationRule:
    """Test ValidationRule dataclass."""

    def test_validation_rule_creation(self):
        """Test creating ValidationRule instance."""
        rule = ValidationRule(
            rule_id="test_rule",
            rule_type="not_null",
            column="test_column",
            parameters={"min": 0, "max": 100},
            description="Test validation rule"
        )

        assert rule.rule_id == "test_rule"
        assert rule.rule_type == "not_null"
        assert rule.column == "test_column"
        assert rule.parameters == {"min": 0, "max": 100}
        assert rule.description == "Test validation rule"


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult instance."""
        result = ValidationResult(
            rule_id="test_rule",
            passed=True,
            errors=["Error 1", "Error 2"],
            affected_rows=[1, 2, 3],
            error_count=2,
            total_rows=100,
            error_rate=0.02
        )

        assert result.rule_id == "test_rule"
        assert result.passed is True
        assert result.errors == ["Error 1", "Error 2"]
        assert result.affected_rows == [1, 2, 3]
        assert result.error_count == 2
        assert result.total_rows == 100
        assert result.error_rate == 0.02


class TestQualityScore:
    """Test QualityScore dataclass."""

    def test_quality_score_creation(self):
        """Test creating QualityScore instance."""
        score = QualityScore(
            completeness=0.95,
            accuracy=0.88,
            consistency=0.92,
            validity=0.90,
            overall=0.91,
            details={"test": "data"}
        )

        assert score.completeness == 0.95
        assert score.accuracy == 0.88
        assert score.consistency == 0.92
        assert score.validity == 0.90
        assert score.overall == 0.91
        assert score.details == {"test": "data"}


class TestAdvancedValidator:
    """Test AdvancedValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AdvancedValidator()

    def test_initialization(self):
        """Test AdvancedValidator initialization."""
        assert len(self.validator.validation_rules) == 0
        assert len(self.validator.validation_results) == 0
        assert 'email' in self.validator.patterns
        assert 'phone' in self.validator.patterns
        assert 'date' in self.validator.patterns

    def test_add_validation_rule(self):
        """Test adding validation rule."""
        rule = ValidationRule(
            rule_id="test_rule",
            rule_type="not_null",
            column="test_column"
        )

        self.validator.add_validation_rule(rule)

        assert len(self.validator.validation_rules) == 1
        assert self.validator.validation_rules[0].rule_id == "test_rule"

    def test_load_schema_from_dict(self):
        """Test loading schema from dictionary."""
        schema = {
            "rules": [
                {
                    "id": "rule1",
                    "type": "not_null",
                    "column": "column1",
                    "parameters": {},
                    "description": "Test rule 1"
                },
                {
                    "id": "rule2",
                    "type": "unique",
                    "column": "column2",
                    "parameters": {},
                    "description": "Test rule 2"
                }
            ]
        }

        self.validator.load_schema_from_dict(schema)

        assert len(self.validator.validation_rules) == 2
        assert self.validator.validation_rules[0].rule_id == "rule1"
        assert self.validator.validation_rules[1].rule_id == "rule2"

    def test_load_schema_from_file(self):
        """Test loading schema from file."""
        schema = {
            "rules": [
                {
                    "id": "file_rule",
                    "type": "not_null",
                    "column": "test_column",
                    "parameters": {},
                    "description": "Rule from file"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema, f)
            schema_file = f.name

        try:
            self.validator.load_schema_from_file(schema_file)

            assert len(self.validator.validation_rules) == 1
            assert self.validator.validation_rules[0].rule_id == "file_rule"
        finally:
            os.unlink(schema_file)

    def test_validate_not_null_success(self):
        """Test not_null validation with valid data."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="not_null_test",
            rule_type="not_null",
            column="A"
        )

        errors, affected_rows = self.validator._validate_not_null(df, rule)

        assert len(errors) == 0
        assert len(affected_rows) == 0

    def test_validate_not_null_with_nulls(self):
        """Test not_null validation with null values."""
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="not_null_test",
            rule_type="not_null",
            column="A"
        )

        errors, affected_rows = self.validator._validate_not_null(df, rule)

        assert len(errors) == 1
        assert "Found 1 null values" in errors[0]
        assert len(affected_rows) == 1
        assert affected_rows[0] == 2  # Index of null value

    def test_validate_unique_success(self):
        """Test unique validation with unique values."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="unique_test",
            rule_type="unique",
            column="A"
        )

        errors, affected_rows = self.validator._validate_unique(df, rule)

        assert len(errors) == 0
        assert len(affected_rows) == 0

    def test_validate_unique_with_duplicates(self):
        """Test unique validation with duplicate values."""
        df = pd.DataFrame({
            'A': [1, 2, 2, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="unique_test",
            rule_type="unique",
            column="A"
        )

        errors, affected_rows = self.validator._validate_unique(df, rule)

        assert len(errors) == 1
        assert "Found 2 duplicate values" in errors[0]
        assert len(affected_rows) == 2
        assert 1 in affected_rows  # Index of first duplicate
        assert 2 in affected_rows  # Index of second duplicate

    def test_validate_range_success(self):
        """Test range validation with values within range."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="range_test",
            rule_type="range",
            column="A",
            parameters={"min": 0, "max": 10}
        )

        errors, affected_rows = self.validator._validate_range(df, rule)

        assert len(errors) == 0
        assert len(affected_rows) == 0

    def test_validate_range_out_of_bounds(self):
        """Test range validation with values out of bounds."""
        df = pd.DataFrame({
            'A': [1, 2, 15, 4, -5],
            'B': ['a', 'b', 'c', 'd', 'e']
        })

        rule = ValidationRule(
            rule_id="range_test",
            rule_type="range",
            column="A",
            parameters={"min": 0, "max": 10}
        )

        errors, affected_rows = self.validator._validate_range(df, rule)

        assert len(errors) == 2
        assert any("above maximum 10" in error for error in errors)
        assert any("below minimum 0" in error for error in errors)
        assert len(affected_rows) == 2
        assert 2 in affected_rows  # Index of value 15
        assert 4 in affected_rows  # Index of value -5

    def test_validate_pattern_success(self):
        """Test pattern validation with matching values."""
        df = pd.DataFrame({
            'A': ['test@example.com', 'user@domain.org', 'admin@site.net'],
            'B': ['a', 'b', 'c']
        })

        rule = ValidationRule(
            rule_id="pattern_test",
            rule_type="pattern",
            column="A",
            parameters={"pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}
        )

        errors, affected_rows = self.validator._validate_pattern(df, rule)

        assert len(errors) == 0
        assert len(affected_rows) == 0

    def test_validate_pattern_no_match(self):
        """Test pattern validation with non-matching values."""
        df = pd.DataFrame({
            'A': ['invalid-email', 'test@', '@domain.com', 'valid@example.com'],
            'B': ['a', 'b', 'c', 'd']
        })

        rule = ValidationRule(
            rule_id="pattern_test",
            rule_type="pattern",
            column="A",
            parameters={"pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}
        )

        errors, affected_rows = self.validator._validate_pattern(df, rule)

        assert len(errors) == 1
        assert "Found 3 values that don't match pattern" in errors[0]
        assert len(affected_rows) == 3

    def test_validate_dataframe(self):
        """Test complete DataFrame validation."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })

        # Add validation rules
        self.validator.add_validation_rule(ValidationRule(
            rule_id="not_null_A",
            rule_type="not_null",
            column="A"
        ))
        self.validator.add_validation_rule(ValidationRule(
            rule_id="unique_B",
            rule_type="unique",
            column="B"
        ))

        results = self.validator.validate_dataframe(df)

        assert len(results) == 2
        assert all(result.passed for result in results)

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': ['a', 'b', 'c', 'd', 'e'],
            'C': [1.1, 2.2, 3.3, 4.4, 5.5]
        })

        # Add some validation rules
        self.validator.add_validation_rule(ValidationRule(
            rule_id="not_null_A",
            rule_type="not_null",
            column="A"
        ))

        # Validate first to populate results
        self.validator.validate_dataframe(df)

        quality_score = self.validator.calculate_quality_score(df)

        assert isinstance(quality_score, QualityScore)
        assert 0.0 <= quality_score.completeness <= 1.0
        assert 0.0 <= quality_score.accuracy <= 1.0
        assert 0.0 <= quality_score.consistency <= 1.0
        assert 0.0 <= quality_score.validity <= 1.0
        assert 0.0 <= quality_score.overall <= 1.0

    def test_calculate_completeness_score(self):
        """Test completeness score calculation."""
        # Complete data
        df_complete = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['a', 'b', 'c']
        })
        completeness = self.validator._calculate_completeness_score(df_complete)
        assert completeness == 1.0

        # Data with nulls
        df_with_nulls = pd.DataFrame({
            'A': [1, 2, np.nan],
            'B': ['a', np.nan, 'c']
        })
        completeness = self.validator._calculate_completeness_score(df_with_nulls)
        assert 0.0 < completeness < 1.0

        # Empty DataFrame
        df_empty = pd.DataFrame()
        completeness = self.validator._calculate_completeness_score(df_empty)
        assert completeness == 0.0

    def test_calculate_accuracy_score(self):
        """Test accuracy score calculation."""
        # No validation results
        accuracy = self.validator._calculate_accuracy_score()
        assert accuracy == 1.0

        # Add some validation results
        self.validator.validation_results = [
            ValidationResult(
                rule_id="rule1",
                passed=True,
                errors=[],
                affected_rows=[],
                error_count=0,
                total_rows=100,
                error_rate=0.0
            ),
            ValidationResult(
                rule_id="rule2",
                passed=False,
                errors=["Error"],
                affected_rows=[1, 2],
                error_count=2,
                total_rows=100,
                error_rate=0.02
            )
        ]

        accuracy = self.validator._calculate_accuracy_score()
        assert 0.0 < accuracy < 1.0

    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Add some validation results
        self.validator.validation_results = [
            ValidationResult(
                rule_id="rule1",
                passed=True,
                errors=[],
                affected_rows=[],
                error_count=0,
                total_rows=100,
                error_rate=0.0
            ),
            ValidationResult(
                rule_id="rule2",
                passed=False,
                errors=["Error"],
                affected_rows=[1, 2],
                error_count=2,
                total_rows=100,
                error_rate=0.02
            )
        ]

        report = self.validator.generate_validation_report()

        assert "DATA VALIDATION REPORT" in report
        assert "Total Rules: 2" in report
        assert "Passed Rules: 1" in report
        assert "Failed Rules: 1" in report

    def test_generate_validation_report_to_file(self):
        """Test validation report generation to file."""
        # Add some validation results
        self.validator.validation_results = [
            ValidationResult(
                rule_id="rule1",
                passed=True,
                errors=[],
                affected_rows=[],
                error_count=0,
                total_rows=100,
                error_rate=0.0
            )
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            report_file = f.name

        try:
            report = self.validator.generate_validation_report(report_file)

            assert "DATA VALIDATION REPORT" in report
            assert os.path.exists(report_file)

            # Check file content
            with open(report_file, 'r') as f:
                file_content = f.read()
                assert "DATA VALIDATION REPORT" in file_content
        finally:
            os.unlink(report_file)


class TestAdvancedValidatorIntegration:
    """Integration tests for AdvancedValidator."""

    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        validator = AdvancedValidator()

        # Create test data with various issues
        df = pd.DataFrame({
            'id': [1, 2, 2, 4, 5],  # Duplicate values
            'name': ['Alice', 'Bob', 'Charlie', 'David', None],  # Null value
            'age': [25, 30, 35, 40, 45],
            'email': ['alice@example.com', 'invalid-email', 'charlie@test.org', 'david@', 'eve@valid.com'],
            'score': [85, 92, 78, 105, 88]  # Value above 100
        })

        # Define validation schema
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
                },
                {
                    "id": "score_range",
                    "type": "range",
                    "column": "score",
                    "parameters": {"min": 0, "max": 100},
                    "description": "Score must be between 0 and 100"
                }
            ]
        }

        # Load schema and validate
        validator.load_schema_from_dict(schema)
        results = validator.validate_dataframe(df)
        quality_score = validator.calculate_quality_score(df)

        # Verify results - now includes both custom rules and default quality checks
        assert len(results) >= 4  # At least 4 custom rules, plus default quality checks

        # Find the custom rules by their IDs
        unique_id_rule = next((r for r in results if r.rule_id == 'unique_id'), None)
        not_null_name_rule = next((r for r in results if r.rule_id == 'not_null_name'), None)
        valid_email_rule = next((r for r in results if r.rule_id == 'valid_email'), None)
        score_range_rule = next((r for r in results if r.rule_id == 'score_range'), None)

        # Verify custom rules failed as expected
        assert unique_id_rule is not None and not unique_id_rule.passed
        assert not_null_name_rule is not None and not not_null_name_rule.passed
        assert valid_email_rule is not None and not valid_email_rule.passed
        assert score_range_rule is not None and not score_range_rule.passed

        # Verify quality score
        assert quality_score.validity < 1.0  # Some rules failed
        assert quality_score.completeness < 1.0  # Has null values

    def test_validation_with_mixed_data_types(self):
        """Test validation with mixed data types."""
        validator = AdvancedValidator()

        df = pd.DataFrame({
            'numeric': [1, 2, 3, 4, 5],
            'string': ['a', 'b', 'c', 'd', 'e'],
            'float': [1.1, 2.2, 3.3, 4.4, 5.5],
            'mixed': [1, 'text', 3.14, True, None]
        })

        # Add validation rules
        validator.add_validation_rule(ValidationRule(
            rule_id="numeric_range",
            rule_type="range",
            column="numeric",
            parameters={"min": 0, "max": 10}
        ))

        validator.add_validation_rule(ValidationRule(
            rule_id="string_unique",
            rule_type="unique",
            column="string"
        ))

        results = validator.validate_dataframe(df)
        quality_score = validator.calculate_quality_score(df)

        # Only the custom rules should pass (default quality checks may fail for mixed data)
        custom_rules = [r for r in results if r.rule_id in ['numeric_range', 'string_unique']]
        assert all(result.passed for result in custom_rules)
        assert len(custom_rules) == 2


class TestAdvancedValidatorImprovements:
    """Test the enhanced validation functionality with default quality checks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AdvancedValidator()

    def test_default_quality_checks_missing_values(self):
        """Test that default quality checks detect missing values."""
        # Create test data with missing values (null and empty strings)
        df = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Age': [25, 30, None, 35],
            'Email': ['john@example.com', 'jane@example.com', '', 'alice@example.com'],
            'City': ['NYC', 'LA', 'Chicago', None]
        })

        # Run validation without any custom rules
        results = self.validator.validate_dataframe(df)

        # Should detect missing values in Age and City columns
        missing_age_rule = next((r for r in results if r.rule_id == 'missing_values_Age'), None)
        missing_city_rule = next((r for r in results if r.rule_id == 'missing_values_City'), None)

        assert missing_age_rule is not None
        assert not missing_age_rule.passed
        assert missing_age_rule.error_count == 1
        assert missing_age_rule.affected_rows == [2]  # Bob's row

        assert missing_city_rule is not None
        assert not missing_city_rule.passed
        assert missing_city_rule.error_count == 1
        assert missing_city_rule.affected_rows == [3]  # Alice's row

    def test_default_quality_checks_duplicate_rows(self):
        """Test that default quality checks detect duplicate rows."""
        # Create test data with duplicate rows
        df = pd.DataFrame({
            'Name': ['John', 'Jane', 'John', 'Bob'],
            'Age': [25, 30, 25, 35],
            'Email': ['john@example.com', 'jane@example.com', 'john@example.com', 'bob@example.com']
        })

        # Run validation
        results = self.validator.validate_dataframe(df)

        # Should detect duplicate rows
        duplicate_rule = next((r for r in results if r.rule_id == 'duplicate_rows'), None)

        assert duplicate_rule is not None
        assert not duplicate_rule.passed
        assert duplicate_rule.error_count == 2  # Two duplicate rows
        assert set(duplicate_rule.affected_rows) == {0, 2}  # John's rows

    def test_default_quality_checks_data_type_consistency(self):
        """Test that default quality checks detect data type inconsistencies."""
        # Create test data with mixed data types in numeric columns
        df = pd.DataFrame({
            'Age': [25, 30, 'invalid', 35, 40],
            'Salary': [50000, 60000, 70000, 'not_a_number', 80000],
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie']
        })

        # Run validation
        results = self.validator.validate_dataframe(df)

        # Should detect data type issues in Age and Salary columns
        age_type_rule = next((r for r in results if r.rule_id == 'data_type_Age'), None)
        salary_type_rule = next((r for r in results if r.rule_id == 'data_type_Salary'), None)

        assert age_type_rule is not None
        assert not age_type_rule.passed
        assert age_type_rule.error_count == 1
        assert age_type_rule.affected_rows == [2]  # 'invalid' value

        assert salary_type_rule is not None
        assert not salary_type_rule.passed
        assert salary_type_rule.error_count == 1
        assert salary_type_rule.affected_rows == [3]  # 'not_a_number' value

    def test_default_quality_checks_email_format(self):
        """Test that default quality checks validate email format."""
        # Create test data with invalid email addresses
        df = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Email': ['john@example.com', 'invalid-email', 'bob@', 'alice@test.org'],
            'Age': [25, 30, 35, 40]
        })

        # Run validation
        results = self.validator.validate_dataframe(df)

        # Should detect invalid email formats
        email_format_rule = next((r for r in results if r.rule_id == 'email_format_Email'), None)

        assert email_format_rule is not None
        assert not email_format_rule.passed
        assert email_format_rule.error_count == 2  # 'invalid-email' and 'bob@'
        assert set(email_format_rule.affected_rows) == {1, 2}

    def test_enhanced_completeness_score_with_empty_strings(self):
        """Test that completeness score properly handles empty strings."""
        # Create test data with empty strings
        df = pd.DataFrame({
            'Name': ['John', 'Jane', '', 'Alice'],
            'Age': [25, 30, 35, 40],
            'Email': ['john@example.com', '', 'bob@example.com', 'alice@example.com']
        })

        completeness_score = self.validator._calculate_completeness_score(df)

        # Should be less than 1.0 due to empty strings
        assert completeness_score < 1.0
        # With 2 empty strings out of 12 total cells, score should be 10/12 = 0.833
        expected_score = 10 / 12
        assert abs(completeness_score - expected_score) < 0.01

    def test_duplicate_penalty_calculation(self):
        """Test duplicate penalty calculation."""
        # Create test data with duplicates
        df = pd.DataFrame({
            'Name': ['John', 'Jane', 'John', 'Bob', 'Jane'],
            'Age': [25, 30, 25, 35, 30]
        })

        penalty = self.validator._calculate_duplicate_penalty(df)

        # 3 duplicate rows out of 5 total = 0.6, but capped at 0.3
        assert penalty == 0.3

        # Test with no duplicates
        df_no_duplicates = pd.DataFrame({
            'Name': ['John', 'Jane', 'Bob', 'Alice'],
            'Age': [25, 30, 35, 40]
        })

        penalty_no_duplicates = self.validator._calculate_duplicate_penalty(df_no_duplicates)
        assert penalty_no_duplicates == 0.0

    def test_enhanced_quality_score_with_duplicate_penalty(self):
        """Test that quality score includes duplicate penalty."""
        # Create test data with duplicates
        df = pd.DataFrame({
            'Name': ['John', 'Jane', 'John', 'Bob'],
            'Age': [25, 30, 25, 35],
            'Email': ['john@example.com', 'jane@example.com', 'john@example.com', 'bob@example.com']
        })

        quality_score = self.validator.calculate_quality_score(df)

        # Should have duplicate penalty applied
        assert 'duplicate_penalty' in quality_score.details
        assert quality_score.details['duplicate_penalty'] > 0.0

        # Overall score should be reduced due to duplicate penalty
        assert quality_score.overall < 1.0

    def test_generate_smart_validation_rules(self):
        """Test smart validation rule generation."""
        # Create test data that should trigger various rule suggestions
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],  # High uniqueness, should suggest unique constraint
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],  # High uniqueness
            'age': [25, 30, 35, 40, 45],  # Numeric, should suggest numeric constraint
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],  # Should suggest email format
            'salary': [50000, 60000, 70000, 80000, 90000],  # Numeric, should suggest numeric constraint
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT']  # Lower uniqueness, shouldn't suggest unique
        })

        smart_rules = self.validator.generate_smart_validation_rules(df)

        # Should generate several rules
        assert len(smart_rules) > 0

        # Check for specific rule types
        rule_ids = [rule.rule_id for rule in smart_rules]

        # Should suggest unique constraints for high-uniqueness columns
        assert 'unique_id' in rule_ids
        assert 'unique_name' in rule_ids

        # Should suggest numeric constraints for numeric columns
        assert 'numeric_age' in rule_ids
        assert 'numeric_salary' in rule_ids

        # Should suggest email format validation
        assert 'email_format_email' in rule_ids

    def test_comprehensive_validation_with_sample_data(self):
        """Test comprehensive validation with sample data similar to the user's data."""
        # Create test data similar to sample_data.csv
        df = pd.DataFrame({
            'Name': ['john doe', 'Jane Smith', 'john doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
            'Age': [25, 30, 25, '', 28, 35],
            'Email': ['john@example.com', 'jane@example.com', 'john@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
            'City': ['New York', 'Los Angeles', 'New York', 'Chicago', '', 'Boston'],
            'Salary': [50000, 60000, 50000, 55000, 65000, 70000]
        })

        # Run validation
        results = self.validator.validate_dataframe(df)
        quality_score = self.validator.calculate_quality_score(df)

        # Should detect all expected issues
        expected_rule_ids = ['missing_values_Age', 'missing_values_City', 'duplicate_rows']
        detected_rule_ids = [r.rule_id for r in results if not r.passed]

        for expected_id in expected_rule_ids:
            assert expected_id in detected_rule_ids, f"Expected rule {expected_id} not found in results"

        # Verify specific issues
        missing_age_rule = next((r for r in results if r.rule_id == 'missing_values_Age'), None)
        missing_city_rule = next((r for r in results if r.rule_id == 'missing_values_City'), None)
        duplicate_rule = next((r for r in results if r.rule_id == 'duplicate_rows'), None)

        assert missing_age_rule is not None and not missing_age_rule.passed
        assert missing_age_rule.error_count == 1
        assert missing_age_rule.affected_rows == [3]  # Bob Johnson's row

        assert missing_city_rule is not None and not missing_city_rule.passed
        assert missing_city_rule.error_count == 1
        assert missing_city_rule.affected_rows == [4]  # Alice Brown's row

        assert duplicate_rule is not None and not duplicate_rule.passed
        assert duplicate_rule.error_count == 2
        assert set(duplicate_rule.affected_rows) == {0, 2}  # john doe rows

        # Verify quality score is realistic (not 98% like before)
        assert quality_score.overall < 0.5  # Should be much lower than the previous 98%
        assert quality_score.details['duplicate_penalty'] > 0.0

    def test_empty_dataframe_handling(self):
        """Test validation with empty DataFrame."""
        df = pd.DataFrame()

        # Should handle empty DataFrame gracefully
        results = self.validator.validate_dataframe(df)
        quality_score = self.validator.calculate_quality_score(df)

        # Should not crash and should return appropriate scores
        assert len(results) == 0  # No validation rules for empty DataFrame
        assert quality_score.completeness == 0.0
        # Overall score calculation for empty DataFrame may vary, but should be low
        assert quality_score.overall < 0.5

    def test_single_row_dataframe(self):
        """Test validation with single row DataFrame."""
        df = pd.DataFrame({
            'Name': ['John'],
            'Age': [25],
            'Email': ['john@example.com']
        })

        # Should handle single row gracefully
        results = self.validator.validate_dataframe(df)
        quality_score = self.validator.calculate_quality_score(df)

        # Should not crash and should return appropriate scores
        assert quality_score.completeness == 1.0  # No missing values
        assert quality_score.details['duplicate_penalty'] == 0.0  # No duplicates

    def test_mixed_data_types_edge_cases(self):
        """Test validation with edge cases in mixed data types."""
        df = pd.DataFrame({
            'age': [1, 2, 3, 'invalid', 5],  # One truly non-numeric string in numeric column
            'text_column': ['a', 'b', 'c', 'd', 'e'],
            'mixed_column': [1, 'text', 3.14, True, None]
        })

        results = self.validator.validate_dataframe(df)

        # Should detect data type issue in age column
        age_type_rule = next((r for r in results if r.rule_id == 'data_type_age'), None)
        assert age_type_rule is not None
        assert not age_type_rule.passed
        assert age_type_rule.error_count == 1
        assert age_type_rule.affected_rows == [3]  # 'invalid' value
