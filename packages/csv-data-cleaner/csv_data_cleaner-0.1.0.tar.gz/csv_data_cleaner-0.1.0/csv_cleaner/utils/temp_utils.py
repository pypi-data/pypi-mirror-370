"""
Utility functions for temporary file management in CSV Data Cleaner.

This module provides helper functions for common temp file operations,
CSV-specific utilities, and bulk cleanup operations.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging

from ..core.temp_file_manager import get_temp_file_manager, TempFileManager
from ..core.config import Config

logger = logging.getLogger(__name__)


def create_temp_csv(
    df: pd.DataFrame,
    prefix: str = "csv_cleaner_",
    suffix: str = ".csv",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Config] = None
) -> Path:
    """Create a temporary CSV file from a DataFrame.

    Args:
        df: DataFrame to save as CSV.
        prefix: File prefix.
        suffix: File suffix.
        tags: Optional tags for the temp file.
        metadata: Optional metadata for the temp file.
        config: Configuration object.

    Returns:
        Path to the created temporary CSV file.
    """
    temp_manager = get_temp_file_manager(config)

    # Create temp file
    temp_file_path = temp_manager.create_temp_file(
        suffix=suffix,
        prefix=prefix,
        tags=tags or ["csv", "dataframe"],
        metadata=metadata or {}
    )

    # Save DataFrame to CSV
    df.to_csv(temp_file_path, index=False)

    # Update file size in tracking
    file_info = temp_manager.get_file_info(temp_file_path)
    if file_info:
        file_info.size_bytes = temp_file_path.stat().st_size

    logger.debug(f"Created temp CSV file: {temp_file_path} ({len(df)} rows)")
    return temp_file_path


def create_temp_backup(
    original_file: Union[str, Path],
    prefix: str = "csv_cleaner_backup_",
    tags: Optional[List[str]] = None,
    config: Optional[Config] = None
) -> Path:
    """Create a temporary backup of a file.

    Args:
        original_file: Path to the original file.
        prefix: Backup file prefix.
        tags: Optional tags for the backup file.
        config: Configuration object.

    Returns:
        Path to the created backup file.
    """
    import shutil

    temp_manager = get_temp_file_manager(config)
    original_path = Path(original_file)

    # Create temp backup file
    backup_path = temp_manager.create_temp_file(
        suffix=original_path.suffix,
        prefix=prefix,
        tags=tags or ["backup", "csv"],
        metadata={"original_file": str(original_path)}
    )

    # Copy original file to backup
    shutil.copy2(original_path, backup_path)

    # Update file size in tracking
    file_info = temp_manager.get_file_info(backup_path)
    if file_info:
        file_info.size_bytes = backup_path.stat().st_size

    logger.debug(f"Created temp backup: {backup_path}")
    return backup_path


def cleanup_temp_files(
    tags: Optional[List[str]] = None,
    max_age_hours: Optional[int] = None,
    config: Optional[Config] = None
) -> Dict[str, Any]:
    """Clean up temporary files with various options.

    Args:
        tags: Optional tags to filter files for cleanup.
        max_age_hours: Optional maximum age in hours for cleanup.
        config: Configuration object.

    Returns:
        Dictionary with cleanup statistics.
    """
    temp_manager = get_temp_file_manager(config)

    stats = {
        "files_cleaned": 0,
        "total_size_cleaned_mb": 0,
        "cleanup_method": "unknown"
    }

    if tags:
        # Cleanup by tags
        stats["files_cleaned"] = temp_manager.cleanup_by_tags(tags)
        stats["cleanup_method"] = "tags"
    elif max_age_hours:
        # Cleanup expired files
        stats["files_cleaned"] = temp_manager.cleanup_expired(max_age_hours)
        stats["cleanup_method"] = "expired"
    else:
        # Cleanup all files
        stats["files_cleaned"] = temp_manager.cleanup_all()
        stats["cleanup_method"] = "all"

    # Get remaining stats
    remaining_stats = temp_manager.get_stats()
    stats["total_size_cleaned_mb"] = remaining_stats["total_size_mb"]

    logger.info(f"Cleanup completed: {stats['files_cleaned']} files cleaned using {stats['cleanup_method']} method")
    return stats


def get_temp_file_stats(config: Optional[Config] = None) -> Dict[str, Any]:
    """Get statistics about temporary files.

    Args:
        config: Configuration object.

    Returns:
        Dictionary with temp file statistics.
    """
    temp_manager = get_temp_file_manager(config)
    return temp_manager.get_stats()


def list_temp_files(
    tags: Optional[List[str]] = None,
    config: Optional[Config] = None
) -> List[Dict[str, Any]]:
    """List all tracked temporary files.

    Args:
        tags: Optional tags to filter files.
        config: Configuration object.

    Returns:
        List of dictionaries with file information.
    """
    temp_manager = get_temp_file_manager(config)
    temp_files = temp_manager.list_temp_files(tags)

    return [
        {
            "path": str(file_info.path),
            "created_at": file_info.created_at.isoformat(),
            "size_bytes": file_info.size_bytes,
            "size_mb": file_info.size_bytes / (1024 * 1024),
            "cleanup_policy": file_info.cleanup_policy,
            "tags": file_info.tags,
            "metadata": file_info.metadata
        }
        for file_info in temp_files
    ]


def create_temp_chunk_file(
    chunk: pd.DataFrame,
    chunk_index: int,
    prefix: str = "csv_cleaner_chunk_",
    tags: Optional[List[str]] = None,
    config: Optional[Config] = None
) -> Path:
    """Create a temporary file for a data chunk.

    Args:
        chunk: DataFrame chunk to save.
        chunk_index: Index of the chunk.
        prefix: File prefix.
        tags: Optional tags for the chunk file.
        config: Configuration object.

    Returns:
        Path to the created chunk file.
    """
    chunk_tags = tags or ["chunk", "processing"]
    chunk_tags.append(f"chunk_{chunk_index}")

    return create_temp_csv(
        df=chunk,
        prefix=prefix,
        suffix=".csv",
        tags=chunk_tags,
        metadata={"chunk_index": chunk_index, "chunk_size": len(chunk)},
        config=config
    )


def cleanup_chunk_files(config: Optional[Config] = None) -> int:
    """Clean up all temporary chunk files.

    Args:
        config: Configuration object.

    Returns:
        Number of chunk files cleaned up.
    """
    return cleanup_temp_files(tags=["chunk"], config=config)["files_cleaned"]


def cleanup_backup_files(config: Optional[Config] = None) -> int:
    """Clean up all temporary backup files.

    Args:
        config: Configuration object.

    Returns:
        Number of backup files cleaned up.
    """
    return cleanup_temp_files(tags=["backup"], config=config)["files_cleaned"]


def cleanup_csv_files(config: Optional[Config] = None) -> int:
    """Clean up all temporary CSV files.

    Args:
        config: Configuration object.

    Returns:
        Number of CSV files cleaned up.
    """
    return cleanup_temp_files(tags=["csv"], config=config)["files_cleaned"]


def monitor_temp_file_usage(
    config: Optional[Config] = None,
    log_interval_seconds: int = 300
) -> None:
    """Monitor temporary file usage and log statistics.

    Args:
        config: Configuration object.
        log_interval_seconds: Interval between log messages in seconds.
    """
    import time
    import threading

    def monitor_worker():
        while True:
            try:
                stats = get_temp_file_stats(config)
                logger.info(
                    f"Temp file usage: {stats['total_files']} files, "
                    f"{stats['total_size_mb']:.2f} MB, "
                    f"Directory: {stats['temp_directory']}"
                )
                time.sleep(log_interval_seconds)
            except Exception as e:
                logger.error(f"Error in temp file monitoring: {e}")
                time.sleep(log_interval_seconds)

    monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
    monitor_thread.start()
    logger.info(f"Started temp file monitoring (log interval: {log_interval_seconds}s)")


def get_temp_directory(config: Optional[Config] = None) -> Path:
    """Get the temporary directory path.

    Args:
        config: Configuration object.

    Returns:
        Path to the temporary directory.
    """
    temp_manager = get_temp_file_manager(config)
    return temp_manager.temp_dir


def is_temp_file_cleanup_enabled(config: Optional[Config] = None) -> bool:
    """Check if temp file cleanup is enabled.

    Args:
        config: Configuration object.

    Returns:
        True if cleanup is enabled, False otherwise.
    """
    if config is None:
        config = Config()
    return getattr(config, 'temp_file_cleanup_enabled', True)


def get_temp_file_config(config: Optional[Config] = None) -> Dict[str, Any]:
    """Get temp file configuration settings.

    Args:
        config: Configuration object.

    Returns:
        Dictionary with temp file configuration.
    """
    if config is None:
        config = Config()

    return {
        "temp_directory": getattr(config, 'temp_directory', None),
        "temp_file_cleanup_interval": getattr(config, 'temp_file_cleanup_interval', 3600),
        "temp_file_max_age_hours": getattr(config, 'temp_file_max_age_hours', 24),
        "temp_file_max_size_mb": getattr(config, 'temp_file_max_size_mb', 1024),
        "temp_file_cleanup_enabled": getattr(config, 'temp_file_cleanup_enabled', True),
        "temp_file_secure_mode": getattr(config, 'temp_file_secure_mode', True),
        "temp_file_auto_cleanup": getattr(config, 'temp_file_auto_cleanup', True)
    }
