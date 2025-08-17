# CSV Data Cleaner - PyPI Deployment Guide

## 🚀 Overview

This guide walks you through deploying the CSV Data Cleaner basic version to PyPI. The deployment process includes safety checks, testing, building, and uploading.

## 📋 Prerequisites

### Required Tools
- Python 3.8+
- pip
- git
- twine (for uploading to PyPI)

### PyPI Account
- **TestPyPI Account**: [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
- **PyPI Account**: [https://pypi.org/account/register/](https://pypi.org/account/register/)

### API Tokens
1. Create API tokens on both TestPyPI and PyPI
2. Configure twine with your credentials:
   ```bash
   # Configure TestPyPI
   python -m twine upload --repository testpypi dist/*

   # Configure PyPI
   python -m twine upload dist/*
   ```

## 🔧 Setup

### 1. Install Build Dependencies
```bash
pip install --upgrade build twine setuptools wheel
```

### 2. Run Setup Script
```bash
python setup_basic_version.py
```

This script will:
- Clean existing builds
- Verify package structure
- Test the build process
- Check the built package

## 🚀 Deployment Process

### Step 1: Test Deployment (Recommended)

First, deploy to TestPyPI to ensure everything works:

```bash
python deploy_to_pypi.py --test
```

This will:
- ✅ Check prerequisites
- ✅ Run all tests
- ✅ Build the package
- ✅ Check package quality
- ✅ Upload to TestPyPI

### Step 2: Test Installation

Test the package from TestPyPI:

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ csv-cleaner

# Test the installation
csv-cleaner --help
```

### Step 3: Production Deployment

If the test deployment works correctly, deploy to production PyPI:

```bash
python deploy_to_pypi.py --version 1.0.0
```

## 📦 Package Information

### Basic Version Features
- **Core Cleaning**: pandas, pyjanitor operations
- **CLI Interface**: Command-line tool
- **Data Validation**: Basic validation features
- **Performance**: Memory management and optimization
- **No AI Features**: AI features are in optional dependencies

### Dependencies
```toml
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pyjanitor>=0.24.0",
    "click>=8.1.0",
    "pyyaml>=6.0",
    "tqdm>=4.65.0",
]
```

### Optional Dependencies
- `ai`: AI-powered features (OpenAI, Anthropic, Ollama)
- `performance`: Advanced performance features (Polars, Dask)
- `ml`: Machine learning features (dedupe)
- `dev`: Development tools (pytest, black, flake8, mypy)

## 🔍 Deployment Script Features

### Safety Checks
- ✅ Git repository check
- ✅ Uncommitted changes check
- ✅ Required tools check
- ✅ Branch check (main/master)

### Testing
- ✅ Full test suite execution
- ✅ Package build verification
- ✅ Package quality checks

### Automation
- ✅ Automatic version tagging
- ✅ Release notes generation
- ✅ Build artifact cleanup
- ✅ Error handling and rollback

## 📝 Version Management

### Automatic Versioning
The project uses `setuptools-scm` for automatic versioning based on git tags:

```bash
# Create a new version tag
git tag v1.0.0
git push origin v1.0.0

# Deploy with the new version
python deploy_to_pypi.py --version 1.0.0
```

### Manual Versioning
You can specify a version manually:

```bash
python deploy_to_pypi.py --version 1.0.0
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Configure twine credentials
python -m twine upload --repository testpypi dist/*
# Enter your username and password/token
```

#### 2. Build Failures
```bash
# Clean and rebuild
rm -rf dist build *.egg-info
python -m build --wheel --sdist
```

#### 3. Test Failures
```bash
# Run tests manually
python -m pytest tests/ -v
```

#### 4. Package Check Failures
```bash
# Check package manually
python -m twine check dist/*
```

### Force Deployment
If you need to bypass safety checks:

```bash
python deploy_to_pypi.py --force
```

⚠️ **Warning**: Only use `--force` when you're absolutely sure about the deployment.

## 📊 Post-Deployment

### Verification
1. Check PyPI page: [https://pypi.org/project/csv-cleaner/](https://pypi.org/project/csv-cleaner/)
2. Test installation: `pip install csv-cleaner`
3. Test functionality: `csv-cleaner --help`

### Monitoring
- Monitor PyPI download statistics
- Check for any reported issues
- Monitor GitHub issues and discussions

## 🔄 Update Process

### For Bug Fixes
```bash
# Create bug fix version
git tag v1.0.1
python deploy_to_pypi.py --version 1.0.1
```

### For New Features
```bash
# Create minor version
git tag v1.1.0
python deploy_to_pypi.py --version 1.1.0
```

### For Breaking Changes
```bash
# Create major version
git tag v2.0.0
python deploy_to_pypi.py --version 2.0.0
```

## 📋 Checklist

Before deploying, ensure:

- [ ] All tests pass
- [ ] No uncommitted changes (unless using --force)
- [ ] On main/master branch (unless using --force)
- [ ] Version is properly tagged
- [ ] README.md is up to date
- [ ] LICENSE file is present
- [ ] Package builds successfully
- [ ] Package passes quality checks
- [ ] TestPyPI deployment works
- [ ] Installation from TestPyPI works

## 🎯 Quick Commands

### Full Deployment Workflow
```bash
# 1. Setup
python setup_basic_version.py

# 2. Test deployment
python deploy_to_pypi.py --test

# 3. Test installation
pip install --index-url https://test.pypi.org/simple/ csv-cleaner

# 4. Production deployment
python deploy_to_pypi.py --version 1.0.0

# 5. Verify
pip install csv-cleaner
csv-cleaner --help
```

### Manual Steps (if needed)
```bash
# Build
python -m build --wheel --sdist

# Check
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## 📞 Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Ensure all prerequisites are met
4. Try the manual steps if automated deployment fails
5. Check PyPI and TestPyPI documentation for updates

---

**Happy Deploying! 🚀**
