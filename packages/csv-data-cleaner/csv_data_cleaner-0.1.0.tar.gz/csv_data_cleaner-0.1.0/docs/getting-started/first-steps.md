# First Steps Tutorial

Your first data cleaning operation with CSV Cleaner - a step-by-step guide for beginners.

## 🎯 What You'll Learn

In this tutorial, you'll:
- Install CSV Cleaner
- Create sample data
- Perform your first data cleaning operation
- Understand basic concepts
- Learn how to interpret results

## 📋 Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- Basic familiarity with command-line interfaces
- A text editor or terminal

## 🚀 Step 1: Installation

### Install CSV Cleaner

```bash
# Install the package
pip install csv-cleaner

# Verify installation
csv-cleaner --version
```

You should see output like:
```
csv-cleaner, version 1.0.0
```

### Check Available Commands

```bash
# See all available commands
csv-cleaner --help
```

## 📊 Step 2: Create Sample Data

Let's create a sample CSV file with some common data quality issues:

```bash
# Create a sample CSV file
cat > sample_data.csv << 'EOF'
Name,Age,Email,City,Salary
john doe,25,john@example.com,New York,50000
Jane Smith,30,jane@example.com,Los Angeles,60000
john doe,25,john@example.com,New York,50000
Bob Johnson,,bob@example.com,Chicago,55000
Alice Brown,28,alice@example.com,,65000
Charlie Wilson,35,charlie@example.com,Boston,70000
EOF
```

This sample data contains several common issues:
- Duplicate rows (John Doe appears twice)
- Missing values (Bob's age, Alice's city)
- Inconsistent formatting (mixed case names)

## 🔍 Step 3: Explore Your Data

### Validate the Data

First, let's see what issues exist in our data:

```bash
# Validate the CSV file
csv-cleaner validate sample_data.csv
```

This will show you:
- Number of rows and columns
- Data types
- Missing value counts
- Basic statistics

### Visualize Data Quality

```bash
# Generate a data quality visualization (Basic Version)
csv-cleaner visualize sample_data.csv --type quality --output quality_plot.png
```

This creates a visual representation of data quality metrics.

> **Pro Feature**: For advanced visualizations like missing data matrix, bar charts, and heatmaps, upgrade to CSV Cleaner Pro:
> ```bash
> # Pro version only - missing data matrix
> csv-cleaner visualize sample_data.csv --type matrix --output missing_data.png
>
> # Pro version only - missing data bar chart
> csv-cleaner visualize sample_data.csv --type bar --output missing_bar.png
>
> # Pro version only - missing data heatmap
> csv-cleaner visualize sample_data.csv --type heatmap --output missing_heatmap.png
> ```

## 🧹 Step 4: Your First Cleaning Operation

### Basic Cleaning

Let's clean the data using some common operations:

```bash
# Clean the data with basic operations
csv-cleaner clean sample_data.csv cleaned_data.csv --operations "remove_duplicates,clean_names"
```

This command:
- Removes duplicate rows
- Cleans column names (standardizes formatting)

### Check the Results

```bash
# View the cleaned data
head cleaned_data.csv

# Compare with original
echo "Original data:"
wc -l sample_data.csv
echo "Cleaned data:"
wc -l cleaned_data.csv
```

You should see that the cleaned file has fewer rows (duplicates removed).

## 🤖 Step 5: Try AI-Powered Cleaning (Pro Version)

> **Pro Feature**: AI-powered cleaning requires CSV Cleaner Pro. If you have the Pro version, you can use AI to get intelligent suggestions:

```bash
# Get AI suggestions for cleaning (Pro Version)
csv-cleaner ai-suggest sample_data.csv
```

The AI will analyze your data and suggest appropriate cleaning operations.

### Activating Pro Version

To activate Pro features for testing, set the environment variable:

```bash
# Activate Pro version
export CSV_CLEANER_VERSION=pro

# Verify Pro version is active
csv-cleaner --version
```

### AI-Powered Cleaning

With Pro version, you can also use automatic AI cleaning:

```bash
# AI-powered automatic cleaning (Pro Version)
csv-cleaner ai-clean sample_data.csv ai_cleaned.csv
```

This will analyze your data, generate suggestions, and automatically apply the best cleaning operations.

## 📈 Step 6: Generate a Report

Let's create a comprehensive report of your data quality:

```bash
# Generate a data quality report
csv-cleaner report sample_data.csv --output data_quality_report.html
```

This creates an HTML report with:
- Data quality metrics
- Missing value analysis
- Duplicate analysis
- Data type information

## 🔧 Step 7: Interactive Mode

Try the interactive cleaning mode for a guided experience:

```bash
# Start interactive cleaning
csv-cleaner clean sample_data.csv interactive_cleaned.csv --interactive
```

The interactive mode will:
- Show you available operations
- Let you select which ones to apply
- Preview changes before applying them
- Guide you through the process

> **Note**: If the interactive selection interface doesn't work, the system will automatically fall back to a simple text-based prompt where you can enter operations manually.

## 📊 Understanding the Results

### What Happened?

After cleaning, your data should have:
- **Removed duplicates**: John Doe's duplicate row was removed
- **Cleaned names**: Column names are now standardized
- **Better structure**: Data is more consistent

### Key Metrics to Check

```bash
# Compare file sizes
ls -lh sample_data.csv cleaned_data.csv

# Check for remaining issues
csv-cleaner validate cleaned_data.csv
```

## 🎯 Common Operations Explained

### `remove_duplicates`
- Removes exact duplicate rows
- Keeps the first occurrence
- Useful for data integrity

### `clean_names`
- Standardizes column names
- Removes special characters
- Converts to lowercase with underscores

### `fill_missing`
- Fills missing values with appropriate defaults
- Can use mean, median, or custom values

### `convert_types`
- Converts data types (strings to numbers, etc.)
- Ensures proper data types for analysis

## 🔄 Next Steps

### Try Different Operations

```bash
# Fill missing values
csv-cleaner clean sample_data.csv filled_data.csv --operations "fill_missing"

# Convert data types
csv-cleaner clean sample_data.csv typed_data.csv --operations "convert_types"

# Combine multiple operations
csv-cleaner clean sample_data.csv final_cleaned.csv --operations "remove_duplicates,clean_names,fill_missing"
```

### Work with Your Own Data

1. **Prepare your CSV file**
2. **Validate it first**: `csv-cleaner validate your_file.csv`
3. **Get AI suggestions**: `csv-cleaner ai-suggest your_file.csv`
4. **Clean with appropriate operations**
5. **Generate a report**: `csv-cleaner report your_file.csv`

## 📚 What You've Learned

✅ **Installation**: How to install and verify CSV Cleaner
✅ **Data Validation**: How to check data quality issues
✅ **Basic Cleaning**: How to remove duplicates and clean names
✅ **Visualization**: How to create data quality visualizations
✅ **Reporting**: How to generate comprehensive reports
✅ **Interactive Mode**: How to use guided cleaning

## 🆘 Troubleshooting

### Common Issues

#### "Command not found"
```bash
# Reinstall if needed
pip install --force-reinstall csv-cleaner
```

#### "File not found"
```bash
# Check your current directory
pwd
ls -la *.csv
```

#### "Permission denied"
```bash
# Check file permissions
chmod 644 your_file.csv
```

### Pro Version Issues

#### "Feature is a Pro feature"
If you see messages about features being Pro-only:
```bash
# Activate Pro version for testing
export CSV_CLEANER_VERSION=pro
```

#### "AI is disabled in configuration"
If AI features aren't working:
```bash
# Check AI configuration
csv-cleaner ai-configure show

# Configure AI if needed
csv-cleaner ai-configure set --provider openai --api-key YOUR_API_KEY
```

#### "Interactive mode not working"
If the interactive selection interface fails:
- The system will automatically fall back to text-based prompts
- You can enter operations manually when prompted
- Example: `remove_duplicates,clean_names,fill_missing`

## 📖 Further Learning

Now that you've completed your first data cleaning operation:

1. **Read the [User Manual](../user-guides/user-manual.md)** for detailed feature explanations
2. **Try [Basic Tutorials](../tutorials/basic-tutorials.md)** for more examples
3. **Explore [AI Features](../user-guides/ai-features.md)** for advanced capabilities
4. **Check [Configuration Guide](../user-guides/configuration.md)** for customization

## 🎉 Congratulations!

You've successfully completed your first data cleaning operation with CSV Cleaner! You now know how to:

- Install and set up CSV Cleaner
- Validate and explore your data
- Perform basic cleaning operations
- Generate reports and visualizations
- Use interactive mode for guided cleaning

You're ready to start cleaning your own data!

## 🚀 Pro Features Overview

CSV Cleaner Pro includes advanced features for power users:

### 🤖 AI-Powered Features
- **AI Suggestions**: Get intelligent cleaning recommendations
- **AI Analysis**: Automated data analysis and insights
- **AI Cleaning**: Automatic cleaning with AI guidance
- **AI Configuration**: Manage AI providers and models

### 📊 Advanced Visualizations
- **Missing Data Matrix**: Visualize missing value patterns
- **Missing Data Bar Charts**: Column-wise missing value analysis
- **Missing Data Heatmaps**: Correlation-based missing value visualization
- **Missing Data Dendrograms**: Hierarchical missing value clustering

### 🔧 Advanced Operations
- **ML-Based Deduplication**: Fuzzy matching for duplicate detection
- **Performance Analysis**: Optimize processing speed and memory usage
- **Batch Processing**: Handle large datasets efficiently
- **Parallel Processing**: Multi-core data processing

### 📈 Enhanced Reporting
- **AI-Powered Insights**: Automated data quality recommendations
- **Performance Metrics**: Processing time and resource usage analysis
- **Advanced Statistics**: Comprehensive data profiling

---

*Ready for more advanced features? Continue to the [User Manual](../user-guides/user-manual.md) for comprehensive coverage.*
