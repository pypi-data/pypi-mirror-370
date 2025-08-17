# CSV Data Cleaner

A powerful, self-contained tool for cleaning CSV data using industry-standard Python libraries with **AI-powered intelligent suggestions and automatic cleaning capabilities**.

## 🚀 Key Features

### **AI-Powered Features**
- **🤖 AI-Powered Automatic Cleaning**: Execute AI suggestions automatically with `ai-clean` command
- **🧠 Intelligent Suggestions**: Get AI-powered cleaning recommendations with `ai-suggest` command
- **📊 Data Analysis**: AI-powered data analysis and insights with `ai-analyze` command
- **🎯 Learning System**: AI learns from your feedback to improve suggestions over time
- **⚡ Multi-Provider Support**: OpenAI, Anthropic, and local LLM support

### **Core Cleaning Capabilities**
- **🔧 Multiple Libraries**: pandas, pyjanitor, feature-engine, dedupe, missingno
- **⚙️ 30+ Operations**: Remove duplicates, handle missing values, clean text, fix dates, etc.
- **📈 Performance Optimization**: Parallel processing, memory management, chunked processing
- **📊 Data Validation**: Schema validation, data quality assessment, comprehensive reporting
- **🎨 Visualization**: Data quality heatmaps, missing data analysis, correlation matrices

## 🛠️ Installation

### Quick Install
```bash
pip install csv-cleaner
```

### From Source
```bash
git clone https://github.com/your-repo/csv-cleaner.git
cd csv-cleaner
pip install -e .
```

## 🚀 Quick Start

### **AI-Powered Automatic Cleaning** (NEW!)
```bash
# Automatic cleaning with AI suggestions
csv-cleaner ai-clean input.csv output.csv

# Auto-confirm all suggestions
csv-cleaner ai-clean input.csv output.csv --auto-confirm

# Preview execution plan without modifying files
csv-cleaner ai-clean input.csv output.csv --dry-run

# Limit number of suggestions
csv-cleaner ai-clean input.csv output.csv --max-suggestions 10
```

### **AI-Powered Suggestions**
```bash
# Get AI-powered cleaning suggestions
csv-cleaner ai-suggest input.csv

# Get suggestions with specific analysis
csv-cleaner ai-suggest input.csv --output suggestions.json
```

### **AI-Powered Data Analysis**
```bash
# Get comprehensive data analysis
csv-cleaner ai-analyze input.csv

# Save analysis to file
csv-cleaner ai-analyze input.csv --output analysis.json
```

### **Traditional Cleaning**
```bash
# Clean with specific operations
csv-cleaner clean input.csv output.csv --operations "remove_duplicates,fill_missing"

# Interactive mode
csv-cleaner clean input.csv output.csv --interactive

# Performance optimized
csv-cleaner clean input.csv output.csv --parallel --chunk-size 10000
```

## 🤖 AI Configuration

### **Setup AI Providers**
```bash
# Configure OpenAI
csv-cleaner ai-configure set --provider openai --api-key sk-...

# Configure Anthropic
csv-cleaner ai-configure set --provider anthropic --api-key sk-ant-...

# Show current configuration
csv-cleaner ai-configure show

# Validate configuration
csv-cleaner ai-configure validate
```

### **AI Features Overview**

#### **AI-Powered Automatic Cleaning (`ai-clean`)**
- **Automatic Execution**: AI generates and executes cleaning suggestions
- **Execution Planning**: Shows detailed execution plan with confidence levels
- **User Control**: Choose between automatic execution and manual confirmation
- **Dry-Run Mode**: Preview changes without modifying files
- **Learning Integration**: AI learns from execution results

#### **AI-Powered Suggestions (`ai-suggest`)**
- **Intelligent Analysis**: AI analyzes data and suggests optimal cleaning operations
- **Confidence Scoring**: Each suggestion includes confidence level and reasoning
- **Library Selection**: AI recommends the best library for each operation
- **Impact Assessment**: Estimates the impact of each suggestion

#### **AI-Powered Analysis (`ai-analyze`)**
- **Comprehensive Profiling**: Detailed data quality assessment
- **Pattern Recognition**: Identifies data patterns and anomalies
- **Recommendation Engine**: Suggests cleaning strategies based on analysis
- **Exportable Reports**: Save analysis results for further review

## 📋 Available Operations

### **Basic Data Cleaning (Pandas)**
- `remove_duplicates` - Remove duplicate rows
- `fill_missing` - Fill missing values with various strategies
- `drop_missing` - Remove rows/columns with missing values
- `clean_text` - Clean and normalize text data
- `fix_dates` - Convert and standardize date formats
- `convert_types` - Convert data types automatically
- `rename_columns` - Rename columns
- `drop_columns` - Remove unwanted columns
- `select_columns` - Select specific columns

### **Advanced Data Cleaning (PyJanitor)**
- `clean_names` - Clean column names
- `remove_empty` - Remove empty rows/columns
- `fill_empty` - Fill empty values
- `handle_missing` - Advanced missing value handling
- `remove_constant_columns` - Remove columns with constant values
- `remove_columns_with_nulls` - Remove columns with null values
- `coalesce_columns` - Combine multiple columns

### **Feature Engineering (Feature-Engine)**
- `advanced_imputation` - Advanced missing value imputation
- `categorical_encoding` - Encode categorical variables
- `outlier_detection` - Detect and handle outliers
- `variable_selection` - Select relevant variables
- `data_transformation` - Apply data transformations
- `missing_indicator` - Create missing value indicators

### **Missing Data Analysis (MissingNo)**
- `missing_matrix` - Generate missing data matrix visualization
- `missing_bar` - Generate missing data bar chart
- `missing_heatmap` - Generate missing data heatmap
- `missing_dendrogram` - Generate missing data dendrogram
- `missing_summary` - Generate missing data summary

### **ML-Based Deduplication (Dedupe)**
- `dedupe` - ML-based deduplication with fuzzy matching

## 📊 Examples

### **Example 1: AI-Powered Automatic Cleaning**
```bash
# Clean messy data automatically
csv-cleaner ai-clean messy_data.csv cleaned_data.csv --auto-confirm
```

**Output:**
```
🤖 AI-Powered Data Cleaning
===========================

📊 Data Analysis Complete
- Rows: 10,000 | Columns: 15
- Missing values: 1,250 (8.3%)
- Duplicates: 150 (1.5%)
- Data quality score: 78%

🎯 AI Suggestions Generated (5 suggestions)
1. Remove duplicates (confidence: 95%)
2. Fill missing values with median (confidence: 88%)
3. Clean column names (confidence: 92%)
4. Convert date columns (confidence: 85%)
5. Handle outliers in 'price' column (confidence: 76%)

📋 Execution Plan
================
1. clean_names (pandas) - Clean column names
2. remove_duplicates (pandas) - Remove 150 duplicate rows
3. fill_missing (pandas) - Fill 1,250 missing values
4. fix_dates (pandas) - Convert date columns
5. handle_outliers (feature-engine) - Handle price outliers

🚀 Executing AI suggestions...
████████████████████████████████████████ 100%

✅ Successfully executed 5 operations
📊 Results: 9,850 rows → 9,700 rows (150 duplicates removed)
💾 Saved to: cleaned_data.csv
```

### **Example 2: AI-Powered Suggestions**
```bash
csv-cleaner ai-suggest data.csv
```

**Output:**
```
🤖 AI-Powered Cleaning Suggestions
==================================

📊 Data Analysis
- Dataset: 5,000 rows × 12 columns
- Quality issues detected: Missing values, inconsistent dates, duplicates

🎯 Recommended Operations:

1. **Remove Duplicates** (Confidence: 94%)
   - Library: pandas
   - Impact: Remove ~50 duplicate rows
   - Reasoning: Found exact duplicates in customer data

2. **Fill Missing Values** (Confidence: 89%)
   - Library: pandas
   - Strategy: Forward fill for dates, median for numeric
   - Impact: Fill 200 missing values

3. **Fix Date Columns** (Confidence: 87%)
   - Library: pandas
   - Columns: 'order_date', 'ship_date'
   - Impact: Standardize date formats

4. **Clean Column Names** (Confidence: 92%)
   - Library: pyjanitor
   - Impact: Standardize naming convention

5. **Handle Outliers** (Confidence: 76%)
   - Library: feature-engine
   - Column: 'amount'
   - Impact: Cap extreme values
```

## 🔧 Configuration

### **Performance Settings**
```bash
# Set memory limit
csv-cleaner config set performance.memory_limit 4.0

# Enable parallel processing
csv-cleaner config set performance.parallel_processing true

# Set chunk size
csv-cleaner config set performance.chunk_size 5000
```

### **AI Settings**
```bash
# Set default AI provider
csv-cleaner config set ai.default_provider openai

# Set suggestion confidence threshold
csv-cleaner config set ai.confidence_threshold 0.7

# Enable learning mode
csv-cleaner config set ai.learning_enabled true
```

## 📈 Performance Features

- **Parallel Processing**: Multi-core data processing
- **Memory Management**: Efficient memory usage for large datasets
- **Chunked Processing**: Process large files in chunks
- **Progress Tracking**: Real-time progress monitoring
- **Performance Monitoring**: Track processing times and resource usage

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=csv_cleaner

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 🚀 Deployment

### **PyPI Deployment**

The project includes automated deployment scripts for PyPI:

```bash
# Setup basic version
python scripts/setup-pypi.py

# Deploy to TestPyPI
python scripts/deploy-pypi.py --test

# Deploy to production PyPI
python scripts/deploy-pypi.py --version 1.0.0
```

### **Deployment Features**
- ✅ Automated testing and validation
- ✅ Safety checks and prerequisites verification
- ✅ Package building and quality checks
- ✅ Version management and tagging
- ✅ Release notes generation

For detailed deployment instructions, see [scripts/deployment-guide.md](scripts/deployment-guide.md).

## 📚 Documentation

- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)
- [AI Features Guide](docs/ai-features.md)
- [Performance Tuning](docs/performance.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/csv-cleaner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/csv-cleaner/discussions)

---

**Made with ❤️ for data scientists and analysts**
