#!/usr/bin/env python3
"""
Setup script for building and publishing mssql_mcp_server_ishaan package.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Setting up mssql_mcp_server_ishaan package for publication...")
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("Error: pyproject.toml not found. Please run this from the project root.")
        sys.exit(1)
    
    # Install build dependencies
    if not run_command("pip3 install build twine", "Installing build dependencies"):
        sys.exit(1)
    
    # Clean previous builds
    if os.path.exists("dist"):
        run_command("rm -rf dist", "Cleaning previous builds")
    
    # Build the package
    if not run_command("python3 -m build", "Building package"):
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Package built successfully!")
    print("Files created in dist/ directory:")
    
    if os.path.exists("dist"):
        for file in os.listdir("dist"):
            print(f"  - {file}")
    
    print("\nNext steps:")
    print("1. Test the package locally:")
    print("   pip3 install dist/mssql_mcp_server_ishaan-*.whl")
    print("\n2. Upload to TestPyPI (recommended first):")
    print("   twine upload --repository testpypi dist/*")
    print("\n3. Upload to PyPI:")
    print("   twine upload dist/*")
    print("\nNote: You'll need to create accounts on PyPI/TestPyPI and configure authentication.")

if __name__ == "__main__":
    main()
