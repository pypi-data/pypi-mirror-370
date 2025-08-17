"""
Library manager for orchestrating data cleaning operations.
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import time
import logging
from ..wrappers.base import BaseWrapper
from ..wrappers.pandas_wrapper import PandasWrapper
from .config import Config

# Try to import AI components, but make them optional
try:
    from .ai_agent import AIAgent, DataProfile
    from .llm_providers import LLMProviderManager
    from .ai_utils import PromptEngineer, ResponseParser

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIAgent = None
    DataProfile = None
    LLMProviderManager = None
    PromptEngineer = None
    ResponseParser = None

# Try to import PyJanitorWrapper, but make it optional
try:
    from ..wrappers.pyjanitor_wrapper import PyJanitorWrapper

    PYJANITOR_AVAILABLE = True
except ImportError:
    PYJANITOR_AVAILABLE = False
    PyJanitorWrapper = None

# Try to import FeatureEngineWrapper, but make it optional
try:
    from ..wrappers.feature_engine_wrapper import FeatureEngineWrapper

    FEATURE_ENGINE_AVAILABLE = True
except ImportError:
    FEATURE_ENGINE_AVAILABLE = False
    FeatureEngineWrapper = None

# Try to import MissingnoWrapper, but make it optional
try:
    from ..wrappers.missingno_wrapper import MissingnoWrapper

    MISSINGNO_AVAILABLE = True
except ImportError:
    MISSINGNO_AVAILABLE = False
    MissingnoWrapper = None

# Try to import DedupeWrapper, but make it optional
try:
    from ..wrappers.dedupe_wrapper import DedupeWrapper

    DEDUPE_AVAILABLE = True
except ImportError:
    DEDUPE_AVAILABLE = False
    DedupeWrapper = None

logger = logging.getLogger(__name__)


class LibraryManager:
    """Manages library wrappers and orchestrates data cleaning operations."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the library manager.

        Args:
            config: Configuration object for the library manager.
        """
        self.config = config or Config()

        # Initialize feature gate
        from ..feature_gate import FeatureGate

        self.feature_gate = FeatureGate(self.config.package_version)

        self.wrappers = self._initialize_wrappers()
        self.performance_cache = {}
        self.operation_history = []

        # Initialize AI components if available and enabled
        self.ai_agent = None
        self.llm_provider_manager = None
        self.prompt_engineer = None
        self.response_parser = None

        if (
            AI_AVAILABLE
            and self.config.ai_enabled
            and self.feature_gate.is_feature_available("ai_agent")
        ):
            self._initialize_ai_components()

    def _initialize_wrappers(self) -> Dict[str, BaseWrapper]:
        """Initialize available wrappers.

        Returns:
            Dictionary of wrapper name to wrapper instance.
        """
        wrappers = {}

        # Always add PandasWrapper as it's the core dependency
        try:
            wrappers["pandas"] = PandasWrapper()
            logger.info("PandasWrapper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PandasWrapper: {e}")
            raise RuntimeError("PandasWrapper is required but failed to initialize")

        # Add PyJanitorWrapper if available and feature is enabled
        if (
            PYJANITOR_AVAILABLE
            and PyJanitorWrapper is not None
            and self.feature_gate.is_feature_available("pyjanitor_wrapper")
        ):
            try:
                wrappers["pyjanitor"] = PyJanitorWrapper()
                logger.info("PyJanitorWrapper initialized successfully")
            except ImportError as e:
                logger.debug(f"PyJanitor not available: {e}")
            except Exception as e:
                logger.debug(f"Failed to initialize PyJanitorWrapper: {e}")
        else:
            logger.debug(
                "PyJanitor not available or feature disabled, PyJanitorWrapper will not be used"
            )

        # Add FeatureEngineWrapper if available and feature is enabled
        if (
            FEATURE_ENGINE_AVAILABLE
            and FeatureEngineWrapper is not None
            and self.feature_gate.is_feature_available("feature_engine_wrapper")
        ):
            try:
                wrappers["feature_engine"] = FeatureEngineWrapper()
                logger.info("FeatureEngineWrapper initialized successfully")
            except ImportError as e:
                logger.debug(f"Feature-Engine not available: {e}")
            except Exception as e:
                logger.debug(f"Failed to initialize FeatureEngineWrapper: {e}")
        else:
            logger.debug(
                "Feature-Engine not available or feature disabled, FeatureEngineWrapper will not be used"
            )

        # Add MissingnoWrapper if available and feature is enabled
        if (
            MISSINGNO_AVAILABLE
            and MissingnoWrapper is not None
            and self.feature_gate.is_feature_available("missingno_wrapper")
        ):
            try:
                wrappers["missingno"] = MissingnoWrapper()
                logger.info("MissingnoWrapper initialized successfully")
            except ImportError as e:
                logger.debug(f"Missingno not available: {e}")
            except Exception as e:
                logger.debug(f"Failed to initialize MissingnoWrapper: {e}")
        else:
            logger.debug(
                "Missingno not available or feature disabled, MissingnoWrapper will not be used"
            )

        # Add DedupeWrapper if available and feature is enabled
        if (
            DEDUPE_AVAILABLE
            and DedupeWrapper is not None
            and self.feature_gate.is_feature_available("dedupe_wrapper")
        ):
            try:
                wrappers["dedupe"] = DedupeWrapper()
                logger.info("DedupeWrapper initialized successfully")
            except ImportError as e:
                logger.debug(f"Dedupe not available: {e}")
            except Exception as e:
                logger.debug(f"Failed to initialize DedupeWrapper: {e}")
        else:
            logger.debug(
                "Dedupe not available or feature disabled, DedupeWrapper will not be used"
            )

        return wrappers

    def get_available_wrappers(self) -> List[str]:
        """Get list of available wrappers for the current version.

        Returns:
            List of available wrapper names.
        """
        return list(self.wrappers.keys())

    def is_wrapper_available(self, wrapper_name: str) -> bool:
        """Check if a specific wrapper is available.

        Args:
            wrapper_name: Name of the wrapper to check.

        Returns:
            True if the wrapper is available, False otherwise.
        """
        return wrapper_name in self.wrappers

    def _initialize_ai_components(self) -> None:
        """Initialize AI components for intelligent library selection."""
        try:
            # Initialize AI agent
            self.ai_agent = AIAgent(self.config)
            logger.info("AI agent initialized successfully")

            # Initialize LLM provider manager
            config_dict = {
                "default_llm_provider": self.config.default_llm_provider,
                "ai_api_keys": self.config.ai_api_keys,
                "ai_openai_model": self.config.ai_openai_model,
                "ai_anthropic_model": self.config.ai_anthropic_model,
                "ai_local_model": self.config.ai_local_model,
            }
            self.llm_provider_manager = LLMProviderManager(config_dict)
            logger.info("LLM provider manager initialized successfully")

            # Initialize prompt engineer and response parser
            self.prompt_engineer = PromptEngineer()
            self.response_parser = ResponseParser()
            logger.info("AI utilities initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize AI components: {e}")
            self.ai_agent = None
            self.llm_provider_manager = None
            self.prompt_engineer = None
            self.response_parser = None

    def register_wrapper(self, name: str, wrapper: BaseWrapper) -> None:
        """Register a new wrapper.

        Args:
            name: Name of the wrapper.
            wrapper: Wrapper instance to register.
        """
        if not isinstance(wrapper, BaseWrapper):
            raise ValueError("Wrapper must inherit from BaseWrapper")

        self.wrappers[name] = wrapper
        logger.info(f"Registered wrapper: {name}")

    def get_best_wrapper(self, operation: str, df: pd.DataFrame) -> BaseWrapper:
        """Get the best wrapper for a given operation.

        Args:
            operation: Name of the operation to perform.
            df: DataFrame to operate on.

        Returns:
            Best wrapper for the operation.

        Raises:
            ValueError: If no wrapper can handle the operation.
        """
        available_wrappers = []

        for name, wrapper in self.wrappers.items():
            if wrapper.can_handle(operation):
                available_wrappers.append((name, wrapper))

        if not available_wrappers:
            # Check if this is a Pro feature and show upgrade prompt
            operation_category = self.feature_gate.get_operation_category(operation)
            if operation_category == "pro":
                upgrade_message = self.feature_gate.get_operation_upgrade_message(operation)
                raise ValueError(upgrade_message)
            else:
                raise ValueError(f"No wrapper found for operation: {operation}")

        # If only one wrapper available, use it
        if len(available_wrappers) == 1:
            return available_wrappers[0][1]

        # Use AI-powered selection if available
        if self.ai_agent and self.config.ai_enabled:
            return self._select_best_wrapper_ai(operation, df, available_wrappers)

        # Fallback to performance-based selection
        return self._select_best_wrapper(operation, df, available_wrappers)

    def _select_best_wrapper(
        self,
        operation: str,
        df: pd.DataFrame,
        available_wrappers: List[Tuple[str, BaseWrapper]],
    ) -> BaseWrapper:
        """Select the best wrapper based on performance and preferences.

        Args:
            operation: Name of the operation.
            df: DataFrame to operate on.
            available_wrappers: List of available wrappers.

        Returns:
            Best wrapper for the operation.
        """
        # Check performance cache first
        cache_key = f"{operation}_{len(df)}"
        if cache_key in self.performance_cache:
            best_wrapper_name = self.performance_cache[cache_key]
            for name, wrapper in available_wrappers:
                if name == best_wrapper_name:
                    return wrapper

        # Benchmark wrappers if not cached
        best_wrapper = None
        best_time = float("inf")

        for name, wrapper in available_wrappers:
            try:
                start_time = time.time()
                # Use a small sample for benchmarking
                sample_df = df.head(1000) if len(df) > 1000 else df
                wrapper.execute(operation, sample_df)
                execution_time = time.time() - start_time

                if execution_time < best_time:
                    best_time = execution_time
                    best_wrapper = wrapper

                logger.debug(f"Benchmark {name}: {execution_time:.4f}s")

            except Exception as e:
                logger.warning(f"Benchmark failed for {name}: {e}")

        if best_wrapper is None:
            # Fallback to first available wrapper
            best_wrapper = available_wrappers[0][1]

        # Cache the result
        self.performance_cache[cache_key] = best_wrapper.__class__.__name__.lower()

        return best_wrapper

    def _select_best_wrapper_ai(
        self,
        operation: str,
        df: pd.DataFrame,
        available_wrappers: List[Tuple[str, BaseWrapper]],
    ) -> BaseWrapper:
        """Select the best wrapper using AI-powered analysis.

        Args:
            operation: Name of the operation.
            df: DataFrame to operate on.
            available_wrappers: List of available wrappers.

        Returns:
            Best wrapper for the operation.
        """
        try:
            # Get available library names
            available_libraries = [name for name, _ in available_wrappers]

            # Use AI to select best library
            recommended_library = self.ai_agent.get_best_library_for_operation(
                operation, df, available_libraries
            )

            # Find the wrapper for the recommended library
            for name, wrapper in available_wrappers:
                if name == recommended_library:
                    logger.info(f"AI selected {name} for {operation}")
                    return wrapper

            # Fallback to first available wrapper if AI recommendation not found
            logger.warning(
                f"AI recommended {recommended_library} but it's not available, using fallback"
            )
            return available_wrappers[0][1]

        except Exception as e:
            logger.warning(f"AI-powered wrapper selection failed: {e}, using fallback")
            return self._select_best_wrapper(operation, df, available_wrappers)

    def execute_operation(
        self, operation: str, df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        """Execute an operation using the best available wrapper.

        Args:
            operation: Name of the operation to execute.
            df: DataFrame to operate on.
            **kwargs: Additional arguments for the operation.

        Returns:
            Processed DataFrame.
        """
        start_time = time.time()

        # Get the best wrapper for this operation
        wrapper = self.get_best_wrapper(operation, df)

        # Execute the operation
        try:
            result = wrapper.execute(operation, df, **kwargs)

            # Record operation history
            execution_time = time.time() - start_time
            self.operation_history.append(
                {
                    "operation": operation,
                    "wrapper": wrapper.__class__.__name__,
                    "execution_time": execution_time,
                    "input_rows": len(df),
                    "output_rows": len(result),
                    "success": True,
                }
            )

            logger.info(
                f"Executed {operation} with {wrapper.__class__.__name__} "
                f"in {execution_time:.2f}s"
            )

            return result

        except Exception as e:
            # Record failed operation
            execution_time = time.time() - start_time
            self.operation_history.append(
                {
                    "operation": operation,
                    "wrapper": wrapper.__class__.__name__,
                    "execution_time": execution_time,
                    "input_rows": len(df),
                    "output_rows": 0,
                    "success": False,
                    "error": str(e),
                }
            )

            logger.error(f"Failed to execute {operation}: {e}")
            raise

    def benchmark_operation(
        self, operation: str, df: pd.DataFrame, **kwargs
    ) -> Dict[str, Any]:
        """Benchmark all available wrappers for an operation.

        Args:
            operation: Name of the operation to benchmark.
            df: DataFrame to operate on.
            **kwargs: Additional arguments for the operation.

        Returns:
            Dictionary with benchmark results.
        """
        results = {}

        for name, wrapper in self.wrappers.items():
            if not wrapper.can_handle(operation):
                continue

            try:
                start_time = time.time()
                sample_df = df.head(1000) if len(df) > 1000 else df
                wrapper.execute(operation, sample_df, **kwargs)
                execution_time = time.time() - start_time

                results[name] = {
                    "execution_time": execution_time,
                    "success": True,
                    "error": None,
                }

            except Exception as e:
                results[name] = {
                    "execution_time": None,
                    "success": False,
                    "error": str(e),
                }

        return results

    def get_available_operations(self) -> List[str]:
        """Get all available operations across all wrappers.

        Returns:
            List of all available operation names.
        """
        operations = set()

        for wrapper in self.wrappers.values():
            operations.update(wrapper.get_supported_operations())

        return sorted(list(operations))

    def get_operation_info(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific operation.

        Args:
            operation: Name of the operation.

        Returns:
            Dictionary with operation information or None if not supported.
        """
        for wrapper in self.wrappers.values():
            info = wrapper.get_operation_info(operation)
            if info:
                return info

        return None

    def get_wrapper_info(self) -> Dict[str, Any]:
        """Get information about all available wrappers.

        Returns:
            Dictionary with wrapper information.
        """
        info = {}

        for name, wrapper in self.wrappers.items():
            info[name] = {
                "class": wrapper.__class__.__name__,
                "supported_operations": wrapper.get_supported_operations(),
                "available": True,
            }

        return info

    def get_ai_suggestions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get AI-powered cleaning suggestions for the dataset.

        Args:
            df: DataFrame to analyze.

        Returns:
            List of cleaning suggestions.
        """
        if not self.ai_agent or not self.config.ai_enabled:
            return []

        try:
            # Get available operations
            available_operations = self.get_available_operations()

            # Get AI suggestions
            suggestions = self.ai_agent.generate_suggestions(df, available_operations)

            # Convert to dictionary format for easier handling
            suggestion_dicts = []
            for suggestion in suggestions:
                suggestion_dicts.append(
                    {
                        "operation": suggestion.operation,
                        "library": suggestion.library,
                        "parameters": suggestion.parameters,
                        "confidence": suggestion.confidence,
                        "reasoning": suggestion.reasoning,
                        "estimated_impact": suggestion.estimated_impact,
                        "priority": suggestion.priority,
                    }
                )

            return suggestion_dicts

        except Exception as e:
            logger.warning(f"Failed to get AI suggestions: {e}")
            return []

    def get_ai_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get AI-powered data analysis.

        Args:
            df: DataFrame to analyze.

        Returns:
            Dictionary with AI analysis results.
        """
        if not self.ai_agent or not self.config.ai_enabled:
            return {}

        try:
            # Get data profile
            profile = self.ai_agent.analyze_data(df)

            # Get learning summary if available
            learning_summary = self.ai_agent.get_learning_summary()

            return {
                "data_profile": {
                    "row_count": profile.row_count,
                    "column_count": profile.column_count,
                    "missing_percentage": profile.missing_percentage,
                    "duplicate_percentage": profile.duplicate_percentage,
                    "memory_usage_mb": profile.memory_usage_mb,
                    "quality_score": profile.quality_score,
                    "data_types": profile.data_types,
                    "has_text_columns": profile.has_text_columns,
                    "has_numeric_columns": profile.has_numeric_columns,
                    "has_date_columns": profile.has_date_columns,
                    "has_categorical_columns": profile.has_categorical_columns,
                },
                "learning_summary": learning_summary,
                "ai_enabled": True,
            }

        except Exception as e:
            logger.warning(f"Failed to get AI analysis: {e}")
            return {"ai_enabled": False, "error": str(e)}

    def record_ai_feedback(
        self,
        operation: str,
        library: str,
        success: bool,
        user_feedback: Optional[str] = None,
    ) -> None:
        """Record feedback for AI learning.

        Args:
            operation: Operation that was performed.
            library: Library that was used.
            success: Whether the operation was successful.
            user_feedback: Optional user feedback.
        """
        if not self.ai_agent or not self.config.ai_learning_enabled:
            return

        try:
            # Create a mock suggestion for feedback recording
            from .ai_agent import CleaningSuggestion

            suggestion = CleaningSuggestion(
                operation=operation,
                library=library,
                parameters={},
                confidence=1.0,
                reasoning="User feedback",
                estimated_impact="",
                priority=1,
            )

            self.ai_agent.record_feedback(suggestion, success, user_feedback)
            logger.debug(f"Recorded AI feedback for {operation} with {library}")

        except Exception as e:
            logger.warning(f"Failed to record AI feedback: {e}")

    def is_ai_available(self) -> bool:
        """Check if AI features are available.

        Returns:
            True if AI is available and enabled.
        """
        return AI_AVAILABLE and self.config.ai_enabled and self.ai_agent is not None

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of recent operations.

        Returns:
            Dictionary with performance statistics.
        """
        if not self.operation_history:
            return {"total_operations": 0}

        successful_ops = [op for op in self.operation_history if op["success"]]
        failed_ops = [op for op in self.operation_history if not op["success"]]

        summary = {
            "total_operations": len(self.operation_history),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(self.operation_history)
            if self.operation_history
            else 0,
            "average_execution_time": sum(op["execution_time"] for op in successful_ops)
            / len(successful_ops)
            if successful_ops
            else 0,
            "total_rows_processed": sum(op["input_rows"] for op in successful_ops),
            "recent_operations": self.operation_history[-10:],  # Last 10 operations
        }

        return summary

    def clear_performance_cache(self) -> None:
        """Clear the performance cache."""
        self.performance_cache.clear()
        logger.info("Performance cache cleared")

    def reset_operation_history(self) -> None:
        """Reset the operation history."""
        self.operation_history.clear()
        logger.info("Operation history reset")
