"""
AI Agent for intelligent CSV data cleaning suggestions and library selection.
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging
import hashlib
import json
from dataclasses import dataclass
import time

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class CleaningSuggestion:
    """Represents an AI-generated cleaning suggestion."""

    operation: str
    library: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    estimated_impact: str
    priority: int = 1

    def __post_init__(self):
        """Validate suggestion data after initialization."""
        self._validate_suggestion()

    def _validate_suggestion(self) -> None:
        """Validate suggestion data integrity."""
        if not self.operation or not isinstance(self.operation, str):
            raise ValueError("Operation must be a non-empty string")

        if not self.library or not isinstance(self.library, str):
            raise ValueError("Library must be a non-empty string")

        if not isinstance(self.parameters, dict):
            raise ValueError("Parameters must be a dictionary")

        if not isinstance(self.confidence, (int, float)) or not (
            0.0 <= self.confidence <= 1.0
        ):
            raise ValueError("Confidence must be a number between 0.0 and 1.0")

        if not self.reasoning or not isinstance(self.reasoning, str):
            raise ValueError("Reasoning must be a non-empty string")

        if not self.estimated_impact or not isinstance(self.estimated_impact, str):
            raise ValueError("Estimated impact must be a non-empty string")

        if not isinstance(self.priority, int) or self.priority < 1:
            raise ValueError("Priority must be a positive integer")

    def is_valid(self) -> bool:
        """Check if the suggestion is valid for execution.

        Returns:
            True if the suggestion is valid, False otherwise.
        """
        try:
            self._validate_suggestion()
            return True
        except ValueError:
            return False

    def get_execution_parameters(self) -> Dict[str, Any]:
        """Get parameters ready for execution.

        Returns:
            Dictionary of parameters for execution.
        """
        return self.parameters.copy()

    def get_confidence_level(self) -> str:
        """Get human-readable confidence level.

        Returns:
            Confidence level as string (High, Medium, Low).
        """
        if self.confidence >= 0.8:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        else:
            return "Low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary format.

        Returns:
            Dictionary representation of the suggestion.
        """
        return {
            "operation": self.operation,
            "library": self.library,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "estimated_impact": self.estimated_impact,
            "priority": self.priority,
        }

    def __str__(self) -> str:
        """String representation of the suggestion.

        Returns:
            Human-readable string representation.
        """
        return (
            f"CleaningSuggestion(operation='{self.operation}', "
            f"library='{self.library}', confidence={self.confidence:.1%}, "
            f"priority={self.priority})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of the suggestion.

        Returns:
            Detailed string representation.
        """
        return (
            f"CleaningSuggestion(operation='{self.operation}', "
            f"library='{self.library}', parameters={self.parameters}, "
            f"confidence={self.confidence}, reasoning='{self.reasoning}', "
            f"estimated_impact='{self.estimated_impact}', priority={self.priority})"
        )


@dataclass
class DataProfile:
    """Profile of data characteristics for AI analysis."""

    row_count: int
    column_count: int
    missing_percentage: float
    duplicate_percentage: float
    data_types: Dict[str, str]
    memory_usage_mb: float
    has_text_columns: bool
    has_numeric_columns: bool
    has_date_columns: bool
    has_categorical_columns: bool
    quality_score: float = 0.0


class AIAgent:
    """AI-powered intelligent cleaning agent."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the AI agent.

        Args:
            config: Configuration object for AI settings.
        """
        self.config = config or Config()
        self.suggestion_cache = {}
        self.learning_history = []
        self.provider = None
        self.llm_provider_manager = None

        # Initialize AI if enabled
        if self.config.ai_enabled:
            self._initialize_ai_provider()

    def _initialize_ai_provider(self) -> None:
        """Initialize AI provider based on configuration."""
        try:
            # Initialize LLM provider manager
            from .llm_providers import LLMProviderManager

            config_dict = {
                "default_llm_provider": self.config.default_llm_provider,
                "ai_api_keys": self.config.ai_api_keys,
                "ai_openai_model": self.config.ai_openai_model,
                "ai_anthropic_model": self.config.ai_anthropic_model,
                "ai_local_model": self.config.ai_local_model,
            }

            self.llm_provider_manager = LLMProviderManager(config_dict)
            logger.info("AI provider initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize AI provider: {e}")
            self.config.ai_enabled = False

    def analyze_data(self, df: pd.DataFrame) -> DataProfile:
        """Analyze data characteristics for AI processing.

        Args:
            df: DataFrame to analyze.

        Returns:
            DataProfile with data characteristics.
        """
        if df.empty:
            return DataProfile(
                row_count=0,
                column_count=0,
                missing_percentage=0.0,
                duplicate_percentage=0.0,
                data_types={},
                memory_usage_mb=0.0,
                has_text_columns=False,
                has_numeric_columns=False,
                has_date_columns=False,
                has_categorical_columns=False,
                quality_score=0.0,
            )

        # Calculate basic statistics
        row_count = len(df)
        column_count = len(df.columns)

        # Calculate missing data percentage
        missing_percentage = (
            df.isnull().sum().sum() / (row_count * column_count)
        ) * 100

        # Calculate duplicate percentage
        duplicate_percentage = (
            (row_count - len(df.drop_duplicates())) / row_count
        ) * 100

        # Analyze data types
        data_types = df.dtypes.astype(str).to_dict()

        # Calculate memory usage
        memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        # Analyze column types
        has_text_columns = any(df[col].dtype == "object" for col in df.columns)
        has_numeric_columns = any(
            pd.api.types.is_numeric_dtype(df[col]) for col in df.columns
        )
        has_date_columns = any(
            pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns
        )
        has_categorical_columns = any(df[col].dtype == "category" for col in df.columns)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            missing_percentage, duplicate_percentage, row_count, column_count
        )

        return DataProfile(
            row_count=row_count,
            column_count=column_count,
            missing_percentage=missing_percentage,
            duplicate_percentage=duplicate_percentage,
            data_types=data_types,
            memory_usage_mb=memory_usage_mb,
            has_text_columns=has_text_columns,
            has_numeric_columns=has_numeric_columns,
            has_date_columns=has_date_columns,
            has_categorical_columns=has_categorical_columns,
            quality_score=quality_score,
        )

    def _calculate_quality_score(
        self, missing_pct: float, duplicate_pct: float, rows: int, cols: int
    ) -> float:
        """Calculate data quality score.

        Args:
            missing_pct: Percentage of missing data.
            duplicate_pct: Percentage of duplicate rows.
            rows: Number of rows.
            cols: Number of columns.

        Returns:
            Quality score between 0 and 1.
        """
        # Base score starts at 1.0
        score = 1.0

        # Penalize missing data (up to 50% penalty)
        missing_penalty = min(missing_pct / 100, 0.5)
        score -= missing_penalty

        # Penalize duplicates (up to 30% penalty)
        duplicate_penalty = min(duplicate_pct / 100, 0.3)
        score -= duplicate_penalty

        # Bonus for reasonable dataset size
        if 100 <= rows <= 1000000 and 2 <= cols <= 100:
            score += 0.1

        return max(0.0, min(1.0, score))

    def generate_suggestions(
        self, df: pd.DataFrame, available_operations: List[str]
    ) -> List[CleaningSuggestion]:
        """Generate intelligent cleaning suggestions.

        Args:
            df: DataFrame to analyze.
            available_operations: List of available cleaning operations.

        Returns:
            List of cleaning suggestions.
        """
        if not self.config.ai_enabled:
            return self._generate_rule_based_suggestions(df, available_operations)

        # Check cache first
        cache_key = self._generate_cache_key(df, available_operations)
        if cache_key in self.suggestion_cache:
            logger.debug("Using cached AI suggestions")
            return self.suggestion_cache[cache_key]

        # Generate AI suggestions using LLM
        try:
            suggestions = self._generate_ai_suggestions(df, available_operations)
            if not suggestions:  # Fallback to rule-based if AI fails
                suggestions = self._generate_rule_based_suggestions(
                    df, available_operations
                )
        except Exception as e:
            logger.warning(
                f"AI suggestion generation failed: {e}, falling back to rule-based"
            )
            suggestions = self._generate_rule_based_suggestions(
                df, available_operations
            )

        # Cache suggestions
        self.suggestion_cache[cache_key] = suggestions

        return suggestions

    def _generate_rule_based_suggestions(
        self, df: pd.DataFrame, available_operations: List[str]
    ) -> List[CleaningSuggestion]:
        """Generate rule-based suggestions when AI is not available.

        Args:
            df: DataFrame to analyze.
            available_operations: List of available cleaning operations.

        Returns:
            List of rule-based cleaning suggestions.
        """
        suggestions = []
        profile = self.analyze_data(df)

        # Suggest duplicate removal if duplicates exist
        if (
            profile.duplicate_percentage > 5.0
            and "remove_duplicates" in available_operations
        ):
            suggestions.append(
                CleaningSuggestion(
                    operation="remove_duplicates",
                    library="pandas",
                    parameters={},
                    confidence=0.9,
                    reasoning=f"Dataset has {profile.duplicate_percentage:.1f}% duplicate rows",
                    estimated_impact=f"Will remove ~{int(profile.row_count * profile.duplicate_percentage / 100)} duplicate rows",
                    priority=1,
                )
            )

        # Suggest missing value handling if missing data exists
        if profile.missing_percentage > 1.0:
            if "fill_missing" in available_operations:
                suggestions.append(
                    CleaningSuggestion(
                        operation="fill_missing",
                        library="pandas",
                        parameters={"method": "ffill"},
                        confidence=0.8,
                        reasoning=f"Dataset has {profile.missing_percentage:.1f}% missing values",
                        estimated_impact="Will fill missing values using forward fill method",
                        priority=2,
                    )
                )
            elif "drop_missing" in available_operations:
                suggestions.append(
                    CleaningSuggestion(
                        operation="drop_missing",
                        library="pandas",
                        parameters={},
                        confidence=0.7,
                        reasoning=f"Dataset has {profile.missing_percentage:.1f}% missing values",
                        estimated_impact="Will remove rows with missing values",
                        priority=2,
                    )
                )

        # Suggest column name cleaning if text columns exist
        if profile.has_text_columns and "rename_columns" in available_operations:
            suggestions.append(
                CleaningSuggestion(
                    operation="rename_columns",
                    library="pandas",
                    parameters={"case": "snake"},
                    confidence=0.7,
                    reasoning="Dataset has text columns that may benefit from standardized naming",
                    estimated_impact="Will standardize column names to snake_case format",
                    priority=3,
                )
            )

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority)

        return suggestions

    def _generate_ai_suggestions(
        self, df: pd.DataFrame, available_operations: List[str]
    ) -> List[CleaningSuggestion]:
        """Generate AI-powered suggestions using LLM.

        Args:
            df: DataFrame to analyze.
            available_operations: List of available cleaning operations.

        Returns:
            List of AI-generated cleaning suggestions.
        """
        if not hasattr(self, "llm_provider_manager") or not self.llm_provider_manager:
            logger.warning("LLM provider manager not available")
            return []

        try:
            # Get data profile for AI analysis
            profile = self.analyze_data(df)

            # Create prompt for AI analysis
            prompt = self._create_suggestion_prompt(df, profile, available_operations)

            # Prepare metadata for logging
            metadata = {
                "dataset_rows": profile.row_count,
                "dataset_columns": profile.column_count,
                "missing_percentage": profile.missing_percentage,
                "duplicate_percentage": profile.duplicate_percentage,
                "quality_score": profile.quality_score,
                "available_operations": available_operations,
            }

            # Get AI response with logging context
            response = self.llm_provider_manager.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                operation_type="suggestion_generation",
                metadata=metadata,
            )

            if not response.success:
                logger.warning(f"AI response failed: {response.error_message}")
                return []

            # Parse AI response into suggestions
            suggestions = self._parse_ai_suggestions(
                response.content, available_operations
            )

            return suggestions

        except Exception as e:
            logger.error(f"Error generating AI suggestions: {e}")
            return []

    def _create_suggestion_prompt(
        self, df: pd.DataFrame, profile: DataProfile, available_operations: List[str]
    ) -> str:
        """Create a prompt for AI suggestion generation.

        Args:
            df: DataFrame to analyze.
            profile: Data profile information.
            available_operations: List of available operations.

        Returns:
            Formatted prompt string.
        """
        # Sample data for context
        sample_data = df.head(3).to_string()

        prompt = f"""
You are an expert data scientist analyzing a CSV dataset. Based on the data profile and sample data below, suggest the best data cleaning operations.

DATASET PROFILE:
- Rows: {profile.row_count}
- Columns: {profile.column_count}
- Missing data: {profile.missing_percentage:.1f}%
- Duplicate rows: {profile.duplicate_percentage:.1f}%
- Memory usage: {profile.memory_usage_mb:.4f} MB
- Quality score: {profile.quality_score:.1%}
- Data types: {profile.data_types}
- Has text columns: {profile.has_text_columns}
- Has numeric columns: {profile.has_numeric_columns}
- Has date columns: {profile.has_date_columns}
- Has categorical columns: {profile.has_categorical_columns}

SAMPLE DATA:
{sample_data}

AVAILABLE OPERATIONS: {', '.join(available_operations)}

Please suggest 2-4 cleaning operations in JSON format:
{{
    "suggestions": [
        {{
            "operation": "operation_name",
            "library": "pandas",
            "parameters": {{"param": "value"}},
            "confidence": 0.85,
            "reasoning": "Why this operation is needed",
            "estimated_impact": "What this will accomplish",
            "priority": 1
        }}
    ]
}}

Focus on the most important issues first. Be specific about parameters and reasoning.
"""
        return prompt

    def _parse_ai_suggestions(
        self, ai_response: str, available_operations: List[str]
    ) -> List[CleaningSuggestion]:
        """Parse AI response into cleaning suggestions.

        Args:
            ai_response: Raw AI response text.
            available_operations: List of available operations.

        Returns:
            List of parsed cleaning suggestions.
        """
        try:
            # Extract JSON from response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in AI response")
                return []

            json_str = json_match.group()
            data = json.loads(json_str)

            suggestions = []
            for suggestion_data in data.get("suggestions", []):
                # Validate operation is available
                operation = suggestion_data.get("operation")
                if operation not in available_operations:
                    logger.warning(f"AI suggested unavailable operation: {operation}")
                    continue

                suggestions.append(
                    CleaningSuggestion(
                        operation=operation,
                        library=suggestion_data.get("library", "pandas"),
                        parameters=suggestion_data.get("parameters", {}),
                        confidence=float(suggestion_data.get("confidence", 0.7)),
                        reasoning=suggestion_data.get("reasoning", "AI suggestion"),
                        estimated_impact=suggestion_data.get(
                            "estimated_impact", "Will improve data quality"
                        ),
                        priority=int(suggestion_data.get("priority", 1)),
                    )
                )

            return suggestions

        except Exception as e:
            logger.error(f"Error parsing AI suggestions: {e}")
            return []

    def _generate_cache_key(
        self, df: pd.DataFrame, available_operations: List[str]
    ) -> str:
        """Generate cache key for suggestions.

        Args:
            df: DataFrame to analyze.
            available_operations: List of available operations.

        Returns:
            Cache key string.
        """
        # Create a hash of DataFrame characteristics and available operations
        df_hash = hashlib.md5(
            f"{df.shape}{df.dtypes.to_dict()}{df.isnull().sum().to_dict()}".encode()
        ).hexdigest()

        ops_hash = hashlib.md5(
            json.dumps(sorted(available_operations)).encode()
        ).hexdigest()

        return f"{df_hash}_{ops_hash}"

    def get_best_library_for_operation(
        self, operation: str, df: pd.DataFrame, available_libraries: List[str]
    ) -> str:
        """Get the best library for a specific operation.

        Args:
            operation: Operation to perform.
            df: DataFrame to operate on.
            available_libraries: List of available library wrappers.

        Returns:
            Best library name for the operation.
        """
        # Simple rule-based library selection
        if operation in ["remove_duplicates", "drop_missing", "fill_missing"]:
            return (
                "pandas" if "pandas" in available_libraries else available_libraries[0]
            )

        if operation in ["clean_names", "remove_empty", "remove_constant_columns"]:
            return "pyjanitor" if "pyjanitor" in available_libraries else "pandas"

        if operation in ["advanced_imputation", "variable_selection"]:
            return (
                "feature_engine"
                if "feature_engine" in available_libraries
                else "pandas"
            )

        if operation in ["missing_summary", "missing_matrix", "missing_heatmap"]:
            return "missingno" if "missingno" in available_libraries else "pandas"

        if operation in ["dedupe", "train", "predict"]:
            return "dedupe" if "dedupe" in available_libraries else "pandas"

        # Default to pandas
        return "pandas" if "pandas" in available_libraries else available_libraries[0]

    def record_feedback(
        self,
        suggestion: CleaningSuggestion,
        success: bool,
        user_feedback: Optional[str] = None,
    ) -> None:
        """Record user feedback for learning.

        Args:
            suggestion: The suggestion that was used.
            success: Whether the suggestion was successful.
            user_feedback: Optional user feedback text.
        """
        feedback_record = {
            "timestamp": time.time(),
            "suggestion": suggestion,
            "success": success,
            "user_feedback": user_feedback,
        }

        self.learning_history.append(feedback_record)
        logger.debug(f"Recorded feedback: {feedback_record}")

    def clear_cache(self) -> None:
        """Clear the suggestion cache."""
        self.suggestion_cache.clear()
        logger.debug("AI suggestion cache cleared")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning history.

        Returns:
            Dictionary with learning statistics.
        """
        if not self.learning_history:
            return {
                "total_feedback": 0,
                "success_rate": 0.0,
                "most_successful_operations": [],
                "most_successful_libraries": [],
            }

        total_feedback = len(self.learning_history)
        successful_suggestions = [f for f in self.learning_history if f["success"]]
        success_rate = len(successful_suggestions) / total_feedback

        # Analyze most successful operations
        operation_success = {}
        library_success = {}

        for feedback in successful_suggestions:
            suggestion = feedback["suggestion"]
            operation_success[suggestion.operation] = (
                operation_success.get(suggestion.operation, 0) + 1
            )
            library_success[suggestion.library] = (
                library_success.get(suggestion.library, 0) + 1
            )

        most_successful_operations = sorted(
            operation_success.items(), key=lambda x: x[1], reverse=True
        )[:5]
        most_successful_libraries = sorted(
            library_success.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "total_feedback": total_feedback,
            "success_rate": success_rate,
            "most_successful_operations": most_successful_operations,
            "most_successful_libraries": most_successful_libraries,
        }

    def execute_suggestions(
        self,
        df: pd.DataFrame,
        suggestions: List[CleaningSuggestion],
        library_manager,
        auto_confirm: bool = False,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Execute a list of AI suggestions on the DataFrame.

        Args:
            df: DataFrame to process.
            suggestions: List of cleaning suggestions to execute.
            library_manager: Library manager instance for executing operations.
            auto_confirm: Whether to automatically confirm all suggestions.

        Returns:
            Tuple of (processed_dataframe, execution_summary).
        """
        if not suggestions:
            logger.warning("No suggestions provided for execution")
            return df, {"success": True, "executed_operations": [], "errors": []}

        # Validate suggestions
        valid_suggestions = self._validate_suggestions_for_execution(suggestions)
        if not valid_suggestions:
            logger.error("No valid suggestions found for execution")
            return df, {
                "success": False,
                "executed_operations": [],
                "errors": ["No valid suggestions"],
            }

        # Resolve dependencies and sort suggestions
        sorted_suggestions = self._resolve_dependencies(valid_suggestions)

        # Execute suggestions
        result_df = df.copy()
        execution_summary = {
            "success": True,
            "executed_operations": [],
            "errors": [],
            "total_suggestions": len(suggestions),
            "valid_suggestions": len(valid_suggestions),
            "executed_count": 0,
        }

        for suggestion in sorted_suggestions:
            try:
                logger.info(
                    f"Executing suggestion: {suggestion.operation} with {suggestion.library}"
                )

                # Execute the operation
                result_df = self._execute_single_suggestion(
                    result_df, suggestion, library_manager
                )

                # Record successful execution
                execution_summary["executed_operations"].append(
                    {
                        "operation": suggestion.operation,
                        "library": suggestion.library,
                        "success": True,
                        "confidence": suggestion.confidence,
                    }
                )
                execution_summary["executed_count"] += 1

                # Record feedback for learning
                self.record_feedback(suggestion, True)

            except Exception as e:
                logger.error(
                    f"Failed to execute suggestion {suggestion.operation}: {e}"
                )
                execution_summary["errors"].append(
                    {
                        "operation": suggestion.operation,
                        "error": str(e),
                        "suggestion": suggestion,
                    }
                )
                execution_summary["success"] = False

                # Record feedback for learning
                self.record_feedback(suggestion, False, str(e))

        return result_df, execution_summary

    def _validate_suggestions_for_execution(
        self, suggestions: List[CleaningSuggestion]
    ) -> List[CleaningSuggestion]:
        """Validate suggestions for execution.

        Args:
            suggestions: List of suggestions to validate.

        Returns:
            List of valid suggestions.
        """
        valid_suggestions = []

        for suggestion in suggestions:
            if not suggestion.is_valid():
                logger.warning(f"Invalid suggestion skipped: {suggestion.operation}")
                continue

            if suggestion.confidence < 0.3:  # Skip very low confidence suggestions
                logger.info(
                    f"Low confidence suggestion skipped: {suggestion.operation} ({suggestion.confidence:.1%})"
                )
                continue

            valid_suggestions.append(suggestion)

        return valid_suggestions

    def _resolve_dependencies(
        self, suggestions: List[CleaningSuggestion]
    ) -> List[CleaningSuggestion]:
        """Resolve dependencies between suggestions and sort them.

        Args:
            suggestions: List of suggestions to sort.

        Returns:
            Sorted list of suggestions in execution order.
        """
        # Define operation dependencies
        dependencies = {
            "clean_names": [],  # No dependencies
            "remove_duplicates": ["clean_names"],  # Clean names first
            "drop_missing": ["clean_names"],  # Clean names first
            "fill_missing": ["drop_missing"],  # Drop missing first
            "convert_types": ["fill_missing"],  # Fill missing first
            "remove_empty": ["clean_names"],  # Clean names first
        }

        # Sort by priority first, then by dependencies
        sorted_suggestions = sorted(
            suggestions, key=lambda x: (x.priority, x.operation)
        )

        # Apply dependency ordering
        result = []
        processed = set()

        for suggestion in sorted_suggestions:
            if suggestion.operation in processed:
                continue

            # Add dependencies first
            deps = dependencies.get(suggestion.operation, [])
            for dep_op in deps:
                dep_suggestions = [
                    s
                    for s in suggestions
                    if s.operation == dep_op and s.operation not in processed
                ]
                result.extend(dep_suggestions)
                processed.update(s.operation for s in dep_suggestions)

            # Add current suggestion
            if suggestion.operation not in processed:
                result.append(suggestion)
                processed.add(suggestion.operation)

        return result

    def _execute_single_suggestion(
        self, df: pd.DataFrame, suggestion: CleaningSuggestion, library_manager
    ) -> pd.DataFrame:
        """Execute a single suggestion on the DataFrame.

        Args:
            df: DataFrame to process.
            suggestion: Suggestion to execute.
            library_manager: Library manager instance.

        Returns:
            Processed DataFrame.
        """
        try:
            # Get the appropriate wrapper
            wrapper = library_manager.wrappers.get(suggestion.library)
            if not wrapper:
                raise ValueError(f"Library '{suggestion.library}' not available")

            # Execute the operation
            result_df = wrapper.execute(
                suggestion.operation, df, **suggestion.get_execution_parameters()
            )

            logger.info(
                f"Successfully executed {suggestion.operation} with {suggestion.library}"
            )
            return result_df

        except Exception as e:
            logger.error(
                f"Failed to execute {suggestion.operation} with {suggestion.library}: {e}"
            )
            raise

    def get_execution_plan(
        self, suggestions: List[CleaningSuggestion]
    ) -> Dict[str, Any]:
        """Get a detailed execution plan for suggestions.

        Args:
            suggestions: List of suggestions to plan.

        Returns:
            Execution plan dictionary.
        """
        valid_suggestions = self._validate_suggestions_for_execution(suggestions)
        sorted_suggestions = self._resolve_dependencies(valid_suggestions)

        plan = {
            "total_suggestions": len(suggestions),
            "valid_suggestions": len(valid_suggestions),
            "execution_order": [],
            "estimated_impact": {},
            "confidence_summary": {"high": 0, "medium": 0, "low": 0},
        }

        for i, suggestion in enumerate(sorted_suggestions, 1):
            plan["execution_order"].append(
                {
                    "step": i,
                    "operation": suggestion.operation,
                    "library": suggestion.library,
                    "confidence": suggestion.confidence,
                    "confidence_level": suggestion.get_confidence_level(),
                    "reasoning": suggestion.reasoning,
                    "estimated_impact": suggestion.estimated_impact,
                    "parameters": suggestion.parameters,
                }
            )

            # Update confidence summary
            level = suggestion.get_confidence_level().lower()
            plan["confidence_summary"][level] += 1

        return plan
