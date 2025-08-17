"""
Missingno wrapper for missing data visualization and analysis.
"""

import pandas as pd
from typing import List
import time
import logging
from .base import BaseWrapper

# Try to import missingno, but make it optional
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import missingno as msno

    MISSINGNO_AVAILABLE = True
except ImportError:
    MISSINGNO_AVAILABLE = False

logger = logging.getLogger(__name__)


class MissingnoWrapper(BaseWrapper):
    """Missingno-specific wrapper for missing data visualization and analysis."""

    def __init__(self):
        """Initialize Missingno wrapper."""
        if not MISSINGNO_AVAILABLE:
            raise ImportError(
                "Missingno is not available. Please install it with: pip install missingno"
            )

    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the wrapper can handle the operation.
        """
        supported_operations = [
            "missing_matrix",
            "missing_bar",
            "missing_heatmap",
            "missing_dendrogram",
            "missing_summary",
        ]
        return operation in supported_operations

    def _execute_operation(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute the specific operation on the DataFrame.

        Args:
            operation: Name of the operation to execute.
            df: Input DataFrame.
            **kwargs: Additional arguments for the operation.

        Returns:
            Processed DataFrame (for analysis operations, returns original DataFrame).
        """
        if df is None:
            raise TypeError("DataFrame cannot be None")

        if operation == "missing_matrix":
            return self._missing_matrix(df, **kwargs)
        elif operation == "missing_bar":
            return self._missing_bar(df, **kwargs)
        elif operation == "missing_heatmap":
            return self._missing_heatmap(df, **kwargs)
        elif operation == "missing_dendrogram":
            return self._missing_dendrogram(df, **kwargs)
        elif operation == "missing_summary":
            return self._missing_summary(df, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of supported operation names.
        """
        return [
            "missing_matrix",
            "missing_bar",
            "missing_heatmap",
            "missing_dendrogram",
            "missing_summary",
        ]

    def _missing_matrix(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Generate missing data matrix visualization.

        Args:
            df: Input DataFrame.
            **kwargs: Visualization specifications.

        Returns:
            Original DataFrame (visualization is saved to file).
        """
        figsize = kwargs.get("figsize", (10, 6))
        save_path = kwargs.get("save_path", "missing_matrix.png")

        # Ensure matplotlib backend is set
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Create missing matrix plot
        msno.matrix(df, figsize=figsize)

        # Save the plot
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Missing matrix saved to {save_path}")
        return df

    def _missing_bar(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Generate missing data bar chart.

        Args:
            df: Input DataFrame.
            **kwargs: Visualization specifications.

        Returns:
            Original DataFrame (visualization is saved to file).
        """
        figsize = kwargs.get("figsize", (10, 6))
        save_path = kwargs.get("save_path", "missing_bar.png")

        # Ensure matplotlib backend is set
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Create missing bar plot
        msno.bar(df, figsize=figsize)

        # Save the plot
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Missing bar chart saved to {save_path}")
        return df

    def _missing_heatmap(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Generate missing data correlation heatmap.

        Args:
            df: Input DataFrame.
            **kwargs: Visualization specifications.

        Returns:
            Original DataFrame (visualization is saved to file).
        """
        figsize = kwargs.get("figsize", (10, 8))
        save_path = kwargs.get("save_path", "missing_heatmap.png")
        cmap = kwargs.get("cmap", None)

        # Ensure matplotlib backend is set
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Create missing heatmap
        if cmap:
            msno.heatmap(df, figsize=figsize, cmap=cmap)
        else:
            msno.heatmap(df, figsize=figsize)

        # Save the plot
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Missing heatmap saved to {save_path}")
        return df

    def _missing_dendrogram(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Generate missing data dendrogram.

        Args:
            df: Input DataFrame.
            **kwargs: Visualization specifications.

        Returns:
            Original DataFrame (visualization is saved to file).
        """
        figsize = kwargs.get("figsize", (10, 8))
        save_path = kwargs.get("save_path", "missing_dendrogram.png")

        # Ensure matplotlib backend is set
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Create missing dendrogram
        msno.dendrogram(df, figsize=figsize)

        # Save the plot
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Missing dendrogram saved to {save_path}")
        return df

    def _missing_summary(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Generate missing data summary statistics.

        Args:
            df: Input DataFrame.
            **kwargs: Analysis specifications.

        Returns:
            Original DataFrame (summary is logged, not returned).
        """
        # Calculate missing data statistics
        missing_stats = df.isnull().sum()
        missing_percent = (missing_stats / len(df)) * 100

        summary_df = pd.DataFrame(
            {
                "Column": missing_stats.index,
                "Missing_Count": missing_stats.values,
                "Missing_Percent": missing_percent.values,
            }
        )

        # Sort by missing count
        summary_df = summary_df.sort_values("Missing_Count", ascending=False)

        # Filter to only show columns with missing values
        summary_df = summary_df[summary_df["Missing_Count"] > 0]

        logger.info(f"Missing data summary generated for {len(summary_df)} columns")
        logger.info(f"Missing data summary:\n{summary_df}")

        return df
