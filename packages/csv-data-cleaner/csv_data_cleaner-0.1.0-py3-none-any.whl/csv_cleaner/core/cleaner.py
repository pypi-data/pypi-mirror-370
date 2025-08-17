"""
Main CSV cleaner class for orchestrating data cleaning operations.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
import time
import logging
from pathlib import Path
from tqdm import tqdm

from .config import Config
from .library_manager import LibraryManager
from .file_operations import FileOperations
from .performance_manager import PerformanceManager
from .parallel_processor import ParallelProcessor
from .validator import AdvancedValidator
from .temp_file_manager import get_temp_file_manager

logger = logging.getLogger(__name__)


class CSVCleaner:
    """Main class for CSV data cleaning operations."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the CSV cleaner.

        Args:
            config: Configuration object for the cleaner.
        """
        self.config = config or Config()
        self.library_manager = LibraryManager(self.config)
        self.file_operations = FileOperations(self.config)

        # Initialize performance components
        self.performance_manager = PerformanceManager(
            max_memory_gb=self.config.max_memory_gb, chunk_size=self.config.chunk_size
        )
        self.parallel_processor = ParallelProcessor(
            max_workers=self.config.max_workers, chunk_size=self.config.chunk_size
        )
        self.validator = AdvancedValidator()

        # Initialize temp file manager
        self.temp_manager = get_temp_file_manager(self.config)

        self.operation_history = []
        self.current_session = None

    def clean_file(
        self, input_path: str, output_path: str, operations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Clean a CSV file using specified operations.

        Args:
            input_path: Path to the input CSV file.
            output_path: Path to the output CSV file.
            operations: List of operations to perform. If None, uses default operations.

        Returns:
            Dictionary with cleaning summary and statistics.

        Raises:
            FileNotFoundError: If the input file doesn't exist.
            ValueError: If operations are invalid.
        """
        start_time = time.time()

        # Validate input file
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Use default operations if none specified
        if operations is None:
            operations = self.config.default_operations

        # Validate operations
        operations = self.validate_operations(operations)

        logger.info(f"Starting CSV cleaning: {input_path} -> {output_path}")
        logger.info(f"Operations: {operations}")

        try:
            # Read the input file
            df = self.file_operations.read_csv(input_path)

            # Create backup if enabled
            backup_path = None
            if self.config.backup_enabled:
                backup_path = self.file_operations.create_backup(input_path)
                logger.info(f"Created backup: {backup_path}")

            # Apply cleaning operations
            df_cleaned = self._apply_operations(df, operations)

            # Write the cleaned file
            self.file_operations.write_csv(df_cleaned, output_path)

            # Create summary
            summary = self._create_operation_summary(
                df, df_cleaned, operations, start_time, backup_path
            )

            # Add temp file statistics to summary
            temp_stats = self.temp_manager.get_stats()
            summary["temp_files_created"] = temp_stats["total_files"]
            summary["temp_files_size_mb"] = temp_stats["total_size_mb"]

            logger.info("CSV cleaning completed successfully")
            logger.info(
                f"Summary: {summary['rows_removed']} rows, {summary['columns_removed']} columns removed"
            )
            logger.info(f"Temp files: {temp_stats['total_files']} files, {temp_stats['total_size_mb']:.2f} MB")

            return summary

        except Exception as e:
            logger.error(f"Error during CSV cleaning: {e}")
            raise

    def clean_dataframe(
        self, df: pd.DataFrame, operations: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Clean a DataFrame using specified operations.

        Args:
            df: Input DataFrame to clean.
            operations: List of operations to perform. If None, uses default operations.

        Returns:
            Cleaned DataFrame.

        Raises:
            ValueError: If operations are invalid.
        """
        if df.empty:
            logger.warning("Input DataFrame is empty")
            return df

        # Use default operations if none specified
        if operations is None:
            operations = self.config.default_operations

        # Validate operations
        operations = self.validate_operations(operations)

        logger.info(f"Starting DataFrame cleaning with {len(operations)} operations")

        try:
            # Apply cleaning operations
            df_cleaned = self._apply_operations(df, operations)

            logger.info("DataFrame cleaning completed successfully")

            return df_cleaned

        except Exception as e:
            logger.error(f"Error during DataFrame cleaning: {e}")
            raise

    def validate_operations(self, operations: List[str]) -> List[str]:
        """Validate and filter operations.

        Args:
            operations: List of operations to validate.

        Returns:
            List of valid operations.

        Raises:
            ValueError: If no valid operations are found.
        """
        if not operations:
            raise ValueError("No operations specified")

        available_operations = self.library_manager.get_available_operations()
        valid_operations = []
        invalid_operations = []

        for operation in operations:
            if operation in available_operations:
                valid_operations.append(operation)
            else:
                # Check if this is a Pro operation that should show upgrade prompt
                operation_category = self.library_manager.feature_gate.get_operation_category(operation)
                if operation_category == "pro":
                    # Allow Pro operations to pass through so they can show upgrade prompts
                    valid_operations.append(operation)
                else:
                    invalid_operations.append(operation)

        if invalid_operations:
            logger.warning(f"Invalid operations ignored: {invalid_operations}")

        if not valid_operations:
            raise ValueError(
                f"No valid operations found. Available: {available_operations}"
            )

        return valid_operations

    def get_operations_summary(self) -> Dict[str, Any]:
        """Get summary of all operations performed in this session.

        Returns:
            Dictionary with operation summary.
        """
        if not self.operation_history:
            return {"total_operations": 0, "operations": []}

        summary = {
            "total_operations": len(self.operation_history),
            "total_files_processed": len(
                set(
                    op.get("file_path")
                    for op in self.operation_history
                    if "file_path" in op
                )
            ),
            "total_rows_processed": sum(
                op.get("input_rows", 0) for op in self.operation_history
            ),
            "total_rows_removed": sum(
                op.get("rows_removed", 0) for op in self.operation_history
            ),
            "total_columns_removed": sum(
                op.get("columns_removed", 0) for op in self.operation_history
            ),
            "total_execution_time": sum(
                op.get("execution_time", 0) for op in self.operation_history
            ),
            "operations": self.operation_history,
        }

        return summary

    def get_supported_operations(self) -> List[str]:
        """Get list of all supported operations.

        Returns:
            List of supported operation names.
        """
        return self.library_manager.get_available_operations()

    def get_operation_info(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific operation.

        Args:
            operation: Name of the operation.

        Returns:
            Dictionary with operation information or None if not supported.
        """
        return self.library_manager.get_operation_info(operation)

    def _apply_operations(
        self, df: pd.DataFrame, operations: List[str]
    ) -> pd.DataFrame:
        """Apply a list of operations to a DataFrame.

        Args:
            df: Input DataFrame.
            operations: List of operations to apply.

        Returns:
            DataFrame with operations applied.
        """
        result = df.copy()

        # Create progress bar if operations are long
        if len(operations) > 1 and self.config.progress_tracking:
            operation_iter = tqdm(operations, desc="Applying operations", unit="op")
        else:
            operation_iter = operations

        for operation in operation_iter:
            try:
                start_time = time.time()

                # Execute the operation
                result = self.library_manager.execute_operation(operation, result)

                execution_time = time.time() - start_time

                # Log operation
                self._log_operation(
                    operation, execution_time, len(df), len(result), True
                )

                if isinstance(operation_iter, tqdm):
                    operation_iter.set_postfix(
                        {"rows": len(result), "time": f"{execution_time:.2f}s"}
                    )

            except Exception as e:
                execution_time = time.time() - start_time
                self._log_operation(
                    operation, execution_time, len(df), len(result), False, str(e)
                )
                logger.error(f"Operation '{operation}' failed: {e}")
                raise

        return result

    def _create_operation_summary(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        operations: List[str],
        start_time: float,
        backup_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a summary of the cleaning operation.

        Args:
            df_before: Original DataFrame.
            df_after: Cleaned DataFrame.
            operations: List of operations performed.
            start_time: Start time of the operation.
            backup_path: Path to backup file if created.

        Returns:
            Dictionary with operation summary.
        """
        total_time = time.time() - start_time

        summary = {
            "input_rows": len(df_before),
            "output_rows": len(df_after),
            "rows_removed": len(df_before) - len(df_after),
            "input_columns": len(df_before.columns),
            "output_columns": len(df_after.columns),
            "columns_removed": len(df_before.columns) - len(df_after.columns),
            "operations_performed": operations,
            "total_execution_time": total_time,
            "backup_created": backup_path is not None,
            "backup_path": backup_path,
            "success": True,
            "timestamp": time.time(),
        }

        # Add performance metrics
        performance_summary = self.library_manager.get_performance_summary()
        summary.update(
            {
                "library_performance": performance_summary,
                "average_operation_time": total_time / len(operations)
                if operations
                else 0,
            }
        )

        return summary

    def _log_operation(
        self,
        operation: str,
        execution_time: float,
        input_rows: int,
        output_rows: int,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log an operation for tracking.

        Args:
            operation: Name of the operation.
            execution_time: Time taken to execute the operation.
            input_rows: Number of rows before operation.
            output_rows: Number of rows after operation.
            success: Whether the operation was successful.
            error: Error message if operation failed.
        """
        log_entry = {
            "operation": operation,
            "execution_time": execution_time,
            "input_rows": input_rows,
            "output_rows": output_rows,
            "rows_removed": input_rows - output_rows,
            "success": success,
            "timestamp": time.time(),
        }

        if error:
            log_entry["error"] = error

        self.operation_history.append(log_entry)

        if success:
            logger.debug(
                f"Operation '{operation}' completed in {execution_time:.2f}s "
                f"({input_rows} -> {output_rows} rows)"
            )
        else:
            logger.error(
                f"Operation '{operation}' failed after {execution_time:.2f}s: {error}"
            )

    def reset_session(self) -> None:
        """Reset the current cleaning session."""
        self.operation_history.clear()
        self.library_manager.reset_operation_history()
        logger.info("Cleaning session reset")

    def export_operation_history(self, file_path: str) -> None:
        """Export operation history to a file.

        Args:
            file_path: Path to save the operation history.
        """
        import json

        history_data = {
            "session_info": {
                "total_operations": len(self.operation_history),
                "export_timestamp": time.time(),
            },
            "operations": self.operation_history,
            "performance_summary": self.get_performance_summary(),
        }

        with open(file_path, "w") as f:
            json.dump(history_data, f, indent=2, default=str)

        logger.info(f"Operation history exported to {file_path}")

    def clean_with_performance_optimization(
        self,
        df: pd.DataFrame,
        operations: List[str],
        chunk_size: Optional[int] = None,
        use_parallel: bool = True,
    ) -> pd.DataFrame:
        """Clean DataFrame with performance optimization.

        Args:
            df: DataFrame to clean.
            operations: List of operations to perform.
            chunk_size: Custom chunk size for processing.
            use_parallel: Whether to use parallel processing.

        Returns:
            Cleaned DataFrame.
        """
        logger.info("Starting performance-optimized cleaning")

        # Optimize chunk size if auto-optimization is enabled
        if self.config.auto_optimize_chunk_size and chunk_size is None:
            chunk_size = self.performance_manager.optimize_chunk_size(df)

        # Use chunked processing for large datasets
        if len(df) > self.config.chunk_size and self.config.enable_chunked_processing:
            logger.info(f"Using chunked processing with chunk size: {chunk_size}")

            def chunk_operation(chunk_df):
                return self._apply_operations(chunk_df, operations)

            return self.performance_manager.process_in_chunks(
                df, chunk_operation, chunk_size=chunk_size
            )

        # Use parallel processing if enabled and beneficial
        elif (
            use_parallel and self.config.enable_parallel_processing and len(df) > 10000
        ):
            logger.info("Using parallel processing")

            operation_configs = []
            for operation in operations:
                wrapper = self.library_manager.get_best_wrapper(operation, df)
                operation_configs.append(
                    {
                        "operation": operation,
                        "function": wrapper.execute_operation,
                        "parameters": {},
                    }
                )

            return self.parallel_processor.process_operations_parallel(
                df, operation_configs
            )

        # Fall back to standard processing
        else:
            logger.info("Using standard processing")
            return self._apply_operations(df, operations)

    def validate_data(
        self, df: pd.DataFrame, schema_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate data using advanced validation.

        Args:
            df: DataFrame to validate.
            schema_file: Optional schema file path.

        Returns:
            Validation results and quality score.
        """
        logger.info("Starting data validation")

        # Load schema if provided
        if schema_file:
            self.validator.load_schema_from_file(schema_file)

        # Validate data
        validation_results = self.validator.validate_dataframe(df)

        # Calculate quality score
        quality_score = self.validator.calculate_quality_score(df)

        return {
            "validation_results": validation_results,
            "quality_score": quality_score,
            "passed": all(result.passed for result in validation_results),
            "total_errors": sum(result.error_count for result in validation_results),
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary.

        Returns:
            Performance summary including all components.
        """
        summary = {
            "performance_manager": self.performance_manager.get_performance_summary(),
            "parallel_processor": self.parallel_processor.get_system_info(),
            "operation_history": self.operation_history,
            "config": {
                "max_memory_gb": self.config.max_memory_gb,
                "chunk_size": self.config.chunk_size,
                "max_workers": self.config.max_workers,
                "enable_chunked_processing": self.config.enable_chunked_processing,
                "enable_parallel_processing": self.config.enable_parallel_processing,
            },
        }

        return summary

    def estimate_processing_time(
        self, df: pd.DataFrame, operations: List[str]
    ) -> float:
        """Estimate processing time for operations.

        Args:
            df: DataFrame to process.
            operations: List of operations to perform.

        Returns:
            Estimated processing time in seconds.
        """
        data_size = len(df)
        operation_complexity = "medium"  # Could be made more sophisticated

        # Get base estimate from parallel processor
        base_estimate = self.parallel_processor.estimate_processing_time(
            data_size, operation_complexity
        )

        # Adjust for number of operations
        adjusted_estimate = base_estimate * len(operations)

        logger.info(
            f"Estimated processing time: {adjusted_estimate:.2f}s for {len(operations)} operations"
        )
        return adjusted_estimate
