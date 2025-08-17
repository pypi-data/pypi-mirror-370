"""
Pandas wrapper for data cleaning operations.
"""

import pandas as pd
import re
from typing import List
import time
import logging
from .base import BaseWrapper

logger = logging.getLogger(__name__)


class PandasWrapper(BaseWrapper):
    """Pandas-specific wrapper for data cleaning operations."""

    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the wrapper can handle the operation.
        """
        supported_operations = [
            "remove_duplicates",
            "drop_missing",
            "fill_missing",
            "convert_types",
            "rename_columns",
            "clean_text",
            "drop_columns",
            "select_columns",
            "fix_dates",
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
        if operation == "remove_duplicates":
            return self._remove_duplicates(df, **kwargs)
        elif operation == "drop_missing":
            return self._drop_missing(df, **kwargs)
        elif operation == "fill_missing":
            return self._fill_missing(df, **kwargs)
        elif operation == "convert_types":
            return self._convert_types(df, **kwargs)
        elif operation == "rename_columns":
            return self._rename_columns(df, **kwargs)
        elif operation == "clean_text":
            return self._clean_text(df, **kwargs)
        elif operation == "drop_columns":
            return self._drop_columns(df, **kwargs)
        elif operation == "select_columns":
            return self._select_columns(df, **kwargs)
        elif operation == "fix_dates":
            return self._fix_dates(df, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of operation names this wrapper supports.
        """
        return [
            "remove_duplicates",
            "drop_missing",
            "fill_missing",
            "convert_types",
            "rename_columns",
            "clean_text",
            "drop_columns",
            "select_columns",
            "fix_dates",
        ]

    def _remove_duplicates(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove duplicate rows from the DataFrame.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for drop_duplicates.

        Returns:
            DataFrame with duplicates removed.
        """
        subset = kwargs.get("subset", None)
        keep = kwargs.get("keep", "first")
        inplace = kwargs.get("inplace", False)

        if inplace:
            df.drop_duplicates(subset=subset, keep=keep, inplace=True)
            return df
        else:
            return df.drop_duplicates(subset=subset, keep=keep)

    def _drop_missing(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Remove rows with missing values.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for dropna.

        Returns:
            DataFrame with missing values dropped.
        """
        axis = kwargs.get("axis", 0)
        how = kwargs.get("how", "any")
        subset = kwargs.get("subset", None)
        inplace = kwargs.get("inplace", False)

        if inplace:
            df.dropna(axis=axis, how=how, subset=subset, inplace=True)
            return df
        else:
            return df.dropna(axis=axis, how=how, subset=subset)

    def _fill_missing(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Fill missing values with specified strategy.

        Args:
            df: Input DataFrame.
            **kwargs: Additional arguments for fillna.

        Returns:
            DataFrame with missing values filled.
        """
        method = kwargs.get("method", "ffill")
        value = kwargs.get("value", None)
        limit = kwargs.get("limit", None)
        inplace = kwargs.get("inplace", False)

        if inplace:
            if value is not None:
                df.fillna(value=value, limit=limit, inplace=True)
            else:
                if method == "ffill":
                    df.ffill(limit=limit, inplace=True)
                elif method == "bfill":
                    df.bfill(limit=limit, inplace=True)
            return df
        else:
            if value is not None:
                return df.fillna(value=value, limit=limit)
            else:
                if method == "ffill":
                    # Suppress FutureWarning for pandas downcasting
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", FutureWarning)
                        result = df.ffill(limit=limit)
                    return result.infer_objects(copy=False)
                elif method == "bfill":
                    # Suppress FutureWarning for pandas downcasting
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", FutureWarning)
                        result = df.bfill(limit=limit)
                    return result.infer_objects(copy=False)
                else:
                    return df.fillna(method=method, limit=limit)

    def _convert_types(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Convert data types of columns.

        Args:
            df: Input DataFrame.
            **kwargs: Type conversion specifications.

        Returns:
            DataFrame with converted data types.
        """
        dtype_mapping = kwargs.get("dtype_mapping", {})
        errors = kwargs.get("errors", "raise")

        if not dtype_mapping:
            return df

        result = df.copy()
        for column, dtype in dtype_mapping.items():
            if column in result.columns:
                try:
                    result[column] = result[column].astype(dtype, errors=errors)
                except Exception as e:
                    logger.warning(f"Could not convert column {column} to {dtype}: {e}")

        return result

    def _rename_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Rename DataFrame columns.

        Args:
            df: Input DataFrame.
            **kwargs: Column renaming specifications.

        Returns:
            DataFrame with renamed columns.
        """
        column_mapping = kwargs.get("column_mapping", {})
        inplace = kwargs.get("inplace", False)

        if not column_mapping:
            return df

        if inplace:
            df.rename(columns=column_mapping, inplace=True)
            return df
        else:
            return df.rename(columns=column_mapping)

    def _clean_text(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Clean text data in the DataFrame.

        Args:
            df: Input DataFrame.
            **kwargs: Text cleaning specifications.

        Returns:
            DataFrame with cleaned text.
        """
        columns = kwargs.get("columns", None)
        strip_whitespace = kwargs.get("strip_whitespace", True)
        lowercase = kwargs.get("lowercase", False)
        remove_special_chars = kwargs.get("remove_special_chars", False)

        result = df.copy()

        if columns is None:
            columns = result.select_dtypes(include=["object"]).columns

        for column in columns:
            if column in result.columns:
                if strip_whitespace:
                    result[column] = result[column].astype(str).str.strip()

                if lowercase:
                    result[column] = result[column].astype(str).str.lower()

                if remove_special_chars:
                    result[column] = (
                        result[column]
                        .astype(str)
                        .str.replace(r"[^\w\s]", "", regex=True)
                    )

        return result

    def _drop_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Drop specified columns from the DataFrame.

        Args:
            df: Input DataFrame.
            **kwargs: Column dropping specifications.

        Returns:
            DataFrame with specified columns dropped.
        """
        columns = kwargs.get("columns", [])
        inplace = kwargs.get("inplace", False)

        if not columns:
            return df

        if inplace:
            df.drop(columns=columns, inplace=True)
            return df
        else:
            return df.drop(columns=columns)

    def _select_columns(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Select specific columns from the DataFrame.

        Args:
            df: Input DataFrame.
            **kwargs: Column selection specifications.

        Returns:
            DataFrame with selected columns.
        """
        columns = kwargs.get("columns", [])

        if not columns:
            return df

        return df[columns]

    def _fix_dates(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Fix common date format issues in the DataFrame.

        Args:
            df: Input DataFrame.
            **kwargs: Date fixing specifications.

        Returns:
            DataFrame with fixed date formats.
        """
        import re

        columns = kwargs.get("columns", None)
        target_format = kwargs.get("target_format", "%Y-%m-%d")
        auto_detect = kwargs.get("auto_detect", True)

        result = df.copy()

        if columns is None:
            # Try to auto-detect date columns
            if auto_detect:
                date_patterns = [
                    r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY-MM-DD or YYYY/MM/DD
                    r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",  # MM-DD-YYYY or MM/DD/YYYY
                    r"\d{1,2}[-/]\d{1,2}[-/]\d{2}",  # MM-DD-YY or MM/DD/YY
                ]

                columns = []
                for col in result.columns:
                    if result[col].dtype == "object":
                        # Check if column contains date-like patterns
                        sample_values = result[col].dropna().astype(str).head(10)
                        for value in sample_values:
                            if any(
                                re.match(pattern, value.strip())
                                for pattern in date_patterns
                            ):
                                columns.append(col)
                                break
            else:
                return result

        if not columns:
            return result

        for column in columns:
            if column in result.columns:
                # Convert to string and clean
                result[column] = result[column].astype(str)

                # Fix common issues
                result[column] = result[column].apply(
                    lambda x: self._fix_single_date(x, target_format)
                )

                # Try to convert to datetime
                try:
                    result[column] = pd.to_datetime(result[column], errors="coerce")
                    logger.info(f"Successfully converted column '{column}' to datetime")
                except Exception as e:
                    logger.warning(
                        f"Could not convert column '{column}' to datetime: {e}"
                    )

        return result

    def _fix_single_date(self, date_str: str, target_format: str) -> str:
        """Fix a single date string.

        Args:
            date_str: Date string to fix.
            target_format: Target format for the date.

        Returns:
            Fixed date string.
        """
        if pd.isna(date_str) or date_str == "nan" or date_str == "":
            return date_str

        # Remove extra whitespace
        date_str = str(date_str).strip()

        # Fix common issues
        # 1. Remove extra spaces around dashes
        date_str = re.sub(r"\s*-\s*", "-", date_str)

        # 2. Fix specific patterns like '0d7' -> '07' (do this first)
        date_str = re.sub(r"0([a-zA-Z])(\d)", r"0\2", date_str)

        # 3. Fix other common typos
        date_str = re.sub(r"0([a-zA-Z])\d", r"0\1", date_str)
        date_str = re.sub(r"(\d)([a-zA-Z])\d", r"\g<1>0\2", date_str)

        # 4. Fix single digit months/days
        parts = date_str.split("-")
        if len(parts) == 3:
            year, month, day = parts
            # Ensure month and day are 2 digits
            if len(month) == 1:
                month = f"0{month}"
            if len(day) == 1:
                day = f"0{day}"
            date_str = f"{year}-{month}-{day}"

        # 5. Handle different separators
        if "/" in date_str:
            date_str = date_str.replace("/", "-")

        return date_str
