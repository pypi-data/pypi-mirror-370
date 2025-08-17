# Configuration Guide

Complete guide to configuring CSV Cleaner for optimal performance and functionality.

## 📋 Overview

CSV Cleaner uses a flexible configuration system that allows you to customize behavior, performance settings, and feature preferences. Configuration can be managed through:

- **Command-line interface**: Direct configuration commands
- **Configuration files**: YAML-based configuration files
- **Environment variables**: System-level configuration
- **Default settings**: Built-in sensible defaults

## 🔧 Configuration Management

### Using the CLI

The `config` command provides a complete interface for managing configuration:

**Note**: Some advanced features require optional dependencies. If you encounter import errors for features like `feature-engine`, `dedupe`, or `missingno`, install them with:
```bash
pip install feature-engine dedupe missingno
```

```bash
# Show current configuration
csv-cleaner config show

# Set a configuration value
csv-cleaner config set backup_enabled true

# Get a specific configuration value
csv-cleaner config get chunk_size

# Initialize default configuration
csv-cleaner config init
```

### Configuration File Location

Configuration files are stored in:
- **User config**: `~/.csv-cleaner/config.yaml`
- **Project config**: `./csv-cleaner.yaml` (in current directory)
- **Custom config**: Specified with `--config` option

## ⚙️ Configuration Options

### Core Settings

#### `chunk_size`
- **Type**: Integer
- **Default**: 10000
- **Description**: Number of rows to process in each chunk for large files
- **Example**: `csv-cleaner config set chunk_size 50000`

#### `backup_enabled`
- **Type**: Boolean
- **Default**: true
- **Description**: Create backup of original files before processing
- **Example**: `csv-cleaner config set backup_enabled false`

#### `chunk_size`
- **Type**: Integer
- **Default**: 10000
- **Description**: Number of rows to process in each chunk for large files
- **Example**: `csv-cleaner config set chunk_size 50000`

#### `max_memory_usage`
- **Type**: Integer
- **Default**: 1073741824 (1GB)
- **Description**: Maximum memory usage in bytes
- **Example**: `csv-cleaner config set max_memory_usage 2147483648`

### Performance Settings

*Note: Performance settings are managed through command-line options rather than configuration files.*

#### Parallel Processing
- **Command Option**: `--parallel/--no-parallel`
- **Default**: True
- **Description**: Enable/disable parallel processing
- **Example**: `csv-cleaner clean input.csv output.csv --no-parallel`

#### Memory Management
- **Command Option**: `--max-memory`
- **Default**: 1.0 GB
- **Description**: Maximum memory usage in GB
- **Example**: `csv-cleaner clean input.csv output.csv --max-memory 2.0`

#### Chunk Size
- **Command Option**: `--chunk-size`
- **Default**: 10000
- **Description**: Number of rows to process in each chunk
- **Example**: `csv-cleaner clean input.csv output.csv --chunk-size 50000`

### Output Settings

#### `output_format`
- **Type**: String
- **Default**: "csv"
- **Description**: Default output format (currently supports csv)
- **Example**: `csv-cleaner config set output_format csv`

*Note: Additional output formats and compression options are planned for future releases.*

### Logging Settings

#### `log_level`
- **Type**: String
- **Default**: "INFO"
- **Description**: Logging level (DEBUG, INFO, WARNING, ERROR)
- **Example**: `csv-cleaner config set log_level DEBUG`

*Note: Log file and format settings are managed internally by the application.*

### AI Settings

*Note: AI features are available in both Basic and Pro versions, with Pro offering enhanced capabilities.*

#### AI Configuration
AI settings are managed through the `ai-configure` command:

```bash
# Show current AI configuration
csv-cleaner ai-configure show

# Set AI provider
csv-cleaner ai-configure set --provider openai --api-key YOUR_KEY

# Validate AI configuration
csv-cleaner ai-configure validate
```

#### Available Providers
- **openai**: OpenAI GPT models
- **anthropic**: Anthropic Claude models
- **local**: Local models via Ollama

*Note: Advanced AI features and model configuration options are available in Pro version.*

## 📁 Configuration File Format

Configuration files use YAML format:

```yaml
# Core settings
chunk_size: 10000
backup_enabled: true
max_memory_usage: 1073741824

# Output settings
output_format: csv

# Logging settings
log_level: INFO

# Default operations
default_operations:
  - remove_duplicates
  - clean_names
  - handle_missing

# Note: AI settings are managed through ai-configure command
# Performance settings are managed through command-line options
```

## 🌍 Environment Variables

*Note: Environment variable support is limited in the current version. Most configuration is managed through the config command and command-line options.*

```bash
# Core settings (if supported)
export CSV_CLEANER_CHUNK_SIZE=2000
export CSV_CLEANER_BACKUP_ENABLED=true
export CSV_CLEANER_MAX_MEMORY_USAGE=1.0

# Logging settings
export CSV_CLEANER_LOG_LEVEL=INFO

# AI settings (managed through ai-configure)
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
```

## 🔄 Configuration Precedence

Configuration values are loaded in the following order (later values override earlier ones):

1. **Built-in defaults**
2. **User configuration file** (`~/.csv-cleaner/config.yaml`)
3. **Project configuration file** (`./csv-cleaner.yaml`)
4. **Environment variables**
5. **Command-line options**

## 📊 Performance Configuration

### For Large Files

```bash
# Increase chunk size for better memory management
csv-cleaner config set chunk_size 100000

# Enable parallel processing
csv-cleaner config set parallel_enabled true

# Set appropriate memory limits
csv-cleaner config set max_memory_usage 8589934592

# Use compression for output
csv-cleaner config set compression gzip
```

### For Small Files

```bash
# Use smaller chunks for faster processing
csv-cleaner config set chunk_size 5000

# Disable parallel processing for small files
csv-cleaner config set parallel_enabled false

# Reduce memory usage
csv-cleaner config set max_memory_usage 2147483648
```

### For Development

```bash
# Enable debug logging
csv-cleaner config set log_level DEBUG

# Disable backups for faster iteration
csv-cleaner config set backup_enabled false

# Use smaller chunks for testing
csv-cleaner config set chunk_size 1000
```

## 🤖 AI Configuration (Pro Version)

### OpenAI Configuration

```bash
# Set OpenAI as default provider
csv-cleaner config set ai_provider openai

# Configure OpenAI model
csv-cleaner config set ai_model gpt-4o

# Set API key (or use environment variable)
export OPENAI_API_KEY=your_api_key_here

# Configure AI parameters
csv-cleaner config set ai_max_tokens 4000
csv-cleaner config set ai_temperature 0.1
```

### Anthropic Configuration

```bash
# Set Anthropic as default provider
csv-cleaner config set ai_provider anthropic

# Configure Anthropic model
csv-cleaner config set ai_model claude-3-haiku-20240307

# Set API key (or use environment variable)
export ANTHROPIC_API_KEY=your_api_key_here
```

### Local Model Configuration

```bash
# Set local provider
csv-cleaner config set ai_provider local

# Configure local model
csv-cleaner config set ai_model llama3.1:8b

# Ensure Ollama is running
ollama serve
```

## 🔍 Configuration Validation

### Validate Configuration

```bash
# Validate current configuration
csv-cleaner config validate

# Check specific settings
csv-cleaner config get chunk_size
csv-cleaner config get parallel_enabled
```

### Reset Configuration

```bash
# Reset to defaults
csv-cleaner config reset

# Initialize fresh configuration
csv-cleaner config init
```

## 📝 Configuration Examples

### Basic Configuration

```bash
# Set up basic configuration
csv-cleaner config init

# Configure for typical usage
csv-cleaner config set chunk_size 10000
csv-cleaner config set parallel_enabled true
csv-cleaner config set backup_enabled true
csv-cleaner config set log_level INFO
```

### Advanced Configuration

```bash
# Performance-optimized configuration
csv-cleaner config set chunk_size 100000
csv-cleaner config set max_workers 8
csv-cleaner config set max_memory_usage 17179869184
csv-cleaner config set cache_enabled true
csv-cleaner config set compression gzip

# AI configuration (Pro version)
csv-cleaner config set ai_provider openai
csv-cleaner config set ai_model gpt-4o
csv-cleaner config set ai_max_tokens 8000
csv-cleaner config set ai_temperature 0.1
```

### Development Configuration

```bash
# Development-friendly settings
csv-cleaner config set log_level DEBUG
csv-cleaner config set backup_enabled false
csv-cleaner config set chunk_size 100
csv-cleaner config set parallel_enabled false
csv-cleaner config set cache_enabled false
```

## 🆘 Troubleshooting Configuration

### Common Issues

#### Configuration Not Loading
```bash
# Check configuration file location
ls -la ~/.csv-cleaner/config.yaml

# Verify file permissions
chmod 600 ~/.csv-cleaner/config.yaml

# Check for syntax errors
csv-cleaner config validate
```

#### Environment Variables Not Working
```bash
# Verify environment variable format
echo $CSV_CLEANER_CHUNK_SIZE

# Check variable naming (must be uppercase with underscores)
export CSV_CLEANER_CHUNK_SIZE=10000
```

#### Configuration Conflicts
```bash
# Show all configuration sources
csv-cleaner config show --verbose

# Reset to defaults
csv-cleaner config reset

# Rebuild configuration step by step
csv-cleaner config init
```

## 📚 Related Documentation

- **[CLI Reference](cli-reference.md)** - Command-line interface reference
- **[User Manual](user-manual.md)** - Complete user guide
- **[AI Features Guide](ai-features.md)** - AI configuration details
- **[Performance Guide](../technical/performance.md)** - Performance optimization

---

*For advanced configuration options and troubleshooting, see the [CLI Reference](cli-reference.md).*
