#!/usr/bin/env python3
"""
Setup script for basic version of CSV Data Cleaner.

This script prepares the project for PyPI deployment by:
1. Ensuring only basic dependencies are included
2. Removing AI and advanced features
3. Setting up proper versioning
4. Creating a clean build environment
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command."""
    print(f"🔄 Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(command)}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        raise


def setup_basic_version():
    """Setup the basic version for PyPI deployment."""
    print("🔧 Setting up basic version for PyPI deployment...")

    # Get project root
    project_root = Path(__file__).parent.parent  # Go up one level to project root

    # Step 1: Clean any existing builds
    print("🧹 Cleaning existing builds...")
    for path in ["dist", "build", "*.egg-info"]:
        for item in project_root.glob(path):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            print(f"   Removed {item}")

    # Step 2: Ensure we're using the basic pyproject.toml
    print("📝 Ensuring basic configuration...")

    # Check if we need to create a basic pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        print("✅ pyproject.toml exists")
    else:
        print("❌ pyproject.toml not found")
        return False

    # Step 3: Install build dependencies
    print("📦 Installing build dependencies...")
    try:
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "build", "twine", "setuptools", "wheel"])
    except subprocess.CalledProcessError:
        print("❌ Failed to install build dependencies")
        return False

    # Step 4: Verify the package structure
    print("🔍 Verifying package structure...")
    required_files = [
        "csv_cleaner/__init__.py",
        "csv_cleaner/cli/__init__.py",
        "csv_cleaner/core/__init__.py",
        "csv_cleaner/utils/__init__.py",
        "csv_cleaner/wrappers/__init__.py",
        "README.md",
        "LICENSE"
    ]

    for file_path in required_files:
        if not (project_root / file_path).exists():
            print(f"❌ Required file missing: {file_path}")
            return False

    print("✅ Package structure verified")

    # Step 5: Test the build process
    print("🔨 Testing build process...")
    try:
        run_command([sys.executable, "-m", "build", "--wheel", "--sdist"])
        print("✅ Build test successful")
    except subprocess.CalledProcessError:
        print("❌ Build test failed")
        return False

    # Step 6: Check the built package
    print("🔍 Checking built package...")
    try:
        dist_files = list((project_root / "dist").glob("*"))
        for file_path in dist_files:
            run_command([sys.executable, "-m", "twine", "check", str(file_path)])
        print("✅ Package check successful")
    except subprocess.CalledProcessError:
        print("❌ Package check failed")
        return False

    # Step 7: Show package information
    print("\n📋 Package Information:")
    try:
        result = run_command([sys.executable, "-m", "pip", "show", "-f", "."])
        print("✅ Package information retrieved")
    except subprocess.CalledProcessError:
        print("⚠️  Could not retrieve package information")

    print("\n🎉 Basic version setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the built package in the 'dist' directory")
    print("2. Test installation: pip install dist/*.whl")
    print("3. Deploy to TestPyPI: python deploy_to_pypi.py --test")
    print("4. Deploy to PyPI: python deploy_to_pypi.py")

    return True


def main():
    """Main entry point."""
    print("🚀 CSV Data Cleaner - Basic Version Setup")
    print("=" * 50)

    success = setup_basic_version()

    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
