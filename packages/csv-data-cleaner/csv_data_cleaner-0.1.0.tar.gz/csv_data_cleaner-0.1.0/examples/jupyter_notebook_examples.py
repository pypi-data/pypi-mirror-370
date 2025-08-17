#!/usr/bin/env python3
"""
Jupyter Notebook Integration Examples

This example demonstrates how to use the CSV Data Cleaner library
in Jupyter notebooks for interactive data analysis and cleaning.

Key concepts covered:
- Interactive data cleaning in notebooks
- Visualization of cleaning results
- Step-by-step cleaning workflows
- Data exploration and analysis
- Custom cleaning pipelines
- Real-time feedback and monitoring

Best practices for:
- Interactive data analysis
- Exploratory data cleaning
- Educational demonstrations
- Research workflows
- Data science projects
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config


def create_notebook_sample_data():
    """Create sample data suitable for Jupyter notebook demonstrations."""
    np.random.seed(42)

    # Create realistic dataset with various data quality issues
    data = {
        'customer_id': range(1, 1001),
        'customer_name': [f'Customer_{i}' for i in range(1, 1001)],
        'email': [f'customer{i}@example.com' for i in range(1, 1001)],
        'phone': [f'+1-555-{str(np.random.randint(100, 999))}-{str(np.random.randint(1000, 9999))}' for _ in range(1000)],
        'age': np.random.randint(18, 80, 1000),
        'income': np.random.randint(30000, 150000, 1000),
        'purchase_amount': np.random.uniform(10, 1000, 1000),
        'purchase_date': pd.date_range('2023-01-01', periods=1000, freq='H'),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], 1000),
        'satisfaction_rating': np.random.randint(1, 6, 1000),
        'loyalty_points': np.random.randint(0, 10000, 1000),
        'is_premium': np.random.choice([True, False], 1000, p=[0.2, 0.8]),
        'last_visit': pd.date_range('2023-01-01', periods=1000, freq='D'),
        'preferred_payment': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'], 1000),
        'marketing_consent': np.random.choice([True, False], 1000),
        'notes': [f'Customer note {i}' for i in range(1, 1001)]
    }

    df = pd.DataFrame(data)

    # Introduce data quality issues
    # 1. Duplicates
    duplicate_indices = np.random.choice(range(1000), 50, replace=False)
    df_duplicates = df.iloc[duplicate_indices].copy()
    df_duplicates['customer_name'] = df_duplicates['customer_name'].str.upper()
    df = pd.concat([df, df_duplicates])

    # 2. Missing values
    missing_patterns = [
        (100, 150, 'age'),
        (200, 250, 'income'),
        (300, 350, 'email'),
        (400, 450, 'phone'),
        (500, 550, 'purchase_amount'),
        (600, 650, 'satisfaction_rating')
    ]

    for start, end, col in missing_patterns:
        if col in df.columns:
            df.iloc[start:end, df.columns.get_loc(col)] = np.nan

    # 3. Inconsistent formatting
    if 'customer_name' in df.columns:
        df.iloc[700:750, df.columns.get_loc('customer_name')] = df.iloc[700:750]['customer_name'].str.lower()
    if 'product_category' in df.columns:
        df.iloc[800:850, df.columns.get_loc('product_category')] = df.iloc[800:850]['product_category'].str.upper()

    # 4. Data type issues
    if 'age' in df.columns:
        df.iloc[900:950, df.columns.get_loc('age')] = 'unknown'
    if 'income' in df.columns:
        df.iloc[950:999, df.columns.get_loc('income')] = 'N/A'

    # 5. Outliers
    if 'purchase_amount' in df.columns:
        outlier_count = min(50, len(df) - 950)
        df.iloc[950:950+outlier_count, df.columns.get_loc('purchase_amount')] = np.random.uniform(10000, 50000, outlier_count)

    return df


def notebook_basic_cleaning_example():
    """Basic cleaning example for Jupyter notebooks."""
    print("🧹 Jupyter Notebook - Basic Cleaning Example")
    print("=" * 60)

    # Create sample data
    print("📊 Creating sample data...")
    df = create_notebook_sample_data()

    # Display initial data info
    print(f"\n📈 Initial Dataset Info:")
    print(f"Shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    # Show data quality issues
    print(f"\n🔍 Data Quality Issues:")
    print(f"Missing values: {df.isnull().sum().sum()}")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"Empty strings: {(df == '').sum().sum()}")

    # Initialize cleaner
    cleaner = CSVCleaner()

    # Define cleaning operations
    operations = ["remove_duplicates", "fill_missing", "clean_names", "convert_types"]

    print(f"\n🎯 Cleaning operations: {', '.join(operations)}")

    # Clean the data
    cleaned_df = cleaner.clean_dataframe(df, operations=operations)

    # Display results
    print(f"\n✅ Cleaning completed!")
    print(f"Original shape: {df.shape}")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print(f"Rows removed: {df.shape[0] - cleaned_df.shape[0]}")
    print(f"Missing values after: {cleaned_df.isnull().sum().sum()}")

    return df, cleaned_df


def notebook_visualization_example():
    """Demonstrate data visualization in notebooks."""
    print("\n" + "=" * 60)
    print("📊 Data Visualization Example")
    print("=" * 60)

    # Create sample data
    df = create_notebook_sample_data()

    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Create visualization functions
    def plot_missing_values(df, title="Missing Values Analysis"):
        """Plot missing values heatmap."""
        plt.figure(figsize=(12, 6))

        # Calculate missing values
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100

        # Create bar plot
        plt.subplot(1, 2, 1)
        missing_data[missing_data > 0].plot(kind='bar')
        plt.title('Missing Values Count')
        plt.xlabel('Columns')
        plt.ylabel('Count')
        plt.xticks(rotation=45)

        # Create heatmap
        plt.subplot(1, 2, 2)
        sns.heatmap(df.isnull(), cbar=True, yticklabels=False, cmap='viridis')
        plt.title('Missing Values Heatmap')

        plt.tight_layout()
        plt.show()

        # Print summary
        print(f"\n📊 Missing Values Summary:")
        for col, count in missing_data[missing_data > 0].items():
            print(f"   {col}: {count} ({missing_percent[col]:.1f}%)")

    def plot_data_distribution(df, columns):
        """Plot distribution of numeric columns."""
        n_cols = len(columns)
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.ravel()

        for i, col in enumerate(columns[:4]):  # Limit to 4 plots
            if col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    # Histogram for numeric data
                    axes[i].hist(df[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
                    axes[i].set_title(f'Distribution of {col}')
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel('Frequency')
                else:
                    # Bar plot for categorical data
                    value_counts = df[col].value_counts().head(10)
                    value_counts.plot(kind='bar', ax=axes[i])
                    axes[i].set_title(f'Top 10 values in {col}')
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel('Count')
                    axes[i].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_cleaning_comparison(original_df, cleaned_df):
        """Compare original vs cleaned data."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Missing values comparison
        original_missing = original_df.isnull().sum().sum()
        cleaned_missing = cleaned_df.isnull().sum().sum()

        axes[0, 0].bar(['Original', 'Cleaned'], [original_missing, cleaned_missing],
                      color=['red', 'green'], alpha=0.7)
        axes[0, 0].set_title('Missing Values Comparison')
        axes[0, 0].set_ylabel('Count')

        # Row count comparison
        original_rows = len(original_df)
        cleaned_rows = len(cleaned_df)

        axes[0, 1].bar(['Original', 'Cleaned'], [original_rows, cleaned_rows],
                      color=['blue', 'orange'], alpha=0.7)
        axes[0, 1].set_title('Row Count Comparison')
        axes[0, 1].set_ylabel('Count')

        # Data types comparison
        original_dtypes = original_df.dtypes.value_counts()
        cleaned_dtypes = cleaned_df.dtypes.value_counts()

        axes[1, 0].pie(original_dtypes.values, labels=original_dtypes.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Original Data Types')

        axes[1, 1].pie(cleaned_dtypes.values, labels=cleaned_dtypes.index, autopct='%1.1f%%')
        axes[1, 1].set_title('Cleaned Data Types')

        plt.tight_layout()
        plt.show()

    # Run visualizations
    print("📊 Creating visualizations...")

    # 1. Missing values analysis
    plot_missing_values(df, "Before Cleaning")

    # 2. Data distribution
    numeric_cols = ['age', 'income', 'purchase_amount', 'satisfaction_rating']
    plot_data_distribution(df, numeric_cols)

    # 3. Clean the data
    cleaner = CSVCleaner()
    cleaned_df = cleaner.clean_dataframe(df, operations=["remove_duplicates", "fill_missing", "clean_names"])

    # 4. Comparison plots
    plot_cleaning_comparison(df, cleaned_df)

    return df, cleaned_df


def notebook_interactive_cleaning_example():
    """Demonstrate interactive cleaning workflow."""
    print("\n" + "=" * 60)
    print("🔄 Interactive Cleaning Workflow")
    print("=" * 60)

    # Create sample data
    df = create_notebook_sample_data()

    def analyze_data_quality(df, step_name=""):
        """Analyze and display data quality metrics."""
        print(f"\n📊 Data Quality Analysis {step_name}:")
        print("-" * 50)
        print(f"Shape: {df.shape}")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        print(f"Missing values: {df.isnull().sum().sum()}")
        print(f"Duplicate rows: {df.duplicated().sum()}")
        print(f"Data types:")
        for col, dtype in df.dtypes.items():
            print(f"   {col}: {dtype}")

    def step_by_step_cleaning(df):
        """Perform cleaning step by step with analysis."""
        cleaner = CSVCleaner()
        current_df = df.copy()

        # Step 1: Initial analysis
        analyze_data_quality(current_df, "(Initial)")

        # Step 2: Remove duplicates
        print(f"\n🔄 Step 1: Removing duplicates...")
        current_df = cleaner.clean_dataframe(current_df, operations=["remove_duplicates"])
        analyze_data_quality(current_df, "(After removing duplicates)")

        # Step 3: Fill missing values
        print(f"\n🔄 Step 2: Filling missing values...")
        current_df = cleaner.clean_dataframe(current_df, operations=["fill_missing"])
        analyze_data_quality(current_df, "(After filling missing values)")

        # Step 4: Clean column names
        print(f"\n🔄 Step 3: Cleaning column names...")
        current_df = cleaner.clean_dataframe(current_df, operations=["clean_names"])
        analyze_data_quality(current_df, "(After cleaning names)")

        # Step 5: Convert data types
        print(f"\n🔄 Step 4: Converting data types...")
        current_df = cleaner.clean_dataframe(current_df, operations=["convert_types"])
        analyze_data_quality(current_df, "(After type conversion)")

        return current_df

    # Run interactive cleaning
    cleaned_df = step_by_step_cleaning(df)

    # Final comparison
    print(f"\n📈 Final Comparison:")
    print(f"Original rows: {len(df):,}")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Rows removed: {len(df) - len(cleaned_df):,}")
    print(f"Missing values reduced: {df.isnull().sum().sum() - cleaned_df.isnull().sum().sum():,}")

    return df, cleaned_df


def notebook_custom_cleaning_pipeline():
    """Demonstrate custom cleaning pipeline."""
    print("\n" + "=" * 60)
    print("🔧 Custom Cleaning Pipeline")
    print("=" * 60)

    # Create sample data
    df = create_notebook_sample_data()

    def custom_cleaning_pipeline(df):
        """Custom cleaning pipeline with specific business rules."""
        cleaner = CSVCleaner()

        print("🔧 Starting custom cleaning pipeline...")

        # Step 1: Basic cleaning
        print("   📝 Step 1: Basic cleaning...")
        df_cleaned = cleaner.clean_dataframe(df, operations=["remove_duplicates", "clean_names"])

        # Step 2: Business-specific cleaning
        print("   🎯 Step 2: Business-specific cleaning...")

        # Remove customers with invalid ages (convert to numeric first)
        df_cleaned['age'] = pd.to_numeric(df_cleaned['age'], errors='coerce')
        invalid_age_mask = (df_cleaned['age'] < 18) | (df_cleaned['age'] > 100)
        df_cleaned = df_cleaned[~invalid_age_mask]
        print(f"      Removed {invalid_age_mask.sum()} rows with invalid ages")

        # Remove outliers in purchase amount (above 95th percentile)
        df_cleaned['purchase_amount'] = pd.to_numeric(df_cleaned['purchase_amount'], errors='coerce')
        purchase_threshold = df_cleaned['purchase_amount'].quantile(0.95)
        outlier_mask = df_cleaned['purchase_amount'] > purchase_threshold
        df_cleaned = df_cleaned[~outlier_mask]
        print(f"      Removed {outlier_mask.sum()} rows with outlier purchase amounts")

        # Standardize email format
        df_cleaned['email'] = df_cleaned['email'].str.lower()
        print(f"      Standardized email formats")

        # Create derived features
        print("   🆕 Step 3: Creating derived features...")
        df_cleaned['income'] = pd.to_numeric(df_cleaned['income'], errors='coerce')

        df_cleaned['age_group'] = pd.cut(df_cleaned['age'],
                                       bins=[0, 25, 35, 50, 65, 100],
                                       labels=['18-25', '26-35', '36-50', '51-65', '65+'])

        df_cleaned['income_category'] = pd.cut(df_cleaned['income'],
                                             bins=[0, 50000, 75000, 100000, 150000, float('inf')],
                                             labels=['Low', 'Medium', 'High', 'Very High', 'Premium'])

        df_cleaned['purchase_category'] = pd.cut(df_cleaned['purchase_amount'],
                                               bins=[0, 50, 100, 200, 500, float('inf')],
                                               labels=['Small', 'Medium', 'Large', 'Very Large', 'Premium'])

        print(f"      Created age_group, income_category, and purchase_category features")

        # Step 4: Final validation
        print("   ✅ Step 4: Final validation...")

        # Check for remaining issues
        remaining_missing = df_cleaned.isnull().sum().sum()
        remaining_duplicates = df_cleaned.duplicated().sum()

        print(f"      Remaining missing values: {remaining_missing}")
        print(f"      Remaining duplicates: {remaining_duplicates}")

        return df_cleaned

    # Run custom pipeline
    cleaned_df = custom_cleaning_pipeline(df)

    # Display results
    print(f"\n📊 Custom Pipeline Results:")
    print(f"Original shape: {df.shape}")
    print(f"Cleaned shape: {cleaned_df.shape}")
    print(f"Data quality improvement: {((len(df) - len(cleaned_df)) / len(df) * 100):.1f}% reduction in rows")

    # Show new features
    print(f"\n🆕 New Features Created:")
    print(f"   age_group: {cleaned_df['age_group'].value_counts().to_dict()}")
    print(f"   income_category: {cleaned_df['income_category'].value_counts().to_dict()}")
    print(f"   purchase_category: {cleaned_df['purchase_category'].value_counts().to_dict()}")

    return df, cleaned_df


def notebook_ai_powered_cleaning_example():
    """Demonstrate AI-powered cleaning in notebooks."""
    print("\n" + "=" * 60)
    print("🤖 AI-Powered Cleaning Example")
    print("=" * 60)

    # Create sample data
    df = create_notebook_sample_data()

    # Check if AI is available
    try:
        from csv_cleaner.core.ai_agent import AIAgent
        ai_available = True
        print("✅ AI components available")
    except ImportError:
        ai_available = False
        print("❌ AI components not available. Install with: pip install csv-cleaner[ai]")
        return df, None

    if not ai_available:
        return df, None

    # Configure AI
    config = Config(
        ai_enabled=True,
        ai_learning_enabled=True,
        ai_explanation_enabled=True
    )

    cleaner = CSVCleaner(config)

    def ai_analysis_workflow(df):
        """AI-powered analysis and cleaning workflow."""
        print("🤖 Starting AI-powered analysis...")

        # Get AI suggestions
        print("   📝 Getting AI suggestions...")
        suggestions = cleaner.library_manager.get_ai_suggestions(df)

        if suggestions:
            print(f"   🎯 AI generated {len(suggestions)} suggestions:")
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"      {i}. {suggestion['operation']} (Confidence: {suggestion['confidence']}%)")
                print(f"         Reasoning: {suggestion['reasoning']}")

        # Get AI analysis
        print("   📊 Getting AI analysis...")
        analysis = cleaner.library_manager.get_ai_analysis(df)

        if analysis:
            profile = analysis.get('data_profile', {})
            print(f"   📈 AI Analysis Results:")
            quality_score = analysis.get('quality_score', 'N/A')
            if isinstance(quality_score, (int, float)):
                print(f"      Quality score: {quality_score:.1%}")
            else:
                print(f"      Quality score: {quality_score}")

            missing_count = profile.get('missing_values_count', 'N/A')
            if isinstance(missing_count, int):
                print(f"      Missing values: {missing_count:,}")
            else:
                print(f"      Missing values: {missing_count}")

            duplicate_rows = profile.get('duplicate_rows', 'N/A')
            if isinstance(duplicate_rows, int):
                print(f"      Duplicate rows: {duplicate_rows:,}")
            else:
                print(f"      Duplicate rows: {duplicate_rows}")

        # Execute AI cleaning (use suggestions to perform cleaning)
        print("   🚀 Executing AI-powered cleaning...")
        if suggestions:
            # Use the first suggestion to perform cleaning
            first_suggestion = suggestions[0]
            operation = first_suggestion.get('operation', 'fill_missing')
            print(f"   🎯 Applying AI suggestion: {operation}")
            cleaned_df = cleaner.clean_dataframe(df, operations=[operation])
        else:
            # Fall back to basic cleaning if no suggestions
            print("   🔄 No AI suggestions available, using basic cleaning")
            cleaned_df = cleaner.clean_dataframe(df, operations=["remove_duplicates", "fill_missing"])

        return cleaned_df, suggestions, analysis

    # Run AI workflow
    cleaned_df, suggestions, analysis = ai_analysis_workflow(df)

    if cleaned_df is not None:
        print(f"\n✅ AI cleaning completed!")
        print(f"Original shape: {df.shape}")
        print(f"Cleaned shape: {cleaned_df.shape}")

    return df, cleaned_df


def notebook_performance_monitoring_example():
    """Demonstrate performance monitoring in notebooks."""
    print("\n" + "=" * 60)
    print("📊 Performance Monitoring Example")
    print("=" * 60)

    import time
    import psutil

    # Create sample data
    df = create_notebook_sample_data()

    def monitor_performance(func, *args, **kwargs):
        """Monitor performance of a function."""
        # Monitor system resources
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        initial_cpu = psutil.cpu_percent()

        # Time the operation
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Final measurements
        final_memory = process.memory_info().rss / 1024 / 1024
        final_cpu = psutil.cpu_percent()

        return {
            'result': result,
            'execution_time': end_time - start_time,
            'memory_usage': final_memory,
            'memory_increase': final_memory - initial_memory,
            'cpu_usage': final_cpu
        }

    def compare_cleaning_methods(df):
        """Compare different cleaning methods."""
        cleaner = CSVCleaner()

        # Method 1: Basic cleaning
        print("🔧 Method 1: Basic cleaning...")
        basic_result = monitor_performance(
            cleaner.clean_dataframe,
            df,
            operations=["remove_duplicates", "fill_missing"]
        )

        # Method 2: Advanced cleaning
        print("🔧 Method 2: Advanced cleaning...")
        advanced_result = monitor_performance(
            cleaner.clean_dataframe,
            df,
            operations=["remove_duplicates", "fill_missing", "clean_names", "convert_types", "fix_dates"]
        )

        # Method 3: AI-powered cleaning
        print("🔧 Method 3: AI-powered cleaning...")
        try:
            config = Config(ai_enabled=True)
            ai_cleaner = CSVCleaner(config)
            ai_result = monitor_performance(
                ai_cleaner.library_manager.execute_ai_cleaning,
                df
            )
        except:
            ai_result = {'result': None, 'execution_time': 0, 'memory_usage': 0, 'memory_increase': 0, 'cpu_usage': 0}

        return basic_result, advanced_result, ai_result

    # Run performance comparison
    basic_result, advanced_result, ai_result = compare_cleaning_methods(df)

    # Display results
    print(f"\n📊 Performance Comparison:")
    print("-" * 60)
    print(f"{'Method':<20} {'Time (s)':<10} {'Memory (MB)':<12} {'CPU (%)':<8}")
    print("-" * 60)
    print(f"{'Basic':<20} {basic_result['execution_time']:<10.2f} {basic_result['memory_usage']:<12.1f} {basic_result['cpu_usage']:<8.1f}")
    print(f"{'Advanced':<20} {advanced_result['execution_time']:<10.2f} {advanced_result['memory_usage']:<12.1f} {advanced_result['cpu_usage']:<8.1f}")
    if ai_result['result'] is not None:
        print(f"{'AI-Powered':<20} {ai_result['execution_time']:<10.2f} {ai_result['memory_usage']:<12.1f} {ai_result['cpu_usage']:<8.1f}")

    return basic_result, advanced_result, ai_result


def main():
    """Run all Jupyter notebook examples."""
    print("🚀 Starting Jupyter Notebook Integration Examples")
    print("=" * 70)

    # Example 1: Basic cleaning
    df1, cleaned_df1 = notebook_basic_cleaning_example()

    # Example 2: Visualization
    df2, cleaned_df2 = notebook_visualization_example()

    # Example 3: Interactive cleaning
    df3, cleaned_df3 = notebook_interactive_cleaning_example()

    # Example 4: Custom pipeline
    df4, cleaned_df4 = notebook_custom_cleaning_pipeline()

    # Example 5: AI-powered cleaning
    df5, cleaned_df5 = notebook_ai_powered_cleaning_example()

    # Example 6: Performance monitoring
    perf_results = notebook_performance_monitoring_example()

    print("\n" + "=" * 70)
    print("✅ All Jupyter notebook examples completed!")
    print("\n📚 Key Notebook Features:")
    print("   - Interactive data exploration")
    print("   - Real-time visualization")
    print("   - Step-by-step cleaning workflows")
    print("   - Performance monitoring")
    print("   - Custom cleaning pipelines")
    print("   - AI-powered analysis")

    print("\n🔧 Notebook Best Practices:")
    print("   - Use markdown cells for documentation")
    print("   - Create reusable functions")
    print("   - Monitor memory usage")
    print("   - Save intermediate results")
    print("   - Use progress bars for long operations")
    print("   - Include error handling")

    print("\n📊 Next Steps:")
    print("   - Adapt examples to your datasets")
    print("   - Create custom visualizations")
    print("   - Build automated cleaning pipelines")
    print("   - Share notebooks with your team")
    print("   - Document your cleaning workflows")


if __name__ == "__main__":
    main()
