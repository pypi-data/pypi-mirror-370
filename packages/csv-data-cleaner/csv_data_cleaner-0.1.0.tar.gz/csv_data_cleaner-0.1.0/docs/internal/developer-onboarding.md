# **Developer Onboarding Guide**
## **CSV Data Cleaner - Quick Start for Developers**

---

## **Table of Contents**

1. [Project Overview](#1-project-overview)
2. [Quick Setup](#2-quick-setup)
3. [Project Structure](#3-project-structure)
4. [Development Workflow](#4-development-workflow)
5. [Code Standards](#5-code-standards)
6. [Common Tasks](#6-common-tasks)
7. [Troubleshooting](#7-troubleshooting)

---

## **1. Project Overview**

**CSV Data Cleaner** is a Python tool for intelligent CSV data cleaning with:
- **Local Mode**: Uses Python libraries (Pandas, PyJanitor, etc.)
- **AI Mode**: Optional LLM integration for smart suggestions
- **Library-First**: Leverages existing libraries, doesn't reinvent the wheel

**Tech Stack**: Python 3.8+, Pandas, NumPy, PyJanitor, Click, pytest

---

## **2. Quick Setup**

### **Prerequisites**
- Python 3.8+
- Git

### **Installation**
```bash
# Clone and setup
git clone <repository-url>
cd csv-cleaner
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .
pip install -e ".[dev]"

# Verify
csv-cleaner --help
```

### **IDE Setup (VS Code)**
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true
}
```

---

## **3. Project Structure**

```
csv-cleaner/
├── csv_cleaner/              # Main package
│   ├── core/                # Core functionality
│   │   ├── config.py       # Configuration management
│   │   └── library_manager.py # Library orchestration
│   ├── wrappers/           # Library wrappers
│   │   ├── base.py        # Abstract base class
│   │   ├── pandas_wrapper.py
│   │   └── pyjanitor_wrapper.py
│   └── cli/               # Command-line interface
│       └── main.py
├── tests/                 # Test suite
├── docs/                 # Documentation
└── pyproject.toml       # Project config
```

**Key Components:**
- **Config Manager**: Handles settings and YAML configs
- **Library Manager**: Orchestrates wrappers, selects best library
- **Wrappers**: Abstract interface to different libraries
- **CLI**: Click-based command interface

---

## **4. Development Workflow**

### **Branch Strategy**
- `main`: Production code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes

### **Development Process**
```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature

# 2. Make changes & test
pytest
flake8 csv_cleaner/
black --check csv_cleaner/

# 3. Commit & push
git add .
git commit -m "feat: add new cleaning operation"
git push origin feature/your-feature

# 4. Create PR to develop
```

### **Conventional Commits**
```
type(scope): description

feat: new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code refactoring
test: adding tests
chore: maintenance
```

---

## **5. Code Standards**

### **Python Style**
- **Line Length**: 88 chars (Black default)
- **Type Hints**: Required for public APIs
- **Docstrings**: Google style
- **Imports**: Grouped and sorted

### **Code Quality**
```bash
# Format code
black csv_cleaner/
isort csv_cleaner/

# Lint
flake8 csv_cleaner/
mypy csv_cleaner/

# Test
pytest --cov=csv_cleaner
```

### **Example Code**
```python
from typing import Dict, List, Optional
import pandas as pd

class DataCleaner:
    """Main data cleaning interface."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize DataCleaner with configuration."""
        self.config = config or {}
        self.library_manager = LibraryManager()

    def clean_data(self, df: pd.DataFrame, operations: List[str]) -> pd.DataFrame:
        """Clean data using specified operations."""
        for operation in operations:
            df = self.library_manager.execute_operation(operation, df)
        return df
```

---

## **6. Common Tasks**

### **Add New Library Wrapper**
```python
# 1. Create wrapper
class NewLibraryWrapper(BaseWrapper):
    def can_handle(self, operation: str) -> bool:
        return operation in ['op1', 'op2']

    def execute(self, operation: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        # Implementation
        return df

    def get_supported_operations(self) -> List[str]:
        return ['op1', 'op2']

# 2. Register in LibraryManager
def _initialize_wrappers(self) -> Dict[str, BaseWrapper]:
    return {
        'pandas': PandasWrapper(),
        'new_library': NewLibraryWrapper(),  # Add here
    }

# 3. Add tests
def test_new_library_wrapper():
    wrapper = NewLibraryWrapper()
    assert 'op1' in wrapper.get_supported_operations()
```

### **Add CLI Command**
```python
@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def new_command(input_file: str):
    """New command description."""
    # Implementation
    pass
```

### **Update Configuration**
```python
@dataclass
class Config:
    # Add new setting
    new_setting: str = "default_value"
```

---

## **7. Troubleshooting**

### **Common Issues**

**Import Errors**
```bash
pip install -e .
python -c "import csv_cleaner; print(csv_cleaner.__file__)"
```

**Test Failures**
```bash
pytest -vvv
pytest tests/test_specific.py::test_function -s
```

**Configuration Issues**
```bash
csv-cleaner config --show
rm ~/.csv-cleaner/config.yaml
csv-cleaner config --init
```

**Dependency Issues**
```bash
pip check
rm -rf venv && python3 -m venv venv
source venv/bin/activate && pip install -e .
```

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

import pdb; pdb.set_trace()  # Python debugger
```

---

## **Resources**

- **Docs**: [README](../README.md), [PRD](prd.md), [Tech Spec](tech.md)
- **External**: [Python](https://docs.python.org/), [Pandas](https://pandas.pydata.org/), [Click](https://click.palletsprojects.com/)
- **Community**: GitHub Issues, Discussions, PRs

---

## **Next Steps**

1. ✅ Complete setup
2. 🔍 Explore codebase
3. 🧪 Run tests
4. 🎯 Pick a task
5. 🤝 Join community

**Welcome to CSV Data Cleaner! 🚀**
