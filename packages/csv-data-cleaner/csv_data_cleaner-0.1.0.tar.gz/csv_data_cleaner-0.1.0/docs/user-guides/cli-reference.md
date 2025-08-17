# CLI Reference

Complete command-line interface reference for CSV Cleaner.

## 📋 Overview

CSV Cleaner provides a comprehensive command-line interface with the following command categories:

- **Core Commands**: Basic data cleaning operations
- **AI Commands**: AI-powered features (Pro version)
- **Utility Commands**: Configuration and information
- **Advanced Commands**: Performance analysis and deduplication (Pro version)

## 🔄 Version Comparison

CSV Cleaner is available in two versions:

| Feature | Basic Version | Pro Version |
|---------|---------------|-------------|
| **Core Operations** | ✅ | ✅ |
| Data Validation | ✅ | ✅ |
| Basic Data Cleaning | ✅ | ✅ |
| Data Analysis | ✅ | ✅ |
| Quality Reports | ✅ | ✅ |
| **Advanced Features** | ❌ | ✅ |
| Missing Data Visualization | ❌ | ✅ |
| Advanced Deduplication | ❌ | ✅ |
| AI-Powered Suggestions | ❌ | ✅ |
| Performance Analysis | ❌ | ✅ |
| Advanced Data Transformation | ❌ | ✅ |

## 📊 Operation Availability Matrix

| Operation | Basic Version | Pro Version | Description |
|-----------|---------------|-------------|-------------|
| **Basic Operations** | ✅ | ✅ | |
| `remove_duplicates` | ✅ | ✅ | Remove duplicate rows |
| `fill_missing` | ✅ | ✅ | Fill missing values |
| `drop_missing` | ✅ | ✅ | Drop rows with missing values |
| `clean_names` | ✅ | ✅ | Clean column names |
| `validate` | ✅ | ✅ | Validate data quality |
| `analyze` | ✅ | ✅ | Analyze data statistics |
| `report` | ✅ | ✅ | Generate data reports |
| `quality_visualization` | ✅ | ✅ | Quality score visualization |
| **Pro Operations** | ❌ | ✅ | |
| `missing_matrix` | ❌ | ✅ | Missing data matrix visualization |
| `missing_bar` | ❌ | ✅ | Missing data bar chart |
| `missing_heatmap` | ❌ | ✅ | Missing data heatmap |
| `missing_dendrogram` | ❌ | ✅ | Missing data dendrogram |
| `missing_summary` | ❌ | ✅ | Missing data summary |
| `dedupe` | ❌ | ✅ | Advanced ML deduplication |
| `train_dedupe` | ❌ | ✅ | Deduplication model training |
| `predict_duplicates` | ❌ | ✅ | Duplicate prediction |
| `advanced_imputation` | ❌ | ✅ | Advanced data imputation |
| `categorical_encoding` | ❌ | ✅ | Categorical variable encoding |
| `outlier_detection` | ❌ | ✅ | Outlier detection |
| `variable_selection` | ❌ | ✅ | Variable selection |
| `data_transformation` | ❌ | ✅ | Data transformation |
| `missing_indicator` | ❌ | ✅ | Missing value indicators |
| `ai_suggest` | ❌ | ✅ | AI-powered suggestions |
| `ai_clean` | ❌ | ✅ | AI-powered cleaning |
| `ai_analyze` | ❌ | ✅ | AI-powered analysis |
| `ai_configure` | ❌ | ✅ | AI configuration |
| `performance_analysis` | ❌ | ✅ | Performance analysis |
| `batch_processing` | ❌ | ✅ | Batch processing |
| `parallel_processing` | ❌ | ✅ | Parallel processing |

## 🔒 Upgrade Prompts

When you try to use a Pro feature in the Basic version, you'll see a helpful upgrade prompt like this:

```
❌ Missing Data Matrix Visualization is a Pro feature!
   Upgrade to CSV Cleaner Pro for advanced data analysis features!
   Visit: https://gumroad.com/csv-cleaner-pro
```

This ensures you know exactly which features require an upgrade and how to get them.

## 🚀 Core Commands

### `clean` - Clean CSV Data

Clean a CSV file using specified operations.

```bash
csv-cleaner clean INPUT_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file
- `OUTPUT_FILE`: Path to the output CSV file

**Options:**
- `--operations, -ops`: Comma-separated list of operations to perform
- `--config, -c`: Path to configuration file
- `--interactive, -i`: Run in interactive mode
- `--verbose, -v`: Enable verbose logging
- `--chunk-size`: Chunk size for processing large files
- `--parallel/--no-parallel`: Enable/disable parallel processing (default: True)
- `--max-memory`: Maximum memory usage in GB
- `--dry-run`: Preview operations without modifying files

**Examples:**
```bash
# Basic cleaning
csv-cleaner clean data.csv cleaned.csv

# Clean with specific operations
csv-cleaner clean data.csv cleaned.csv --operations "remove_duplicates,clean_names"

# Interactive mode
csv-cleaner clean data.csv cleaned.csv --interactive

# Dry run to preview changes
csv-cleaner clean data.csv cleaned.csv --dry-run
```

### `analyze` - Analyze CSV Data

Analyze CSV data and generate smart validation rules.

```bash
csv-cleaner analyze INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the CSV file to analyze

**Options:**
- `--output, -o`: Output path for analysis report
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Basic analysis
csv-cleaner analyze data.csv

# Generate analysis report
csv-cleaner analyze data.csv --output analysis_report.txt

# Verbose analysis
csv-cleaner analyze data.csv --verbose
```

### `validate` - Validate CSV Data

Validate a CSV file and show information.

```bash
csv-cleaner validate INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the CSV file to validate

**Options:**
- `--schema, -s`: Path to validation schema file
- `--output, -o`: Output path for validation report
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Basic validation
csv-cleaner validate data.csv

# Validation with schema
csv-cleaner validate data.csv --schema schema.json

# Generate validation report
csv-cleaner validate data.csv --output validation_report.json
```

### `visualize` - Generate Visualizations

Generate data visualizations.

```bash
csv-cleaner visualize INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file

**Options:**
- `--type, -t`: Type of visualization (matrix, bar, heatmap, dendrogram, quality, correlation, distribution)
- `--output, -o`: Output path for visualization
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Generate missing data matrix
csv-cleaner visualize data.csv --type matrix

# Create quality heatmap
csv-cleaner visualize data.csv --type quality --output quality_plot.png

# Generate correlation heatmap
csv-cleaner visualize data.csv --type correlation
```

### `report` - Generate Data Quality Reports

Generate comprehensive data quality reports.

```bash
csv-cleaner report INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file

**Options:**
- `--output, -o`: Output path for report
- `--format, -f`: Report format (html, json)
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Generate HTML report
csv-cleaner report data.csv --output report.html

# Generate JSON report
csv-cleaner report data.csv --format json --output report.json
```

## 🤖 AI Commands (Pro Version)

### `ai-suggest` - Get AI Suggestions

Get AI-powered cleaning suggestions for a CSV file.

```bash
csv-cleaner ai-suggest INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file

**Options:**
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--max-suggestions`: Maximum number of suggestions to show (default: 5)
- `--no-analysis`: Skip data analysis in output

**Examples:**
```bash
# Get AI suggestions
csv-cleaner ai-suggest data.csv

# Get more suggestions
csv-cleaner ai-suggest data.csv --max-suggestions 10

# Skip analysis
csv-cleaner ai-suggest data.csv --no-analysis
```

### `ai-clean` - AI-Powered Cleaning

AI-powered automatic cleaning of CSV data.

```bash
csv-cleaner ai-clean INPUT_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file
- `OUTPUT_FILE`: Path to the output CSV file

**Options:**
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--auto-confirm`: Automatically confirm all AI suggestions
- `--dry-run`: Show execution plan without modifying files
- `--max-suggestions`: Maximum number of suggestions to consider (default: 5)

**Examples:**
```bash
# AI-powered cleaning
csv-cleaner ai-clean data.csv cleaned.csv

# Auto-confirm all suggestions
csv-cleaner ai-clean data.csv cleaned.csv --auto-confirm

# Preview AI cleaning plan
csv-cleaner ai-clean data.csv cleaned.csv --dry-run
```

### `ai-analyze` - AI Data Analysis

Get AI-powered data analysis for a CSV file.

```bash
csv-cleaner ai-analyze INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file

**Options:**
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--output, -o`: Output file for analysis results (JSON format)

**Examples:**
```bash
# AI data analysis
csv-cleaner ai-analyze data.csv

# Save analysis to file
csv-cleaner ai-analyze data.csv --output analysis.json
```

### `ai-configure` - Configure AI Settings

Configure AI settings and API keys.

```bash
csv-cleaner ai-configure ACTION [OPTIONS]
```

**Arguments:**
- `ACTION`: Configuration action (show, set, remove, validate)

**Options:**
- `--provider`: AI provider name (openai, anthropic, local)
- `--api-key`: API key for the provider
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Show current AI configuration
csv-cleaner ai-configure show

# Set OpenAI API key
csv-cleaner ai-configure set --provider openai --api-key sk-...

# Remove provider configuration
csv-cleaner ai-configure remove --provider openai

# Validate AI configuration
csv-cleaner ai-configure validate
```

### `ai-model` - Configure AI Models

Configure AI models for providers.

```bash
csv-cleaner ai-model ACTION [OPTIONS]
```

**Arguments:**
- `ACTION`: Configuration action (show, set)

**Options:**
- `--provider`: Provider name (openai, anthropic, local)
- `--model`: Model name to set
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Show current models
csv-cleaner ai-model show

# Set OpenAI model
csv-cleaner ai-model set --provider openai --model gpt-4o

# Set Anthropic model
csv-cleaner ai-model set --provider anthropic --model claude-3-haiku-20240307
```

### `ai-logs` - View AI Logs

View AI interaction logs and usage summary.

```bash
csv-cleaner ai-logs [OPTIONS]
```

**Options:**
- `--days, -d`: Number of days to include in summary (default: 7)
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# View recent logs
csv-cleaner ai-logs

# View logs for last 30 days
csv-cleaner ai-logs --days 30

# Verbose log output
csv-cleaner ai-logs --verbose
```

## 🔧 Utility Commands

### `info` - Show System Information

Show information about CSV Cleaner.

```bash
csv-cleaner info
```

**Examples:**
```bash
# Show system information
csv-cleaner info
```

### `config` - Manage Configuration

Manage CSV Cleaner configuration.

```bash
csv-cleaner config ACTION [KEY] [VALUE] [OPTIONS]
```

**Arguments:**
- `ACTION`: Configuration action (show, set, get, init)
- `KEY`: Configuration key (for set/get actions)
- `VALUE`: Configuration value (for set action)

**Options:**
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Show current configuration
csv-cleaner config show

# Set configuration value
csv-cleaner config set backup_enabled true

# Get specific configuration
csv-cleaner config get chunk_size

# Initialize configuration
csv-cleaner config init
```

## ⚡ Advanced Commands (Pro Version)

### `dedupe` - ML-Based Deduplication

Perform ML-based deduplication on CSV data.

```bash
csv-cleaner dedupe INPUT_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file
- `OUTPUT_FILE`: Path to the output CSV file

**Options:**
- `--threshold, -t`: Deduplication threshold (0.0-1.0, default: 0.5)
- `--interactive, -i`: Enable interactive training
- `--training-file`: Path to training data file
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Basic deduplication
csv-cleaner dedupe data.csv deduplicated.csv

# Higher threshold
csv-cleaner dedupe data.csv deduplicated.csv --threshold 0.8

# Interactive training
csv-cleaner dedupe data.csv deduplicated.csv --interactive

# Use training file
csv-cleaner dedupe data.csv deduplicated.csv --training-file training.json
```

### `performance` - Performance Analysis

Analyze performance characteristics of data cleaning operations.

```bash
csv-cleaner performance INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Path to the input CSV file

**Options:**
- `--operations, -ops`: Comma-separated list of operations to test
- `--config, -c`: Path to configuration file
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Analyze all operations
csv-cleaner performance data.csv

# Analyze specific operations
csv-cleaner performance data.csv --operations "remove_duplicates,clean_names"

# Verbose performance analysis
csv-cleaner performance data.csv --verbose
```

## 📊 Available Operations

### Pandas Operations
- `remove_duplicates`: Remove duplicate rows
- `drop_missing`: Drop rows with missing values
- `fill_missing`: Fill missing values
- `convert_types`: Convert data types
- `rename_columns`: Rename columns
- `drop_columns`: Drop specified columns
- `sort_values`: Sort data by columns
- `reset_index`: Reset DataFrame index

### PyJanitor Operations
- `clean_names`: Clean column names
- `remove_empty`: Remove empty rows/columns
- `fill_empty`: Fill empty values
- `handle_missing`: Handle missing data
- `remove_duplicates`: Remove duplicates
- `drop_columns`: Drop columns
- `rename_columns`: Rename columns

*Note: Available operations may vary based on your CSV Cleaner version and installed dependencies. Use `csv-cleaner info` to see available operations for your installation.*

## 🔧 Global Options

All commands support these global options:

- `--version`: Show version and exit
- `--help`: Show help message and exit
- `--verbose, -v`: Enable verbose logging
- `--config, -c`: Path to configuration file

## 📝 Examples

### Complete Workflow Example

```bash
# 1. Analyze your data
csv-cleaner analyze data.csv

# 2. Validate your data
csv-cleaner validate data.csv

# 3. Get AI suggestions
csv-cleaner ai-suggest data.csv

# 4. Clean the data
csv-cleaner clean data.csv cleaned.csv --operations "remove_duplicates,clean_names"

# 5. Generate a report
csv-cleaner report cleaned.csv --output final_report.html

# 6. Visualize the results
csv-cleaner visualize cleaned.csv --type quality --output quality_plot.png
```

### Interactive Cleaning Example

```bash
# Start interactive cleaning session
csv-cleaner clean data.csv cleaned.csv --interactive

# The tool will guide you through:
# - Selecting operations
# - Configuring parameters
# - Previewing changes
# - Confirming execution
```

### AI-Powered Workflow Example

```bash
# 1. Configure AI
csv-cleaner ai-configure set --provider openai --api-key YOUR_KEY

# 2. Get AI analysis
csv-cleaner ai-analyze data.csv --output analysis.json

# 3. Get AI suggestions
csv-cleaner ai-suggest data.csv

# 4. Execute AI cleaning
csv-cleaner ai-clean data.csv cleaned.csv --auto-confirm
```

## 🆘 Getting Help

### Command Help
```bash
# Get help for specific command
csv-cleaner clean --help
csv-cleaner ai-suggest --help
```

### General Help
```bash
# Show all available commands
csv-cleaner --help
```

### Version Information
```bash
# Show version
csv-cleaner --version
```

## 📚 Related Documentation

- **[User Manual](user-manual.md)** - Complete user guide
- **[Configuration Guide](configuration.md)** - Configuration management
- **[AI Features Guide](ai-features.md)** - AI-powered features
- **[Quick Start Guide](../getting-started/quick-start.md)** - Getting started

---

*For more detailed information about specific features, see the [User Manual](user-manual.md).*
