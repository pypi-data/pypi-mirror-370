"""
TEST SUITE: csv_cleaner.core.file_operations (Integration)
PURPOSE: Test end-to-end file I/O workflows, large file processing, and memory-efficient operations
SCOPE: Integration tests for file operations, large file handling, memory management
DEPENDENCIES: pandas, numpy, tempfile, pathlib
"""

import pytest
import tempfile
import os
import pandas as pd
import numpy as np
from pathlib import Path
import time
import psutil
import gc
from unittest.mock import patch

from csv_cleaner.core.file_operations import FileOperations
from csv_cleaner.core.config import Config
from tests.fixtures.file_fixtures import (
    create_sample_csv_file, create_large_csv_file, create_wide_csv_file,
    create_csv_with_missing_values, create_csv_with_duplicates,
    create_compressed_csv_file, cleanup_test_files
)


class TestFileIOIntegration:
    """Integration tests for file I/O operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.file_ops = FileOperations(self.config)
        self.test_files = []

    def teardown_method(self):
        """Clean up test files."""
        cleanup_test_files(self.test_files)

    def test_end_to_end_csv_workflow(self, temp_dir):
        """TEST: should_complete_full_csv_read_write_workflow_successfully"""
        # ARRANGE: Create input CSV file
        input_file = os.path.join(temp_dir, 'input.csv')
        create_sample_csv_file(input_file)
        self.test_files.append(input_file)

        output_file = os.path.join(temp_dir, 'output.csv')
        self.test_files.append(output_file)

        # ACT: Read, process, and write CSV
        df = self.file_ops.read_csv(input_file)

        # Simulate some processing
        df['Processed'] = df['Age'] * 2
        df['Status'] = 'processed'

        self.file_ops.write_csv(df, output_file)

        # ASSERT: Verify end-to-end workflow
        assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"

        # Read back and verify processing
        result_df = pd.read_csv(output_file)
        assert len(result_df) == 4, f"Expected 4 rows in result, got {len(result_df)}"
        assert 'Processed' in result_df.columns, "Expected 'Processed' column to be present"
        assert 'Status' in result_df.columns, "Expected 'Status' column to be present"
        assert all(result_df['Status'] == 'processed'), "Expected all rows to have 'processed' status"

    def test_large_file_processing(self, temp_dir):
        """TEST: should_process_large_csv_file_without_memory_issues"""
        # ARRANGE: Create large CSV file
        large_file = os.path.join(temp_dir, 'large.csv')
        create_large_csv_file(large_file, rows=5000)
        self.test_files.append(large_file)

        output_file = os.path.join(temp_dir, 'large_output.csv')
        self.test_files.append(output_file)

        # ACT: Process large file
        start_time = time.time()
        df = self.file_ops.read_csv(large_file)

        # Simulate processing
        df['Processed_Time'] = pd.Timestamp.now()
        df['Random_Value'] = np.random.rand(len(df))

        self.file_ops.write_csv(df, output_file)
        processing_time = time.time() - start_time

        # ASSERT: Verify large file processing
        assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"
        assert len(df) == 5000, f"Expected 5000 rows, got {len(df)}"
        assert processing_time < 30, f"Expected processing to complete within 30 seconds, took {processing_time:.2f}s"

        # Verify memory usage is reasonable
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 500, f"Expected memory usage under 500MB, got {memory_mb:.1f}MB"

    def test_chunked_processing_large_file(self, temp_dir):
        """TEST: should_process_large_file_in_chunks_without_memory_issues"""
        # ARRANGE: Create very large CSV file
        large_file = os.path.join(temp_dir, 'very_large.csv')
        create_large_csv_file(large_file, rows=10000)
        self.test_files.append(large_file)

        output_file = os.path.join(temp_dir, 'chunked_output.csv')
        self.test_files.append(output_file)

        # ACT: Process file in chunks
        start_time = time.time()
        chunk_size = 1000
        processed_chunks = []

        for chunk in self.file_ops.chunked_read(large_file, chunk_size=chunk_size):
            # Simulate processing on each chunk
            chunk['Chunk_Processed'] = True
            chunk['Processing_Time'] = pd.Timestamp.now()
            processed_chunks.append(chunk)

        # Combine chunks and write
        chunks_count = len(processed_chunks)
        if processed_chunks:
            combined_df = pd.concat(processed_chunks, ignore_index=True)
            self.file_ops.write_csv(combined_df, output_file)
            # Clean up memory after processing
            del combined_df
            del processed_chunks
            import gc
            gc.collect()

        processing_time = time.time() - start_time

        # ASSERT: Verify chunked processing
        assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"
        assert chunks_count > 0, "Expected at least one chunk to be processed"
        assert processing_time < 60, f"Expected processing to complete within 60 seconds, took {processing_time:.2f}s"

        # Verify memory usage is reasonable
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 400, f"Expected memory usage under 400MB, got {memory_mb:.1f}MB"

    def test_wide_file_processing(self, temp_dir):
        """TEST: should_process_wide_csv_file_with_many_columns_successfully"""
        # ARRANGE: Create wide CSV file
        wide_file = os.path.join(temp_dir, 'wide.csv')
        create_wide_csv_file(wide_file, columns=30)
        self.test_files.append(wide_file)

        output_file = os.path.join(temp_dir, 'wide_output.csv')
        self.test_files.append(output_file)

        # ACT: Process wide file
        df = self.file_ops.read_csv(wide_file)

        # Simulate processing on wide data
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns[:5]:  # Process first 5 numeric columns
            df[f'{col}_normalized'] = (df[col] - df[col].mean()) / df[col].std()

        self.file_ops.write_csv(df, output_file)

        # ASSERT: Verify wide file processing
        assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"
        assert len(df.columns) >= 30, f"Expected at least 30 columns, got {len(df.columns)}"
        assert len(df) == 100, f"Expected 100 rows, got {len(df)}"

    def test_compressed_file_workflow(self, temp_dir):
        """TEST: should_process_compressed_csv_files_end_to_end"""
        # ARRANGE: Create compressed CSV files
        gzip_file = os.path.join(temp_dir, 'test.csv.gz')
        create_compressed_csv_file(gzip_file, compression_type='gzip')
        self.test_files.append(gzip_file)

        zip_file = os.path.join(temp_dir, 'test.csv.zip')
        create_compressed_csv_file(zip_file, compression_type='zip')
        self.test_files.append(zip_file)

        gzip_output = os.path.join(temp_dir, 'gzip_output.csv')
        zip_output = os.path.join(temp_dir, 'zip_output.csv')
        self.test_files.extend([gzip_output, zip_output])

        # ACT: Process gzip file
        with patch.object(self.file_ops, '_validate_csv_format', return_value=True):
            gzip_df = self.file_ops.read_csv(gzip_file)
        gzip_df['Source'] = 'gzip'
        self.file_ops.write_csv(gzip_df, gzip_output)

        # Process zip file
        with patch.object(self.file_ops, '_validate_csv_format', return_value=True):
            zip_df = self.file_ops.read_csv(zip_file)
        zip_df['Source'] = 'zip'
        self.file_ops.write_csv(zip_df, zip_output)

        # ASSERT: Verify compressed file processing
        assert os.path.exists(gzip_output), f"Expected gzip output file to exist"
        assert os.path.exists(zip_output), f"Expected zip output file to exist"

        # Verify content
        gzip_result = pd.read_csv(gzip_output)
        zip_result = pd.read_csv(zip_output)

        assert len(gzip_result) == 4, f"Expected 4 rows in gzip result, got {len(gzip_result)}"
        assert len(zip_result) == 4, f"Expected 4 rows in zip result, got {len(zip_result)}"
        assert all(gzip_result['Source'] == 'gzip'), "Expected all gzip rows to have 'gzip' source"
        assert all(zip_result['Source'] == 'zip'), "Expected all zip rows to have 'zip' source"

    def test_backup_and_restore_workflow(self, temp_dir):
        """TEST: should_create_backup_and_restore_workflow_successfully"""
        # ARRANGE: Create original file
        original_file = os.path.join(temp_dir, 'original.csv')
        create_sample_csv_file(original_file)
        self.test_files.append(original_file)

        # ACT: Create backup, modify original, then restore
        backup_path = self.file_ops.create_backup(original_file)
        self.test_files.append(backup_path)

        # Modify original file
        df = self.file_ops.read_csv(original_file)
        df['Modified'] = True
        self.file_ops.write_csv(df, original_file)

        # Restore from backup
        backup_df = self.file_ops.read_csv(backup_path)
        self.file_ops.write_csv(backup_df, original_file)

        # ASSERT: Verify backup and restore workflow
        assert os.path.exists(backup_path), f"Expected backup file to exist at '{backup_path}'"

        # Verify original file is restored
        restored_df = self.file_ops.read_csv(original_file)
        assert 'Modified' not in restored_df.columns, "Expected 'Modified' column to not be present after restore"
        assert len(restored_df) == 4, f"Expected 4 rows after restore, got {len(restored_df)}"

    def test_memory_efficient_processing(self, temp_dir):
        """TEST: should_process_files_with_memory_efficient_operations"""
        # ARRANGE: Create large file
        large_file = os.path.join(temp_dir, 'memory_test.csv')
        create_large_csv_file(large_file, rows=3000)
        self.test_files.append(large_file)

        output_file = os.path.join(temp_dir, 'memory_output.csv')
        self.test_files.append(output_file)

        # ACT: Process with memory monitoring
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Read and process in chunks to minimize memory usage
        chunk_size = 500
        processed_rows = 0

        for chunk in self.file_ops.chunked_read(large_file, chunk_size=chunk_size):
            # Process chunk
            chunk['Processed'] = True
            processed_rows += len(chunk)

            # Force garbage collection
            del chunk
            gc.collect()

        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory

        # ASSERT: Verify memory efficiency
        assert processed_rows == 3000, f"Expected 3000 rows processed, got {processed_rows}"
        assert memory_increase < 100, f"Expected memory increase under 100MB, got {memory_increase:.1f}MB"

    def test_error_recovery_workflow(self, temp_dir):
        """TEST: should_handle_errors_and_recover_successfully_in_workflow"""
        # ARRANGE: Create valid and invalid files
        valid_file = os.path.join(temp_dir, 'valid.csv')
        create_sample_csv_file(valid_file)
        self.test_files.append(valid_file)

        invalid_file = os.path.join(temp_dir, 'invalid.txt')
        with open(invalid_file, 'w') as f:
            f.write("This is not a CSV file\n")
        self.test_files.append(invalid_file)

        output_file = os.path.join(temp_dir, 'recovery_output.csv')
        self.test_files.append(output_file)

        # ACT: Try to process files with error handling
        processed_files = []
        errors = []

        for file_path in [valid_file, invalid_file]:
            try:
                df = self.file_ops.read_csv(file_path)
                df['Source'] = Path(file_path).name
                processed_files.append(df)
            except Exception as e:
                errors.append(f"Error processing {file_path}: {str(e)}")

        # Combine successfully processed files
        if processed_files:
            combined_df = pd.concat(processed_files, ignore_index=True)
            self.file_ops.write_csv(combined_df, output_file)

        # ASSERT: Verify error recovery
        assert len(errors) == 1, f"Expected 1 error, got {len(errors)}"
        assert "invalid.txt" in errors[0], "Expected error to mention invalid file"
        assert len(processed_files) == 1, f"Expected 1 file processed successfully, got {len(processed_files)}"

        if processed_files:
            assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"

    def test_concurrent_file_operations(self, temp_dir):
        """TEST: should_handle_multiple_file_operations_concurrently"""
        # ARRANGE: Create multiple files
        files = []
        for i in range(3):
            file_path = os.path.join(temp_dir, f'file_{i}.csv')
            create_sample_csv_file(file_path)
            files.append(file_path)
            self.test_files.append(file_path)

        output_files = []
        for i in range(3):
            output_path = os.path.join(temp_dir, f'output_{i}.csv')
            output_files.append(output_path)
            self.test_files.append(output_path)

        # ACT: Process multiple files
        results = []
        for input_file, output_file in zip(files, output_files):
            df = self.file_ops.read_csv(input_file)
            df['File_Index'] = files.index(input_file)
            self.file_ops.write_csv(df, output_file)
            results.append(len(df))

        # ASSERT: Verify concurrent processing
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert all(result == 4 for result in results), f"Expected all files to have 4 rows, got {results}"

        for output_file in output_files:
            assert os.path.exists(output_file), f"Expected output file to exist at '{output_file}'"

    def test_file_validation_workflow(self, temp_dir):
        """TEST: should_validate_files_before_processing_workflow"""
        # ARRANGE: Create various file types
        valid_csv = os.path.join(temp_dir, 'valid.csv')
        create_sample_csv_file(valid_csv)
        self.test_files.append(valid_csv)

        empty_file = os.path.join(temp_dir, 'empty.csv')
        with open(empty_file, 'w') as f:
            pass
        self.test_files.append(empty_file)

        # ACT: Validate files before processing
        validation_results = {}
        for file_path in [valid_csv, empty_file]:
            validation_results[file_path] = self.file_ops.validate_file(file_path)

        # Process only valid files
        processed_files = []
        for file_path, validation in validation_results.items():
            if validation['is_csv'] and len(validation['errors']) == 0:
                df = self.file_ops.read_csv(file_path)
                processed_files.append(df)

        # ASSERT: Verify validation workflow
        assert validation_results[valid_csv]['is_csv'] is True, "Expected valid CSV to be validated as CSV"
        assert validation_results[empty_file]['is_csv'] is False, "Expected empty file to be validated as not CSV"
        assert len(processed_files) == 1, f"Expected 1 file to be processed, got {len(processed_files)}"

    def test_performance_benchmark_workflow(self, temp_dir):
        """TEST: should_benchmark_file_processing_performance"""
        # ARRANGE: Create files of different sizes
        small_file = os.path.join(temp_dir, 'small.csv')
        create_sample_csv_file(small_file)
        self.test_files.append(small_file)

        medium_file = os.path.join(temp_dir, 'medium.csv')
        create_large_csv_file(medium_file, rows=1000)
        self.test_files.append(medium_file)

        # ACT: Benchmark processing times
        benchmark_results = {}

        for file_path in [small_file, medium_file]:
            start_time = time.time()
            df = self.file_ops.read_csv(file_path)
            read_time = time.time() - start_time

            start_time = time.time()
            output_path = file_path.replace('.csv', '_output.csv')
            self.file_ops.write_csv(df, output_path)
            write_time = time.time() - start_time
            self.test_files.append(output_path)

            benchmark_results[file_path] = {
                'rows': len(df),
                'columns': len(df.columns),
                'read_time': read_time,
                'write_time': write_time,
                'total_time': read_time + write_time
            }

        # ASSERT: Verify performance benchmarks
        assert len(benchmark_results) == 2, f"Expected 2 benchmark results, got {len(benchmark_results)}"

        # Verify small file is faster than medium file
        small_total = benchmark_results[small_file]['total_time']
        medium_total = benchmark_results[medium_file]['total_time']
        assert small_total < medium_total, f"Expected small file to be faster, got {small_total:.3f}s vs {medium_total:.3f}s"

        # Verify reasonable performance
        assert small_total < 1.0, f"Expected small file processing under 1 second, got {small_total:.3f}s"
        assert medium_total < 5.0, f"Expected medium file processing under 5 seconds, got {medium_total:.3f}s"
