"""
Feature-Engine wrapper for advanced data cleaning operations.
"""

import pandas as pd
from typing import List
import time
import logging
from .base import BaseWrapper

# Try to import feature-engine, but make it optional
try:
    from feature_engine.imputation import (
        MeanMedianImputer,
        CategoricalImputer,
        RandomSampleImputer,
        EndTailImputer,
        AddMissingIndicator,
    )
    from feature_engine.encoding import (
        OneHotEncoder,
        OrdinalEncoder,
        MeanEncoder,
        RareLabelEncoder,
    )
    from feature_engine.outliers import OutlierTrimmer, Winsorizer
    from feature_engine.selection import (
        DropConstantFeatures,
        DropCorrelatedFeatures,
        DropDuplicateFeatures,
    )
    from feature_engine.transformation import LogTransformer, PowerTransformer

    FEATURE_ENGINE_AVAILABLE = True
except ImportError:
    FEATURE_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


class FeatureEngineWrapper(BaseWrapper):
    """Feature-Engine-specific wrapper for advanced data cleaning operations."""

    def __init__(self):
        """Initialize Feature-Engine wrapper."""
        if not FEATURE_ENGINE_AVAILABLE:
            raise ImportError(
                "Feature-Engine is not available. Please install it with: pip install feature-engine"
            )

    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the wrapper can handle the operation.
        """
        supported_operations = [
            "advanced_imputation",
            "categorical_encoding",
            "outlier_detection",
            "variable_selection",
            "data_transformation",
            "missing_indicator",
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

        if operation == "advanced_imputation":
            return self._advanced_imputation(df, **kwargs)
        elif operation == "categorical_encoding":
            return self._categorical_encoding(df, **kwargs)
        elif operation == "outlier_detection":
            return self._outlier_detection(df, **kwargs)
        elif operation == "variable_selection":
            return self._variable_selection(df, **kwargs)
        elif operation == "data_transformation":
            return self._data_transformation(df, **kwargs)
        elif operation == "missing_indicator":
            return self._missing_indicator(df, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of supported operation names.
        """
        return [
            "advanced_imputation",
            "categorical_encoding",
            "outlier_detection",
            "variable_selection",
            "data_transformation",
            "missing_indicator",
        ]

    def _advanced_imputation(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Perform advanced imputation using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Imputation specifications.

        Returns:
            DataFrame with imputed values.
        """
        method = kwargs.get("method", "mean")
        variables = kwargs.get("variables", None)
        random_state = kwargs.get("random_state", 42)

        result = df.copy()

        if method == "mean":
            imputer = MeanMedianImputer(imputation_method="mean", variables=variables)
        elif method == "median":
            imputer = MeanMedianImputer(imputation_method="median", variables=variables)
        elif method == "random":
            imputer = RandomSampleImputer(
                variables=variables, random_state=random_state
            )
        elif method == "end_tail":
            imputer = EndTailImputer(variables=variables)
        elif method == "categorical":
            imputer = CategoricalImputer(variables=variables)
        else:
            raise ValueError(f"Unknown imputation method: {method}")

        result = imputer.fit_transform(result)
        # Log the number of variables processed (handle case where variables_ might not exist)
        try:
            num_variables = (
                len(imputer.variables_) if hasattr(imputer, "variables_") else "unknown"
            )
            logger.info(f"Applied {method} imputation to {num_variables} variables")
        except (TypeError, AttributeError):
            logger.info(f"Applied {method} imputation")
        return result

    def _categorical_encoding(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Perform categorical encoding using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Encoding specifications.

        Returns:
            DataFrame with encoded categorical variables.
        """
        method = kwargs.get("method", "onehot")
        variables = kwargs.get("variables", None)
        drop_first = kwargs.get("drop_first", True)

        result = df.copy()

        if method == "onehot":
            encoder = OneHotEncoder(variables=variables, drop_last=drop_first)
        elif method == "ordinal":
            encoder = OrdinalEncoder(variables=variables)
        elif method == "mean":
            target_variable = kwargs.get("target_variable")
            if not target_variable:
                raise ValueError("target_variable is required for mean encoding")
            encoder = MeanEncoder(variables=variables)
            result = encoder.fit_transform(result, result[target_variable])
            return result
        elif method == "rare":
            tol = kwargs.get("tol", 0.05)
            n_categories = kwargs.get("n_categories", 10)
            encoder = RareLabelEncoder(
                variables=variables, tol=tol, n_categories=n_categories
            )
        else:
            raise ValueError(f"Unknown encoding method: {method}")

        result = encoder.fit_transform(result)
        # Log the number of variables processed (handle case where variables_ might not exist)
        try:
            num_variables = (
                len(encoder.variables_) if hasattr(encoder, "variables_") else "unknown"
            )
            logger.info(f"Applied {method} encoding to {num_variables} variables")
        except (TypeError, AttributeError):
            logger.info(f"Applied {method} encoding")
        return result

    def _outlier_detection(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Detect and handle outliers using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Outlier detection specifications.

        Returns:
            DataFrame with outliers handled.
        """
        method = kwargs.get("method", "iqr")
        variables = kwargs.get("variables", None)
        action = kwargs.get("action", "trim")  # 'trim' or 'winsorize'

        result = df.copy()

        if action == "trim":
            if method == "iqr":
                outlier_handler = OutlierTrimmer(
                    variables=variables, capping_method="iqr"
                )
            else:
                outlier_handler = OutlierTrimmer(
                    variables=variables, capping_method="gaussian"
                )
        elif action == "winsorize":
            outlier_handler = Winsorizer(variables=variables, capping_method=method)
        else:
            raise ValueError(f"Unknown action: {action}")

        result = outlier_handler.fit_transform(result)
        logger.info(f"Applied {method} outlier detection with {action} action")

        return result

    def _variable_selection(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Perform variable selection using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Variable selection specifications.

        Returns:
            DataFrame with selected variables.
        """
        method = kwargs.get("method", "constant")
        threshold = kwargs.get("threshold", 0.95)

        result = df.copy()

        if method == "constant":
            selector = DropConstantFeatures(variables=None, tol=1.0)
        elif method == "correlated":
            selector = DropCorrelatedFeatures(variables=None, threshold=threshold)
        elif method == "duplicate":
            selector = DropDuplicateFeatures(variables=None)
        else:
            raise ValueError(f"Unknown selection method: {method}")

        result = selector.fit_transform(result)
        logger.info(
            f"Applied {method} variable selection, kept {len(result.columns)} variables"
        )

        return result

    def _data_transformation(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Perform data transformation using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Transformation specifications.

        Returns:
            DataFrame with transformed variables.
        """
        method = kwargs.get("method", "log")
        variables = kwargs.get("variables", None)

        result = df.copy()

        if method == "log":
            transformer = LogTransformer(variables=variables)
        elif method == "power":
            transformer = PowerTransformer(variables=variables)
        else:
            raise ValueError(f"Unknown transformation method: {method}")

        result = transformer.fit_transform(result)
        # Log the number of variables processed (handle case where variables_ might not exist)
        try:
            num_variables = (
                len(transformer.variables_)
                if hasattr(transformer, "variables_")
                else "unknown"
            )
            logger.info(f"Applied {method} transformation to {num_variables} variables")
        except (TypeError, AttributeError):
            logger.info(f"Applied {method} transformation")
        return result

    def _missing_indicator(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Add missing value indicators using Feature-Engine.

        Args:
            df: Input DataFrame.
            **kwargs: Missing indicator specifications.

        Returns:
            DataFrame with missing indicators added.
        """
        variables = kwargs.get("variables", None)
        missing_only = kwargs.get("missing_only", True)

        result = df.copy()

        indicator = AddMissingIndicator(variables=variables, missing_only=missing_only)
        result = indicator.fit_transform(result)

        # Log the number of variables processed (handle case where variables_ might not exist)
        try:
            num_variables = (
                len(indicator.variables_)
                if hasattr(indicator, "variables_")
                else "unknown"
            )
            logger.info(f"Added missing indicators for {num_variables} variables")
        except (TypeError, AttributeError):
            logger.info("Added missing indicators")
        return result
