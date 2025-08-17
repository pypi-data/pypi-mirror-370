# CSV Data Cleaner - Library Usage Examples

This folder contains comprehensive examples demonstrating how to use the CSV Data Cleaner as a library in your Python projects.

## 📚 Examples Overview

### **Basic Usage**
- `basic_cleaning.py` - Simple data cleaning operations
- `dataframe_cleaning.py` - Working with pandas DataFrames directly
- `custom_operations.py` - Using specific cleaning operations

### **Advanced Features**
- `ai_powered_cleaning.py` - AI-powered intelligent cleaning
- `performance_optimization.py` - Large file processing and optimization
- `custom_configuration.py` - Advanced configuration management

### **Real-World Scenarios**
- `ecommerce_data_cleaning.py` - Cleaning e-commerce datasets
- `financial_data_cleaning.py` - Financial data processing
- `survey_data_cleaning.py` - Survey and research data cleaning

### **Integration Examples**
- `web_application_integration.py` - Flask/Django integration
- `data_pipeline_integration.py` - ETL pipeline integration
- `jupyter_notebook_examples.py` - Jupyter notebook usage

## 🚀 Quick Start

### Installation
```bash
pip install csv-cleaner
```

### Basic Example
```python
from csv_cleaner.core.cleaner import CSVCleaner
import pandas as pd

# Load data
df = pd.read_csv("your_data.csv")

# Initialize cleaner
cleaner = CSVCleaner()

# Clean data
cleaned_df = cleaner.clean_dataframe(
    df,
    operations=["remove_duplicates", "fill_missing", "clean_names"]
)

# Save results
cleaned_df.to_csv("cleaned_data.csv", index=False)
```

## 📁 Example Files

Each example file includes:
- **Complete working code** that you can run immediately
- **Detailed comments** explaining each step
- **Sample data** or instructions for creating test data
- **Expected outputs** and results
- **Best practices** and tips

## 🔧 Running Examples

1. **Install dependencies**:
   ```bash
   pip install csv-cleaner pandas numpy
   ```

2. **Run any example**:
   ```bash
   python examples/basic_cleaning.py
   ```

3. **Modify examples** to work with your own data

## 📊 Sample Data

Most examples include sample data generation or use common datasets. You can:
- Replace sample data with your own CSV files
- Modify the data generation functions to match your data structure
- Use the examples as templates for your specific use cases

## 🤖 AI Features

Examples with AI features require API keys:
- **OpenAI**: Set `OPENAI_API_KEY` environment variable
- **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable
- **Local LLMs**: Configure Ollama or other local providers

## 📈 Performance Tips

- Use chunked processing for large files (>1GB)
- Enable parallel processing for better performance
- Monitor memory usage with large datasets
- Use appropriate chunk sizes based on your system

## 🔗 Integration Patterns

The examples demonstrate common integration patterns:
- **Web Applications**: Flask/Django integration
- **Data Pipelines**: ETL and data processing workflows
- **Jupyter Notebooks**: Interactive data analysis
- **Batch Processing**: Automated cleaning workflows

## 📝 Contributing

Feel free to:
- Modify examples for your specific use cases
- Add new examples for different scenarios
- Improve existing examples with better practices
- Share your use cases and examples

## 🆘 Getting Help

- Check the [main documentation](../docs/) for detailed API reference
- Review [troubleshooting guide](../docs/reference/troubleshooting.md) for common issues
- Open an issue for bugs or feature requests
