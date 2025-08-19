#!/usr/bin/env python3
"""
Anges Package Installation Script
================================

This script installs the Anges package in development mode and verifies the installation.

Features:
- Installs the package in development mode using pip
- Verifies the installation by checking for entry points
- Provides clear output about success or failure
- Handles errors gracefully
- Cross-platform compatible

Usage:
    python install_anges.py

Requirements:
    - Python 3.8 or higher
    - pip

Exit Codes:
    0: Success
    1: Installation failed
    2: Verification failed
"""

import os
import sys
import subprocess
import importlib
import shutil
from pathlib import Path


def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80)


def print_step(message):
    """Print a step message."""
    print(f"\n>> {message}")


def print_success(message):
    """Print a success message."""
    print(f"\n✅ {message}")


def print_error(message):
    """Print an error message."""
    print(f"\n❌ {message}")


def run_command(command, error_message):
    """Run a shell command and handle errors."""
    try:
        print(f"Executing: {' '.join(command)}")
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(error_message)
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_step("Checking Python version")
    
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 8):
        print_error(f"Python 3.8 or higher is required. You have Python {major}.{minor}")
        return False
    
    print_success(f"Python version {major}.{minor} meets requirements")
    return True


def check_pip():
    """Check if pip is installed."""
    print_step("Checking pip installation")
    
    if shutil.which("pip") is None:
        print_error("pip is not installed or not in PATH")
        return False
    
    return run_command(
        ["pip", "--version"],
        "Failed to get pip version"
    )


def install_package():
    """Install the package in development mode."""
    print_header("INSTALLING ANGES PACKAGE")
    
    print_step("Installing package in development mode")
    return run_command(
        ["pip", "install", "-e", "."],
        "Failed to install package"
    )


def verify_installation():
    """Verify the package installation."""
    print_header("VERIFYING INSTALLATION")
    
    # Check if the package can be imported
    print_step("Checking if package can be imported")
    try:
        import anges
        print_success("Package 'anges' imported successfully")
    except ImportError as e:
        print_error(f"Failed to import 'anges' package: {e}")
        return False
    
    # Check if entry points are installed
    print_step("Checking entry points")
    entry_points = ["anges", "anges-web"]
    all_found = True
    
    for entry_point in entry_points:
        if shutil.which(entry_point) is None:
            print_error(f"Entry point '{entry_point}' not found in PATH")
            all_found = False
        else:
            print_success(f"Entry point '{entry_point}' found in PATH")
    
    return all_found


def print_usage_instructions():
    """Print usage instructions for the installed package."""
    print_header("USAGE INSTRUCTIONS")
    
    print("""
After installation, you can use the following commands:

1. anges - Command line interface for Anges
   Example: anges --help

2. anges-web - Web interface for Anges
   Example: anges-web

For more information, refer to the documentation in the README.md file.
""")


def main():
    """Main function to install and verify the package."""
    print_header("ANGES INSTALLATION SCRIPT")
    
    # Check prerequisites
    if not check_python_version() or not check_pip():
        print_error("Prerequisites check failed")
        sys.exit(1)
    
    # Install package
    if not install_package():
        print_error("Installation failed")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print_error("Verification failed")
        sys.exit(2)
    
    # Print usage instructions
    print_usage_instructions()
    
    print_header("INSTALLATION COMPLETED SUCCESSFULLY")
    return 0


if __name__ == "__main__":
    sys.exit(main())