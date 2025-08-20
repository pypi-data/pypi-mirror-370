#!/usr/bin/env python3
"""
Local CI testing script for Django Auto Admin.

This script runs the same checks that the GitHub Actions CI pipeline runs,
allowing you to catch issues before pushing to GitHub.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Running: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def main():
    """Run all CI checks locally."""
    print("🚀 Running local CI checks for Django Auto Admin")
    print("=" * 60)

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    checks = [
        # Install dependencies
        ("pip install -e '.[dev]'", "Installing development dependencies"),
        # Run tests with coverage
        ("pytest --cov=src/django_admin_magic --cov-report=term-missing", "Running tests with coverage"),
        # Run linting
        ("ruff check .", "Running ruff linting"),
        # Check formatting
        ("ruff format --check .", "Checking code formatting"),
        # Run security checks
        ("bandit -r src/", "Running security checks with bandit"),
        # Build package
        ("python -m build", "Building package"),
        # Check package
        ("twine check dist/*", "Checking package with twine"),
    ]

    failed_checks = []

    for cmd, description in checks:
        if not run_command(cmd, description):
            failed_checks.append(description)

    print("\n" + "=" * 60)

    if failed_checks:
        print("❌ Some checks failed:")
        for check in failed_checks:
            print(f"  - {check}")
        print("\nPlease fix the issues above before pushing to GitHub.")
        sys.exit(1)
    else:
        print("✅ All checks passed! Ready to push to GitHub.")
        print("\nNext steps:")
        print("1. Commit your changes")
        print("2. Push to GitHub")
        print("3. Check the Actions tab to see the CI pipeline run")


if __name__ == "__main__":
    main()
