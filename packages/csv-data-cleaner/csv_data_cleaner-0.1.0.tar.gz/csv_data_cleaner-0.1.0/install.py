#!/usr/bin/env python3
"""
CSV Data Cleaner Pro - Installation Script
Run this script to install the package after downloading from Gumroad.
"""

import os
import sys
import subprocess
import glob

def find_wheel_file():
    """Find the .whl file in the current directory"""
    wheel_files = glob.glob("*.whl")
    if not wheel_files:
        print("❌ No .whl file found in current directory")
        print("Please make sure you downloaded the file from Gumroad")
        return None

    if len(wheel_files) > 1:
        print("⚠️  Multiple .whl files found, using the first one")

    return wheel_files[0]

def install_package(wheel_file):
    """Install the package using pip"""
    print(f"📦 Installing {wheel_file}...")

    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", wheel_file
        ], capture_output=True, text=True, check=True)

        print("✅ Installation successful!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def verify_installation():
    """Verify that the package was installed correctly"""
    print("🔍 Verifying installation...")

    try:
        result = subprocess.run([
            "csv-cleaner", "--help"
        ], capture_output=True, text=True, check=True)

        print("✅ Package installed successfully!")
        print("\n📋 Next steps:")
        print("1. Setup API credentials: csv-cleaner --setup")
        print("2. Test configuration: csv-cleaner --test")
        print("3. Get help: csv-cleaner --help")
        return True

    except subprocess.CalledProcessError:
        print("❌ Package verification failed")
        return False
    except FileNotFoundError:
        print("❌ csv-cleaner command not found")
        return False

def main():
    """Main installation process"""
    print("🚀 CSV Data Cleaner Pro - Installation")
    print("=" * 40)

    # Find the wheel file
    wheel_file = find_wheel_file()
    if not wheel_file:
        sys.exit(1)

    # Install the package
    if not install_package(wheel_file):
        sys.exit(1)

    # Verify installation
    if not verify_installation():
        sys.exit(1)

    print("\n🎉 Installation completed successfully!")
    print("You can now use CSV Data Cleaner Pro!")

if __name__ == "__main__":
    main()
