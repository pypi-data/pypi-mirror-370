# CSV Data Cleaner - Complete Package

## 📦 What's Included

This package contains everything you need to install and use CSV Data Cleaner Pro:

### **Files Included:**
- `csv-cleaner-1.0.0-py3-none-any.whl` - **Quick Install** (Pro version)
- `csv-cleaner-1.0.0.tar.gz` - **Source Code** (Pro version)
- `install.py` - **Installation Helper Script**
- `SOURCE_INSTALLATION.md` - **Source Code Installation Guide**
- `README.md` - **Complete Documentation**
- `SUPPORT.md` - **Support Information**

## 🚀 Quick Start (Recommended)

### **For Most Users:**
1. Download the `.whl` file
2. Run: `pip install csv-cleaner-1.0.0-py3-none-any.whl`
3. Setup: `csv-cleaner --setup`
4. Use: `csv-cleaner --action process --input data.json`

### **Using the Installation Script:**
1. Download all files
2. Run: `python3 install.py`
3. Follow the prompts

## 🔧 Source Code Installation

### **For Advanced Users:**
1. Download the `.tar.gz` file
2. Extract: `tar -xzf csv-cleaner-1.0.0.tar.gz`
3. Install: `pip install -e csv-cleaner-1.0.0/`
4. Setup: `csv-cleaner --setup`

## 📋 Installation Options

### **Option 1: Wheel File (Fastest)**
```bash
pip install csv-cleaner-1.0.0-py3-none-any.whl
```

### **Option 2: Source Code (Customizable)**
```bash
tar -xzf csv-cleaner-1.0.0.tar.gz
cd csv-cleaner-1.0.0
pip install -e .
```

### **Option 3: Development Mode**
```bash
tar -xzf csv-cleaner-1.0.0.tar.gz
cd csv-cleaner-1.0.0
pip install -e ".[dev]"
```

## 🎯 Usage Examples

### **Basic Usage:**
```bash
# Test configuration
csv-cleaner --test

# Process data
csv-cleaner --action process --input data.json --output result.json

# Fetch data from API
csv-cleaner --action fetch --output api_data.json

# Transform data format
csv-cleaner --action transform --input raw.json --output clean.json
```

### **AI-Powered Features (Pro Only):**
```bash
# AI-powered cleaning suggestions
csv-cleaner ai-suggest input.csv

# AI-powered automatic cleaning
csv-cleaner ai-clean input.csv output.csv

# AI-powered data analysis
csv-cleaner ai-analyze input.csv
```

### **Setup and Configuration:**
```bash
# Setup API credentials
csv-cleaner --setup

# Test connection
csv-cleaner --test

# Get help
csv-cleaner --help
```

## 🔍 Customization (Source Code)

### **Modify Default Settings:**
Edit `csv_cleaner/core/config.py`

### **Add Custom Actions:**
Extend `csv_cleaner/core/main.py`

### **Enhance CLI Options:**
Modify `csv_cleaner/cli/main.py`

### **Use Python API:**
```python
from csv_cleaner import CSVCleaner

plugin = CSVCleaner()
result = await plugin.perform_action(
    action="process",
    input_data="data.json",
    output_path="result.json"
)
```

## 📁 File Structure

```
📦 Complete Package
├── 📄 csv-cleaner-1.0.0-py3-none-any.whl (Quick Install - Pro)
├── 📄 csv-cleaner-1.0.0.tar.gz (Source Code - Pro)
├── 📄 install.py (Installation Helper)
├── 📄 SOURCE_INSTALLATION.md (Source Guide)
├── 📄 README.md (Documentation)
├── 📄 SUPPORT.md (Support Info)
└── 📄 LICENSE (License Terms)
```

## 🛠️ Requirements

- **Python 3.8+**
- **pip** (Python package installer)
- **API credentials** (get from your service provider)

## 📞 Support

- **Email**: jai.crys@gmail.com
- **Documentation**: See README.md
- **Troubleshooting**: See SUPPORT.md
- **Source Code Help**: See SOURCE_INSTALLATION.md

## 📄 License

Commercial License Agreement - See LICENSE file for complete terms.

---

**Choose Your Installation Method:**
- **Quick Install**: Use the .whl file for fastest setup
- **Source Code**: Use the .tar.gz file for customization
- **Helper Script**: Use install.py for guided installation

All methods provide the same functionality - choose based on your needs!
