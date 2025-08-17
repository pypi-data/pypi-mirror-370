# Quick Start Guide

Get up and running with CSV Data Cleaner in minutes! This guide will walk you through the essential steps to start cleaning your CSV data.

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Install CSV Data Cleaner
```bash
pip install csv-cleaner
```

### Verify Installation
```bash
csv-cleaner --version
```

## 🎯 Your First Data Cleaning

### 1. Basic Cleaning
```bash
# Clean a CSV file with default operations
csv-cleaner clean input.csv output.csv
```

### 2. AI-Powered Cleaning (Recommended)
```bash
# Get AI suggestions for cleaning
csv-cleaner ai-suggest input.csv

# Execute AI suggestions automatically
csv-cleaner ai-clean input.csv output.csv
```

### 3. Interactive Mode
```bash
# Clean with Firebase CLI-style interactive prompts
csv-cleaner clean input.csv output.csv --interactive
```

The interactive mode provides a modern, user-friendly interface with:
- **Spacebar toggles** for enabling/disabling operations
- **Arrow key navigation** through available operations
- **Descriptive operation names** with explanations
- **Visual selection indicators** showing selected/unselected state
- **Fallback support** for environments without advanced terminal support

## 🤖 Setting Up AI Features

### 1. Configure AI Provider
```bash
# Set up OpenAI (recommended for beginners)
csv-cleaner ai-configure set --provider openai --api-key YOUR_API_KEY

# Or set up Anthropic
csv-cleaner ai-configure set --provider anthropic --api-key YOUR_API_KEY
```

### 2. Validate Configuration
```bash
csv-cleaner ai-configure validate
```

## 📊 Common Use Cases

### Remove Duplicates
```bash
csv-cleaner clean input.csv output.csv --operations "remove_duplicates"
```

### Handle Missing Values
```bash
csv-cleaner clean input.csv output.csv --operations "fill_missing"
```

### Clean Text Data
```bash
csv-cleaner clean input.csv output.csv --operations "clean_text"
```

### Validate Data
```bash
csv-cleaner validate input.csv
```

### Generate Report
```bash
csv-cleaner report input.csv --format html
```

## 🔧 Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `clean` | Clean CSV data | `csv-cleaner clean input.csv output.csv` |
| `ai-suggest` | Get AI suggestions | `csv-cleaner ai-suggest input.csv` |
| `ai-clean` | AI-powered cleaning | `csv-cleaner ai-clean input.csv output.csv` |
| `validate` | Validate data quality | `csv-cleaner validate input.csv` |
| `info` | Show system information | `csv-cleaner info` |
| `config` | Manage configuration | `csv-cleaner config show` |

## 📈 Performance Tips

### For Large Files
```bash
# Use parallel processing
csv-cleaner clean input.csv output.csv --parallel

# Process in chunks
csv-cleaner clean input.csv output.csv --chunk-size 10000
```

### For Memory Optimization
```bash
# Set memory limit
csv-cleaner clean input.csv output.csv --memory-limit 2GB
```

## 🎨 Visualization

### Generate Data Quality Visualizations
```bash
# Create quality heatmap
csv-cleaner visualize input.csv --type quality

# Create missing data visualization
csv-cleaner visualize input.csv --type missing
```

## 📋 Next Steps

1. **Read the [User Manual](../user-guides/user-manual.md)** for detailed feature explanations
2. **Try [Basic Tutorials](../tutorials/basic-tutorials.md)** for step-by-step examples
3. **Explore [AI Features](../user-guides/ai-features.md)** for advanced AI capabilities
4. **Check [Configuration Guide](../user-guides/configuration.md)** for customization options

## 🆘 Need Help?

- **Quick Issues**: Check [Troubleshooting](../reference/troubleshooting.md)
- **Common Questions**: See [FAQ](../reference/faq.md)
- **Detailed Support**: Visit [Support Guide](../../SUPPORT.md)

## 🎉 Congratulations!

You've successfully started using CSV Data Cleaner! The tool is now ready to help you clean and analyze your CSV data efficiently.

---

*Ready to dive deeper? Continue to the [User Manual](../user-guides/user-manual.md) for comprehensive feature coverage.*
