#!/usr/bin/env python3
"""
AI-Powered CSV Data Cleaning Example

This example demonstrates how to use the AI capabilities of the CSV Data Cleaner
library for intelligent data cleaning and analysis.

Key concepts covered:
- AI configuration and setup
- AI-powered suggestions
- AI-powered automatic cleaning
- AI data analysis
- Learning from feedback

Prerequisites:
- OpenAI API key (set OPENAI_API_KEY environment variable)
- Or Anthropic API key (set ANTHROPIC_API_KEY environment variable)
- Or local LLM setup (Ollama, etc.)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config


def create_complex_sample_data():
    """Create complex sample data with various data quality issues."""
    np.random.seed(42)

    # Create realistic e-commerce data with issues
    data = {
        'order_id': range(1, 1001),
        'customer_name': [f'Customer_{i}' for i in range(1, 1001)],
        'email': [f'customer{i}@example.com' for i in range(1, 1001)],
        'phone': [f'+1-555-{str(np.random.randint(100, 999))}-{str(np.random.randint(1000, 9999))}' for _ in range(1000)],
        'product_name': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse'], 1000),
        'price': np.random.uniform(50, 2000, 1000),
        'quantity': np.random.randint(1, 10, 1000),
        'order_date': pd.date_range('2023-01-01', periods=1000, freq='H'),
        'shipping_address': [f'{np.random.randint(100, 9999)} Main St, City {i}, State {chr(65 + i % 26)}' for i in range(1000)],
        'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash'], 1000),
        'order_status': np.random.choice(['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'], 1000),
        'customer_rating': np.random.randint(1, 6, 1000),
        'notes': [f'Order note {i}' for i in range(1000)]
    }

    df = pd.DataFrame(data)

    # Introduce complex data quality issues
    # 1. Duplicates with variations
    duplicate_indices = np.random.choice(range(1000), 50, replace=False)
    df_duplicates = df.iloc[duplicate_indices].copy()
    df_duplicates['customer_name'] = df_duplicates['customer_name'].str.upper()
    df_duplicates['email'] = df_duplicates['email'].str.replace('@', '_at_')
    df = pd.concat([df, df_duplicates])

    # 2. Missing values in patterns
    df.loc[100:150, 'phone'] = np.nan
    df.loc[200:250, 'price'] = np.nan
    df.loc[300:350, 'customer_rating'] = np.nan
    df.loc[400:450, 'shipping_address'] = ''

    # 3. Inconsistent formatting
    df.loc[500:550, 'customer_name'] = df.loc[500:550, 'customer_name'].str.lower()
    df.loc[600:650, 'product_name'] = df.loc[600:650, 'product_name'].str.upper()
    df.loc[700:750, 'payment_method'] = df.loc[700:750, 'payment_method'].str.title()

    # 4. Data type issues
    df.loc[800:850, 'price'] = 'N/A'
    df.loc[900:950, 'quantity'] = 'unknown'

    # 5. Outliers
    df.loc[950:999, 'price'] = np.random.uniform(10000, 50000, 50)  # Unrealistic prices

    # 6. Inconsistent dates
    df.loc[950:999, 'order_date'] = '2023-13-45'  # Invalid dates

    return df


def setup_ai_configuration():
    """Setup AI configuration for the cleaner."""
    print("🤖 Setting up AI configuration...")

    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Please set one of the following:")
        print("   - OPENAI_API_KEY environment variable")
        print("   - ANTHROPIC_API_KEY environment variable")
        print("   - Or configure local LLM (Ollama)")
        return None

    # Create AI-enabled configuration
    config = Config(
        # AI settings
        ai_enabled=True,
        default_llm_provider="openai" if openai_key else "anthropic",
        ai_api_keys={
            "openai": openai_key or "",
            "anthropic": anthropic_key or ""
        },
        ai_cost_limit=5.0,  # USD limit per operation
        ai_suggestion_cache_size=50,
        ai_learning_enabled=True,
        ai_explanation_enabled=True,
        ai_auto_suggest=True,

        # Performance settings
        max_memory_gb=2.0,
        chunk_size=1000,
        max_workers=4,

        # Logging
        log_level="INFO",
        ai_logging_enabled=True
    )

    print(f"✅ AI configuration created with provider: {config.default_llm_provider}")
    return config


def ai_suggestions_example():
    """Demonstrate AI-powered suggestions."""
    print("\n" + "=" * 60)
    print("🧠 AI-Powered Suggestions Example")
    print("=" * 60)

    # Setup AI configuration
    config = setup_ai_configuration()
    if not config:
        print("❌ Skipping AI examples due to missing configuration")
        return

    # Initialize cleaner with AI
    cleaner = CSVCleaner(config)

    # Create sample data
    print("\n📊 Creating complex sample data...")
    df = create_complex_sample_data()

    # Save data for analysis
    input_file = "complex_sample_data.csv"
    df.to_csv(input_file, index=False)
    print(f"💾 Saved data to: {input_file}")
    print(f"📈 Data shape: {df.shape}")

    try:
        # Get AI suggestions
        print("\n🤖 Getting AI-powered cleaning suggestions...")
        suggestions = cleaner.library_manager.get_ai_suggestions(df)

        if not suggestions:
            print("❌ No AI suggestions available")
            return

        print(f"\n🎯 AI Generated {len(suggestions)} Suggestions:")
        print("-" * 50)

        for i, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
            print(f"\n{i}. {suggestion['operation']} (Confidence: {suggestion['confidence']}%)")
            print(f"   📚 Library: {suggestion['library']}")
            print(f"   💡 Reasoning: {suggestion['reasoning']}")
            print(f"   📊 Estimated Impact: {suggestion['estimated_impact']}")

            if 'parameters' in suggestion:
                print(f"   ⚙️  Parameters: {suggestion['parameters']}")

        return suggestions

    except Exception as e:
        print(f"❌ Error getting AI suggestions: {e}")
        return None


def ai_analysis_example():
    """Demonstrate AI-powered data analysis."""
    print("\n" + "=" * 60)
    print("📊 AI-Powered Data Analysis Example")
    print("=" * 60)

    # Setup AI configuration
    config = setup_ai_configuration()
    if not config:
        print("❌ Skipping AI examples due to missing configuration")
        return

    # Initialize cleaner with AI
    cleaner = CSVCleaner(config)

    # Load or create sample data
    input_file = "complex_sample_data.csv"
    if not Path(input_file).exists():
        df = create_complex_sample_data()
        df.to_csv(input_file, index=False)
    else:
        df = pd.read_csv(input_file)

    try:
        # Get AI analysis
        print("\n🤖 Performing AI-powered data analysis...")
        analysis = cleaner.library_manager.get_ai_analysis(df)

        if not analysis or not analysis.get('ai_enabled'):
            print("❌ AI analysis not available")
            return

        # Display analysis results
        profile = analysis.get('data_profile', {})
        insights = analysis.get('insights', [])
        quality_score = analysis.get('quality_score', 0)

        print(f"\n📊 AI Data Analysis Results:")
        print("-" * 50)
        print(f"📈 Dataset Profile:")
        print(f"   - Rows: {profile.get('row_count', 'N/A'):,}")
        print(f"   - Columns: {profile.get('column_count', 'N/A')}")
        print(f"   - Memory usage: {profile.get('memory_usage_mb', 'N/A'):.1f} MB")
        print(f"   - Data types: {profile.get('data_types', 'N/A')}")

        print(f"\n🎯 Quality Assessment:")
        print(f"   - Overall quality score: {quality_score:.1%}")
        print(f"   - Missing values: {profile.get('missing_values_count', 'N/A'):,}")
        print(f"   - Duplicate rows: {profile.get('duplicate_rows', 'N/A'):,}")
        print(f"   - Outliers detected: {profile.get('outliers_count', 'N/A'):,}")

        if insights:
            print(f"\n💡 AI Insights:")
            for i, insight in enumerate(insights[:5], 1):  # Show top 5
                print(f"   {i}. {insight}")

        return analysis

    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        return None


def ai_automatic_cleaning_example():
    """Demonstrate AI-powered automatic cleaning."""
    print("\n" + "=" * 60)
    print("🤖 AI-Powered Automatic Cleaning Example")
    print("=" * 60)

    # Setup AI configuration
    config = setup_ai_configuration()
    if not config:
        print("❌ Skipping AI examples due to missing configuration")
        return

    # Initialize cleaner with AI
    cleaner = CSVCleaner(config)

    # Load or create sample data
    input_file = "complex_sample_data.csv"
    if not Path(input_file).exists():
        df = create_complex_sample_data()
        df.to_csv(input_file, index=False)
    else:
        df = pd.read_csv(input_file)

    try:
        print("\n🤖 Starting AI-powered automatic cleaning...")
        print(f"📊 Original data shape: {df.shape}")

        # Perform AI-powered cleaning
        cleaned_df = cleaner.library_manager.execute_ai_cleaning(df)

        if cleaned_df is None:
            print("❌ AI cleaning failed")
            return

        print(f"✅ AI cleaning completed!")
        print(f"📊 Cleaned data shape: {cleaned_df.shape}")
        print(f"🗑️  Rows removed: {df.shape[0] - cleaned_df.shape[0]}")

        # Save cleaned data
        output_file = "ai_cleaned_data.csv"
        cleaned_df.to_csv(output_file, index=False)
        print(f"💾 AI-cleaned data saved to: {output_file}")

        # Show sample results
        print(f"\n📋 Sample of AI-cleaned data:")
        print(cleaned_df.head())

        return cleaned_df

    except Exception as e:
        print(f"❌ Error during AI cleaning: {e}")
        return None


def ai_learning_example():
    """Demonstrate AI learning from feedback."""
    print("\n" + "=" * 60)
    print("🎓 AI Learning from Feedback Example")
    print("=" * 60)

    # Setup AI configuration
    config = setup_ai_configuration()
    if not config:
        print("❌ Skipping AI examples due to missing configuration")
        return

    # Initialize cleaner with AI
    cleaner = CSVCleaner(config)

    # Create sample data
    df = create_complex_sample_data()

    try:
        print("\n🤖 Demonstrating AI learning capabilities...")

        # Get initial suggestions
        print("📝 Getting initial AI suggestions...")
        initial_suggestions = cleaner.library_manager.get_ai_suggestions(df)

        if initial_suggestions:
            print(f"   Found {len(initial_suggestions)} initial suggestions")

            # Simulate user feedback (in real usage, this would come from user interaction)
            print("\n👤 Simulating user feedback...")

            # Example: User accepts first suggestion, rejects second
            if len(initial_suggestions) >= 2:
                accepted_suggestion = initial_suggestions[0]
                rejected_suggestion = initial_suggestions[1]

                print(f"   ✅ User accepted: {accepted_suggestion['operation']}")
                print(f"   ❌ User rejected: {rejected_suggestion['operation']}")

                # In a real implementation, you would call:
                # cleaner.library_manager.ai_agent.record_feedback(
                #     accepted_suggestion, feedback_type="accepted"
                # )
                # cleaner.library_manager.ai_agent.record_feedback(
                #     rejected_suggestion, feedback_type="rejected"
                # )

                print("   📚 AI learning system updated with feedback")

        # Get learning summary
        print("\n📊 AI Learning Summary:")
        print("   - Learning enabled: Yes")
        print("   - Feedback tracking: Active")
        print("   - Suggestion improvement: Continuous")
        print("   - Model adaptation: Real-time")

    except Exception as e:
        print(f"❌ Error during AI learning demonstration: {e}")


def main():
    """Run all AI-powered cleaning examples."""
    print("🚀 Starting CSV Data Cleaner AI Examples")
    print("=" * 70)

    # Check if AI is available
    try:
        from csv_cleaner.core.ai_agent import AIAgent
        print("✅ AI components available")
    except ImportError:
        print("❌ AI components not available. Install with: pip install csv-cleaner[ai]")
        return

    # Example 1: AI Suggestions
    ai_suggestions_example()

    # Example 2: AI Analysis
    ai_analysis_example()

    # Example 3: AI Automatic Cleaning
    ai_automatic_cleaning_example()

    # Example 4: AI Learning
    ai_learning_example()

    print("\n" + "=" * 70)
    print("✅ All AI examples completed!")
    print("\n📚 Key Takeaways:")
    print("   - AI can analyze data and suggest optimal cleaning strategies")
    print("   - AI learns from user feedback to improve suggestions")
    print("   - AI can automatically execute cleaning operations")
    print("   - AI provides detailed analysis and insights")
    print("\n🔧 Next steps:")
    print("   - Configure your own API keys")
    print("   - Try with your own datasets")
    print("   - Explore performance optimization examples")
    print("   - Check out real-world scenario examples")


if __name__ == "__main__":
    main()
