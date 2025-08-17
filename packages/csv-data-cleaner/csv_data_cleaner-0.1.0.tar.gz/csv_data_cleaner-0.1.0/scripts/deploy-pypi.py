#!/usr/bin/env python3
"""
Deployment script for CSV Data Cleaner to PyPI.

This script handles the complete deployment process including:
- Version management
- Testing
- Building
- Uploading to PyPI
- Safety checks

Usage:
    python deploy_to_pypi.py [--test] [--version VERSION] [--force]
"""

import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional, List


class PyPIDeployer:
    """Handles deployment to PyPI with safety checks and automation."""

    def __init__(self, test_pypi: bool = False, version: Optional[str] = None, force: bool = False):
        self.test_pypi = test_pypi
        self.version = version
        self.force = force
        self.project_root = Path(__file__).parent.parent  # Go up one level to project root
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

    def run_command(self, command: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command with proper error handling."""
        print(f"🔄 Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root
            )
            if result.stdout and not capture_output:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            raise

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for deployment."""
        print("🔍 Checking prerequisites...")

        # Check if we're in a git repository
        if not (self.project_root / ".git").exists():
            print("❌ Not in a git repository")
            return False

        # Check if we have uncommitted changes (unless --force)
        if not self.force:
            result = self.run_command(["git", "status", "--porcelain"], capture_output=True)
            if result.stdout.strip():
                print("❌ You have uncommitted changes. Use --force to override.")
                print("Uncommitted changes:")
                print(result.stdout)
                return False

        # Check if required tools are installed
        required_tools = ["python", "pip", "twine"]
        for tool in required_tools:
            try:
                self.run_command([tool, "--version"], capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ Required tool not found: {tool}")
                return False

        # Check if we're on main/master branch (unless --force)
        if not self.force:
            result = self.run_command(["git", "branch", "--show-current"], capture_output=True)
            current_branch = result.stdout.strip()
            if current_branch not in ["main", "master"]:
                print(f"❌ Not on main/master branch (current: {current_branch}). Use --force to override.")
                return False

        print("✅ Prerequisites check passed")
        return True

    def run_tests(self) -> bool:
        """Run the test suite to ensure everything works."""
        print("🧪 Running tests...")
        try:
            self.run_command([
                sys.executable, "-m", "pytest", "tests/",
                "--tb=short", "--maxfail=5"
            ])
            print("✅ Tests passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            return False

    def clean_build_artifacts(self) -> None:
        """Clean previous build artifacts."""
        print("🧹 Cleaning build artifacts...")
        for path in [self.dist_dir, self.build_dir]:
            if path.exists():
                shutil.rmtree(path)
                print(f"   Removed {path}")

        # Clean egg-info directories
        for egg_info in self.project_root.glob("*.egg-info"):
            shutil.rmtree(egg_info)
            print(f"   Removed {egg_info}")

    def set_version(self) -> None:
        """Set the version for the release."""
        if self.version:
            print(f"📝 Setting version to {self.version}")
            # Create a git tag for the version
            self.run_command(["git", "tag", f"v{self.version}"])
        else:
            print("📝 Using version from git tags")

    def build_package(self) -> bool:
        """Build the package for distribution."""
        print("🔨 Building package...")
        try:
            # Build wheel and source distribution
            self.run_command([
                sys.executable, "-m", "build", "--wheel", "--sdist"
            ])
            print("✅ Package built successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Package build failed")
            return False

    def check_package(self) -> bool:
        """Check the built package for issues."""
        print("🔍 Checking package...")
        try:
            # Check wheel
            wheel_files = list(self.dist_dir.glob("*.whl"))
            if wheel_files:
                self.run_command([
                    sys.executable, "-m", "twine", "check", str(wheel_files[0])
                ])

            # Check source distribution
            sdist_files = list(self.dist_dir.glob("*.tar.gz"))
            if sdist_files:
                self.run_command([
                    sys.executable, "-m", "twine", "check", str(sdist_files[0])
                ])

            print("✅ Package check passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Package check failed")
            return False

    def upload_to_pypi(self) -> bool:
        """Upload the package to PyPI."""
        pypi_url = "https://test.pypi.org/legacy/" if self.test_pypi else "https://upload.pypi.org/legacy/"
        pypi_name = "TestPyPI" if self.test_pypi else "PyPI"

        print(f"📤 Uploading to {pypi_name}...")
        try:
            self.run_command([
                sys.executable, "-m", "twine", "upload",
                "--repository-url", pypi_url,
                "dist/*"
            ])
            print(f"✅ Successfully uploaded to {pypi_name}")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Upload to {pypi_name} failed")
            return False

    def create_release_notes(self) -> None:
        """Create release notes from git commits."""
        print("📝 Creating release notes...")
        try:
            # Get commits since last tag
            result = self.run_command([
                "git", "log", "--oneline", "--no-merges",
                "$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD"
            ], capture_output=True)

            if result.stdout.strip():
                release_notes_file = self.project_root / "RELEASE_NOTES.md"
                with open(release_notes_file, "w") as f:
                    f.write("# Release Notes\n\n")
                    f.write("## Recent Changes\n\n")
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            f.write(f"- {line.strip()}\n")

                print(f"✅ Release notes created: {release_notes_file}")
            else:
                print("ℹ️  No new commits since last tag")
        except Exception as e:
            print(f"⚠️  Could not create release notes: {e}")

    def deploy(self) -> bool:
        """Run the complete deployment process."""
        print("🚀 Starting deployment process...")
        print(f"📦 Target: {'TestPyPI' if self.test_pypi else 'PyPI'}")
        print(f"🔧 Force mode: {self.force}")
        if self.version:
            print(f"📝 Version: {self.version}")
        print()

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False

            # Step 2: Run tests
            if not self.run_tests():
                return False

            # Step 3: Clean build artifacts
            self.clean_build_artifacts()

            # Step 4: Set version
            self.set_version()

            # Step 5: Build package
            if not self.build_package():
                return False

            # Step 6: Check package
            if not self.check_package():
                return False

            # Step 7: Create release notes
            self.create_release_notes()

            # Step 8: Upload to PyPI
            if not self.upload_to_pypi():
                return False

            print("\n🎉 Deployment completed successfully!")

            # Show next steps
            if self.test_pypi:
                print("\n📋 Next steps:")
                print("1. Test the package: pip install --index-url https://test.pypi.org/simple/ csv-cleaner")
                print("2. If everything works, deploy to production PyPI")
            else:
                print("\n📋 Package is now available on PyPI!")
                print("Install with: pip install csv-cleaner")

            return True

        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            return False


def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(
        description="Deploy CSV Data Cleaner to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy to TestPyPI
  python deploy_to_pypi.py --test

  # Deploy to production PyPI with specific version
  python deploy_to_pypi.py --version 1.0.0

  # Force deploy (bypass safety checks)
  python deploy_to_pypi.py --force
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to TestPyPI instead of production PyPI"
    )

    parser.add_argument(
        "--version",
        type=str,
        help="Set specific version for the release"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force deployment (bypass safety checks)"
    )

    args = parser.parse_args()

    # Create deployer and run deployment
    deployer = PyPIDeployer(
        test_pypi=args.test,
        version=args.version,
        force=args.force
    )

    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
