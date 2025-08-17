"""
Advanced validator for CSV Data Cleaner.
Provides comprehensive data validation, schema validation, and quality scoring.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import time
import logging
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Represents a validation rule."""

    rule_id: str
    rule_type: str
    column: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    description: str = ""


@dataclass
class ValidationResult:
    """Represents a validation result."""

    rule_id: str
    passed: bool
    errors: List[str]
    affected_rows: List[int]
    error_count: int
    total_rows: int
    error_rate: float


@dataclass
class QualityScore:
    """Represents a data quality score."""

    completeness: float
    accuracy: float
    consistency: float
    validity: float
    overall: float
    details: Dict[str, Any]


class AdvancedValidator:
    """Advanced data validation and quality assessment."""

    def __init__(self):
        """Initialize the advanced validator."""
        self.validation_rules: List[ValidationRule] = []
        self.validation_results: List[ValidationResult] = []

        # Predefined validation patterns
        self.patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone": r"^\+?[\d\s\-\(\)]{10,}$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "url": r"^https?://[^\s/$.?#].[^\s]*$",
            "postal_code": r"^\d{5}(-\d{4})?$",
        }

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule.

        Args:
            rule: Validation rule to add.
        """
        self.validation_rules.append(rule)
        logger.info(f"Added validation rule: {rule.rule_id}")

    def load_schema_from_file(self, schema_file: str) -> None:
        """Load validation schema from JSON file.

        Args:
            schema_file: Path to schema JSON file.
        """
        try:
            with open(schema_file, "r") as f:
                schema = json.load(f)

            self.load_schema_from_dict(schema)
            logger.info(f"Loaded validation schema from {schema_file}")

        except Exception as e:
            logger.error(f"Error loading schema from {schema_file}: {str(e)}")
            raise

    def load_schema_from_dict(self, schema: Dict[str, Any]) -> None:
        """Load validation schema from dictionary.

        Args:
            schema: Schema dictionary.
        """
        self.validation_rules.clear()

        for rule_config in schema.get("rules", []):
            rule = ValidationRule(
                rule_id=rule_config.get("id"),
                rule_type=rule_config.get("type"),
                column=rule_config.get("column"),
                parameters=rule_config.get("parameters", {}),
                description=rule_config.get("description", ""),
            )
            self.add_validation_rule(rule)

    def validate_dataframe(self, df: pd.DataFrame) -> List[ValidationResult]:
        """Validate DataFrame against all rules and default quality checks.

        Args:
            df: DataFrame to validate.

        Returns:
            List of validation results.
        """
        self.validation_results.clear()

        logger.info(f"Starting validation of DataFrame with {len(df)} rows")

        # Apply custom validation rules
        for rule in self.validation_rules:
            result = self._apply_validation_rule(df, rule)
            self.validation_results.append(result)

            if result.passed:
                logger.info(f"Rule {rule.rule_id} passed")
            else:
                logger.warning(
                    f"Rule {rule.rule_id} failed: {result.error_count} errors"
                )

        # Apply default quality checks
        self._apply_default_quality_checks(df)

        return self.validation_results

    def _apply_default_quality_checks(self, df: pd.DataFrame) -> None:
        """Apply default quality checks to detect common data issues.

        Args:
            df: DataFrame to check.
        """
        if df.empty:
            return

        # Check for missing values in each column
        for column in df.columns:
            missing_count = df[column].isna().sum() + (df[column] == '').sum()
            if missing_count > 0:
                missing_rows = df[df[column].isna() | (df[column] == '')].index.tolist()
                result = ValidationResult(
                    rule_id=f"missing_values_{column}",
                    passed=False,
                    errors=[f"Column '{column}' has {missing_count} missing values"],
                    affected_rows=missing_rows,
                    error_count=missing_count,
                    total_rows=len(df),
                    error_rate=missing_count / len(df)
                )
                self.validation_results.append(result)
                logger.warning(f"Missing values detected in column '{column}': {missing_count} values")

        # Check for duplicate rows
        duplicate_mask = df.duplicated(keep=False)
        duplicate_count = duplicate_mask.sum()
        if duplicate_count > 0:
            duplicate_rows = df[duplicate_mask].index.tolist()
            result = ValidationResult(
                rule_id="duplicate_rows",
                passed=False,
                errors=[f"Found {duplicate_count} duplicate rows"],
                affected_rows=duplicate_rows,
                error_count=duplicate_count,
                total_rows=len(df),
                error_rate=duplicate_count / len(df)
            )
            self.validation_results.append(result)
            logger.warning(f"Duplicate rows detected: {duplicate_count} rows")

        # Check for data type consistency
        for column in df.columns:
            non_null_values = df[column].dropna()
            if not non_null_values.empty:
                # Try to detect if column should be numeric
                if column.lower() in ['age', 'salary', 'price', 'amount', 'count', 'number']:
                    try:
                        pd.to_numeric(non_null_values, errors='raise')
                    except (ValueError, TypeError):
                        non_numeric_count = len(non_null_values) - len(pd.to_numeric(non_null_values, errors='coerce').dropna())
                        if non_numeric_count > 0:
                            non_numeric_rows = df[~pd.to_numeric(df[column], errors='coerce').notna()].index.tolist()
                            result = ValidationResult(
                                rule_id=f"data_type_{column}",
                                passed=False,
                                errors=[f"Column '{column}' contains {non_numeric_count} non-numeric values"],
                                affected_rows=non_numeric_rows,
                                error_count=non_numeric_count,
                                total_rows=len(df),
                                error_rate=non_numeric_count / len(df)
                            )
                            self.validation_results.append(result)
                            logger.warning(f"Data type inconsistency in column '{column}': {non_numeric_count} non-numeric values")

                # Check email format for email columns
                elif column.lower() in ['email', 'e-mail', 'email_address']:
                    email_pattern = self.patterns['email']
                    invalid_emails = non_null_values[~non_null_values.astype(str).str.match(email_pattern, na=False)]
                    invalid_count = len(invalid_emails)
                    if invalid_count > 0:
                        invalid_rows = df[df[column].isin(invalid_emails)].index.tolist()
                        result = ValidationResult(
                            rule_id=f"email_format_{column}",
                            passed=False,
                            errors=[f"Column '{column}' contains {invalid_count} invalid email addresses"],
                            affected_rows=invalid_rows,
                            error_count=invalid_count,
                            total_rows=len(df),
                            error_rate=invalid_count / len(df)
                        )
                        self.validation_results.append(result)
                        logger.warning(f"Invalid email format in column '{column}': {invalid_count} invalid emails")

    def _apply_validation_rule(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> ValidationResult:
        """Apply a single validation rule to DataFrame.

        Args:
            df: DataFrame to validate.
            rule: Validation rule to apply.

        Returns:
            Validation result.
        """
        errors = []
        affected_rows = []

        if rule.rule_type == "not_null":
            result = self._validate_not_null(df, rule)
        elif rule.rule_type == "unique":
            result = self._validate_unique(df, rule)
        elif rule.rule_type == "range":
            result = self._validate_range(df, rule)
        elif rule.rule_type == "pattern":
            result = self._validate_pattern(df, rule)
        elif rule.rule_type == "data_type":
            result = self._validate_data_type(df, rule)
        elif rule.rule_type == "custom":
            result = self._validate_custom(df, rule)
        else:
            errors.append(f"Unknown validation rule type: {rule.rule_type}")
            result = (errors, affected_rows)

        errors, affected_rows = result
        error_count = len(errors)
        total_rows = len(df)
        error_rate = error_count / total_rows if total_rows > 0 else 0

        return ValidationResult(
            rule_id=rule.rule_id,
            passed=error_count == 0,
            errors=errors,
            affected_rows=affected_rows,
            error_count=error_count,
            total_rows=total_rows,
            error_rate=error_rate,
        )

    def _validate_not_null(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate that column is not null.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        if not rule.column:
            errors.append("Column not specified for not_null validation")
            return errors, affected_rows

        if rule.column not in df.columns:
            errors.append(f"Column '{rule.column}' not found in DataFrame")
            return errors, affected_rows

        null_mask = df[rule.column].isnull()
        null_indices = null_mask[null_mask].index.tolist()

        if null_indices:
            errors.append(
                f"Found {len(null_indices)} null values in column '{rule.column}'"
            )
            affected_rows = null_indices

        return errors, affected_rows

    def _validate_unique(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate that column values are unique.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        if not rule.column:
            errors.append("Column not specified for unique validation")
            return errors, affected_rows

        if rule.column not in df.columns:
            errors.append(f"Column '{rule.column}' not found in DataFrame")
            return errors, affected_rows

        duplicates = df[df[rule.column].duplicated(keep=False)]

        if not duplicates.empty:
            duplicate_indices = duplicates.index.tolist()
            errors.append(
                f"Found {len(duplicate_indices)} duplicate values in column '{rule.column}'"
            )
            affected_rows = duplicate_indices

        return errors, affected_rows

    def _validate_range(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate that column values are within specified range.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        if not rule.column:
            errors.append("Column not specified for range validation")
            return errors, affected_rows

        if rule.column not in df.columns:
            errors.append(f"Column '{rule.column}' not found in DataFrame")
            return errors, affected_rows

        min_val = rule.parameters.get("min")
        max_val = rule.parameters.get("max")

        if min_val is not None:
            below_min = df[rule.column] < min_val
            below_min_indices = below_min[below_min].index.tolist()
            if below_min_indices:
                errors.append(
                    f"Found {len(below_min_indices)} values below minimum {min_val}"
                )
                affected_rows.extend(below_min_indices)

        if max_val is not None:
            above_max = df[rule.column] > max_val
            above_max_indices = above_max[above_max].index.tolist()
            if above_max_indices:
                errors.append(
                    f"Found {len(above_max_indices)} values above maximum {max_val}"
                )
                affected_rows.extend(above_max_indices)

        return errors, list(set(affected_rows))

    def _validate_pattern(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate that column values match specified pattern.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        if not rule.column:
            errors.append("Column not specified for pattern validation")
            return errors, affected_rows

        if rule.column not in df.columns:
            errors.append(f"Column '{rule.column}' not found in DataFrame")
            return errors, affected_rows

        pattern = rule.parameters.get("pattern")
        if not pattern:
            errors.append("Pattern not specified for pattern validation")
            return errors, affected_rows

        # Convert to string for pattern matching
        column_str = df[rule.column].astype(str)
        pattern_matches = column_str.str.match(pattern, na=False)
        invalid_indices = pattern_matches[~pattern_matches].index.tolist()

        if invalid_indices:
            errors.append(
                f"Found {len(invalid_indices)} values that don't match pattern"
            )
            affected_rows = invalid_indices

        return errors, affected_rows

    def _validate_data_type(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate that column has specified data type.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        if not rule.column:
            errors.append("Column not specified for data_type validation")
            return errors, affected_rows

        if rule.column not in df.columns:
            errors.append(f"Column '{rule.column}' not found in DataFrame")
            return errors, affected_rows

        expected_type = rule.parameters.get("type")
        if not expected_type:
            errors.append("Data type not specified for data_type validation")
            return errors, affected_rows

        # Check data type
        actual_type = str(df[rule.column].dtype)
        if actual_type != expected_type:
            errors.append(f"Expected type '{expected_type}', got '{actual_type}'")
            affected_rows = df.index.tolist()

        return errors, affected_rows

    def _validate_custom(
        self, df: pd.DataFrame, rule: ValidationRule
    ) -> Tuple[List[str], List[int]]:
        """Validate using custom validation function.

        Args:
            df: DataFrame to validate.
            rule: Validation rule.

        Returns:
            Tuple of (errors, affected_rows).
        """
        errors = []
        affected_rows = []

        # Custom validation would be implemented here
        # For now, return no errors
        return errors, affected_rows

    def calculate_quality_score(self, df: pd.DataFrame) -> QualityScore:
        """Calculate comprehensive data quality score.

        Args:
            df: DataFrame to assess.

        Returns:
            Quality score with detailed metrics.
        """
        logger.info("Calculating data quality score")

        # Completeness score
        completeness = self._calculate_completeness_score(df)

        # Accuracy score (based on validation results)
        accuracy = self._calculate_accuracy_score()

        # Consistency score
        consistency = self._calculate_consistency_score(df)

        # Validity score
        validity = self._calculate_validity_score()

        # Apply duplicate penalty
        duplicate_penalty = self._calculate_duplicate_penalty(df)

        # Overall score (weighted average with duplicate penalty)
        overall = (
            completeness * 0.25 + accuracy * 0.25 + consistency * 0.2 + validity * 0.2
        ) * (1 - duplicate_penalty)

        details = {
            "completeness_details": self._get_completeness_details(df),
            "accuracy_details": self._get_accuracy_details(),
            "consistency_details": self._get_consistency_details(df),
            "validity_details": self._get_validity_details(),
            "duplicate_penalty": duplicate_penalty,
        }

        return QualityScore(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            validity=validity,
            overall=overall,
            details=details,
        )

    def _calculate_duplicate_penalty(self, df: pd.DataFrame) -> float:
        """Calculate penalty for duplicate rows.

        Args:
            df: DataFrame to assess.

        Returns:
            Duplicate penalty (0-0.3).
        """
        if df.empty:
            return 0.0

        duplicate_count = df.duplicated(keep=False).sum()
        duplicate_ratio = duplicate_count / len(df)

        # Cap penalty at 30%
        return min(duplicate_ratio, 0.3)

    def generate_smart_validation_rules(self, df: pd.DataFrame) -> List[ValidationRule]:
        """Generate validation rules based on data analysis.

        Args:
            df: DataFrame to analyze.

        Returns:
            List of generated validation rules.
        """
        rules = []

        for column in df.columns:
            # Check if column should be required (not null)
            null_ratio = df[column].isna().sum() / len(df)
            if null_ratio < 0.1:  # If less than 10% nulls, suggest making it required
                rules.append(ValidationRule(
                    rule_id=f"not_null_{column}",
                    rule_type="not_null",
                    column=column,
                    description=f"Column '{column}' should not contain null values"
                ))

            # Check for unique constraints
            unique_ratio = df[column].nunique() / len(df)
            if unique_ratio > 0.95:  # If more than 95% unique, suggest unique constraint
                rules.append(ValidationRule(
                    rule_id=f"unique_{column}",
                    rule_type="unique",
                    column=column,
                    description=f"Column '{column}' should contain unique values"
                ))

            # Check for data type constraints
            if column.lower() in ['age', 'salary', 'price', 'amount', 'count', 'number']:
                try:
                    pd.to_numeric(df[column].dropna(), errors='raise')
                    rules.append(ValidationRule(
                        rule_id=f"numeric_{column}",
                        rule_type="data_type",
                        column=column,
                        parameters={"data_type": "numeric"},
                        description=f"Column '{column}' should contain numeric values"
                    ))
                except (ValueError, TypeError):
                    pass

            # Check for email format
            if column.lower() in ['email', 'e-mail', 'email_address']:
                rules.append(ValidationRule(
                    rule_id=f"email_format_{column}",
                    rule_type="pattern",
                    column=column,
                    parameters={"pattern": self.patterns['email']},
                    description=f"Column '{column}' should contain valid email addresses"
                ))

        return rules

    def _calculate_completeness_score(self, df: pd.DataFrame) -> float:
        """Calculate completeness score.

        Args:
            df: DataFrame to assess.

        Returns:
            Completeness score (0-1).
        """
        if df.empty:
            return 0.0

        total_cells = len(df) * len(df.columns)
        # Count cells that are not null and not empty strings
        non_null_cells = df.notna().sum().sum()
        empty_string_cells = (df == '').sum().sum()

        # Subtract empty strings from non-null count
        valid_cells = non_null_cells - empty_string_cells

        return valid_cells / total_cells if total_cells > 0 else 0.0

    def _calculate_accuracy_score(self) -> float:
        """Calculate accuracy score based on validation results.

        Returns:
            Accuracy score (0-1).
        """
        if not self.validation_results:
            return 1.0  # No validation rules means perfect accuracy

        total_errors = sum(result.error_count for result in self.validation_results)
        total_rows = (
            self.validation_results[0].total_rows if self.validation_results else 0
        )

        if total_rows == 0:
            return 1.0

        return max(0.0, 1.0 - (total_errors / total_rows))

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate consistency score.

        Args:
            df: DataFrame to assess.

        Returns:
            Consistency score (0-1).
        """
        if df.empty:
            return 0.0

        # Check for data type consistency
        type_consistency = 1.0
        for column in df.columns:
            try:
                # Try to infer consistent data type
                pd.to_numeric(df[column], errors="raise")
            except (ValueError, TypeError):
                # If conversion fails, check if it's consistent string data
                if df[column].dtype == "object":
                    # Check if all non-null values are strings
                    non_null_values = df[column].dropna()
                    if not non_null_values.empty:
                        string_ratio = (
                            non_null_values.astype(str) == non_null_values
                        ).mean()
                        type_consistency *= string_ratio

        return type_consistency

    def _calculate_validity_score(self) -> float:
        """Calculate validity score based on validation results.

        Returns:
            Validity score (0-1).
        """
        if not self.validation_results:
            return 1.0

        passed_rules = sum(1 for result in self.validation_results if result.passed)
        total_rules = len(self.validation_results)

        return passed_rules / total_rules if total_rules > 0 else 1.0

    def _get_completeness_details(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed completeness information.

        Args:
            df: DataFrame to analyze.

        Returns:
            Completeness details.
        """
        completeness_by_column = {}
        for column in df.columns:
            non_null_count = df[column].notna().sum()
            total_count = len(df)
            completeness_by_column[column] = {
                "non_null_count": non_null_count,
                "total_count": total_count,
                "completeness_ratio": non_null_count / total_count
                if total_count > 0
                else 0,
            }

        return {
            "overall_completeness": self._calculate_completeness_score(df),
            "completeness_by_column": completeness_by_column,
        }

    def _get_accuracy_details(self) -> Dict[str, Any]:
        """Get detailed accuracy information.

        Returns:
            Accuracy details.
        """
        return {
            "total_validation_rules": len(self.validation_results),
            "passed_rules": sum(
                1 for result in self.validation_results if result.passed
            ),
            "failed_rules": sum(
                1 for result in self.validation_results if not result.passed
            ),
            "total_errors": sum(
                result.error_count for result in self.validation_results
            ),
            "error_rate": self._calculate_accuracy_score(),
        }

    def _get_consistency_details(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get detailed consistency information.

        Args:
            df: DataFrame to analyze.

        Returns:
            Consistency details.
        """
        data_types = df.dtypes.to_dict()
        return {
            "data_types": data_types,
            "consistency_score": self._calculate_consistency_score(df),
        }

    def _get_validity_details(self) -> Dict[str, Any]:
        """Get detailed validity information.

        Returns:
            Validity details.
        """
        return {
            "validation_results": [
                {
                    "rule_id": result.rule_id,
                    "passed": result.passed,
                    "error_count": result.error_count,
                    "error_rate": result.error_rate,
                }
                for result in self.validation_results
            ],
            "validity_score": self._calculate_validity_score(),
        }

    def generate_validation_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive validation report.

        Args:
            output_file: Optional output file path.

        Returns:
            Report content.
        """
        if not self.validation_results:
            report = "No validation results available."
        else:
            report = self._format_validation_report()

        if output_file:
            with open(output_file, "w") as f:
                f.write(report)
            logger.info(f"Validation report saved to {output_file}")

        return report

    def _format_validation_report(self) -> str:
        """Format validation results into a report.

        Returns:
            Formatted report string.
        """
        report_lines = [
            "=" * 60,
            "DATA VALIDATION REPORT",
            "=" * 60,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Rules: {len(self.validation_results)}",
            f"Passed Rules: {sum(1 for r in self.validation_results if r.passed)}",
            f"Failed Rules: {sum(1 for r in self.validation_results if not r.passed)}",
            "",
            "DETAILED RESULTS:",
            "-" * 30,
        ]

        for result in self.validation_results:
            status = "PASSED" if result.passed else "FAILED"
            report_lines.extend(
                [
                    f"Rule: {result.rule_id} - {status}",
                    f"  Error Count: {result.error_count}",
                    f"  Error Rate: {result.error_rate:.2%}",
                    f"  Affected Rows: {len(result.affected_rows)}",
                    "",
                ]
            )

        return "\n".join(report_lines)
