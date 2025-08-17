#!/usr/bin/env python3
"""
Performance Optimization Example

This example demonstrates how to optimize CSV Data Cleaner performance
for large files and high-throughput scenarios.

Key concepts covered:
- Large file processing with chunking
- Memory optimization
- Parallel processing
- Performance monitoring
- Batch processing
- Resource management

Best practices for:
- Files > 1GB
- High-frequency processing
- Memory-constrained environments
- Multi-core systems
"""

import os
import time
import psutil
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import multiprocessing as mp

from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config
from csv_cleaner.core.performance_manager import PerformanceManager


def create_large_sample_data(size_mb: int = 100):
    """Create large sample data for performance testing."""
    print(f"📊 Creating {size_mb}MB sample data...")

    # Calculate rows needed (roughly 1MB per 10,000 rows)
    rows_needed = int(size_mb * 10000)

    np.random.seed(42)

    # Create large dataset with various data types
    data = {
        'id': range(1, rows_needed + 1),
        'user_id': np.random.randint(1, 1000000, rows_needed),
        'name': [f'User_{i}' for i in range(1, rows_needed + 1)],
        'email': [f'user{i}@example.com' for i in range(1, rows_needed + 1)],
        'age': np.random.randint(18, 80, rows_needed),
        'salary': np.random.randint(30000, 150000, rows_needed),
        'score': np.random.uniform(0, 100, rows_needed),
        'status': np.random.choice(['active', 'inactive', 'pending'], rows_needed),
        'category': np.random.choice(['A', 'B', 'C', 'D'], rows_needed),
        'created_at': pd.date_range('2020-01-01', periods=rows_needed, freq='s'),
        'description': [f'Description for user {i}' for i in range(1, rows_needed + 1)],
        'tags': [f'tag_{np.random.randint(1, 100)}' for _ in range(rows_needed)],
        'rating': np.random.randint(1, 6, rows_needed),
        'price': np.random.uniform(10, 1000, rows_needed),
        'quantity': np.random.randint(1, 100, rows_needed)
    }

    df = pd.DataFrame(data)

    # Introduce data quality issues
    # 1. Duplicates (5% of data)
    duplicate_count = int(rows_needed * 0.05)
    duplicate_indices = np.random.choice(range(rows_needed), duplicate_count, replace=False)
    df_duplicates = df.iloc[duplicate_indices].copy()
    df_duplicates['name'] = df_duplicates['name'].str.upper()
    df = pd.concat([df, df_duplicates])

    # 2. Missing values (10% of data) - use a simpler approach
    total_rows = len(df)
    for col in ['age', 'salary', 'email', 'description']:
        # Select random 10% of rows for missing values
        missing_count = total_rows // 10
        missing_indices = np.random.choice(total_rows, missing_count, replace=False)
        df.iloc[missing_indices, df.columns.get_loc(col)] = np.nan

    # 3. Inconsistent formatting
    format_count = int(total_rows * 0.03)
    format_indices = np.random.choice(total_rows, format_count, replace=False)
    df.iloc[format_indices, df.columns.get_loc('name')] = df.iloc[format_indices]['name'].str.lower()

    return df


def monitor_memory_usage():
    """Monitor current memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent()
    }


def performance_optimization_example():
    """Demonstrate performance optimization techniques."""
    print("\n" + "=" * 60)
    print("⚡ Performance Optimization Example")
    print("=" * 60)

    # Create large sample data
    print("\n📊 Creating large sample dataset...")
    df = create_large_sample_data(size_mb=50)  # 50MB dataset

    # Save to file
    input_file = "large_sample_data.csv"
    df.to_csv(input_file, index=False)

    file_size_mb = os.path.getsize(input_file) / 1024 / 1024
    print(f"💾 Saved {file_size_mb:.1f}MB file: {input_file}")
    print(f"📈 Dataset shape: {df.shape}")

    # Monitor initial memory
    initial_memory = monitor_memory_usage()
    print(f"🧠 Initial memory usage: {initial_memory['rss_mb']:.1f}MB")

    return df, input_file


def chunked_processing_example():
    """Demonstrate chunked processing for large files."""
    print("\n" + "=" * 60)
    print("📦 Chunked Processing Example")
    print("=" * 60)

    # Create sample data
    df, input_file = performance_optimization_example()

    # Configure for chunked processing
    config = Config(
        # Performance settings
        max_memory_gb=1.0,  # Limit memory usage
        chunk_size=5000,    # Process 5K rows at a time
        enable_chunked_processing=True,
        enable_parallel_processing=True,
        max_workers=4,

        # Monitoring
        performance_monitoring=True,
        auto_optimize_chunk_size=True
    )

    print("\n⚙️ Configuration for chunked processing:")
    print(f"   💾 Max memory: {config.max_memory_gb}GB")
    print(f"   📦 Chunk size: {config.chunk_size:,} rows")
    print(f"   🔄 Parallel processing: {config.enable_parallel_processing}")
    print(f"   👥 Max workers: {config.max_workers}")
    print(f"   📊 Performance monitoring: {config.performance_monitoring}")

    # Initialize cleaner with optimized config
    cleaner = CSVCleaner(config)

    # Define operations
    operations = ["remove_duplicates", "fill_missing", "clean_names"]

    print(f"\n🎯 Cleaning operations: {', '.join(operations)}")

    # Monitor memory before processing
    memory_before = monitor_memory_usage()
    print(f"🧠 Memory before processing: {memory_before['rss_mb']:.1f}MB")

    # Process with chunking
    start_time = time.time()

    try:
        output_file = "chunked_cleaned_data.csv"
        summary = cleaner.clean_file(input_file, output_file, operations)

        processing_time = time.time() - start_time
        memory_after = monitor_memory_usage()

        print(f"\n✅ Chunked processing completed!")
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"🧠 Memory after processing: {memory_after['rss_mb']:.1f}MB")
        print(f"📈 Memory increase: {memory_after['rss_mb'] - memory_before['rss_mb']:.1f}MB")

        # Display summary
        print(f"\n📊 Processing Summary:")
        print(f"   📈 Rows processed: {summary.get('rows_processed', 'N/A'):,}")
        print(f"   🗑️  Rows removed: {summary.get('rows_removed', 'N/A'):,}")
        print(f"   🗑️  Columns removed: {summary.get('columns_removed', 'N/A')}")
        print(f"   ✅ Success: {summary.get('success', 'N/A')}")

        # Check output file
        if os.path.exists(output_file):
            output_size_mb = os.path.getsize(output_file) / 1024 / 1024
            print(f"💾 Output file size: {output_size_mb:.1f}MB")

        return summary

    except Exception as e:
        print(f"❌ Error during chunked processing: {e}")
        return None


def parallel_processing_example():
    """Demonstrate parallel processing optimization."""
    print("\n" + "=" * 60)
    print("🔄 Parallel Processing Example")
    print("=" * 60)

    # Create sample data
    df, input_file = performance_optimization_example()

    # Test different worker configurations
    worker_configs = [1, 2, 4, 8]
    results = {}

    print(f"\n🧪 Testing parallel processing with different worker counts...")
    print(f"🖥️  Available CPU cores: {mp.cpu_count()}")

    for workers in worker_configs:
        print(f"\n🔧 Testing with {workers} worker(s)...")

        # Configure cleaner
        config = Config(
            max_memory_gb=2.0,
            chunk_size=10000,
            enable_parallel_processing=True,
            max_workers=workers,
            performance_monitoring=True
        )

        cleaner = CSVCleaner(config)

        # Monitor memory
        memory_before = monitor_memory_usage()

        # Process file
        start_time = time.time()

        try:
            output_file = f"parallel_cleaned_{workers}workers.csv"
            summary = cleaner.clean_file(input_file, output_file, operations=["remove_duplicates", "fill_missing"])

            processing_time = time.time() - start_time
            memory_after = monitor_memory_usage()

            results[workers] = {
                'processing_time': processing_time,
                'memory_usage': memory_after['rss_mb'],
                'memory_increase': memory_after['rss_mb'] - memory_before['rss_mb'],
                'success': True
            }

            print(f"   ✅ Completed in {processing_time:.2f}s")
            print(f"   🧠 Memory usage: {memory_after['rss_mb']:.1f}MB")

        except Exception as e:
            results[workers] = {
                'processing_time': None,
                'memory_usage': None,
                'memory_increase': None,
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Failed: {e}")

    # Display results comparison
    print(f"\n📊 Parallel Processing Results:")
    print("-" * 50)
    print(f"{'Workers':<8} {'Time (s)':<10} {'Memory (MB)':<12} {'Success':<8}")
    print("-" * 50)

    for workers, result in results.items():
        if result['success']:
            print(f"{workers:<8} {result['processing_time']:<10.2f} {result['memory_usage']:<12.1f} {'✅':<8}")
        else:
            print(f"{workers:<8} {'N/A':<10} {'N/A':<12} {'❌':<8}")

    # Find optimal configuration
    successful_results = {k: v for k, v in results.items() if v['success']}
    if successful_results:
        fastest = min(successful_results.items(), key=lambda x: x[1]['processing_time'])
        print(f"\n🏆 Fastest configuration: {fastest[0]} workers ({fastest[1]['processing_time']:.2f}s)")

    return results


def memory_optimization_example():
    """Demonstrate memory optimization techniques."""
    print("\n" + "=" * 60)
    print("🧠 Memory Optimization Example")
    print("=" * 60)

    # Create sample data
    df, input_file = performance_optimization_example()

    # Test different memory configurations
    memory_configs = [0.5, 1.0, 2.0, 4.0]  # GB
    results = {}

    print(f"\n🧪 Testing memory optimization with different limits...")
    print(f"🖥️  System memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB")

    for memory_gb in memory_configs:
        print(f"\n🔧 Testing with {memory_gb}GB memory limit...")

        # Configure cleaner
        config = Config(
            max_memory_gb=memory_gb,
            chunk_size=5000,
            enable_chunked_processing=True,
            enable_parallel_processing=True,
            max_workers=4,
            performance_monitoring=True
        )

        cleaner = CSVCleaner(config)

        # Monitor memory
        memory_before = monitor_memory_usage()

        # Process file
        start_time = time.time()

        try:
            output_file = f"memory_optimized_{int(memory_gb*1000)}mb.csv"
            summary = cleaner.clean_file(input_file, output_file, operations=["remove_duplicates", "fill_missing"])

            processing_time = time.time() - start_time
            memory_after = monitor_memory_usage()

            results[memory_gb] = {
                'processing_time': processing_time,
                'peak_memory': memory_after['rss_mb'],
                'memory_efficiency': memory_after['rss_mb'] / (memory_gb * 1024) * 100,
                'success': True
            }

            print(f"   ✅ Completed in {processing_time:.2f}s")
            print(f"   🧠 Peak memory: {memory_after['rss_mb']:.1f}MB")
            print(f"   📊 Memory efficiency: {results[memory_gb]['memory_efficiency']:.1f}%")

        except Exception as e:
            results[memory_gb] = {
                'processing_time': None,
                'peak_memory': None,
                'memory_efficiency': None,
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Failed: {e}")

    # Display results
    print(f"\n📊 Memory Optimization Results:")
    print("-" * 60)
    print(f"{'Limit (GB)':<10} {'Time (s)':<10} {'Peak (MB)':<10} {'Efficiency':<12} {'Success':<8}")
    print("-" * 60)

    for memory_gb, result in results.items():
        if result['success']:
            print(f"{memory_gb:<10} {result['processing_time']:<10.2f} {result['peak_memory']:<10.1f} {result['memory_efficiency']:<12.1f} {'✅':<8}")
        else:
            print(f"{memory_gb:<10} {'N/A':<10} {'N/A':<10} {'N/A':<12} {'❌':<8}")

    return results


def batch_processing_example():
    """Demonstrate batch processing for multiple files."""
    print("\n" + "=" * 60)
    print("📚 Batch Processing Example")
    print("=" * 60)

    # Create multiple sample files
    print("\n📁 Creating multiple sample files for batch processing...")

    file_paths = []
    for i in range(5):
        # Create smaller datasets for batch processing
        df = create_large_sample_data(size_mb=10)  # 10MB each
        file_path = f"batch_file_{i+1}.csv"
        df.to_csv(file_path, index=False)
        file_paths.append(file_path)
        print(f"   📄 Created: {file_path} ({os.path.getsize(file_path) / 1024 / 1024:.1f}MB)")

    # Configure for batch processing
    config = Config(
        max_memory_gb=2.0,
        chunk_size=5000,
        enable_parallel_processing=True,
        max_workers=4,
        performance_monitoring=True
    )

    cleaner = CSVCleaner(config)
    operations = ["remove_duplicates", "fill_missing", "clean_names"]

    print(f"\n🎯 Batch processing {len(file_paths)} files...")
    print(f"🔧 Operations: {', '.join(operations)}")

    # Process files in batch
    start_time = time.time()
    batch_results = []

    for i, input_file in enumerate(file_paths, 1):
        print(f"\n📄 Processing file {i}/{len(file_paths)}: {input_file}")

        try:
            output_file = input_file.replace('.csv', '_cleaned.csv')
            summary = cleaner.clean_file(input_file, output_file, operations)

            batch_results.append({
                'input_file': input_file,
                'output_file': output_file,
                'success': True,
                'summary': summary
            })

            print(f"   ✅ Completed successfully")

        except Exception as e:
            batch_results.append({
                'input_file': input_file,
                'success': False,
                'error': str(e)
            })
            print(f"   ❌ Failed: {e}")

    total_time = time.time() - start_time

    # Display batch results
    print(f"\n📊 Batch Processing Summary:")
    print(f"⏱️  Total processing time: {total_time:.2f} seconds")
    print(f"📁 Files processed: {len(file_paths)}")
    print(f"✅ Successful: {sum(1 for r in batch_results if r['success'])}")
    print(f"❌ Failed: {sum(1 for r in batch_results if not r['success'])}")
    print(f"📈 Average time per file: {total_time / len(file_paths):.2f} seconds")

    # Show individual results
    print(f"\n📋 Individual File Results:")
    for result in batch_results:
        if result['success']:
            summary = result['summary']
            rows_processed = summary.get('rows_processed', 'N/A')
            if isinstance(rows_processed, int):
                print(f"   ✅ {result['input_file']}: {rows_processed:,} rows processed")
            else:
                print(f"   ✅ {result['input_file']}: {rows_processed} rows processed")
        else:
            print(f"   ❌ {result['input_file']}: {result['error']}")

    return batch_results


def performance_monitoring_example():
    """Demonstrate performance monitoring capabilities."""
    print("\n" + "=" * 60)
    print("📊 Performance Monitoring Example")
    print("=" * 60)

    # Create sample data
    df, input_file = performance_optimization_example()

    # Configure with detailed monitoring
    config = Config(
        max_memory_gb=2.0,
        chunk_size=10000,
        enable_parallel_processing=True,
        max_workers=4,
        performance_monitoring=True,
        auto_optimize_chunk_size=True
    )

    cleaner = CSVCleaner(config)

    print("\n🔍 Starting performance monitoring...")

    # Monitor system resources
    initial_cpu = psutil.cpu_percent()
    initial_memory = monitor_memory_usage()

    print(f"🖥️  Initial CPU usage: {initial_cpu:.1f}%")
    print(f"🧠 Initial memory: {initial_memory['rss_mb']:.1f}MB")

    # Process with monitoring
    start_time = time.time()

    try:
        output_file = "monitored_cleaned_data.csv"
        summary = cleaner.clean_file(input_file, output_file, operations=["remove_duplicates", "fill_missing"])

        processing_time = time.time() - start_time

        # Final measurements
        final_cpu = psutil.cpu_percent()
        final_memory = monitor_memory_usage()

        print(f"\n📊 Performance Monitoring Results:")
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"🖥️  CPU usage: {initial_cpu:.1f}% → {final_cpu:.1f}%")
        print(f"🧠 Memory usage: {initial_memory['rss_mb']:.1f}MB → {final_memory['rss_mb']:.1f}MB")
        print(f"📈 Memory increase: {final_memory['rss_mb'] - initial_memory['rss_mb']:.1f}MB")

        # Performance metrics
        if 'performance_metrics' in summary:
            metrics = summary['performance_metrics']
            print(f"\n📈 Detailed Performance Metrics:")
            print(f"   🔄 Chunks processed: {metrics.get('chunks_processed', 'N/A')}")
            print(f"   ⚡ Average chunk time: {metrics.get('avg_chunk_time', 'N/A'):.3f}s")
            print(f"   🧠 Peak memory usage: {metrics.get('peak_memory_mb', 'N/A'):.1f}MB")
            print(f"   🔄 Parallel efficiency: {metrics.get('parallel_efficiency', 'N/A'):.1f}%")

        return summary

    except Exception as e:
        print(f"❌ Error during monitored processing: {e}")
        return None


def main():
    """Run all performance optimization examples."""
    print("🚀 Starting CSV Data Cleaner Performance Examples")
    print("=" * 70)

    # Example 1: Chunked Processing
    chunked_processing_example()

    # Example 2: Parallel Processing
    parallel_processing_example()

    # Example 3: Memory Optimization
    memory_optimization_example()

    # Example 4: Batch Processing
    batch_processing_example()

    # Example 5: Performance Monitoring
    performance_monitoring_example()

    print("\n" + "=" * 70)
    print("✅ All performance examples completed!")
    print("\n📚 Performance Optimization Best Practices:")
    print("   - Use chunked processing for files > 1GB")
    print("   - Enable parallel processing for multi-core systems")
    print("   - Monitor memory usage and set appropriate limits")
    print("   - Use batch processing for multiple files")
    print("   - Enable performance monitoring for optimization")
    print("   - Adjust chunk size based on available memory")

    print("\n🔧 Configuration Recommendations:")
    print("   - Small files (< 100MB): 1-2 workers, 1GB memory")
    print("   - Medium files (100MB-1GB): 4 workers, 2GB memory")
    print("   - Large files (> 1GB): 4-8 workers, 4GB+ memory")
    print("   - Memory-constrained: Reduce chunk size, disable parallel")
    print("   - High-throughput: Increase workers, optimize chunk size")

    print("\n📊 Next Steps:")
    print("   - Profile your specific datasets")
    print("   - Test different configurations")
    print("   - Monitor system resources")
    print("   - Optimize based on your hardware")
    print("   - Consider using SSDs for large files")


if __name__ == "__main__":
    main()
