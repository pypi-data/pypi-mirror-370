#!/usr/bin/env python3
"""
Professional Build Script for CSV Data Cleaner
Creates distribution packages for commercial release.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and handle errors."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        if os.path.exists(pattern):
            shutil.rmtree(pattern)
            print(f"Removed: {pattern}")

def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    if os.path.exists("tests"):
        run_command("python3 -m pytest tests/ -v")
    else:
        print("⚠️  No tests directory found, skipping tests")

def check_code_quality():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    run_command("black --check --line-length 120 csv_cleaner/")
    run_command("flake8 csv_cleaner/")
    run_command("mypy csv_cleaner/")

def build_package(pro_version=False):
    """Build the distribution package."""
    print("📦 Building distribution package...")
    
    if pro_version:
        print("🔒 Building PRO version...")
        # Backup current pyproject.toml
        if os.path.exists("pyproject.toml"):
            shutil.copy2("pyproject.toml", "pyproject.toml.backup")
        
        # Use pro version configuration
        shutil.copy2("pyproject-pro.toml", "pyproject.toml")
        
        try:
            run_command("python3 -m build")
        finally:
            # Restore original pyproject.toml
            if os.path.exists("pyproject.toml.backup"):
                shutil.copy2("pyproject.toml.backup", "pyproject.toml")
                os.remove("pyproject.toml.backup")
    else:
        print("📦 Building BASIC version...")
        run_command("python3 -m build")

def create_release_notes():
    """Create release notes from changelog."""
    print("📝 Creating release notes...")
    if os.path.exists("CHANGELOG.md"):
        with open("CHANGELOG.md", "r") as f:
            content = f.read()

        # Extract latest version info
        lines = content.split('\n')
        release_notes = []
        in_latest_release = False

        for line in lines:
            if line.startswith('## [1.0.0]'):
                in_latest_release = True
                release_notes.append(line)
            elif in_latest_release and line.startswith('## ['):
                break
            elif in_latest_release:
                release_notes.append(line)

        with open("RELEASE_NOTES.md", "w") as f:
            f.write('\n'.join(release_notes))
        print("✅ Release notes created: RELEASE_NOTES.md")

def create_gumroad_package(version="1.0.0", pro_version=False):
    """Create a zip file with all files needed for Gumroad upload."""
    print("📦 Creating Gumroad package...")
    
    if pro_version:
        print("🔒 Building PRO version package...")
        package_name = "csv-cleaner-pro"
        package_description = "CSV Data Cleaner Pro"
    else:
        print("📦 Building BASIC version package...")
        package_name = "csv-cleaner"
        package_description = "CSV Data Cleaner"

    # Find the actual built files
    dist_files = []
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            if file.endswith(('.whl', '.tar.gz')):
                dist_files.append(f"dist/{file}")
    
    if not dist_files:
        print("❌ No distribution files found in dist/")
        return False
    
    print(f"📦 Found distribution files: {dist_files}")

    # Files to include in the package
    gumroad_files = [
        # Core installation files
        *dist_files,

        # Documentation and guides
        "GUMROAD_PACKAGE.md",
        "README.md",
        "LICENSE",

        # Installation helper
        "install.py",

        # Release notes
        "RELEASE_NOTES.md"
    ]

    # Add pro-specific files if building pro version
    if pro_version:
        pro_files = [
            "pyproject-pro.toml",
            "README_PRO.md",
            "docs/",
            "examples/",
            "scripts/"
        ]
        gumroad_files.extend(pro_files)

    # Check if all files exist
    missing_files = []
    for file_path in gumroad_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    # Create zip file in dist folder
    zip_filename = f"dist/{package_name}_gumroad_package.zip"

    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in gumroad_files:
                if os.path.isfile(file_path):
                    # Get just the filename for the zip
                    filename = os.path.basename(file_path)
                    zipf.write(file_path, filename)
                    print(f"  📄 Added: {filename}")
                elif os.path.isdir(file_path):
                    # Add directory contents recursively
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            file_path_full = os.path.join(root, file)
                            # Create relative path for zip
                            arcname = os.path.relpath(file_path_full, '.')
                            zipf.write(file_path_full, arcname)
                            print(f"  📁 Added: {arcname}")

        # Get file size
        file_size = os.path.getsize(zip_filename)
        file_size_mb = file_size / (1024 * 1024)

        print(f"✅ {package_description} Gumroad package created: {zip_filename}")
        print(f"📊 Package size: {file_size_mb:.2f} MB")
        print(f"📋 Files included: {len(gumroad_files)}")

        return True

    except Exception as e:
        print(f"❌ Failed to create zip file: {e}")
        return False

def main():
    """Main build process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build CSV Data Cleaner package")
    parser.add_argument("--pro", action="store_true", help="Build PRO version")
    parser.add_argument("--version", default="1.0.0", help="Version number (default: 1.0.0)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-quality", action="store_true", help="Skip code quality checks")
    args = parser.parse_args()
    
    pro_version = args.pro
    version = args.version
    
    if pro_version:
        print("🚀 Starting CSV Data Cleaner PRO build process...")
        print("🔒 Building PRO version with enhanced features...")
    else:
        print("🚀 Starting CSV Data Cleaner BASIC build process...")
        print("📦 Building BASIC version...")

    # Ensure we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found. Run this script from the project root.")
        sys.exit(1)

    try:
        # Clean previous builds
        clean_build()

        # Run quality checks (unless skipped)
        if not args.skip_quality:
            check_code_quality()
        else:
            print("⚠️  Skipping code quality checks...")

        # Run tests (unless skipped)
        if not args.skip_tests:
            run_tests()
        else:
            print("⚠️  Skipping tests...")

        # Build package
        build_package(pro_version=pro_version)

        # Create release notes
        create_release_notes()

        # Create Gumroad package
        create_gumroad_package(version=version, pro_version=pro_version)

        package_name = "csv-cleaner-pro" if pro_version else "csv-cleaner"
        zip_filename = f"dist/{package_name}_gumroad_package.zip"
        
        print("\n✅ Build completed successfully!")
        print(f"\n📋 Package: {package_name} v{version}")
        print(f"📦 Gumroad package: {zip_filename}")
        print("\n📋 Next steps:")
        print("1. Review the built package in dist/")
        print("2. Test the installation: pip install dist/*.whl")
        print("3. Upload to PyPI: python -m twine upload dist/*")
        print("4. Create GitHub release with RELEASE_NOTES.md")
        print(f"5. Upload {zip_filename} to Gumroad")

    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
