"""
PyJanitor wrapper for data cleaning operations.
"""

import pandas as pd
from typing import List
import time
import logging
from .base import BaseWrapper

# Try to import pyjanitor (janitor), but make it optional
try:
    import janitor as pj

    PYJANITOR_AVAILABLE = True
except ImportError:
    PYJANITOR_AVAILABLE = False
    pj = None

logger = logging.getLogger(__name__)


class PyJanitorWrapper(BaseWrapper):
    """PyJanitor-specific wrapper for data cleaning operations."""

    def __init__(self):
        """Initialize PyJanitor wrapper."""
        if not PYJANITOR_AVAILABLE:
            raise ImportError(
                "PyJanitor is not available. Please install it with: pip install pyjanitor"
            )

    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the wrapper can handle the operation.
        """
        supported_operations = [
            "clean_names",
            "remove_empty",
            "fill_empty",
            "remove_duplicates",
            "handle_missing",
            "remove_constant_columns",
            "remove_columns_with_nulls",
            "coalesce_columns",
        ]
        return operation in supported_operations

    def _execute_operation(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute the specific operation on the DataFrame.

        Args:
            operation: Name of the operation to execute.
            df: Input DataFrame.
            **kwargs: Additional arguments for the operation.

        Returns:
            Processed DataFrame.
        """
        if df is None:
            raise TypeError("DataFrame cannot be None")

        if operation == "clean_names":
            return self._clean_names(df, **kwargs)
        elif operation == "remove_empty":
            return self._remove_empty(df, **kwargs)
        elif operation == "fill_empty":
            return self._fill_empty(df, **kwargs)
        elif operation == "remove_duplicates":
            return self._remove_duplicates(df, **kwargs)
        elif operation == "handle_missing":
            return self._handle_missing(df, **kwargs)
        elif operation == "remove_constant_columns":
            return self._remove_constant_columns(df, **kwargs)
        elif operation == "remove_columns_with_nulls":
            return self._remove_columns_with_nulls(df, **kwargs)
        elif operation == "coalesce_columns":
            return self._coalesce_columns(df, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of operation names this wrapper supports.
        """
        return [
            "clean_names",
            "remove_empty",
            "fill_empty",
            "remove_duplicates",
            "handle_missing",
            "remove_constant_columns",
            "remove_columns_with_nulls",
            "coalesce_columns",
        ]

    def _clean_names(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Clean column names using PyJanitor's clean_names.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for clean_names.

        Returns:
            DataFrame with cleaned column names.
        """
        case_type = kwargs.get("case_type", kwargs.get("case", "snake"))
        remove_special = kwargs.get("remove_special", True)
        strip_underscores = kwargs.get("strip_underscores", True)

        return pj.clean_names(
            df,
            case_type=case_type,
            remove_special=remove_special,
            strip_underscores=strip_underscores,
        )

    def _remove_empty(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove empty rows and columns using PyJanitor.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for remove_empty.

        Returns:
            DataFrame with empty rows/columns removed.
        """
        rows = kwargs.get("rows", True)
        columns = kwargs.get("columns", True)

        result = df.copy()

        if rows:
            result = pj.remove_empty(result)

        if columns:
            result = pj.remove_empty(result, axis="columns")

        return result

    def _fill_empty(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Fill empty values using PyJanitor's fill_empty.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for fill_empty.

        Returns:
            DataFrame with empty values filled.
        """
        value = kwargs.get("value", "")
        columns = kwargs.get("columns", None)

        if columns:
            return pj.fill_empty(df, columns=columns, value=value)
        else:
            return pj.fill_empty(df, value=value)

    def _remove_duplicates(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove duplicate rows using pandas drop_duplicates.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for remove_duplicates.

        Returns:
            DataFrame with duplicates removed.
        """
        subset = kwargs.get("subset", None)
        keep = kwargs.get("keep", "first")

        return df.drop_duplicates(subset=subset, keep=keep)

    def _handle_missing(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Handle missing values using PyJanitor's methods.

        Args:
            df: Input DataFrame.
            **kwargs: Missing value handling specifications.

        Returns:
            DataFrame with missing values handled.
        """
        strategy = kwargs.get("strategy", "drop")
        threshold = kwargs.get("threshold", 0.5)
        columns = kwargs.get("columns", None)

        # Use pyjanitor's handle_missing method if available, otherwise fall back to pandas
        try:
            return pj.handle_missing(
                df, strategy=strategy, threshold=threshold, columns=columns
            )
        except AttributeError:
            # Fall back to pandas implementation
            result = df.copy()

            if strategy == "drop":
                if columns:
                    result = result.dropna(subset=columns)
                else:
                    result = result.dropna()
            elif strategy == "fill":
                value = kwargs.get("value", "")
                if columns:
                    result = result.fillna(subset=columns, value=value)
                else:
                    result = result.fillna(value=value)
            elif strategy == "threshold":
                if columns:
                    result = result.dropna(
                        subset=columns, thresh=int(len(columns) * threshold)
                    )
                else:
                    result = result.dropna(thresh=int(len(result.columns) * threshold))

            return result

    def _remove_constant_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove columns with constant values using PyJanitor.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for remove_constant_columns.

        Returns:
            DataFrame with constant columns removed.
        """
        columns = kwargs.get("columns", None)

        if columns:
            return pj.remove_constant_columns(df, columns=columns)
        else:
            return pj.remove_constant_columns(df)

    def _remove_columns_with_nulls(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove columns with null values using PyJanitor.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for remove_columns_with_nulls.

        Returns:
            DataFrame with columns containing nulls removed.
        """
        threshold = kwargs.get("threshold", 0.5)

        return pj.remove_columns_with_nulls(df, threshold=threshold)

    def _coalesce_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Coalesce columns using PyJanitor's coalesce_columns.

        Args:
            df: Input DataFrame.
            **kwargs: Column coalescing specifications.

        Returns:
            DataFrame with coalesced columns.
        """
        column_groups = kwargs.get("column_groups", {})
        columns = kwargs.get("columns", None)
        default_value = kwargs.get("default_value", "")

        # If columns is provided, create a simple column group
        if columns and not column_groups:
            if len(columns) >= 2:
                column_groups = {"coalesced": columns}

        if not column_groups:
            return df

        result = df.copy()
        for new_column, source_columns in column_groups.items():
            if all(col in result.columns for col in source_columns):
                result = pj.coalesce_columns(
                    result,
                    source_columns=source_columns,
                    target_column_name=new_column,
                    default_value=default_value,
                )

        return result
