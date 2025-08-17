# Frequently Asked Questions (FAQ)

Common questions and answers about CSV Data Cleaner. If you don't find your answer here, check the [Troubleshooting Guide](troubleshooting.md) or [Support Guide](../../SUPPORT.md).

## 🚀 Getting Started

### Q: How do I install CSV Data Cleaner?
**A**: You can install CSV Data Cleaner using pip:
```bash
pip install csv-cleaner
```

For source installation, see the [Installation Guide](../getting-started/installation.md).

### Q: What are the system requirements?
**A**:
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large files)
- 1GB disk space
- Internet connection (for AI features)

### Q: How do I verify the installation?
**A**: Run the version command:
```bash
csv-cleaner --version
```

### Q: What's the difference between basic and AI-powered cleaning?
**A**:
- **Basic cleaning**: Uses predefined rules and operations
- **AI-powered cleaning**: Uses AI to analyze your data and suggest optimal cleaning strategies

## 🔧 Basic Usage

### Q: How do I clean a simple CSV file?
**A**: Use the basic clean command:
```bash
csv-cleaner clean input.csv output.csv
```

### Q: What operations are available?
**A**: Operations are organized by library:

**Pandas (Basic):** `remove_duplicates`, `fill_missing`, `drop_missing`, `clean_text`, `convert_types`, `fix_dates`, `rename_columns`, `drop_columns`, `select_columns`

**PyJanitor (Advanced):** `clean_names`, `remove_empty`, `fill_empty`, `handle_missing`, `remove_constant_columns`, `remove_columns_with_nulls`, `coalesce_columns`

**Feature-Engine:** `advanced_imputation`, `categorical_encoding`, `outlier_detection`, `variable_selection`, `data_transformation`, `missing_indicator`

**MissingNo:** `missing_matrix`, `missing_bar`, `missing_heatmap`, `missing_dendrogram`, `missing_summary`

**Dedupe:** `dedupe` (ML-based deduplication)

See the [User Manual](../user-guides/user-manual.md) for the complete list.

### Q: How do I specify which operations to use?
**A**: Use the `--operations` flag:
```bash
csv-cleaner clean input.csv output.csv --operations "remove_duplicates,fill_missing"
```

### Q: Can I clean specific columns only?
**A**: Yes, use the `--columns` flag:
```bash
csv-cleaner clean input.csv output.csv --operations "clean_text" --columns "name,email"
```

## 🤖 AI Features

### Q: How do I set up AI features?
**A**: Configure an AI provider:
```bash
csv-cleaner ai-configure set --provider openai --api-key YOUR_API_KEY
```

### Q: Which AI providers are supported?
**A**: Currently supported:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Local models (via Ollama)

### Q: How much do AI features cost?
**A**: Costs depend on:
- AI provider (OpenAI, Anthropic, etc.)
- Model used (GPT-4, Claude, etc.)
- Amount of data processed
- Number of AI operations

Use `csv-cleaner ai-stats --costs` to monitor costs.

### Q: Can I use AI features without an API key?
**A**: You can use local models with Ollama, but cloud AI providers require API keys.

### Q: How do I get AI suggestions?
**A**: Use the ai-suggest command:
```bash
csv-cleaner ai-suggest input.csv
```

### Q: How do I execute AI suggestions automatically?
**A**: Use the ai-clean command:
```bash
csv-cleaner ai-clean input.csv output.csv --auto-confirm
```

## 📊 Data Operations

### Q: How do I handle missing values?
**A**: Use the `fill_missing` operation with different methods:
```bash
# Fill with specific value
csv-cleaner clean input.csv output.csv --operations "fill_missing" --method "value" --fill-value "0"

# Fill with mean
csv-cleaner clean input.csv output.csv --operations "fill_missing" --method "mean"

# Drop rows with missing values
csv-cleaner clean input.csv output.csv --operations "drop_missing"
```

### Q: How do I remove duplicates?
**A**: Use the `remove_duplicates` operation:
```bash
# Remove all duplicates
csv-cleaner clean input.csv output.csv --operations "remove_duplicates"

# Remove duplicates based on specific columns
csv-cleaner clean input.csv output.csv --operations "remove_duplicates" --subset "email"
```

### Q: How do I clean text data?
**A**: Use the `clean_text` operation:
```bash
csv-cleaner clean input.csv output.csv --operations "clean_text" --columns "name,description"
```

### Q: How do I fix date formats?
**A**: Use the `fix_dates` operation:
```bash
csv-cleaner clean input.csv output.csv --operations "fix_dates" --date-format "%Y-%m-%d"
```

## ✅ Data Validation

### Q: How do I validate my data?
**A**: Use the validate command:
```bash
csv-cleaner validate input.csv
```

### Q: How do I create a custom validation schema?
**A**: Create a JSON schema file and use it:
```bash
csv-cleaner validate input.csv --schema schema.json
```

### Q: How do I generate a data quality report?
**A**: Use the report command:
```bash
csv-cleaner report input.csv --format html --output report.html
```

## 📈 Performance

### Q: How do I handle large files?
**A**: Use performance optimization options:
```bash
# Use parallel processing
csv-cleaner clean input.csv output.csv --parallel

# Process in chunks
csv-cleaner clean input.csv output.csv --chunk-size 10000

# Set memory limit
csv-cleaner clean input.csv output.csv --memory-limit 2GB
```

### Q: How do I monitor performance?
**A**: Enable performance monitoring:
```bash
csv-cleaner clean input.csv output.csv --monitor-performance
```

### Q: What's the maximum file size supported?
**A**: There's no hard limit, but performance depends on:
- Available RAM
- File complexity
- Operations performed

Use chunked processing for files larger than available RAM.

## 🎨 Visualization

### Q: How do I create data quality visualizations?
**A**: Use the visualize command:
```bash
# Quality heatmap
csv-cleaner visualize input.csv --type quality

# Missing data visualization
csv-cleaner visualize input.csv --type missing

# Correlation matrix
csv-cleaner visualize input.csv --type correlation
```

### Q: What output formats are supported?
**A**: Supported formats:
- PNG (default)
- JPG
- PDF
- SVG

### Q: How do I customize visualizations?
**A**: Basic customization is available:
```bash
csv-cleaner visualize input.csv --type quality --output custom_heatmap.png
```

## 🔧 Configuration

### Q: How do I view my current configuration?
**A**: Use the config command:
```bash
csv-cleaner config show
```

### Q: How do I change configuration settings?
**A**: Use the config set command:
```bash
csv-cleaner config set --key "default_operations" --value "remove_duplicates,fill_missing"
```

### Q: How do I reset configuration?
**A**: Use the config reset command:
```bash
csv-cleaner config reset
```

### Q: Can I use environment variables for configuration?
**A**: Yes, set environment variables:
```bash
export CSV_CLEANER_DEFAULT_OPERATIONS="remove_duplicates,fill_missing"
export CSV_CLEANER_PARALLEL_ENABLED="true"
```

## 🔄 Batch Processing

### Q: How do I process multiple files?
**A**: Batch processing is not directly supported in CLI. Use shell scripts:
```bash
#!/bin/bash
for file in *.csv; do
    csv-cleaner clean "$file" "cleaned_$file" --operations "remove_duplicates,fill_missing"
done
```

### Q: Can I use different operations for different files?
**A**: Use the Python API for advanced batch processing with different operations per file.

## 🆘 Troubleshooting

### Q: I get a "command not found" error
**A**:
1. Verify installation: `pip list | grep csv-cleaner`
2. Check PATH: `which csv-cleaner`
3. Reinstall if needed: `pip install --force-reinstall csv-cleaner`

### Q: I get a memory error
**A**:
1. Use chunked processing: `--chunk-size 1000`
2. Set memory limit: `--memory-limit 1GB`
3. Close other applications to free memory

### Q: AI features are not working
**A**:
1. Check configuration: `csv-cleaner ai-configure show`
2. Validate API keys: `csv-cleaner ai-configure validate`
3. Test connection: `csv-cleaner ai-configure test`

### Q: The tool is running slowly
**A**:
1. Enable parallel processing: `--parallel`
2. Optimize chunk size: `--chunk-size 10000`
3. Use appropriate operations only
4. Monitor performance: `--monitor-performance`

### Q: I get an error about missing libraries
**A**:
1. Install optional dependencies: `pip install csv-cleaner[all]`
2. Check feature gates: `csv-cleaner config show`
3. Install specific libraries manually

## 🔒 Security & Privacy

### Q: Is my data sent to external services?
**A**:
- **Basic cleaning**: No, all processing is local
- **AI features**: Data may be sent to AI providers (OpenAI, Anthropic)
- **Local AI**: No external data transmission

### Q: How can I protect sensitive data?
**A**:
1. Use local AI models only
2. Enable data anonymization: `--anonymize`
3. Review data before AI processing
4. Use secure API key storage

### Q: Are API keys stored securely?
**A**:
- API keys are stored in encrypted configuration files
- Keys are not logged or transmitted unnecessarily
- Use environment variables for additional security

## 📚 Advanced Usage

### Q: How do I create custom operations?
**A**:
1. Use the Python API for custom operations
2. Extend the BaseWrapper class
3. Implement custom logic in Python

### Q: Can I integrate with other tools?
**A**:
- Use as a Python library
- Process output with other tools
- Use shell scripts for automation

### Q: How do I automate cleaning workflows?
**A**:
1. Create shell scripts
2. Use the Python API
3. Integrate with CI/CD pipelines
4. Use configuration files

## 💰 Pricing & Licensing

### Q: Is CSV Data Cleaner free?
**A**:
- **Basic features**: Free and open source
- **AI features**: May incur costs from AI providers
- **Commercial use**: Check the LICENSE file

### Q: How much do AI features cost?
**A**: Costs depend on:
- AI provider pricing
- Model selection
- Data volume
- Usage frequency

Monitor costs with: `csv-cleaner ai-stats --costs`

## 🔮 Future Features

### Q: Will there be a web interface?
**A**: A web API is planned for future releases.

### Q: Will there be database integration?
**A**: Direct database connections are planned.

### Q: Will there be more AI models?
**A**: Support for additional AI providers and models is planned.

## 📞 Getting Help

### Q: Where can I get more help?
**A**:
1. **Documentation**: Check the [User Manual](../user-guides/user-manual.md)
2. **Tutorials**: Follow the [Basic Tutorials](../tutorials/basic-tutorials.md)
3. **Troubleshooting**: See the [Troubleshooting Guide](troubleshooting.md)
4. **Support**: Visit the [Support Guide](../../SUPPORT.md)
5. **Community**: Join discussions on GitHub

### Q: How do I report a bug?
**A**:
1. Check existing issues on GitHub
2. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Error messages
   - System information

### Q: How do I request a feature?
**A**:
1. Check existing feature requests
2. Create a new issue with:
   - Feature description
   - Use case
   - Expected behavior

### Q: Can I contribute to the project?
**A**: Yes! See the [Contributing Guidelines](../development/contributing.md) for details.

---

*Still have questions? Check the [Troubleshooting Guide](troubleshooting.md) or [Support Guide](../../SUPPORT.md) for more help.*
