# CSV Data Cleaner - Scripts

This folder contains deployment and utility scripts for the CSV Data Cleaner project.

## 📁 Scripts Overview

### 🚀 Deployment Scripts

#### `deploy-pypi.py`
Comprehensive deployment script for uploading to PyPI with safety checks and automation.

**Features:**
- ✅ Prerequisites checking
- ✅ Test suite execution
- ✅ Package building and validation
- ✅ Automatic versioning
- ✅ Release notes generation
- ✅ Upload to TestPyPI or PyPI

**Usage:**
```bash
# Deploy to TestPyPI
python scripts/deploy-pypi.py --test

# Deploy to production PyPI with specific version
python scripts/deploy-pypi.py --version 1.0.0

# Force deploy (bypass safety checks)
python scripts/deploy-pypi.py --force
```

#### `setup-pypi.py`
Setup script to prepare the basic version for PyPI deployment.

**Features:**
- ✅ Clean build artifacts
- ✅ Verify package structure
- ✅ Test build process
- ✅ Check package quality
- ✅ Install build dependencies

**Usage:**
```bash
python scripts/setup-pypi.py
```

### 🔒 Security Scripts

#### `audit-security.py`
Comprehensive security audit script for checking dependencies, code security, and compliance.

**Features:**
- ✅ Dependency vulnerability scanning
- ✅ Code security analysis
- ✅ File permission checks
- ✅ Data privacy compliance
- ✅ Security recommendations
- ✅ Compliance scoring

**Usage:**
```bash
python scripts/audit-security.py
```

### 📦 Build Scripts

#### `build-gumroad-release.py`
Professional build script for creating distribution packages for commercial release.

**Features:**
- ✅ Clean build artifacts
- ✅ Run test suite
- ✅ Code quality checks
- ✅ Build distribution package (Basic/Pro versions)
- ✅ Create release notes
- ✅ Create Gumroad package
- ✅ Support for both Basic and Pro versions
- ✅ Dynamic file detection
- ✅ Recursive directory inclusion

**Usage:**
```bash
# Build basic version
python scripts/build-gumroad-release.py

# Build pro version
python scripts/build-gumroad-release.py --pro

# Build with custom version
python scripts/build-gumroad-release.py --version 2.0.0

# Skip tests and quality checks
python scripts/build-gumroad-release.py --pro --skip-tests --skip-quality
```

**Options:**
- `--pro`: Build PRO version with enhanced features
- `--version VERSION`: Set version number (default: 1.0.0)
- `--skip-tests`: Skip running tests
- `--skip-quality`: Skip code quality checks

### 📚 Documentation

#### `DEPLOYMENT_GUIDE.md`
Comprehensive deployment guide with step-by-step instructions, troubleshooting, and best practices.

**Contents:**
- Prerequisites and setup
- Deployment process
- Version management
- Troubleshooting guide
- Post-deployment verification
- Update process

## 🎯 Quick Start

### 1. Setup Basic Version
```bash
python scripts/setup_basic_version.py
```

### 2. Test Deployment
```bash
python scripts/deploy_to_pypi.py --test
```

### 3. Production Deployment
```bash
python scripts/deploy_to_pypi.py --version 1.0.0
```

## 📋 Prerequisites

Before running the scripts, ensure you have:

- Python 3.8+
- pip, git, twine installed
- PyPI and TestPyPI accounts
- API tokens configured
- All tests passing
- Clean git repository

## 🔧 Script Dependencies

The scripts require the following Python packages:
- `build`: For building packages
- `twine`: For uploading to PyPI
- `setuptools`: For package configuration
- `wheel`: For wheel distribution

Install with:
```bash
pip install build twine setuptools wheel
```

## 🛠️ Customization

### Environment Variables
The scripts can be customized using environment variables:

- `PYPI_USERNAME`: PyPI username
- `PYPI_PASSWORD`: PyPI password/token
- `TEST_PYPI_USERNAME`: TestPyPI username
- `TEST_PYPI_PASSWORD`: TestPyPI password/token

### Configuration Files
- `pyproject.toml`: Main project configuration
- `.pypirc`: PyPI credentials (optional)

## 📞 Support

For issues with the scripts:

1. Check the `DEPLOYMENT_GUIDE.md` for troubleshooting
2. Ensure all prerequisites are met
3. Run scripts with verbose output for debugging
4. Check PyPI and TestPyPI documentation

## 🔄 Script Updates

The scripts are designed to be:
- **Safe**: Multiple safety checks before deployment
- **Automated**: Minimal manual intervention required
- **Flexible**: Support for different deployment scenarios
- **Maintainable**: Clear code structure and documentation

---

**Happy Deploying! 🚀**
