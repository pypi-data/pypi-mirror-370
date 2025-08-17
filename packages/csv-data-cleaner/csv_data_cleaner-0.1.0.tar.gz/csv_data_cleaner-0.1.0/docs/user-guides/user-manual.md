# User Manual

Complete guide to using CSV Data Cleaner - from basic operations to advanced AI-powered features.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [AI-Powered Features](#ai-powered-features)
4. [Command Reference](#command-reference)
5. [Data Operations](#data-operations)
6. [Performance & Optimization](#performance--optimization)
7. [Visualization](#visualization)
8. [Advanced Features](#advanced-features)

## 🎯 Overview

CSV Data Cleaner is a comprehensive tool for cleaning, validating, and analyzing CSV data. It combines traditional data cleaning techniques with AI-powered intelligence to provide the most effective data cleaning experience.

### Key Capabilities
- **30+ Data Operations**: Remove duplicates, handle missing values, clean text, fix dates, etc.
- **AI-Powered Intelligence**: Get intelligent suggestions for data cleaning
- **Multi-Library Support**: pandas, pyjanitor, feature-engine, dedupe, missingno
- **Performance Optimization**: Parallel processing, memory management, chunked processing
- **Data Validation**: Schema validation, data quality assessment
- **Visualization**: Data quality heatmaps, missing data analysis

## 🔧 Core Features

### Basic Cleaning Operations

#### Remove Duplicates
```bash
# Remove duplicate rows
csv-cleaner clean input.csv output.csv --operations "remove_duplicates"

# Remove duplicates based on specific columns
csv-cleaner clean input.csv output.csv --operations "remove_duplicates" --subset "column1,column2"
```

#### Handle Missing Values
```bash
# Fill missing values with forward fill
csv-cleaner clean input.csv output.csv --operations "fill_missing"

# Fill missing values with specific value
csv-cleaner clean input.csv output.csv --operations "fill_missing" --method "value" --fill-value "N/A"

# Drop rows with missing values
csv-cleaner clean input.csv output.csv --operations "drop_missing"
```

#### Clean Column Names
```bash
# Clean column names
csv-cleaner clean input.csv output.csv --operations "clean_names"

# Clean specific column names
csv-cleaner clean input.csv output.csv --operations "clean_names" --columns "name,description"
```

#### Clean Text Data
```bash
# Clean text columns
csv-cleaner clean input.csv output.csv --operations "clean_text"

# Clean specific text columns
csv-cleaner clean input.csv output.csv --operations "clean_text" --columns "name,description"
```

#### Fix Date Formats
```bash
# Fix date columns
csv-cleaner clean input.csv output.csv --operations "fix_dates"

# Specify date format
csv-cleaner clean input.csv output.csv --operations "fix_dates" --date-format "%Y-%m-%d"
```

### Data Validation

#### Analyze Data
```bash
# Analyze data and generate validation rules
csv-cleaner analyze input.csv

# Generate analysis report
csv-cleaner analyze input.csv --output analysis_report.txt
```

#### Validate Data Quality
```bash
# Validate data quality
csv-cleaner validate input.csv

# Validate with custom schema
csv-cleaner validate input.csv --schema schema.json
```

#### Generate Quality Report
```bash
# Generate comprehensive quality report
csv-cleaner report input.csv --format html

# Generate JSON report
csv-cleaner report input.csv --format json
```

## 🤖 AI-Powered Features

### AI Suggestions

#### Get Cleaning Suggestions
```bash
# Get AI suggestions for data cleaning
csv-cleaner ai-suggest input.csv

# Save suggestions to file
csv-cleaner ai-suggest input.csv --output suggestions.json

# Get suggestions with specific focus
csv-cleaner ai-suggest input.csv --focus "data_quality"
```

#### AI-Powered Automatic Cleaning
```bash
# Execute AI suggestions automatically
csv-cleaner ai-clean input.csv output.csv

# Preview execution plan
csv-cleaner ai-clean input.csv output.csv --dry-run

# Auto-confirm all suggestions
csv-cleaner ai-clean input.csv output.csv --auto-confirm

# Limit number of suggestions
csv-cleaner ai-clean input.csv output.csv --max-suggestions 10
```

#### AI Data Analysis
```bash
# Get comprehensive data analysis
csv-cleaner ai-analyze input.csv

# Save analysis to file
csv-cleaner ai-analyze input.csv --output analysis.json

# Focus on specific aspects
csv-cleaner ai-analyze input.csv --focus "outliers,patterns"
```

### AI Configuration

#### Setup AI Providers
```bash
# Configure OpenAI
csv-cleaner ai-configure set --provider openai --api-key YOUR_API_KEY

# Configure Anthropic
csv-cleaner ai-configure set --provider anthropic --api-key YOUR_API_KEY

# Configure local model
csv-cleaner ai-configure set --provider local --model llama3.1:8b
```

#### Manage AI Settings
```bash
# Show current configuration
csv-cleaner ai-configure show

# Validate configuration
csv-cleaner ai-configure validate

# Remove provider
csv-cleaner ai-configure remove --provider openai
```

## 📝 Command Reference

### Main Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `clean` | Clean CSV data | `csv-cleaner clean <input> <output> [options]` |
| `analyze` | Analyze data and generate validation rules | `csv-cleaner analyze <input> [options]` |
| `validate` | Validate data quality | `csv-cleaner validate <input> [options]` |
| `info` | Show system information | `csv-cleaner info` |
| `report` | Generate reports | `csv-cleaner report <input> [options]` |
| `visualize` | Create visualizations | `csv-cleaner visualize <input> [options]` |
| `dedupe` | ML-based deduplication | `csv-cleaner dedupe <input> <output> [options]` |
| `performance` | Performance testing | `csv-cleaner performance <input> [options]` |

### AI Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `ai-suggest` | Get AI suggestions | `csv-cleaner ai-suggest <input> [options]` |
| `ai-clean` | AI-powered cleaning | `csv-cleaner ai-clean <input> <output> [options]` |
| `ai-analyze` | AI data analysis | `csv-cleaner ai-analyze <input> [options]` |
| `ai-configure` | Manage AI settings | `csv-cleaner ai-configure <action> [options]` |
| `ai-logs` | View AI logs | `csv-cleaner ai-logs [options]` |
| `ai-model` | Manage AI models | `csv-cleaner ai-model <action> [options]` |

### Configuration Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `config` | Manage configuration | `csv-cleaner config <action> [options]` |

## 🔄 Data Operations

### Available Operations

#### Basic Operations (Pandas)
- `remove_duplicates` - Remove duplicate rows
- `drop_missing` - Drop rows with missing values
- `fill_missing` - Fill missing values
- `clean_text` - Clean text data
- `convert_types` - Convert data types
- `rename_columns` - Rename columns
- `drop_columns` - Drop columns
- `select_columns` - Select specific columns
- `fix_dates` - Fix date formats

#### Advanced Operations (PyJanitor)
- `clean_names` - Clean column names
- `remove_empty` - Remove empty rows/columns
- `fill_empty` - Fill empty values
- `handle_missing` - Advanced missing value handling
- `remove_constant_columns` - Remove columns with constant values
- `remove_columns_with_nulls` - Remove columns with null values
- `coalesce_columns` - Combine multiple columns

#### Feature Engineering (Feature-Engine)
- `advanced_imputation` - Advanced missing value imputation
- `categorical_encoding` - Encode categorical variables
- `outlier_detection` - Detect and handle outliers
- `variable_selection` - Select relevant variables
- `data_transformation` - Apply data transformations
- `missing_indicator` - Create missing value indicators

#### Missing Data Analysis (MissingNo)
- `missing_matrix` - Generate missing data matrix visualization
- `missing_bar` - Generate missing data bar chart
- `missing_heatmap` - Generate missing data heatmap
- `missing_dendrogram` - Generate missing data dendrogram
- `missing_summary` - Generate missing data summary

#### ML-Based Deduplication (Dedupe)
- `dedupe` - ML-based deduplication with fuzzy matching

### Operation Parameters

#### Method Parameters
```bash
# Specify method for operations
csv-cleaner clean input.csv output.csv --operations "fill_missing" --method "forward"

# Available methods for fill_missing:
# - forward: Forward fill
# - backward: Backward fill
# - mean: Mean value
# - median: Median value
# - mode: Mode value
# - value: Specific value
```

#### Column Parameters
```bash
# Specify columns for operations
csv-cleaner clean input.csv output.csv --operations "clean_text" --columns "name,description"

# Use all columns
csv-cleaner clean input.csv output.csv --operations "clean_text" --columns "all"
```

## ⚡ Performance & Optimization

### Parallel Processing
```bash
# Enable parallel processing
csv-cleaner clean input.csv output.csv --parallel

# Specify number of workers
csv-cleaner clean input.csv output.csv --parallel --workers 4
```

### Memory Management
```bash
# Set memory limit
csv-cleaner clean input.csv output.csv --memory-limit 2GB

# Process in chunks
csv-cleaner clean input.csv output.csv --chunk-size 10000
```

### Performance Monitoring
```bash
# Enable performance monitoring
csv-cleaner clean input.csv output.csv --monitor-performance

# Show performance summary
csv-cleaner performance input.csv
```

## 🎨 Visualization

### Data Quality Visualizations
```bash
# Create quality heatmap
csv-cleaner visualize input.csv --type quality

# Create missing data visualization
csv-cleaner visualize input.csv --type missing

# Create correlation matrix
csv-cleaner visualize input.csv --type correlation
```

### Custom Visualizations
```bash
# Specify output format
csv-cleaner visualize input.csv --type quality --format png

# Set figure size
csv-cleaner visualize input.csv --type quality --figsize "12,8"

# Custom color scheme
csv-cleaner visualize input.csv --type quality --colormap "viridis"
```

## 🚀 Advanced Features

### Batch Processing
```bash
# Process multiple files (requires custom script)
# Note: Batch processing is not directly supported in CLI
# Use shell scripts or Python API for batch operations
```

### Custom Operations
```bash
# Note: Custom operations are not directly supported in CLI
# Use the Python API for custom operations
```

### Integration with Other Tools
```bash
# Note: Direct format conversion and cloud storage integration
# are not currently supported in CLI
# Use the Python API for advanced integrations
```

## 📊 Output Formats

### Supported Output Formats
- CSV (default)
- HTML (reports only)
- JSON (reports only)

### Output Options
```bash
# Note: Format conversion is limited to reports
# CSV output is the primary format for cleaned data
```

## 🔧 Configuration

### Global Configuration
```bash
# Show current configuration
csv-cleaner config show

# Set configuration value
csv-cleaner config set --key "default_operations" --value "remove_duplicates,fill_missing"

# Reset configuration
csv-cleaner config reset
```

### Environment Variables
```bash
# Set configuration via environment variables
export CSV_CLEANER_DEFAULT_OPERATIONS="remove_duplicates,fill_missing"
export CSV_CLEANER_PARALLEL_ENABLED="true"
```

## 🆘 Troubleshooting

### Common Issues

#### Memory Issues
```bash
# Reduce chunk size
csv-cleaner clean input.csv output.csv --chunk-size 1000

# Set memory limit
csv-cleaner clean input.csv output.csv --memory-limit 1GB
```

#### Performance Issues
```bash
# Enable parallel processing
csv-cleaner clean input.csv output.csv --parallel

# Note: --optimize flag is not currently supported
```

#### AI Issues
```bash
# Check AI configuration
csv-cleaner ai-configure validate

# Test AI connection
csv-cleaner ai-configure test
```

## 📚 Next Steps

1. **Explore [AI Features Guide](ai-features.md)** for detailed AI capabilities
2. **Check [CLI Reference](cli-reference.md)** for complete command documentation
3. **Try [Tutorials](../tutorials/)** for practical examples
4. **Read [Performance Guide](../technical/performance.md)** for optimization tips

## 🔧 Recommended Workflow

For best results, follow this recommended workflow:

1. **Analyze**: Start with `csv-cleaner analyze` to understand your data
2. **Validate**: Use `csv-cleaner validate` to check data quality
3. **Get AI Suggestions**: Use `csv-cleaner ai-suggest` for intelligent recommendations
4. **Clean**: Execute cleaning operations with `csv-cleaner clean`
5. **Report**: Generate quality reports with `csv-cleaner report`
6. **Visualize**: Create visualizations with `csv-cleaner visualize`

---

*For technical details, see the [API Reference](../technical/api-reference.md) and [Architecture Overview](../technical/architecture.md).*
