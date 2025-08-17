# Installation Guide

Complete installation instructions for CSV Cleaner across different platforms and environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for large files)
- **Disk Space**: 1GB available space
- **Internet**: Required for AI features and package installation

### Python Installation
If you don't have Python installed:

#### Windows
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer with "Add Python to PATH" checked
3. Verify: `python --version`

#### macOS
```bash
# Using Homebrew
brew install python

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install python3 python3-pip
```

## 🚀 Quick Installation

### Standard Installation
```bash
pip install csv-cleaner
```

### Verify Installation
```bash
csv-cleaner --version
```

## 📦 Installation Options

### Basic Installation
```bash
# Install core functionality only
pip install csv-cleaner
```

### Full Installation (Recommended)
```bash
# Install with all optional dependencies
pip install csv-cleaner[all]
```

### Development Installation
```bash
# Install in development mode
git clone https://github.com/your-repo/csv-cleaner.git
cd csv-cleaner
pip install -e .
```

## 🔧 Advanced Installation

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv csv-cleaner-env

# Activate environment
# Windows
csv-cleaner-env\Scripts\activate

# macOS/Linux
source csv-cleaner-env/bin/activate

# Install in virtual environment
pip install csv-cleaner[all]
```

### Conda Installation
```bash
# Create conda environment
conda create -n csv-cleaner python=3.9

# Activate environment
conda activate csv-cleaner

# Install
pip install csv-cleaner[all]
```

### Docker Installation
```bash
# Pull Docker image
docker pull csv-cleaner/csv-cleaner:latest

# Run container
docker run -v $(pwd):/data csv-cleaner/csv-cleaner:latest clean /data/input.csv /data/output.csv
```

## 🎯 Platform-Specific Instructions

### Windows Installation

#### Using pip
```bash
# Install Python first, then:
pip install csv-cleaner[all]
```

#### Using Chocolatey
```bash
choco install csv-cleaner
```

#### Troubleshooting Windows Issues
```bash
# If you get permission errors:
pip install --user csv-cleaner[all]

# If pip is not recognized:
python -m pip install csv-cleaner[all]
```

### macOS Installation

#### Using Homebrew
```bash
# Install Python first
brew install python

# Install CSV Data Cleaner
pip3 install csv-cleaner[all]
```

#### Using MacPorts
```bash
# Install Python first
sudo port install python39

# Install CSV Data Cleaner
pip3 install csv-cleaner[all]
```

#### Troubleshooting macOS Issues
```bash
# If you get SSL errors:
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org csv-cleaner[all]

# If you get permission errors:
pip3 install --user csv-cleaner[all]
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv csv-cleaner-env
source csv-cleaner-env/bin/activate

# Install CSV Data Cleaner
pip install csv-cleaner[all]
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and pip
sudo yum install python3 python3-pip

# Or for newer versions:
sudo dnf install python3 python3-pip

# Create virtual environment
python3 -m venv csv-cleaner-env
source csv-cleaner-env/bin/activate

# Install CSV Data Cleaner
pip install csv-cleaner[all]
```

#### Arch Linux
```bash
# Install Python
sudo pacman -S python python-pip

# Create virtual environment
python -m venv csv-cleaner-env
source csv-cleaner-env/bin/activate

# Install CSV Data Cleaner
pip install csv-cleaner[all]
```

## 🔧 Dependencies

### Required Dependencies
- **pandas**: Core data manipulation
- **numpy**: Numerical operations
- **click**: Command-line interface

### Optional Dependencies
- **pyjanitor**: Advanced data cleaning
- **feature-engine**: Feature engineering
- **missingno**: Missing data visualization
- **dedupe**: Advanced deduplication
- **openai**: OpenAI AI integration
- **anthropic**: Anthropic AI integration
- **ollama**: Local AI models

### Install Specific Dependencies
```bash
# Install only specific libraries
pip install csv-cleaner[pyjanitor,feature-engine]

# Install AI dependencies
pip install csv-cleaner[ai]

# Install visualization dependencies
pip install csv-cleaner[visualization]
```

## 🧪 Testing Installation

### Basic Test
```bash
# Test basic functionality
csv-cleaner --version
csv-cleaner --help
```

### Create Test Data
```bash
# Create sample CSV file
echo "name,age,email
John,25,john@example.com
Jane,30,jane@example.com" > test.csv

# Test basic cleaning
csv-cleaner clean test.csv cleaned_test.csv
```

### Test AI Features
```bash
# Test AI configuration
csv-cleaner ai-configure show

# Test AI analysis (requires API key)
csv-cleaner ai-analyze test.csv
```

## 🔧 Configuration

### Initial Setup
```bash
# Show current configuration
csv-cleaner config show

# Set default operations
csv-cleaner config set --key "default_operations" --value "remove_duplicates,fill_missing"

# Set parallel processing
csv-cleaner config set --key "parallel_enabled" --value "true"
```

### Environment Variables
```bash
# Set configuration via environment variables
export CSV_CLEANER_DEFAULT_OPERATIONS="remove_duplicates,fill_missing"
export CSV_CLEANER_PARALLEL_ENABLED="true"
export CSV_CLEANER_LOG_LEVEL="INFO"
```

## 🆘 Troubleshooting

### Common Installation Issues

#### Permission Errors
```bash
# Use --user flag
pip install --user csv-cleaner[all]

# Or use virtual environment
python -m venv csv-cleaner-env
source csv-cleaner-env/bin/activate
pip install csv-cleaner[all]
```

#### SSL Certificate Errors
```bash
# Trust hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org csv-cleaner[all]

# Or upgrade pip
pip install --upgrade pip
```

#### Missing Dependencies
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt install python3-dev build-essential

# Install system dependencies (CentOS/RHEL)
sudo yum install python3-devel gcc

# Reinstall with all dependencies
pip install --force-reinstall csv-cleaner[all]
```

#### Version Conflicts
```bash
# Create fresh virtual environment
python -m venv fresh-env
source fresh-env/bin/activate
pip install csv-cleaner[all]
```

### Platform-Specific Issues

#### Windows Issues
```bash
# Install Visual C++ Build Tools
# Download from Microsoft Visual Studio

# Or use conda
conda install -c conda-forge csv-cleaner
```

#### macOS Issues
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Or use Homebrew
brew install csv-cleaner
```

#### Linux Issues
```bash
# Install development tools
sudo apt install build-essential python3-dev

# Or use system package manager
sudo apt install python3-csv-cleaner
```

## 🔄 Updating

### Update CSV Data Cleaner
```bash
# Update to latest version
pip install --upgrade csv-cleaner

# Update with all dependencies
pip install --upgrade csv-cleaner[all]
```

### Check for Updates
```bash
# Check current version
csv-cleaner --version

# Check available updates
pip list --outdated | grep csv-cleaner
```

## 🗑️ Uninstallation

### Remove CSV Data Cleaner
```bash
# Uninstall package
pip uninstall csv-cleaner

# Remove configuration files
rm -rf ~/.csv-cleaner
```

### Clean Virtual Environment
```bash
# Deactivate environment
deactivate

# Remove environment
rm -rf csv-cleaner-env
```

## 📚 Next Steps

After successful installation:

1. **Read the [Quick Start Guide](quick-start.md)** to get started
2. **Follow [Basic Tutorials](../tutorials/basic-tutorials.md)** for hands-on learning
3. **Check [User Manual](../user-guides/user-manual.md)** for comprehensive usage
4. **Explore [AI Features](../user-guides/ai-features.md)** for advanced capabilities

## 🆘 Getting Help

If you encounter installation issues:

1. **Check [Troubleshooting](../reference/troubleshooting.md)** for common solutions
2. **Review [FAQ](../reference/faq.md)** for quick answers
3. **Visit [Support Guide](../../SUPPORT.md)** for additional help
4. **Create an issue** on GitHub with detailed error information

---

*Installation complete? Start with the [Quick Start Guide](quick-start.md) to begin using CSV Data Cleaner!*
