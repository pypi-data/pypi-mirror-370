"""
Base wrapper class for library integrations.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional


class BaseWrapper(ABC):
    """Base class for library wrappers."""

    @abstractmethod
    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the wrapper can handle the operation.
        """
        pass

    def execute(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Template method for operation execution.

        Args:
            operation: Name of the operation to execute.
            df: Input DataFrame.
            **kwargs: Additional arguments for the operation.

        Returns:
            Processed DataFrame.
        """
        if not self.can_handle(operation):
            raise ValueError(f"Operation '{operation}' not supported by {self.__class__.__name__}")

        import time
        import logging
        logger = logging.getLogger(__name__)

        start_time = time.time()
        logger.info(f"Executing {operation} with {self.__class__.__name__}")

        try:
            result = self._execute_operation(operation, df, **kwargs)

            execution_time = time.time() - start_time
            logger.info(f"Completed {operation} in {execution_time:.2f} seconds")
            return result

        except Exception as e:
            logger.error(f"Error executing {operation}: {str(e)}")
            raise

    @abstractmethod
    def _execute_operation(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute the specific operation on the DataFrame.

        Args:
            operation: Name of the operation to execute.
            df: Input DataFrame.
            **kwargs: Additional arguments for the operation.

        Returns:
            Processed DataFrame.
        """
        pass

    @abstractmethod
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of operation names this wrapper supports.
        """
        pass

    def get_operation_info(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific operation.

        Args:
            operation: Name of the operation.

        Returns:
            Dictionary with operation information or None if not supported.
        """
        if not self.can_handle(operation):
            return None

        return {
            "name": operation,
            "description": self._get_operation_description(operation),
            "parameters": self._get_operation_parameters(operation),
            "wrapper": self.__class__.__name__,
        }

    def _get_operation_description(self, operation: str) -> str:
        """Get description of an operation.

        Args:
            operation: Name of the operation.

        Returns:
            Description of the operation.
        """
        descriptions = {
            "remove_duplicates": "Remove duplicate rows from the DataFrame",
            "drop_missing": "Remove rows with missing values",
            "fill_missing": "Fill missing values with specified strategy",
            "convert_types": "Convert data types of columns",
            "rename_columns": "Rename DataFrame columns",
            "clean_names": "Clean column names (remove special chars, normalize)",
            "remove_empty": "Remove empty rows and columns",
            "handle_missing": "Handle missing values with various strategies",
        }
        return descriptions.get(operation, f"Perform {operation} operation")

    def _get_operation_parameters(self, operation: str) -> Dict[str, Any]:
        """Get parameters for an operation.

        Args:
            operation: Name of the operation.

        Returns:
            Dictionary of parameter information.
        """
        # Default parameters for common operations
        default_params = {
            "remove_duplicates": {
                "subset": "Columns to consider for duplicates (default: all)",
                "keep": "Which duplicates to keep: first, last, or False (default: first)",
            },
            "drop_missing": {
                "axis": "Axis to drop on: 0 for rows, 1 for columns (default: 0)",
                "how": "How to drop: any or all (default: any)",
                "subset": "Columns to consider for missing values",
            },
            "fill_missing": {
                "method": "Method to use: ffill, bfill, or value (default: ffill)",
                "value": "Value to fill with (if method is value)",
                "limit": "Maximum number of consecutive fills",
            },
            "convert_types": {
                "columns": "Dictionary mapping column names to target types",
                "infer_types": "Whether to automatically infer types (default: True)",
            },
            "rename_columns": {
                "columns": "Dictionary mapping old names to new names",
                "inplace": "Whether to modify in place (default: False)",
            },
        }
        return default_params.get(operation, {})

    def validate_operation(self, operation: str) -> None:
        """Validate that an operation is supported.

        Args:
            operation: Name of the operation to validate.

        Raises:
            ValueError: If operation is not supported.
        """
        if not self.can_handle(operation):
            supported = ", ".join(self.get_supported_operations())
            raise ValueError(
                f"Operation '{operation}' not supported by {self.__class__.__name__}. "
                f"Supported operations: {supported}"
            )

    def get_performance_estimate(
        self, operation: str, df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get performance estimate for an operation.

        Args:
            operation: Name of the operation.
            df: Input DataFrame.

        Returns:
            Dictionary with performance estimates.
        """
        if not self.can_handle(operation):
            return {"error": f"Operation {operation} not supported"}

        # Basic performance estimates based on DataFrame size
        rows, cols = df.shape
        total_cells = rows * cols

        # Rough estimates (these would be refined with actual benchmarking)
        estimates = {
            "remove_duplicates": {
                "time_estimate": f"{total_cells * 0.0001:.2f}s",
                "memory_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB",
                "complexity": "O(n log n)",
            },
            "drop_missing": {
                "time_estimate": f"{total_cells * 0.00005:.2f}s",
                "memory_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB",
                "complexity": "O(n)",
            },
            "fill_missing": {
                "time_estimate": f"{total_cells * 0.0001:.2f}s",
                "memory_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB",
                "complexity": "O(n)",
            },
            "convert_types": {
                "time_estimate": f"{cols * 0.01:.2f}s",
                "memory_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB",
                "complexity": "O(n)",
            },
        }

        return estimates.get(
            operation,
            {
                "time_estimate": "Unknown",
                "memory_estimate": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}MB",
                "complexity": "Unknown",
            },
        )
