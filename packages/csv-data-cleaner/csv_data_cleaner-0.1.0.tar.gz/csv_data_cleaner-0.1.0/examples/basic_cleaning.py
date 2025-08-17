#!/usr/bin/env python3
"""
Basic CSV Data Cleaning Example

This example demonstrates the fundamental usage of the CSV Data Cleaner library
for simple data cleaning operations.

Key concepts covered:
- Initializing the cleaner
- Basic cleaning operations
- Working with file paths
- Understanding cleaning results
"""

import pandas as pd
import numpy as np
from pathlib import Path
from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config


def create_sample_data():
    """Create sample messy data for demonstration."""
    np.random.seed(42)

    # Create sample data with common issues
    data = {
        'customer_id': range(1, 101),
        'customer_name': [f'Customer_{i}' for i in range(1, 101)],
        'email': [f'customer{i}@example.com' for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'salary': np.random.randint(30000, 150000, 100),
        'join_date': pd.date_range('2020-01-01', periods=100, freq='D'),
        'status': np.random.choice(['active', 'inactive', 'pending'], 100),
        'notes': [f'Note for customer {i}' for i in range(1, 101)]
    }

    df = pd.DataFrame(data)

    # Introduce common data quality issues
    # 1. Duplicate rows
    df = pd.concat([df, df.iloc[:5]])  # Add 5 duplicate rows

    # 2. Missing values
    df.loc[10:15, 'age'] = np.nan
    df.loc[20:25, 'salary'] = np.nan
    df.loc[30:35, 'email'] = ''

    # 3. Inconsistent text
    df.loc[40:45, 'customer_name'] = df.loc[40:45, 'customer_name'].str.upper()
    df.loc[50:55, 'customer_name'] = df.loc[50:55, 'customer_name'].str.lower()

    # 4. Mixed data types
    df.loc[60:65, 'age'] = 'unknown'
    df.loc[70:75, 'salary'] = 'N/A'

    return df


def basic_cleaning_example():
    """Demonstrate basic cleaning operations."""
    print("🧹 CSV Data Cleaner - Basic Cleaning Example")
    print("=" * 50)

    # Step 1: Create sample data
    print("\n1️⃣ Creating sample data with common issues...")
    df = create_sample_data()

    # Save original data
    input_file = "sample_data.csv"
    df.to_csv(input_file, index=False)
    print(f"   📁 Saved sample data to: {input_file}")
    print(f"   📊 Original data shape: {df.shape}")
    print(f"   🔍 Issues detected:")
    print(f"      - Duplicate rows: {df.duplicated().sum()}")
    print(f"      - Missing values: {df.isnull().sum().sum()}")
    print(f"      - Empty strings: {(df == '').sum().sum()}")

    # Step 2: Initialize the cleaner
    print("\n2️⃣ Initializing CSV Cleaner...")
    cleaner = CSVCleaner()
    print("   ✅ Cleaner initialized successfully")

    # Step 3: Define cleaning operations
    print("\n3️⃣ Defining cleaning operations...")
    operations = [
        "remove_duplicates",    # Remove duplicate rows
        "fill_missing",         # Fill missing values
        "clean_text",           # Clean text data
        "convert_types",        # Convert data types
        "clean_names"           # Clean column names
    ]
    print(f"   🎯 Operations: {', '.join(operations)}")

    # Step 4: Clean the data
    print("\n4️⃣ Performing data cleaning...")
    try:
        cleaned_df = cleaner.clean_dataframe(df, operations=operations)
        print("   ✅ Data cleaning completed successfully!")

        # Step 5: Analyze results
        print("\n5️⃣ Analyzing cleaning results...")
        print(f"   📊 Original shape: {df.shape}")
        print(f"   📊 Cleaned shape: {cleaned_df.shape}")
        print(f"   🗑️  Rows removed: {df.shape[0] - cleaned_df.shape[0]}")
        print(f"   🧹 Missing values before: {df.isnull().sum().sum()}")
        print(f"   🧹 Missing values after: {cleaned_df.isnull().sum().sum()}")

        # Step 6: Save cleaned data
        output_file = "cleaned_data.csv"
        cleaned_df.to_csv(output_file, index=False)
        print(f"\n6️⃣ Saving cleaned data...")
        print(f"   💾 Cleaned data saved to: {output_file}")

        # Step 7: Display sample of cleaned data
        print("\n7️⃣ Sample of cleaned data:")
        print(cleaned_df.head())

        return cleaned_df

    except Exception as e:
        print(f"   ❌ Error during cleaning: {e}")
        return None


def file_cleaning_example():
    """Demonstrate cleaning files directly."""
    print("\n" + "=" * 50)
    print("📁 File-Based Cleaning Example")
    print("=" * 50)

    # Create sample file if it doesn't exist
    input_file = "sample_data.csv"
    if not Path(input_file).exists():
        df = create_sample_data()
        df.to_csv(input_file, index=False)

    # Initialize cleaner
    cleaner = CSVCleaner()

    # Clean file directly
    output_file = "file_cleaned_data.csv"
    operations = ["remove_duplicates", "fill_missing", "clean_names"]

    print(f"\n🎯 Cleaning file: {input_file} -> {output_file}")
    print(f"🔧 Operations: {', '.join(operations)}")

    try:
        # Clean file and get summary
        summary = cleaner.clean_file(input_file, output_file, operations=operations)

        print("\n📊 Cleaning Summary:")
        print(f"   ⏱️  Processing time: {summary.get('processing_time', 'N/A')}")
        print(f"   📈 Rows processed: {summary.get('rows_processed', 'N/A')}")
        print(f"   🗑️  Rows removed: {summary.get('rows_removed', 'N/A')}")
        print(f"   🗑️  Columns removed: {summary.get('columns_removed', 'N/A')}")
        print(f"   ✅ Success: {summary.get('success', 'N/A')}")

        # Load and display results
        cleaned_df = pd.read_csv(output_file)
        print(f"\n📊 Final data shape: {cleaned_df.shape}")
        print("\n📋 Sample of cleaned data:")
        print(cleaned_df.head())

    except Exception as e:
        print(f"❌ Error: {e}")


def custom_configuration_example():
    """Demonstrate custom configuration."""
    print("\n" + "=" * 50)
    print("⚙️ Custom Configuration Example")
    print("=" * 50)

    # Create custom configuration
    config = Config(
        # Performance settings
        max_memory_gb=1.0,
        chunk_size=5000,
        max_workers=2,

        # File settings
        backup_enabled=True,
        backup_suffix=".backup",

        # Logging
        log_level="INFO",

        # Default operations
        default_operations=["remove_duplicates", "fill_missing"]
    )

    print("🔧 Custom configuration created:")
    print(f"   💾 Max memory: {config.max_memory_gb}GB")
    print(f"   📦 Chunk size: {config.chunk_size}")
    print(f"   🔄 Max workers: {config.max_workers}")
    print(f"   💿 Backup enabled: {config.backup_enabled}")
    print(f"   🎯 Default operations: {config.default_operations}")

    # Initialize cleaner with custom config
    cleaner = CSVCleaner(config)

    # Create sample data
    df = create_sample_data()

    # Clean with custom configuration
    print("\n🧹 Cleaning with custom configuration...")
    cleaned_df = cleaner.clean_dataframe(df)  # Uses default operations from config

    print(f"✅ Cleaning completed!")
    print(f"📊 Results: {df.shape} -> {cleaned_df.shape}")


def main():
    """Run all basic cleaning examples."""
    print("🚀 Starting CSV Data Cleaner Basic Examples")
    print("=" * 60)

    # Example 1: Basic DataFrame cleaning
    basic_cleaning_example()

    # Example 2: File-based cleaning
    file_cleaning_example()

    # Example 3: Custom configuration
    custom_configuration_example()

    print("\n" + "=" * 60)
    print("✅ All basic examples completed!")
    print("\n📚 Next steps:")
    print("   - Try the AI-powered cleaning examples")
    print("   - Explore performance optimization examples")
    print("   - Check out real-world scenario examples")
    print("\n📖 For more information, see the documentation and other examples.")


if __name__ == "__main__":
    main()
