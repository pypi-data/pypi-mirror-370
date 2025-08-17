# Basic Tutorials

Step-by-step tutorials to get you started with CSV Data Cleaner. These tutorials cover the most common data cleaning scenarios.

## 📋 Tutorial Index

1. [Getting Started](#getting-started)
2. [Basic Data Cleaning](#basic-data-cleaning)
3. [Handling Missing Values](#handling-missing-values)
4. [Removing Duplicates](#removing-duplicates)
5. [Text Data Cleaning](#text-data-cleaning)
6. [Data Validation](#data-validation)
7. [AI-Powered Cleaning](#ai-powered-cleaning)
8. [Creating Visualizations](#creating-visualizations)

## 🚀 Getting Started

### Prerequisites
- CSV Data Cleaner installed
- Basic knowledge of CSV files
- Sample data files (provided in examples)

### Setup
```bash
# Verify installation
csv-cleaner --version

# Check available commands
csv-cleaner --help
```

## 🔧 Basic Data Cleaning

### Tutorial 1: Simple Data Cleaning

**Objective**: Clean a basic CSV file with common issues.

**Sample Data** (`sample_data.csv`):
```csv
name,age,email,city
John Doe,25,john@example.com,New York
Jane Smith,30,jane@example.com,Los Angeles
Bob Johnson,,bob@example.com,Chicago
Alice Brown,28,alice@example.com,New York
John Doe,25,john@example.com,New York
```

**Step 1: Analyze the Data**
```bash
# Get information about the file
csv-cleaner info sample_data.csv
```

**Step 2: Validate Data Quality**
```bash
# Check for data quality issues
csv-cleaner validate sample_data.csv
```

**Step 3: Clean the Data**
```bash
# Clean with basic operations
csv-cleaner clean sample_data.csv cleaned_data.csv --operations "remove_duplicates,fill_missing"
```

**Step 4: Verify Results**
```bash
# Check the cleaned data
csv-cleaner info cleaned_data.csv
```

**Expected Output**:
```csv
name,age,email,city
John Doe,25,john@example.com,New York
Jane Smith,30,jane@example.com,Los Angeles
Bob Johnson,0,bob@example.com,Chicago
Alice Brown,28,alice@example.com,New York
```

### Tutorial 2: Interactive Cleaning

**Objective**: Use interactive mode for step-by-step cleaning.

```bash
# Start interactive cleaning
csv-cleaner clean sample_data.csv cleaned_data.csv --interactive
```

**Interactive Prompts**:
```
Found 1 duplicate row. Remove duplicates? [y/N]: y
Found 1 missing value in 'age' column. Fill with: [0/mean/median/drop]: 0
Clean text in 'name' column? [y/N]: y
```

## 🔍 Handling Missing Values

### Tutorial 3: Missing Value Strategies

**Objective**: Learn different strategies for handling missing values.

**Sample Data** (`missing_data.csv`):
```csv
id,name,age,salary,department
1,John,25,50000,Engineering
2,Jane,,60000,Marketing
3,Bob,30,,Sales
4,Alice,28,55000,
5,Charlie,,,HR
```

**Strategy 1: Fill with Default Values**
```bash
# Fill missing values with specific defaults
csv-cleaner clean missing_data.csv filled_data.csv \
  --operations "fill_missing" \
  --method "value" \
  --fill-value "0"
```

**Strategy 2: Fill with Statistical Values**
```bash
# Fill missing values with mean/median
csv-cleaner clean missing_data.csv filled_data.csv \
  --operations "fill_missing" \
  --method "mean" \
  --columns "age,salary"
```

**Strategy 3: Drop Rows with Missing Values**
```bash
# Remove rows with any missing values
csv-cleaner clean missing_data.csv cleaned_data.csv \
  --operations "drop_missing"
```

**Strategy 4: Forward Fill**
```bash
# Use forward fill for time-series data
csv-cleaner clean missing_data.csv filled_data.csv \
  --operations "fill_missing" \
  --method "forward"
```

### Tutorial 4: Conditional Missing Value Handling

**Objective**: Handle missing values differently based on conditions.

```bash
# Fill missing ages with median, missing salaries with mean
csv-cleaner clean missing_data.csv filled_data.csv \
  --operations "fill_missing" \
  --method "median" \
  --columns "age" \
  --method "mean" \
  --columns "salary"
```

## 🗑️ Removing Duplicates

### Tutorial 5: Basic Duplicate Removal

**Objective**: Remove duplicate rows from data.

**Sample Data** (`duplicate_data.csv`):
```csv
id,name,email,city
1,John,john@example.com,New York
2,Jane,jane@example.com,Los Angeles
1,John,john@example.com,New York
3,Bob,bob@example.com,Chicago
2,Jane,jane@example.com,Los Angeles
```

**Remove All Duplicates**
```bash
# Remove all duplicate rows
csv-cleaner clean duplicate_data.csv cleaned_data.csv \
  --operations "remove_duplicates"
```

**Remove Duplicates Based on Specific Columns**
```bash
# Remove duplicates based on email only
csv-cleaner clean duplicate_data.csv cleaned_data.csv \
  --operations "remove_duplicates" \
  --subset "email"
```

**Keep Specific Duplicate**
```bash
# Keep the last occurrence of duplicates
csv-cleaner clean duplicate_data.csv cleaned_data.csv \
  --operations "remove_duplicates" \
  --keep "last"
```

### Tutorial 6: ML-Based Deduplication

**Objective**: Use ML-based deduplication for fuzzy matching.

```bash
# Use dedupe library for fuzzy matching
csv-cleaner dedupe duplicate_data.csv cleaned_data.csv \
  --threshold 0.8 \
  --interactive
```

## 📝 Text Data Cleaning

### Tutorial 7: Basic Text Cleaning

**Objective**: Clean text data for consistency.

**Sample Data** (`text_data.csv`):
```csv
name,description,category
"John Doe","  Senior Developer  ","Engineering"
"Jane Smith","Data Scientist","Data Science"
"Bob Johnson","  Product Manager  ","Product"
"Alice Brown","UX Designer","Design"
```

**Basic Text Cleaning**
```bash
# Clean text data (trim whitespace, standardize case)
csv-cleaner clean text_data.csv cleaned_data.csv \
  --operations "clean_text" \
  --columns "name,description"
```

**Advanced Text Cleaning**
```bash
# Clean text with specific options
csv-cleaner clean text_data.csv cleaned_data.csv \
  --operations "clean_text" \
  --columns "name,description" \
  --text-options "lowercase,trim,remove_extra_spaces"
```

### Tutorial 8: Text Cleaning

**Objective**: Clean and standardize text data.

```bash
# Clean text data
csv-cleaner clean text_data.csv cleaned_data.csv \
  --operations "clean_text" \
  --columns "description"
```

## ✅ Data Validation

### Tutorial 9: Basic Validation

**Objective**: Validate data quality and structure.

**Sample Data** (`validation_data.csv`):
```csv
id,name,age,email,salary
1,John,25,john@example.com,50000
2,Jane,30,jane@example.com,60000
3,Bob,35,bob@example.com,70000
4,Alice,28,alice@example.com,55000
5,Charlie,40,charlie@example.com,80000
```

**Basic Validation**
```bash
# Validate data quality
csv-cleaner validate validation_data.csv
```

**Validation with Custom Schema**
```bash
# Create schema file (schema.json)
echo '{
  "id": {"type": "integer", "required": true},
  "name": {"type": "string", "required": true, "min_length": 2},
  "age": {"type": "integer", "min": 18, "max": 100},
  "email": {"type": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
  "salary": {"type": "integer", "min": 0}
}' > schema.json

# Validate with schema
csv-cleaner validate validation_data.csv --schema schema.json
```

### Tutorial 10: Data Quality Report

**Objective**: Generate comprehensive data quality reports.

```bash
# Generate HTML report
csv-cleaner report validation_data.csv --format html --output quality_report.html

# Generate JSON report
csv-cleaner report validation_data.csv --format json --output quality_report.json
```

## 🤖 AI-Powered Cleaning

### Tutorial 11: AI Data Analysis

**Objective**: Use AI to analyze data and get insights.

```bash
# Get AI analysis of data
csv-cleaner ai-analyze validation_data.csv

# Save analysis to file
csv-cleaner ai-analyze validation_data.csv --output analysis.json
```

**Focus on Specific Aspects**
```bash
# Focus on data quality issues
csv-cleaner ai-analyze validation_data.csv --focus "data_quality"

# Focus on outliers
csv-cleaner ai-analyze validation_data.csv --focus "outliers"
```

### Tutorial 12: AI-Powered Suggestions

**Objective**: Get AI suggestions for data cleaning.

```bash
# Get AI suggestions
csv-cleaner ai-suggest validation_data.csv

# Save suggestions to file
csv-cleaner ai-suggest validation_data.csv --output suggestions.json
```

**Focus on Specific Issues**
```bash
# Focus on data quality improvements
csv-cleaner ai-suggest validation_data.csv --focus "data_quality"

# Focus on data type improvements
csv-cleaner ai-suggest validation_data.csv --focus "data_types"
```

### Tutorial 13: AI-Powered Automatic Cleaning

**Objective**: Execute AI suggestions automatically.

```bash
# Execute AI suggestions with preview
csv-cleaner ai-clean validation_data.csv cleaned_data.csv --dry-run

# Execute AI suggestions automatically
csv-cleaner ai-clean validation_data.csv cleaned_data.csv --auto-confirm

# Execute with confidence threshold
csv-cleaner ai-clean validation_data.csv cleaned_data.csv --min-confidence 0.8
```

**Interactive AI Cleaning**
```bash
# Interactive mode - confirm each suggestion
csv-cleaner ai-clean validation_data.csv cleaned_data.csv --interactive
```

## 📊 Creating Visualizations

### Tutorial 14: Data Quality Visualizations

**Objective**: Create visualizations to understand data quality.

```bash
# Create quality heatmap
csv-cleaner visualize validation_data.csv --type quality --output quality_heatmap.png

# Create missing data visualization
csv-cleaner visualize validation_data.csv --type missing --output missing_data.png

# Create correlation matrix
csv-cleaner visualize validation_data.csv --type correlation --output correlation.png
```

### Tutorial 15: Basic Visualizations

**Objective**: Create data quality visualizations.

```bash
# Quality heatmap
csv-cleaner visualize validation_data.csv \
  --type quality \
  --output quality_heatmap.png
```

## 🔄 Batch Processing

### Tutorial 16: Processing Multiple Files

**Objective**: Clean multiple CSV files efficiently.

**Sample Files**:
- `data1.csv`
- `data2.csv`
- `data3.csv`

```bash
# Process all CSV files in directory using shell script
#!/bin/bash
for file in *.csv; do
    csv-cleaner clean "$file" "cleaned_$file" --operations "remove_duplicates,fill_missing"
done
```

**Alternative: Use Python API for Advanced Batch Processing**
```python
import os
from csv_cleaner import CSVCleaner

cleaner = CSVCleaner()
for file in os.listdir('.'):
    if file.endswith('.csv'):
        cleaner.clean_file(file, f"cleaned_{file}", ["remove_duplicates", "fill_missing"])
```

## ⚡ Performance Optimization

### Tutorial 17: Optimizing for Large Files

**Objective**: Clean large CSV files efficiently.

```bash
# Use parallel processing
csv-cleaner clean large_data.csv cleaned_data.csv \
  --operations "remove_duplicates,fill_missing" \
  --parallel \
  --workers 4

# Process in chunks
csv-cleaner clean large_data.csv cleaned_data.csv \
  --operations "remove_duplicates,fill_missing" \
  --chunk-size 10000

# Set memory limit
csv-cleaner clean large_data.csv cleaned_data.csv \
  --operations "remove_duplicates,fill_missing" \
  --memory-limit 2GB
```

### Tutorial 18: Performance Monitoring

**Objective**: Monitor and optimize performance.

```bash
# Enable performance monitoring
csv-cleaner clean validation_data.csv cleaned_data.csv \
  --operations "remove_duplicates,fill_missing" \
  --monitor-performance

# Show performance summary
csv-cleaner performance validation_data.csv
```

## 🎯 Best Practices

### General Best Practices
1. **Always Backup**: Create backups before cleaning
2. **Start Small**: Test on sample data first
3. **Validate Results**: Check cleaned data quality
4. **Document Changes**: Keep track of cleaning operations
5. **Use AI Wisely**: Review AI suggestions before execution

### Performance Best Practices
1. **Use Parallel Processing**: For large files
2. **Optimize Chunk Size**: Based on available memory
3. **Monitor Resources**: Watch memory and CPU usage
4. **Cache Results**: For repeated operations

### AI Best Practices
1. **Review Suggestions**: Always review AI suggestions
2. **Provide Feedback**: Help AI learn from your preferences
3. **Monitor Costs**: Keep track of AI usage costs
4. **Use Appropriate Models**: Choose models based on task complexity

## 📚 Next Steps

After completing these tutorials, you should be comfortable with:

- Basic data cleaning operations
- Handling missing values and duplicates
- Text data cleaning and normalization
- Data validation and quality assessment
- AI-powered data analysis and cleaning
- Creating data visualizations
- Batch processing and performance optimization

**Continue Learning**:
1. **Advanced Tutorials**: Explore complex data cleaning scenarios
2. **AI Tutorials**: Deep dive into AI-powered features
3. **Real-World Examples**: See practical applications
4. **Performance Guide**: Optimize for your specific use cases

---

*Ready for more advanced topics? Check out the [Advanced Tutorials](advanced-tutorials.md) and [AI Tutorials](ai-tutorials.md).*
