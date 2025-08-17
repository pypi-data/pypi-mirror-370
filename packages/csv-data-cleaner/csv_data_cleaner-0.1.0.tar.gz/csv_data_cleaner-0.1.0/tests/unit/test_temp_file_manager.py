"""
TEST SUITE: csv_cleaner.core.temp_file_manager
PURPOSE: Test temporary file management system with secure file creation, tracking, and cleanup
SCOPE: TempFileManager class, file creation, cleanup policies, context managers, error handling
DEPENDENCIES: tempfile, pathlib, threading, atexit, signal
"""

import pytest
import tempfile
import os
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import shutil

from csv_cleaner.core.temp_file_manager import TempFileManager, TempFileInfo, get_temp_file_manager
from csv_cleaner.core.config import Config


class TestTempFileManager:
    """Test the TempFileManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config(
            temp_file_cleanup_enabled=True,
            temp_file_auto_cleanup=True,
            temp_file_cleanup_interval=1,  # 1 second for testing
            temp_file_max_age_hours=1
        )
        self.temp_manager = TempFileManager(self.config)

    def teardown_method(self):
        """Clean up test files."""
        self.temp_manager.cleanup_all()
        self.temp_manager.shutdown()

    def test_init_with_config(self):
        """TEST: should_initialize_with_configuration_settings"""
        # ARRANGE: Config with temp file settings
        config = Config(
            temp_directory="/tmp/test_csv_cleaner",
            temp_file_cleanup_interval=1800,
            temp_file_max_age_hours=12
        )

        # ACT: Create temp file manager
        manager = TempFileManager(config)

        # ASSERT: Verify initialization
        assert manager.config == config
        assert manager.temp_dir == Path("/tmp/test_csv_cleaner")
        assert not manager._shutdown

        # Cleanup
        manager.cleanup_all()
        manager.shutdown()

    def test_create_temp_file(self):
        """TEST: should_create_secure_temporary_file_with_tracking"""
        # ARRANGE: Test parameters
        suffix = ".csv"
        prefix = "test_"
        tags = ["test", "csv"]

        # ACT: Create temp file
        file_path = self.temp_manager.create_temp_file(
            suffix=suffix,
            prefix=prefix,
            tags=tags
        )

        # ASSERT: Verify file creation and tracking
        assert file_path.exists()
        assert file_path.suffix == suffix
        assert file_path.name.startswith(prefix)

        file_info = self.temp_manager.get_file_info(file_path)
        assert file_info is not None
        assert file_info.path == file_path
        assert file_info.tags == tags
        assert file_info.cleanup_policy == "auto"

    def test_create_temp_file_with_custom_directory(self):
        """TEST: should_create_temp_file_in_custom_directory"""
        # ARRANGE: Custom directory
        custom_dir = Path(tempfile.mkdtemp())

        # ACT: Create temp file in custom directory
        file_path = self.temp_manager.create_temp_file(
            directory=custom_dir,
            suffix=".txt"
        )

        # ASSERT: Verify file location
        assert file_path.parent == custom_dir
        assert file_path.exists()

        # Cleanup
        shutil.rmtree(custom_dir)

    def test_create_temp_directory(self):
        """TEST: should_create_temporary_directory_with_tracking"""
        # ARRANGE: Test parameters
        prefix = "test_dir_"
        tags = ["directory", "test"]

        # ACT: Create temp directory
        dir_path = self.temp_manager.create_temp_directory(
            prefix=prefix,
            tags=tags
        )

        # ASSERT: Verify directory creation and tracking
        assert dir_path.exists()
        assert dir_path.is_dir()
        assert dir_path.name.startswith(prefix)

        dir_info = self.temp_manager.get_file_info(dir_path)
        assert dir_info is not None
        assert dir_info.path == dir_path
        assert dir_info.tags == tags
        assert dir_info.metadata["type"] == "directory"

    def test_temp_file_context_manager(self):
        """TEST: should_automatically_cleanup_file_in_context_manager"""
        # ARRANGE: Context manager parameters
        tags = ["context", "test"]

        # ACT: Use context manager
        with self.temp_manager.temp_file(tags=tags) as file_path:
            # Write some data
            file_path.write_text("test data")
            assert file_path.exists()
            assert file_path.read_text() == "test data"

        # ASSERT: File should be cleaned up automatically
        assert not file_path.exists()

        # Verify it's not tracked anymore
        file_info = self.temp_manager.get_file_info(file_path)
        assert file_info is None

    def test_temp_directory_context_manager(self):
        """TEST: should_automatically_cleanup_directory_in_context_manager"""
        # ARRANGE: Context manager parameters
        tags = ["context", "directory"]

        # ACT: Use context manager
        with self.temp_manager.temp_directory(tags=tags) as dir_path:
            # Create a file in the directory
            test_file = dir_path / "test.txt"
            test_file.write_text("test data")
            assert dir_path.exists()
            assert test_file.exists()

        # ASSERT: Directory should be cleaned up automatically
        assert not dir_path.exists()

    def test_cleanup_file(self):
        """TEST: should_cleanup_specific_temporary_file"""
        # ARRANGE: Create temp file
        file_path = self.temp_manager.create_temp_file(tags=["cleanup_test"])
        file_path.write_text("test data")
        assert file_path.exists()

        # ACT: Cleanup the file
        result = self.temp_manager.cleanup_file(file_path)

        # ASSERT: Verify cleanup
        assert result is True
        assert not file_path.exists()

        # Verify it's not tracked anymore
        file_info = self.temp_manager.get_file_info(file_path)
        assert file_info is None

    def test_cleanup_untracked_file(self):
        """TEST: should_return_false_when_cleaning_up_untracked_file"""
        # ARRANGE: Create untracked file
        untracked_file = Path(tempfile.mktemp())
        untracked_file.write_text("test data")

        # ACT: Try to cleanup untracked file
        result = self.temp_manager.cleanup_file(untracked_file)

        # ASSERT: Should return False
        assert result is False

        # Cleanup
        untracked_file.unlink()

    def test_cleanup_by_tags(self):
        """TEST: should_cleanup_files_with_matching_tags"""
        # ARRANGE: Create multiple files with different tags
        file1 = self.temp_manager.create_temp_file(tags=["tag1", "common"])
        file2 = self.temp_manager.create_temp_file(tags=["tag2", "common"])
        file3 = self.temp_manager.create_temp_file(tags=["tag3"])

        # ACT: Cleanup files with "common" tag
        cleaned_count = self.temp_manager.cleanup_by_tags(["common"])

        # ASSERT: Verify cleanup
        assert cleaned_count == 2
        assert not file1.exists()
        assert not file2.exists()
        assert file3.exists()  # Should still exist

    def test_cleanup_expired(self):
        """TEST: should_cleanup_files_older_than_specified_age"""
        # ARRANGE: Create files with different ages
        old_file = self.temp_manager.create_temp_file(tags=["old"])
        new_file = self.temp_manager.create_temp_file(tags=["new"])

        # Manually set old file creation time
        old_file_info = self.temp_manager.get_file_info(old_file)
        old_file_info.created_at = old_file_info.created_at.replace(year=2020)

        # ACT: Cleanup expired files (older than 1 hour)
        cleaned_count = self.temp_manager.cleanup_expired(max_age_hours=1)

        # ASSERT: Verify cleanup
        assert cleaned_count == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_cleanup_all(self):
        """TEST: should_cleanup_all_tracked_files"""
        # ARRANGE: Create multiple files
        file1 = self.temp_manager.create_temp_file(tags=["test1"])
        file2 = self.temp_manager.create_temp_file(tags=["test2"])
        dir1 = self.temp_manager.create_temp_directory(tags=["test3"])

        # ACT: Cleanup all files
        cleaned_count = self.temp_manager.cleanup_all()

        # ASSERT: Verify cleanup
        assert cleaned_count == 3
        assert not file1.exists()
        assert not file2.exists()
        assert not dir1.exists()

    def test_register_cleanup_handler(self):
        """TEST: should_call_custom_cleanup_handler"""
        # ARRANGE: Create temp file and custom handler
        file_path = self.temp_manager.create_temp_file(tags=["handler_test"])
        handler_called = False

        def custom_handler(path):
            nonlocal handler_called
            handler_called = True

        self.temp_manager.register_cleanup_handler(file_path, custom_handler)

        # ACT: Cleanup the file
        self.temp_manager.cleanup_file(file_path)

        # ASSERT: Verify handler was called
        assert handler_called

    def test_get_file_info(self):
        """TEST: should_return_file_info_for_tracked_file"""
        # ARRANGE: Create temp file
        file_path = self.temp_manager.create_temp_file(
            tags=["info_test"],
            metadata={"test_key": "test_value"}
        )

        # ACT: Get file info
        file_info = self.temp_manager.get_file_info(file_path)

        # ASSERT: Verify file info
        assert file_info is not None
        assert file_info.path == file_path
        assert file_info.tags == ["info_test"]
        assert file_info.metadata["test_key"] == "test_value"

    def test_list_temp_files(self):
        """TEST: should_list_tracked_files_with_optional_tag_filter"""
        # ARRANGE: Create files with different tags
        file1 = self.temp_manager.create_temp_file(tags=["tag1", "common"])
        file2 = self.temp_manager.create_temp_file(tags=["tag2", "common"])
        file3 = self.temp_manager.create_temp_file(tags=["tag3"])

        # ACT: List all files
        all_files = self.temp_manager.list_temp_files()

        # ACT: List files with specific tag
        tagged_files = self.temp_manager.list_temp_files(tags=["common"])

        # ASSERT: Verify listing
        assert len(all_files) == 3
        assert len(tagged_files) == 2

    def test_get_stats(self):
        """TEST: should_return_statistics_about_tracked_files"""
        # ARRANGE: Create files with different properties
        file1 = self.temp_manager.create_temp_file(tags=["stats_test"])
        file2 = self.temp_manager.create_temp_file(tags=["stats_test"])
        file1.write_text("data1")
        file2.write_text("data2")

        # Update file sizes in tracking
        file1_info = self.temp_manager.get_file_info(file1)
        file2_info = self.temp_manager.get_file_info(file2)
        if file1_info:
            file1_info.size_bytes = file1.stat().st_size
        if file2_info:
            file2_info.size_bytes = file2.stat().st_size

        # ACT: Get statistics
        stats = self.temp_manager.get_stats()

        # ASSERT: Verify statistics
        assert stats["total_files"] == 2
        assert stats["total_directories"] == 0
        assert stats["total_size_bytes"] > 0
        assert "stats_test" in stats["tag_counts"]
        assert stats["tag_counts"]["stats_test"] == 2

    def test_shutdown(self):
        """TEST: should_shutdown_manager_and_cleanup_all_files"""
        # ARRANGE: Create temp files
        file1 = self.temp_manager.create_temp_file(tags=["shutdown_test"])
        file2 = self.temp_manager.create_temp_file(tags=["shutdown_test"])

        # ACT: Shutdown manager
        self.temp_manager.shutdown()

        # ASSERT: Verify shutdown
        assert self.temp_manager._shutdown is True
        assert not file1.exists()
        assert not file2.exists()

    def test_error_handling_in_file_creation(self):
        """TEST: should_handle_errors_during_file_creation"""
        # ARRANGE: Mock tempfile to raise error
        with patch('tempfile.NamedTemporaryFile', side_effect=OSError("Permission denied")):
            # ACT & ASSERT: Should raise OSError
            with pytest.raises(OSError, match="Permission denied"):
                self.temp_manager.create_temp_file()

    def test_error_handling_in_cleanup(self):
        """TEST: should_handle_errors_during_cleanup"""
        # ARRANGE: Create temp file and mock unlink to raise error
        file_path = self.temp_manager.create_temp_file(tags=["error_test"])

        with patch.object(Path, 'unlink', side_effect=OSError("File busy")):
            # ACT: Try to cleanup
            result = self.temp_manager.cleanup_file(file_path)

            # ASSERT: Should return False on error
            assert result is False

    def test_thread_safety(self):
        """TEST: should_be_thread_safe_for_concurrent_operations"""
        # ARRANGE: Create multiple threads
        results = []
        errors = []

        def worker(thread_id):
            try:
                # Create temp file
                file_path = self.temp_manager.create_temp_file(
                    tags=[f"thread_{thread_id}"]
                )
                file_path.write_text(f"data from thread {thread_id}")

                # Get stats
                stats = self.temp_manager.get_stats()
                results.append((thread_id, stats["total_files"]))

                # Cleanup
                self.temp_manager.cleanup_file(file_path)
            except Exception as e:
                errors.append((thread_id, str(e)))

        # ACT: Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # ASSERT: Verify thread safety
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(results) == 5


class TestGlobalTempFileManager:
    """Test the global temp file manager functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset global instance
        import csv_cleaner.core.temp_file_manager as tfm
        tfm._temp_file_manager = None

    def teardown_method(self):
        """Clean up test files."""
        manager = get_temp_file_manager()
        manager.cleanup_all()
        manager.shutdown()

    def test_get_temp_file_manager_singleton(self):
        """TEST: should_return_same_instance_for_multiple_calls"""
        # ACT: Get manager multiple times
        manager1 = get_temp_file_manager()
        manager2 = get_temp_file_manager()

        # ASSERT: Should be the same instance
        assert manager1 is manager2

    def test_get_temp_file_manager_with_config(self):
        """TEST: should_use_config_for_first_initialization_only"""
        # ARRANGE: Custom config
        config = Config(temp_directory="/tmp/custom_test")

        # ACT: Get manager with config
        manager1 = get_temp_file_manager(config)

        # Get manager again without config
        manager2 = get_temp_file_manager()

        # ASSERT: Should be the same instance with original config
        assert manager1 is manager2
        assert manager1.temp_dir == Path("/tmp/custom_test")

    def test_cleanup_global_temp_files(self):
        """TEST: should_cleanup_all_global_temp_files"""
        # ARRANGE: Create temp files using global manager
        manager = get_temp_file_manager()
        file1 = manager.create_temp_file(tags=["global_test"])
        file2 = manager.create_temp_file(tags=["global_test"])

        # ACT: Cleanup global files
        from csv_cleaner.core.temp_file_manager import cleanup_global_temp_files
        cleanup_global_temp_files()

        # ASSERT: Files should be cleaned up
        assert not file1.exists()
        assert not file2.exists()
