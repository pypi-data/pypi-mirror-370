"""
Dedupe wrapper for CSV Data Cleaner.
Provides ML-based deduplication using the Dedupe library.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import os
from dataclasses import dataclass

from .base import BaseWrapper

logger = logging.getLogger(__name__)

# Conditional import for dedupe
try:
    import dedupe
    from dedupe import StaticDedupe, Dedupe

    DEDUPE_AVAILABLE = True
    logger.info("Dedupe library is available")
except ImportError:
    DEDUPE_AVAILABLE = False
    logger.warning("Dedupe library is not available. Install with: pip install dedupe")


@dataclass
class DedupeConfig:
    """Configuration for dedupe operations."""

    fields: List[Any]  # List of dedupe variable objects (e.g., dedupe.variables.String)
    training_file: Optional[str] = None
    settings_file: Optional[str] = None
    threshold: float = 0.5
    sample_size: int = 1000
    blocked_proportion: float = 0.9


class DedupeWrapper(BaseWrapper):
    """Wrapper for Dedupe library functionality."""

    def __init__(self):
        """Initialize the dedupe wrapper."""
        if not DEDUPE_AVAILABLE:
            raise ImportError(
                "Dedupe library is not available. Install with: pip install dedupe"
            )

        self.dedupe_model = None
        self.config = None
        self.is_trained = False

        logger.info("Initialized DedupeWrapper")

    def configure(self, config: DedupeConfig) -> None:
        """Configure the dedupe model.

        Args:
            config: Dedupe configuration.
        """
        self.config = config

        # Initialize dedupe model
        if config.settings_file and os.path.exists(config.settings_file):
            # Load existing settings
            with open(config.settings_file, "rb") as f:
                self.dedupe_model = StaticDedupe(f)
            self.is_trained = True
            logger.info(f"Loaded existing dedupe model from {config.settings_file}")
        else:
            # Create new model with dedupe 3.0 API
            self.dedupe_model = Dedupe(config.fields)
            self.is_trained = False
            logger.info("Created new dedupe model with dedupe 3.0 API")

    def train(self, df: pd.DataFrame, interactive: bool = False) -> None:
        """Train the dedupe model using dedupe 3.0 API.

        Args:
            df: DataFrame to train on.
            interactive: Whether to use interactive training.
        """
        if not self.dedupe_model:
            raise ValueError("Dedupe model not configured. Call configure() first.")

        logger.info("Starting dedupe training with dedupe 3.0 API")

        # Convert DataFrame to dedupe format
        data = self._dataframe_to_dedupe_format(df)

        if interactive:
            # Interactive training with dedupe 3.0
            logger.info("Starting interactive training")
            try:
                # Use the new dedupe 3.0 prepare_training method
                self.dedupe_model.prepare_training(data, sample_size=self.config.sample_size)

                # Start interactive labeling
                dedupe.console_label(self.dedupe_model)

                # Train the model
                self.dedupe_model.train()
                logger.info("Interactive training completed successfully")

            except Exception as e:
                logger.error(f"Error during interactive training: {e}")
                raise ValueError(f"Interactive training failed: {e}")

        else:
            # Non-interactive training (requires training file)
            if not self.config.training_file or not os.path.exists(
                self.config.training_file
            ):
                raise ValueError("Training file required for non-interactive training")

            logger.info(f"Loading training data from {self.config.training_file}")
            try:
                with open(self.config.training_file, "r") as f:
                    training_data = json.load(f)

                # Use dedupe 3.0 API for non-interactive training
                self.dedupe_model.prepare_training(data, sample_size=self.config.sample_size)
                self.dedupe_model.mark_pairs(training_data)
                self.dedupe_model.train()
                logger.info("Non-interactive training completed successfully")

            except Exception as e:
                logger.error(f"Error during non-interactive training: {e}")
                raise ValueError(f"Non-interactive training failed: {e}")

        self.is_trained = True
        logger.info("Dedupe training completed")

    def predict(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[Tuple[int, int, float]]]:
        """Predict duplicates in the DataFrame using dedupe 3.0 API.

        Args:
            df: DataFrame to deduplicate.

        Returns:
            Tuple of (deduplicated_dataframe, duplicate_pairs).
        """
        if not self.dedupe_model or not self.is_trained:
            raise ValueError("Dedupe model not trained. Call train() first.")

        logger.info("Starting duplicate prediction with dedupe 3.0 API")

        # Convert DataFrame to dedupe format
        data = self._dataframe_to_dedupe_format(df)

        try:
            # Use dedupe 3.0 API for prediction
            # Get candidate pairs
            candidate_pairs = self.dedupe_model.candidate_pairs(data)

            # Score the pairs
            scores = self.dedupe_model.score(candidate_pairs)

            # Filter by threshold
            thresholded_pairs = [
                (pair[0], pair[1], score)
                for pair, score in zip(candidate_pairs, scores)
                if score > self.config.threshold
            ]

            logger.info(
                f"Found {len(thresholded_pairs)} duplicate pairs above threshold {self.config.threshold}"
            )

            # Remove duplicates from DataFrame
            deduplicated_df = self._remove_duplicates(df, thresholded_pairs)

            return deduplicated_df, thresholded_pairs

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise ValueError(f"Prediction failed: {e}")

    def save_settings(self, settings_file: str) -> None:
        """Save the trained model settings.

        Args:
            settings_file: Path to save settings file.
        """
        if not self.dedupe_model or not self.is_trained:
            raise ValueError("No trained model to save")

        with open(settings_file, "wb") as f:
            self.dedupe_model.write_settings(f)

        logger.info(f"Saved dedupe settings to {settings_file}")

    def _dataframe_to_dedupe_format(
        self, df: pd.DataFrame
    ) -> Dict[str, Dict[str, Any]]:
        """Convert DataFrame to dedupe format.

        Args:
            df: DataFrame to convert.

        Returns:
            Data in dedupe format.
        """
        data = {}
        for idx, row in df.iterrows():
            record = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    record[col] = ""
                else:
                    record[col] = str(value)
            data[str(idx)] = record

        return data

    def _remove_duplicates(
        self, df: pd.DataFrame, duplicate_pairs: List[Tuple[int, int, float]]
    ) -> pd.DataFrame:
        """Remove duplicates from DataFrame based on duplicate pairs.

        Args:
            df: Original DataFrame.
            duplicate_pairs: List of duplicate pairs with scores.

        Returns:
            DataFrame with duplicates removed.
        """
        if not duplicate_pairs:
            return df.copy()

        # Create a set of indices to remove
        indices_to_remove = set()

        for idx1, idx2, score in duplicate_pairs:
            # Keep the first occurrence, remove the second
            indices_to_remove.add(idx2)

        # Remove duplicates
        deduplicated_df = df.drop(indices_to_remove).reset_index(drop=True)

        logger.info(f"Removed {len(indices_to_remove)} duplicate records")
        return deduplicated_df

    def get_duplicate_statistics(
        self, duplicate_pairs: List[Tuple[int, int, float]]
    ) -> Dict[str, Any]:
        """Get statistics about duplicate pairs.

        Args:
            duplicate_pairs: List of duplicate pairs with scores.

        Returns:
            Dictionary with duplicate statistics.
        """
        if not duplicate_pairs:
            return {
                "total_pairs": 0,
                "average_score": 0.0,
                "score_distribution": {},
                "duplicate_count": 0,
            }

        scores = [score for _, _, score in duplicate_pairs]

        return {
            "total_pairs": len(duplicate_pairs),
            "average_score": np.mean(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "score_distribution": {
                "high_confidence": len([s for s in scores if s > 0.8]),
                "medium_confidence": len([s for s in scores if 0.5 < s <= 0.8]),
                "low_confidence": len([s for s in scores if s <= 0.5]),
            },
            "duplicate_count": len(
                set([idx for idx1, idx2, _ in duplicate_pairs for idx in [idx1, idx2]])
            ),
        }

    def create_training_data(
        self, df: pd.DataFrame, output_file: str, sample_size: Optional[int] = None
    ) -> None:
        """Create training data for dedupe.

        Args:
            df: DataFrame to create training data from.
            output_file: Path to save training data.
            sample_size: Number of samples to generate.
        """
        if not self.dedupe_model:
            raise ValueError("Dedupe model not configured. Call configure() first.")

        sample_size = sample_size or self.config.sample_size

        # Convert DataFrame to dedupe format
        data = self._dataframe_to_dedupe_format(df)

        # Sample pairs for training
        self.dedupe_model.sample(data, sample_size)

        # Get training pairs
        training_pairs = self.dedupe_model.uncertain_pairs()

        # Save training data
        training_data = {"distinct": [], "match": [], "uncertain": training_pairs}

        with open(output_file, "w") as f:
            json.dump(training_data, f, indent=2)

        logger.info(f"Created training data with {len(training_pairs)} uncertain pairs")
        logger.info(f"Training data saved to {output_file}")

    def can_handle(self, operation: str) -> bool:
        """Check if this wrapper can handle the given operation.

        Args:
            operation: Name of the operation to check.

        Returns:
            True if the operation is supported, False otherwise.
        """
        return operation in self.get_supported_operations()

    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations.

        Returns:
            List of supported operation names.
        """
        return ["dedupe", "train_dedupe", "predict_duplicates", "remove_duplicates"]

    def _execute_operation(
        self, operation: str, df: pd.DataFrame, **kwargs
    ) -> pd.DataFrame:
        """Execute a dedupe operation.

        Args:
            operation: Operation to execute.
            df: DataFrame to process.
            **kwargs: Additional arguments.

        Returns:
            Processed DataFrame.
        """
        if operation == "dedupe":
            return self._execute_dedupe(df, **kwargs)
        elif operation == "train_dedupe":
            return self._execute_train(df, **kwargs)
        elif operation == "predict_duplicates":
            return self._execute_predict(df, **kwargs)
        elif operation == "remove_duplicates":
            return self._execute_remove_duplicates(df, **kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def _execute_dedupe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute deduplication operation.

        Args:
            df: DataFrame to deduplicate.
            **kwargs: Additional arguments.

        Returns:
            Deduplicated DataFrame.
        """
        threshold = kwargs.get(
            "threshold", self.config.threshold if self.config else 0.5
        )

        # Configure if not already done
        if not self.config:
            fields = kwargs.get("fields", [])
            if not fields:
                # Auto-generate fields from DataFrame columns using dedupe 3.0 API
                fields = [dedupe.variables.String(col) for col in df.columns]

            training_file = kwargs.get("training_file", None)
            config = DedupeConfig(fields=fields, threshold=threshold, training_file=training_file)
            self.configure(config)

        # Train if not already trained
        if not self.is_trained:
            interactive = kwargs.get("interactive", False)
            try:
                self.train(df, interactive=interactive)
            except Exception as e:
                logger.warning(f"Dedupe training failed: {e}")
                logger.info("Falling back to simple pandas deduplication")
                # Fallback to simple pandas deduplication
                return self._execute_remove_duplicates(df, **kwargs)

        # Predict and remove duplicates
        deduplicated_df, duplicate_pairs = self.predict(df)

        # Log statistics
        stats = self.get_duplicate_statistics(duplicate_pairs)
        logger.info(f"Deduplication completed: {stats}")

        return deduplicated_df

    def _execute_train(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute training operation.

        Args:
            df: DataFrame to train on.
            **kwargs: Additional arguments.

        Returns:
            Original DataFrame (training doesn't modify data).
        """
        interactive = kwargs.get("interactive", False)
        self.train(df, interactive=interactive)
        return df

    def _execute_predict(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute prediction operation.

        Args:
            df: DataFrame to predict duplicates in.
            **kwargs: Additional arguments.

        Returns:
            DataFrame with duplicate information added.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        _, duplicate_pairs = self.predict(df)

        # Add duplicate information to DataFrame
        df_with_duplicates = df.copy()
        df_with_duplicates["is_duplicate"] = False
        df_with_duplicates["duplicate_score"] = 0.0

        for idx1, idx2, score in duplicate_pairs:
            df_with_duplicates.loc[idx2, "is_duplicate"] = True
            df_with_duplicates.loc[idx2, "duplicate_score"] = score

        return df_with_duplicates

    def _execute_remove_duplicates(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute remove_duplicates operation using simple pandas drop_duplicates.

        Args:
            df: DataFrame to process.
            **kwargs: Additional arguments.

        Returns:
            DataFrame with duplicates removed.
        """
        # Use pandas drop_duplicates for simple duplicate removal
        subset = kwargs.get("subset", None)
        keep = kwargs.get("keep", "first")

        result_df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)

        removed_count = len(df) - len(result_df)
        logger.info(
            f"Removed {removed_count} duplicate rows using pandas drop_duplicates"
        )

        return result_df

    def execute(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute an operation (alias for base class execute method for compatibility).

        Args:
            operation: Operation to execute.
            df: DataFrame to process.
            **kwargs: Additional arguments.

        Returns:
            Processed DataFrame.
        """
        return super().execute(operation, df, **kwargs)
