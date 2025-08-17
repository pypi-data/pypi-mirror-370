"""
Temporary file management for CSV data cleaning operations.

This module provides a centralized system for managing temporary files
with automatic cleanup, security features, and configurable policies.
"""

import os
import tempfile
import shutil
import time
import logging
import atexit
import signal
import threading
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import weakref

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class TempFileInfo:
    """Information about a temporary file."""
    path: Path
    created_at: datetime
    size_bytes: int = 0
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    cleanup_policy: str = "auto"  # auto, manual, session
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)


class TempFileManager:
    """
    Centralized temporary file management system.

    Features:
    - Automatic cleanup on exit
    - Configurable cleanup policies
    - Security features (secure file creation)
    - File tracking and monitoring
    - Custom cleanup handlers
    - Memory-efficient operations
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the temp file manager.

        Args:
            config: Configuration object for temp file settings.
        """
        self.config = config or Config()
        self._temp_files: Dict[str, TempFileInfo] = {}
        self._temp_dirs: Dict[str, Path] = {}
        self._cleanup_handlers: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown = False

        # Configure temp directory
        self.temp_dir = self._get_temp_directory()

        # Register cleanup handlers
        self._register_cleanup_handlers()

        # Start background cleanup thread if enabled
        if getattr(self.config, 'temp_file_cleanup_interval', 0) > 0:
            self._start_cleanup_thread()

    def _get_temp_directory(self) -> Path:
        """Get the temporary directory path.

        Returns:
            Path to the temporary directory.
        """
        if hasattr(self.config, 'temp_directory') and self.config.temp_directory:
            temp_dir = Path(self.config.temp_directory)
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir
        else:
            return Path(tempfile.gettempdir()) / "csv_cleaner"

    def _register_cleanup_handlers(self) -> None:
        """Register cleanup handlers for graceful shutdown."""
        # Register atexit handler
        atexit.register(self.cleanup_all)

        # Register signal handlers
        for sig in [signal.SIGINT, signal.SIGTERM]:
            try:
                signal.signal(sig, self._signal_handler)
            except (OSError, ValueError):
                # Signal handlers may not work in all environments
                pass

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, cleaning up temp files...")
        self.cleanup_all()

    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        def cleanup_worker():
            while not self._shutdown:
                try:
                    time.sleep(getattr(self.config, 'temp_file_cleanup_interval', 3600))
                    if not self._shutdown:
                        self._cleanup_expired_files()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def create_temp_file(
        self,
        suffix: str = ".csv",
        prefix: str = "csv_cleaner_",
        directory: Optional[Union[str, Path]] = None,
        cleanup_policy: str = "auto",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, any]] = None
    ) -> Path:
        """Create a secure temporary file.

        Args:
            suffix: File suffix (e.g., '.csv', '.tmp').
            prefix: File prefix.
            directory: Optional directory for the temp file.
            cleanup_policy: When to cleanup ('auto', 'manual', 'session').
            tags: Optional tags for categorizing the file.
            metadata: Optional metadata for the file.

        Returns:
            Path to the created temporary file.

        Raises:
            OSError: If file creation fails.
        """
        with self._lock:
            # Create the temp file using secure method
            temp_dir = Path(directory) if directory else self.temp_dir
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Use NamedTemporaryFile for security
            with tempfile.NamedTemporaryFile(
                mode='w+b',
                suffix=suffix,
                prefix=prefix,
                dir=temp_dir,
                delete=False
            ) as temp_file:
                file_path = Path(temp_file.name)

            # Track the file
            file_id = str(file_path)
            self._temp_files[file_id] = TempFileInfo(
                path=file_path,
                created_at=datetime.now(),
                cleanup_policy=cleanup_policy,
                tags=tags or [],
                metadata=metadata or {}
            )

            logger.debug(f"Created temp file: {file_path}")
            return file_path

    def create_temp_directory(
        self,
        prefix: str = "csv_cleaner_",
        directory: Optional[Union[str, Path]] = None,
        cleanup_policy: str = "auto",
        tags: Optional[List[str]] = None
    ) -> Path:
        """Create a temporary directory.

        Args:
            prefix: Directory prefix.
            directory: Optional parent directory.
            cleanup_policy: When to cleanup ('auto', 'manual', 'session').
            tags: Optional tags for categorizing the directory.

        Returns:
            Path to the created temporary directory.
        """
        with self._lock:
            temp_dir = Path(directory) if directory else self.temp_dir
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create temp directory
            dir_path = Path(tempfile.mkdtemp(prefix=prefix, dir=temp_dir))

            # Track the directory
            dir_id = str(dir_path)
            self._temp_dirs[dir_id] = dir_path

            # Create a file entry for tracking
            self._temp_files[dir_id] = TempFileInfo(
                path=dir_path,
                created_at=datetime.now(),
                cleanup_policy=cleanup_policy,
                tags=tags or [],
                metadata={"type": "directory"}
            )

            logger.debug(f"Created temp directory: {dir_path}")
            return dir_path

    @contextmanager
    def temp_file(
        self,
        suffix: str = ".csv",
        prefix: str = "csv_cleaner_",
        cleanup_policy: str = "auto",
        tags: Optional[List[str]] = None
    ):
        """Context manager for temporary file creation and cleanup.

        Args:
            suffix: File suffix.
            prefix: File prefix.
            cleanup_policy: When to cleanup.
            tags: Optional tags.

        Yields:
            Path to the temporary file.
        """
        file_path = None
        try:
            file_path = self.create_temp_file(
                suffix=suffix,
                prefix=prefix,
                cleanup_policy=cleanup_policy,
                tags=tags
            )
            yield file_path
        finally:
            if file_path and cleanup_policy == "auto":
                self.cleanup_file(file_path)

    @contextmanager
    def temp_directory(
        self,
        prefix: str = "csv_cleaner_",
        cleanup_policy: str = "auto",
        tags: Optional[List[str]] = None
    ):
        """Context manager for temporary directory creation and cleanup.

        Args:
            prefix: Directory prefix.
            cleanup_policy: When to cleanup.
            tags: Optional tags.

        Yields:
            Path to the temporary directory.
        """
        dir_path = None
        try:
            dir_path = self.create_temp_directory(
                prefix=prefix,
                cleanup_policy=cleanup_policy,
                tags=tags
            )
            yield dir_path
        finally:
            if dir_path and cleanup_policy == "auto":
                self.cleanup_directory(dir_path)

    def cleanup_file(self, file_path: Union[str, Path]) -> bool:
        """Clean up a specific temporary file.

        Args:
            file_path: Path to the file to cleanup.

        Returns:
            True if cleanup was successful, False otherwise.
        """
        file_path = Path(file_path)
        file_id = str(file_path)

        with self._lock:
            if file_id not in self._temp_files:
                logger.warning(f"Attempted to cleanup untracked file: {file_path}")
                return False

            file_info = self._temp_files[file_id]

            try:
                # Call custom cleanup handler if registered
                if file_id in self._cleanup_handlers:
                    self._cleanup_handlers[file_id](file_path)

                # Remove the file
                if file_path.exists():
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)

                # Remove from tracking
                del self._temp_files[file_id]
                if file_id in self._temp_dirs:
                    del self._temp_dirs[file_id]

                logger.debug(f"Cleaned up temp file: {file_path}")
                return True

            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
                return False

    def cleanup_directory(self, dir_path: Union[str, Path]) -> bool:
        """Clean up a temporary directory and all its contents.

        Args:
            dir_path: Path to the directory to cleanup.

        Returns:
            True if cleanup was successful, False otherwise.
        """
        return self.cleanup_file(dir_path)

    def cleanup_by_tags(self, tags: List[str]) -> int:
        """Clean up all temporary files with matching tags.

        Args:
            tags: List of tags to match.

        Returns:
            Number of files cleaned up.
        """
        cleaned_count = 0

        with self._lock:
            files_to_cleanup = [
                file_id for file_id, file_info in self._temp_files.items()
                if any(tag in file_info.tags for tag in tags)
            ]

        for file_id in files_to_cleanup:
            if self.cleanup_file(self._temp_files[file_id].path):
                cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} files with tags: {tags}")
        return cleaned_count

    def cleanup_expired(self, max_age_hours: Optional[int] = None) -> int:
        """Clean up files older than the specified age.

        Args:
            max_age_hours: Maximum age in hours (uses config default if None).

        Returns:
            Number of files cleaned up.
        """
        if max_age_hours is None:
            max_age_hours = getattr(self.config, 'temp_file_max_age_hours', 24)

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0

        with self._lock:
            files_to_cleanup = [
                file_id for file_id, file_info in self._temp_files.items()
                if file_info.created_at < cutoff_time
            ]

        for file_id in files_to_cleanup:
            if self.cleanup_file(self._temp_files[file_id].path):
                cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} expired files (older than {max_age_hours}h)")
        return cleaned_count

    def _cleanup_expired_files(self) -> None:
        """Internal method for background cleanup of expired files."""
        if getattr(self.config, 'temp_file_max_age_hours', 24) > 0:
            self.cleanup_expired()

    def cleanup_all(self) -> int:
        """Clean up all temporary files.

        Returns:
            Number of files cleaned up.
        """
        logger.info("Starting cleanup of all temporary files...")

        with self._lock:
            files_to_cleanup = list(self._temp_files.keys())

        cleaned_count = 0
        for file_id in files_to_cleanup:
            if self.cleanup_file(self._temp_files[file_id].path):
                cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} temporary files")
        return cleaned_count

    def register_cleanup_handler(
        self,
        file_path: Union[str, Path],
        handler: Callable[[Path], None]
    ) -> None:
        """Register a custom cleanup handler for a specific file.

        Args:
            file_path: Path to the file.
            handler: Function to call during cleanup.
        """
        file_id = str(Path(file_path))
        self._cleanup_handlers[file_id] = handler

    def get_file_info(self, file_path: Union[str, Path]) -> Optional[TempFileInfo]:
        """Get information about a tracked temporary file.

        Args:
            file_path: Path to the file.

        Returns:
            TempFileInfo object or None if not tracked.
        """
        file_id = str(Path(file_path))
        return self._temp_files.get(file_id)

    def list_temp_files(self, tags: Optional[List[str]] = None) -> List[TempFileInfo]:
        """List all tracked temporary files.

        Args:
            tags: Optional filter by tags.

        Returns:
            List of TempFileInfo objects.
        """
        with self._lock:
            if tags:
                return [
                    file_info for file_info in self._temp_files.values()
                    if any(tag in file_info.tags for tag in tags)
                ]
            else:
                return list(self._temp_files.values())

    def get_stats(self) -> Dict[str, any]:
        """Get statistics about temporary files.

        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            total_files = len(self._temp_files)
            total_dirs = len(self._temp_dirs)
            total_size = sum(
                file_info.size_bytes for file_info in self._temp_files.values()
            )

            # Count by cleanup policy
            policy_counts = {}
            for file_info in self._temp_files.values():
                policy = file_info.cleanup_policy
                policy_counts[policy] = policy_counts.get(policy, 0) + 1

            # Count by tags
            tag_counts = {}
            for file_info in self._temp_files.values():
                for tag in file_info.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            return {
                "total_files": total_files,
                "total_directories": total_dirs,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "cleanup_policy_counts": policy_counts,
                "tag_counts": tag_counts,
                "temp_directory": str(self.temp_dir)
            }

    def shutdown(self) -> None:
        """Shutdown the temp file manager."""
        logger.info("Shutting down temp file manager...")
        self._shutdown = True

        # Stop cleanup thread
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)

        # Cleanup all files
        self.cleanup_all()


# Global instance
_temp_file_manager: Optional[TempFileManager] = None


def get_temp_file_manager(config: Optional[Config] = None) -> TempFileManager:
    """Get the global temp file manager instance.

    Args:
        config: Configuration object (only used for first initialization).

    Returns:
        Global TempFileManager instance.
    """
    global _temp_file_manager
    if _temp_file_manager is None:
        _temp_file_manager = TempFileManager(config)
    return _temp_file_manager


def cleanup_global_temp_files() -> None:
    """Clean up all global temporary files."""
    if _temp_file_manager:
        _temp_file_manager.cleanup_all()


# Register global cleanup
atexit.register(cleanup_global_temp_files)
