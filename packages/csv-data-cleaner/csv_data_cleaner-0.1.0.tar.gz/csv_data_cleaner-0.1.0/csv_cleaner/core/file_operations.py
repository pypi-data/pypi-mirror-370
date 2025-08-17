"""
File operations for CSV data cleaning.
"""

import pandas as pd
from typing import Dict, Any, Optional, Iterator
import time
import logging
import shutil
from pathlib import Path
import chardet
import gzip
import zipfile
from .config import Config
from .temp_file_manager import get_temp_file_manager

logger = logging.getLogger(__name__)


class FileOperations:
    """Handles file I/O operations for CSV data cleaning."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize file operations.

        Args:
            config: Configuration object for file operations.
        """
        self.config = config or Config()
        self.supported_encodings = [
            "utf-8",
            "utf-8-sig",
            "latin-1",
            "cp1252",
            "iso-8859-1",
        ]

    def read_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Read CSV file with automatic encoding detection.

        Args:
            file_path: Path to the CSV file.
            **kwargs: Additional arguments for pd.read_csv.

        Returns:
            DataFrame containing the CSV data.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file format is not supported.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file format
        if not self._validate_csv_format(file_path):
            raise ValueError(f"File {file_path} is not a valid CSV file")

        # Detect encoding
        encoding = kwargs.pop("encoding", None)
        if encoding is None:
            encoding = self._detect_encoding(file_path)

        # Handle compressed files
        if self._is_compressed(file_path):
            return self._read_compressed_csv(file_path, encoding, **kwargs)

        # Read the file
        try:
            logger.info(f"Reading CSV file: {file_path}")
            start_time = time.time()

            df = pd.read_csv(file_path, encoding=encoding, **kwargs)

            read_time = time.time() - start_time
            logger.info(f"Successfully read {len(df)} rows in {read_time:.2f} seconds")

            return df

        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            # Try alternative encodings
            for alt_encoding in self.supported_encodings:
                if alt_encoding != encoding:
                    try:
                        logger.info(f"Trying alternative encoding: {alt_encoding}")
                        df = pd.read_csv(file_path, encoding=alt_encoding, **kwargs)
                        logger.info(f"Successfully read with {alt_encoding}")
                        return df
                    except UnicodeDecodeError:
                        continue

            raise ValueError(f"Could not read {file_path} with any supported encoding")

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise

    def write_csv(self, df: pd.DataFrame, file_path: str, **kwargs) -> None:
        """Write DataFrame to CSV file.

        Args:
            df: DataFrame to write.
            file_path: Path to the output file.
            **kwargs: Additional arguments for df.to_csv.

        Raises:
            ValueError: If the DataFrame is empty.
        """
        if df.empty:
            raise ValueError("Cannot write empty DataFrame")

        file_path = Path(file_path)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Set default parameters
        kwargs.setdefault("index", False)
        kwargs.setdefault("encoding", "utf-8")

        try:
            logger.info(f"Writing CSV file: {file_path}")
            start_time = time.time()

            df.to_csv(file_path, **kwargs)

            write_time = time.time() - start_time
            logger.info(
                f"Successfully wrote {len(df)} rows in {write_time:.2f} seconds"
            )

        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
            raise

    def create_backup(self, file_path: str) -> str:
        """Create backup of the original file.

        Args:
            file_path: Path to the file to backup.

        Returns:
            Path to the backup file.

        Raises:
            FileNotFoundError: If the original file doesn't exist.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use temp file manager for backup creation
        temp_manager = get_temp_file_manager(self.config)

        try:
            # Create temp backup file
            backup_path = temp_manager.create_temp_file(
                suffix=file_path.suffix,
                prefix="csv_cleaner_backup_",
                tags=["backup", "csv"],
                metadata={"original_file": str(file_path)}
            )

            logger.info(f"Creating backup: {backup_path}")
            shutil.copy2(file_path, backup_path)

            # Update file size in tracking
            file_info = temp_manager.get_file_info(backup_path)
            if file_info:
                file_info.size_bytes = backup_path.stat().st_size

            logger.info("Backup created successfully")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate CSV file and return information.

        Args:
            file_path: Path to the file to validate.

        Returns:
            Dictionary with validation results and file information.
        """
        file_path = Path(file_path)

        validation_result = {
            "file_path": str(file_path),
            "exists": file_path.exists(),
            "is_file": file_path.is_file() if file_path.exists() else False,
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "is_csv": False,
            "encoding": None,
            "estimated_rows": 0,
            "estimated_columns": 0,
            "errors": [],
        }

        if not validation_result["exists"]:
            validation_result["errors"].append("File does not exist")
            return validation_result

        if not validation_result["is_file"]:
            validation_result["errors"].append("Path is not a file")
            return validation_result

        # Check if it's a CSV file
        validation_result["is_csv"] = self._validate_csv_format(file_path)
        if not validation_result["is_csv"]:
            validation_result["errors"].append("File is not a valid CSV")
            return validation_result

        # Detect encoding
        try:
            validation_result["encoding"] = self._detect_encoding(file_path)
        except Exception as e:
            validation_result["errors"].append(f"Could not detect encoding: {e}")

        # Estimate rows and columns
        try:
            sample_df = pd.read_csv(
                file_path, nrows=1000, encoding=validation_result["encoding"]
            )
            validation_result["estimated_columns"] = len(sample_df.columns)

            # Estimate total rows based on file size
            sample_size = sample_df.memory_usage(deep=True).sum()
            if sample_size > 0:
                validation_result["estimated_rows"] = int(
                    validation_result["size_bytes"] * len(sample_df) / sample_size
                )
        except Exception as e:
            validation_result["errors"].append(f"Could not estimate dimensions: {e}")

        return validation_result

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file.

        Args:
            file_path: Path to the file.

        Returns:
            Dictionary with file information.
        """
        file_path = Path(file_path)

        info = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "parent_directory": str(file_path.parent),
            "exists": file_path.exists(),
            "size_bytes": 0,
            "size_mb": 0,
            "created_time": None,
            "modified_time": None,
            "is_compressed": False,
            "compression_type": None,
        }

        if file_path.exists():
            stat = file_path.stat()
            info.update(
                {
                    "size_bytes": stat.st_size,
                    "size_mb": stat.st_size / (1024 * 1024),
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "is_compressed": self._is_compressed(file_path),
                    "compression_type": self._get_compression_type(file_path),
                }
            )

        return info

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding using chardet.

        Args:
            file_path: Path to the file.

        Returns:
            Detected encoding.
        """
        try:
            with open(file_path, "rb") as f:
                # Read a sample for encoding detection
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result["encoding"]
                confidence = result["confidence"]

                logger.info(
                    f"Detected encoding: {encoding} (confidence: {confidence:.2f})"
                )

                if confidence > 0.7:
                    return encoding
                else:
                    logger.warning(f"Low confidence encoding detection: {encoding}")
                    return "utf-8"  # Default fallback

        except Exception as e:
            logger.warning(f"Error detecting encoding: {e}")
            return "utf-8"  # Default fallback

    def _validate_csv_format(self, file_path: Path) -> bool:
        """Validate that the file is a valid CSV.

        Args:
            file_path: Path to the file.

        Returns:
            True if the file appears to be a valid CSV.
        """
        # Check file extension
        if file_path.suffix.lower() not in [".csv", ".txt"]:
            return False

        # Check if file is not empty
        if file_path.stat().st_size == 0:
            return False

        # Try to read first few lines to check format
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if not first_line or "," not in first_line:
                    return False
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    first_line = f.readline().strip()
                    if not first_line or "," not in first_line:
                        return False
            except Exception:
                return False

        return True

    def _create_backup_path(self, file_path: Path) -> Path:
        """Create backup file path.

        Args:
            file_path: Original file path.

        Returns:
            Backup file path.
        """
        timestamp = int(time.time())
        backup_name = f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
        return file_path.parent / backup_name

    def _is_compressed(self, file_path: Path) -> bool:
        """Check if file is compressed.

        Args:
            file_path: Path to the file.

        Returns:
            True if the file is compressed.
        """
        return file_path.suffix.lower() in [".gz", ".zip"]

    def _get_compression_type(self, file_path: Path) -> Optional[str]:
        """Get compression type of the file.

        Args:
            file_path: Path to the file.

        Returns:
            Compression type or None if not compressed.
        """
        if file_path.suffix.lower() == ".gz":
            return "gzip"
        elif file_path.suffix.lower() == ".zip":
            return "zip"
        return None

    def _read_compressed_csv(
        self, file_path: Path, encoding: str, **kwargs
    ) -> pd.DataFrame:
        """Read compressed CSV file.

        Args:
            file_path: Path to the compressed file.
            encoding: File encoding.
            **kwargs: Additional arguments for pd.read_csv.

        Returns:
            DataFrame containing the CSV data.
        """
        if file_path.suffix.lower() == ".gz":
            with gzip.open(file_path, "rt", encoding=encoding) as f:
                return pd.read_csv(f, **kwargs)
        elif file_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(file_path, "r") as zip_file:
                # Assume first CSV file in zip
                csv_files = [f for f in zip_file.namelist() if f.endswith(".csv")]
                if not csv_files:
                    raise ValueError("No CSV files found in zip archive")

                with zip_file.open(csv_files[0]) as f:
                    return pd.read_csv(f, encoding=encoding, **kwargs)
        else:
            raise ValueError(f"Unsupported compression type: {file_path.suffix}")

    def chunked_read(
        self, file_path: str, chunk_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """Read CSV file in chunks for memory efficiency.

        Args:
            file_path: Path to the CSV file.
            chunk_size: Number of rows per chunk.

        Yields:
            DataFrame chunks.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        encoding = self._detect_encoding(file_path)

        try:
            logger.info(f"Reading {file_path} in chunks of {chunk_size}")

            for chunk in pd.read_csv(
                file_path, encoding=encoding, chunksize=chunk_size
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error in chunked read: {e}")
            raise

    def create_temp_chunk_file(
        self, chunk: pd.DataFrame, chunk_index: int
    ) -> Path:
        """Create a temporary file for a data chunk.

        Args:
            chunk: DataFrame chunk to save.
            chunk_index: Index of the chunk.

        Returns:
            Path to the created chunk file.
        """
        temp_manager = get_temp_file_manager(self.config)

        # Create temp chunk file
        chunk_path = temp_manager.create_temp_file(
            suffix=".csv",
            prefix="csv_cleaner_chunk_",
            tags=["chunk", "processing", f"chunk_{chunk_index}"],
            metadata={"chunk_index": chunk_index, "chunk_size": len(chunk)}
        )

        # Save chunk to CSV
        chunk.to_csv(chunk_path, index=False)

        # Update file size in tracking
        file_info = temp_manager.get_file_info(chunk_path)
        if file_info:
            file_info.size_bytes = chunk_path.stat().st_size

        logger.debug(f"Created temp chunk file: {chunk_path} ({len(chunk)} rows)")
        return chunk_path
