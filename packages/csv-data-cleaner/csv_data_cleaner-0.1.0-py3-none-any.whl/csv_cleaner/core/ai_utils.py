"""
AI utilities for prompt engineering and response parsing.
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptEngineer:
    """Engineer prompts for AI data cleaning tasks."""

    def __init__(self):
        """Initialize the prompt engineer."""
        self.base_prompts = self._load_base_prompts()

    def _load_base_prompts(self) -> Dict[str, str]:
        """Load base prompt templates."""
        return {
            "data_analysis": """You are a data cleaning expert. Analyze the following dataset characteristics and provide intelligent cleaning suggestions.

Dataset Profile:
- Rows: {row_count}
- Columns: {column_count}
- Missing data: {missing_percentage:.1f}%
- Duplicate rows: {duplicate_percentage:.1f}%
- Data types: {data_types}
- Memory usage: {memory_usage_mb:.1f} MB
- Has text columns: {has_text_columns}
- Has numeric columns: {has_numeric_columns}
- Has date columns: {has_date_columns}
- Has categorical columns: {has_categorical_columns}
- Quality score: {quality_score:.2f}

Available operations: {available_operations}

Provide 3-5 specific cleaning suggestions in JSON format:
{{
    "suggestions": [
        {{
            "operation": "operation_name",
            "library": "best_library",
            "parameters": {{"param1": "value1"}},
            "confidence": 0.9,
            "reasoning": "Why this operation is recommended",
            "estimated_impact": "What this will accomplish",
            "priority": 1
        }}
    ]
}}

Focus on the most impactful operations first. Be specific about parameters and reasoning.""",
            "library_selection": """You are a data cleaning library expert. Given a dataset and operation, recommend the best library to use.

Dataset characteristics:
- Rows: {row_count}
- Columns: {column_count}
- Data types: {data_types}
- Missing data: {missing_percentage:.1f}%

Operation: {operation}

Available libraries: {available_libraries}

Consider:
1. Performance for dataset size
2. Feature completeness for the operation
3. Memory efficiency
4. Ease of use

Respond with JSON:
{{
    "recommended_library": "library_name",
    "confidence": 0.9,
    "reasoning": "Why this library is best",
    "alternative_libraries": ["alt1", "alt2"]
}}""",
            "parameter_optimization": """You are a data cleaning parameter optimization expert. Given an operation and dataset, suggest optimal parameters.

Operation: {operation}
Library: {library}

Dataset characteristics:
- Rows: {row_count}
- Columns: {column_count}
- Missing data: {missing_percentage:.1f}%
- Data types: {data_types}

Current parameters: {current_parameters}

Suggest optimized parameters in JSON format:
{{
    "optimized_parameters": {{"param1": "value1"}},
    "confidence": 0.9,
    "reasoning": "Why these parameters are optimal",
    "expected_improvement": "What improvement to expect"
}}""",
            "explanation": """You are a data cleaning expert. Explain the following cleaning operation in simple terms.

Operation: {operation}
Library: {library}
Parameters: {parameters}

Dataset context:
- Rows: {row_count}
- Columns: {column_count}
- Missing data: {missing_percentage:.1f}%

Provide a clear, non-technical explanation of:
1. What this operation does
2. Why it's recommended for this dataset
3. What the user can expect
4. Any potential risks or considerations

Keep the explanation under 200 words and use simple language.""",
        }

    def create_data_analysis_prompt(
        self, profile: Dict[str, Any], available_operations: List[str]
    ) -> str:
        """Create prompt for data analysis and suggestion generation.

        Args:
            profile: Data profile dictionary.
            available_operations: List of available operations.

        Returns:
            Formatted prompt string.
        """
        return self.base_prompts["data_analysis"].format(
            row_count=profile.get("row_count", 0),
            column_count=profile.get("column_count", 0),
            missing_percentage=profile.get("missing_percentage", 0.0),
            duplicate_percentage=profile.get("duplicate_percentage", 0.0),
            data_types=profile.get("data_types", {}),
            memory_usage_mb=profile.get("memory_usage_mb", 0.0),
            has_text_columns=profile.get("has_text_columns", False),
            has_numeric_columns=profile.get("has_numeric_columns", False),
            has_date_columns=profile.get("has_date_columns", False),
            has_categorical_columns=profile.get("has_categorical_columns", False),
            quality_score=profile.get("quality_score", 0.0),
            available_operations=available_operations,
        )

    def create_library_selection_prompt(
        self, operation: str, profile: Dict[str, Any], available_libraries: List[str]
    ) -> str:
        """Create prompt for library selection.

        Args:
            operation: Operation to perform.
            profile: Data profile dictionary.
            available_libraries: List of available libraries.

        Returns:
            Formatted prompt string.
        """
        return self.base_prompts["library_selection"].format(
            operation=operation,
            row_count=profile.get("row_count", 0),
            column_count=profile.get("column_count", 0),
            data_types=profile.get("data_types", {}),
            missing_percentage=profile.get("missing_percentage", 0.0),
            available_libraries=available_libraries,
        )

    def create_parameter_optimization_prompt(
        self,
        operation: str,
        library: str,
        profile: Dict[str, Any],
        current_parameters: Dict[str, Any],
    ) -> str:
        """Create prompt for parameter optimization.

        Args:
            operation: Operation to perform.
            library: Library to use.
            profile: Data profile dictionary.
            current_parameters: Current parameters.

        Returns:
            Formatted prompt string.
        """
        return self.base_prompts["parameter_optimization"].format(
            operation=operation,
            library=library,
            row_count=profile.get("row_count", 0),
            column_count=profile.get("column_count", 0),
            missing_percentage=profile.get("missing_percentage", 0.0),
            data_types=profile.get("data_types", {}),
            current_parameters=current_parameters,
        )

    def create_explanation_prompt(
        self,
        operation: str,
        library: str,
        parameters: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> str:
        """Create prompt for operation explanation.

        Args:
            operation: Operation to explain.
            library: Library used.
            parameters: Operation parameters.
            profile: Data profile dictionary.

        Returns:
            Formatted prompt string.
        """
        return self.base_prompts["explanation"].format(
            operation=operation,
            library=library,
            parameters=parameters,
            row_count=profile.get("row_count", 0),
            column_count=profile.get("column_count", 0),
            missing_percentage=profile.get("missing_percentage", 0.0),
        )


class ResponseParser:
    """Parse AI responses into structured data."""

    def __init__(self):
        """Initialize the response parser."""
        self.json_patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"(\{.*\})",
        ]

    def parse_suggestions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response containing cleaning suggestions.

        Args:
            response: AI response string.

        Returns:
            List of suggestion dictionaries.
        """
        try:
            # Extract JSON from response
            json_str = self._extract_json(response)
            if not json_str:
                logger.warning("No JSON found in AI response")
                return []

            # Parse JSON
            data = json.loads(json_str)
            suggestions = data.get("suggestions", [])

            # Validate suggestions
            validated_suggestions = []
            for suggestion in suggestions:
                if self._validate_suggestion(suggestion):
                    validated_suggestions.append(suggestion)
                else:
                    logger.warning(f"Invalid suggestion format: {suggestion}")

            return validated_suggestions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse suggestions response: {e}")
            return []

    def parse_library_selection_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for library selection.

        Args:
            response: AI response string.

        Returns:
            Library selection dictionary.
        """
        try:
            json_str = self._extract_json(response)
            if not json_str:
                return {"recommended_library": None, "confidence": 0.0}

            data = json.loads(json_str)
            return {
                "recommended_library": data.get("recommended_library"),
                "confidence": data.get("confidence", 0.0),
                "reasoning": data.get("reasoning", ""),
                "alternative_libraries": data.get("alternative_libraries", []),
            }

        except Exception as e:
            logger.error(f"Failed to parse library selection response: {e}")
            return {"recommended_library": None, "confidence": 0.0}

    def parse_parameter_optimization_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for parameter optimization.

        Args:
            response: AI response string.

        Returns:
            Parameter optimization dictionary.
        """
        try:
            json_str = self._extract_json(response)
            if not json_str:
                return {"optimized_parameters": {}, "confidence": 0.0}

            data = json.loads(json_str)
            return {
                "optimized_parameters": data.get("optimized_parameters", {}),
                "confidence": data.get("confidence", 0.0),
                "reasoning": data.get("reasoning", ""),
                "expected_improvement": data.get("expected_improvement", ""),
            }

        except Exception as e:
            logger.error(f"Failed to parse parameter optimization response: {e}")
            return {"optimized_parameters": {}, "confidence": 0.0}

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON string from text.

        Args:
            text: Text containing JSON.

        Returns:
            JSON string or None if not found.
        """
        for pattern in self.json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Try to find JSON without code blocks
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        return None

    def _validate_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Validate suggestion format.

        Args:
            suggestion: Suggestion dictionary.

        Returns:
            True if suggestion is valid.
        """
        required_fields = [
            "operation",
            "library",
            "parameters",
            "confidence",
            "reasoning",
        ]
        return all(field in suggestion for field in required_fields)


class AIPromptTemplates:
    """Pre-defined prompt templates for common AI tasks."""

    @staticmethod
    def get_operation_explanation_template() -> str:
        """Get template for explaining operations."""
        return """Explain the data cleaning operation "{operation}" in simple terms.

What it does: {description}
When to use it: {use_cases}
What to expect: {expected_outcome}

Keep the explanation clear and non-technical."""

    @staticmethod
    def get_data_quality_assessment_template() -> str:
        """Get template for data quality assessment."""
        return """Assess the quality of this dataset and provide recommendations.

Dataset size: {rows} rows, {columns} columns
Missing data: {missing_pct}%
Duplicate rows: {duplicate_pct}%
Data types: {data_types}

Provide a quality score (0-100) and specific improvement recommendations."""

    @staticmethod
    def get_cleaning_workflow_template() -> str:
        """Get template for cleaning workflow generation."""
        return """Generate an optimal cleaning workflow for this dataset.

Dataset characteristics: {characteristics}
Available operations: {operations}
Constraints: {constraints}

Provide a step-by-step workflow with reasoning for each step."""

    @staticmethod
    def get_error_diagnosis_template() -> str:
        """Get template for error diagnosis."""
        return """Diagnose the issue with this data cleaning operation.

Operation: {operation}
Error: {error}
Dataset context: {context}

Provide:
1. Likely cause of the error
2. Suggested solution
3. Prevention tips for the future"""


class AICostEstimator:
    """Estimate costs for AI operations."""

    def __init__(self):
        """Initialize the cost estimator."""
        self.cost_rates = {
            # OpenAI Models
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1K tokens
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-4": {"input": 0.03, "output": 0.06},
            # Anthropic Models
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            # Local Models (free)
            "llama3.1:8b": {"input": 0.0, "output": 0.0},
            "llama3.1:70b": {"input": 0.0, "output": 0.0},
            "llama2": {"input": 0.0, "output": 0.0},  # Legacy support
        }

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for AI operation.

        Args:
            model: Model name.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        if model not in self.cost_rates:
            logger.warning(f"Unknown model for cost estimation: {model}")
            return 0.0

        rates = self.cost_rates[model]
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]

        return input_cost + output_cost

    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text.

        Args:
            text: Input text.

        Returns:
            Estimated token count.
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def get_cost_summary(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get cost summary for multiple operations.

        Args:
            operations: List of operation dictionaries.

        Returns:
            Cost summary dictionary.
        """
        total_cost = 0.0
        total_tokens = 0
        model_breakdown = {}

        for op in operations:
            model = op.get("model", "unknown")
            tokens = op.get("tokens_used", 0)
            cost = op.get("cost_usd", 0.0)

            total_cost += cost
            total_tokens += tokens

            if model not in model_breakdown:
                model_breakdown[model] = {"cost": 0.0, "tokens": 0}
            model_breakdown[model]["cost"] += cost
            model_breakdown[model]["tokens"] += tokens

        return {
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "model_breakdown": model_breakdown,
            "average_cost_per_operation": total_cost / max(len(operations), 1),
        }
