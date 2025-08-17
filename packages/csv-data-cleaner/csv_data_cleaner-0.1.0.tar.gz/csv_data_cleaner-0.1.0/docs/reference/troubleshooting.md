# Troubleshooting Guide

Common issues and solutions for CSV Cleaner.

## 🚨 Quick Fixes

### Installation Issues

#### "Command not found: csv-cleaner"
```bash
# Check if installed correctly
pip list | grep csv-cleaner

# Reinstall if needed
pip install --force-reinstall csv-cleaner

# Check PATH
which csv-cleaner
```

#### Permission Errors During Installation
```bash
# Use --user flag
pip install --user csv-cleaner

# Or use virtual environment
python -m venv csv-cleaner-env
source csv-cleaner-env/bin/activate
pip install csv-cleaner
```

### Basic Usage Issues

#### "File not found" Error
```bash
# Check file path
ls -la your_file.csv

# Use absolute path
csv-cleaner clean /full/path/to/file.csv output.csv

# Check file permissions
chmod 644 your_file.csv
```

#### "Permission denied" Error
```bash
# Check write permissions for output directory
ls -la /path/to/output/directory

# Create directory if needed
mkdir -p /path/to/output/directory

# Set proper permissions
chmod 755 /path/to/output/directory
```

## 🔧 Common Problems

### Memory Issues

#### "Out of memory" Error
```bash
# Reduce chunk size
csv-cleaner clean input.csv output.csv --chunk-size 1000

# Disable parallel processing
csv-cleaner clean input.csv output.csv --no-parallel

# Set memory limit
csv-cleaner clean input.csv output.csv --max-memory 2
```

#### Large File Processing Slow
```bash
# Enable parallel processing
csv-cleaner clean input.csv output.csv --parallel

# Increase chunk size
csv-cleaner clean input.csv output.csv --chunk-size 50000

# Use compression
csv-cleaner clean input.csv output.csv.gz --compression gzip
```

### File Format Issues

#### Encoding Problems
```bash
# Check file encoding
file -i your_file.csv

# Specify encoding
csv-cleaner clean input.csv output.csv --encoding utf-8

# Try different encodings
csv-cleaner clean input.csv output.csv --encoding latin-1
```

#### Malformed CSV
```bash
# Use different delimiter
csv-cleaner clean input.csv output.csv --delimiter ";"

# Skip problematic rows
csv-cleaner clean input.csv output.csv --error-bad-lines false

# Preview file structure
head -10 your_file.csv
```

### Performance Issues

#### Slow Processing
```bash
# Check system resources
top
df -h

# Optimize configuration
csv-cleaner config set parallel_enabled true
csv-cleaner config set chunk_size 50000

# Use SSD storage if available
```

#### High CPU Usage
```bash
# Reduce parallel workers
csv-cleaner config set parallel_workers 2

# Disable parallel processing for small files
csv-cleaner clean input.csv output.csv --no-parallel
```

## 🤖 AI Feature Issues (Pro Version)

### API Key Problems

#### "Invalid API key" Error
```bash
# Check API key format
echo $OPENAI_API_KEY

# Reconfigure AI provider
csv-cleaner ai-configure set --provider openai --api-key YOUR_NEW_KEY

# Validate configuration
csv-cleaner ai-configure validate
```

#### "Rate limit exceeded" Error
```bash
# Wait and retry
sleep 60
csv-cleaner ai-suggest input.csv

# Use different model
csv-cleaner ai-model set --provider openai --model gpt-3.5-turbo

# Check usage limits
csv-cleaner ai-logs --days 1
```

### Model Issues

#### "Model not found" Error
```bash
# Check available models
csv-cleaner ai-model show

# Use default model
csv-cleaner ai-model set --provider openai --model gpt-4o

# Check provider status
csv-cleaner ai-configure validate
```

#### Local Model Not Working
```bash
# Check Ollama installation
ollama --version

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama3.1:8b

# Test local provider
csv-cleaner ai-configure set --provider local --model llama3.1:8b
```

## 📊 Data Quality Issues

### Missing Data Problems

#### Too Many Missing Values
```bash
# Analyze missing data
csv-cleaner visualize input.csv --type matrix

# Fill missing values
csv-cleaner clean input.csv output.csv --operations "fill_missing"

# Drop rows with too many missing values
csv-cleaner clean input.csv output.csv --operations "drop_missing"
```

#### Inconsistent Data Types
```bash
# Check data types
csv-cleaner validate input.csv

# Convert data types
csv-cleaner clean input.csv output.csv --operations "convert_types"

# Use specific type conversion
csv-cleaner clean input.csv output.csv --operations "convert_types" --dtype "column_name:int"
```

### Duplicate Data Issues

#### Duplicate Detection Not Working
```bash
# Check for exact duplicates
csv-cleaner clean input.csv output.csv --operations "remove_duplicates"

# Use subset of columns
csv-cleaner clean input.csv output.csv --operations "remove_duplicates" --subset "col1,col2"

# Use ML-based deduplication (Pro)
csv-cleaner dedupe input.csv output.csv --threshold 0.8
```

## 🔧 Configuration Issues

### Configuration Not Loading

#### "Configuration file not found"
```bash
# Check configuration location
ls -la ~/.csv-cleaner/

# Initialize configuration
csv-cleaner config init

# Create configuration directory
mkdir -p ~/.csv-cleaner
```

#### "Invalid configuration format"
```bash
# Validate configuration
csv-cleaner config validate

# Reset to defaults
csv-cleaner config reset

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.csv-cleaner/config.yaml'))"
```

### Environment Variables Not Working

#### "Environment variable not recognized"
```bash
# Check variable format
echo $CSV_CLEANER_CHUNK_SIZE

# Use correct naming convention
export CSV_CLEANER_CHUNK_SIZE=10000

# Restart terminal session
source ~/.bashrc
```

## 🐛 Debugging

### Enable Debug Logging

```bash
# Set debug level
csv-cleaner config set log_level DEBUG

# Run with verbose output
csv-cleaner clean input.csv output.csv --verbose

# Check log files
tail -f ~/.csv-cleaner/logs/csv-cleaner.log
```

### System Information

```bash
# Show system info
csv-cleaner info

# Check Python version
python --version

# Check available memory
free -h

# Check disk space
df -h
```

### Test Installation

```bash
# Create test data
echo "name,age,email
John,25,john@example.com
Jane,30,jane@example.com" > test.csv

# Test basic functionality
csv-cleaner clean test.csv test_output.csv

# Test validation
csv-cleaner validate test.csv

# Test visualization
csv-cleaner visualize test.csv --type matrix
```

## 📞 Getting Help

### Self-Diagnosis

```bash
# Check version
csv-cleaner --version

# Show help
csv-cleaner --help

# Check configuration
csv-cleaner config show

# Validate setup
csv-cleaner info
```

### Error Reporting

When reporting issues, include:

1. **Error message**: Copy the exact error text
2. **Command used**: The command that caused the error
3. **File information**: Size, format, encoding of input file
4. **System information**: OS, Python version, CSV Cleaner version
5. **Configuration**: Relevant configuration settings

### Example Error Report

```
Error: Permission denied: 'output.csv'
Command: csv-cleaner clean input.csv output.csv
Input file: 1MB CSV, UTF-8 encoding
System: macOS 12.0, Python 3.9, CSV Cleaner 1.0.0
Configuration: Default settings
```

## 🔄 Recovery Procedures

### Reset Configuration

```bash
# Reset to defaults
csv-cleaner config reset

# Remove configuration files
rm -rf ~/.csv-cleaner/

# Reinstall if needed
pip install --force-reinstall csv-cleaner
```

### Recover Corrupted Files

```bash
# Check for backup files
ls -la *.csv.backup

# Restore from backup
cp input.csv.backup input.csv

# Use dry run to preview changes
csv-cleaner clean input.csv output.csv --dry-run
```

### Clean Installation

```bash
# Uninstall completely
pip uninstall csv-cleaner

# Remove configuration
rm -rf ~/.csv-cleaner/

# Fresh install
pip install csv-cleaner

# Initialize configuration
csv-cleaner config init
```

## 📚 Related Documentation

- **[Installation Guide](../getting-started/installation.md)** - Installation troubleshooting
- **[Configuration Guide](../user-guides/configuration.md)** - Configuration issues
- **[CLI Reference](../user-guides/cli-reference.md)** - Command reference
- **[FAQ](faq.md)** - Frequently asked questions

## 🆘 Still Need Help?

If you're still experiencing issues:

1. **Check the [FAQ](faq.md)** for quick answers
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information
4. **Contact support** with your error details

---

*For more detailed troubleshooting, see the [Configuration Guide](../user-guides/configuration.md) and [CLI Reference](../user-guides/cli-reference.md).*
