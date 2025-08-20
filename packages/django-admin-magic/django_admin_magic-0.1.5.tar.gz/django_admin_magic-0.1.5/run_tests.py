#!/usr/bin/env python3
"""
Test runner script for Django Admin Magic.

This script provides an easy way to run the comprehensive test suite
with various options for different testing scenarios.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, env=None):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")

    try:
        subprocess.run(cmd, check=True, capture_output=False, env=env)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_tests_with_options(options):
    """Run tests with the specified options."""
    # Base pytest command
    cmd = ["uv", "run", "pytest"]

    # Set Django settings module
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "tests.test_settings"

    # Add test directory
    cmd.append("tests/")

    # Add verbosity
    if options.verbose:
        cmd.append("-v")
    if options.very_verbose:
        cmd.append("-vv")

    # Add coverage
    if options.coverage:
        cmd.extend(["--cov=django_admin_magic", "--cov-report=term-missing", "--cov-report=html"])

    # Add specific test files
    if options.test_files:
        cmd.extend(options.test_files)

    # Add specific test classes
    if options.test_classes:
        for test_class in options.test_classes:
            cmd.extend(["-k", test_class])

    # Add markers
    if options.markers:
        for marker in options.markers:
            cmd.extend(["-m", marker])

    # Add parallel execution
    if options.parallel:
        cmd.extend(["-n", "auto"])

    # Add stop on first failure
    if options.stop_on_failure:
        cmd.append("-x")

    # Add max failures
    if options.max_failures:
        cmd.extend(["--maxfail", str(options.max_failures)])

    # Add output options
    if options.quiet:
        cmd.append("-q")

    # Add database options
    if options.reuse_db:
        cmd.append("--reuse-db")

    # Run the command
    return run_command(cmd, "Test Suite", env)


def run_linting():
    """Run code linting with ruff."""
    return run_command(["uv", "run", "ruff", "check", "src/", "tests/"], "Code Linting (ruff)")


def run_formatting():
    """Run code formatting with ruff."""
    return run_command(["uv", "run", "ruff", "format", "src/", "tests/"], "Code Formatting (ruff)")


def run_type_checking():
    """Run type checking with mypy."""
    return run_command(["uv", "run", "mypy", "src/", "tests/"], "Type Checking (mypy)")


def run_security_checks():
    """Run security checks with bandit."""
    return run_command(["uv", "run", "bandit", "-r", "src/"], "Security Checks (bandit)")


def run_all_checks():
    """Run all quality checks."""
    checks = [
        ("Code Linting", run_linting),
        ("Code Formatting", run_formatting),
        ("Type Checking", run_type_checking),
        ("Security Checks", run_security_checks),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{'=' * 60}")
        print(f"Running {name}")
        print(f"{'=' * 60}")
        results.append(check_func())

    return all(results)


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Django Admin Magic Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v                 # Run tests with verbose output
  python run_tests.py --coverage         # Run tests with coverage report
  python run_tests.py tests/test_registrar.py  # Run specific test file
  python run_tests.py -k TestRegistrar   # Run specific test class
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --lint             # Run linting only
  python run_tests.py --all-checks       # Run all quality checks
  python run_tests.py --database-tests   # Run database-agnostic tests
  python run_tests.py --database postgresql  # Run tests with PostgreSQL
        """,
    )

    # Test execution options
    parser.add_argument("-v", "--verbose", action="store_true", help="Run tests with verbose output")
    parser.add_argument("-vv", "--very-verbose", action="store_true", help="Run tests with very verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("-x", "--stop-on-failure", action="store_true", help="Stop on first test failure")
    parser.add_argument("--max-failures", type=int, help="Maximum number of test failures before stopping")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run tests quietly")
    parser.add_argument("--reuse-db", action="store_true", help="Reuse test database for faster runs")

    # Test selection options
    parser.add_argument("test_files", nargs="*", help="Specific test files to run")
    parser.add_argument("-k", "--test-classes", nargs="+", help="Specific test classes to run")
    parser.add_argument("-m", "--markers", nargs="+", help="Run tests with specific markers")

    # Quality check options
    parser.add_argument("--lint", action="store_true", help="Run code linting only")
    parser.add_argument("--format", action="store_true", help="Run code formatting only")
    parser.add_argument("--type-check", action="store_true", help="Run type checking only")
    parser.add_argument("--security", action="store_true", help="Run security checks only")
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run all quality checks (linting, formatting, type checking, security)",
    )

    parser.add_argument(
        "--database-tests", action="store_true", help="Run database-agnostic tests against all available databases"
    )

    parser.add_argument(
        "--database",
        choices=["sqlite", "postgresql", "mysql", "oracle"],
        help="Run tests against a specific database backend",
    )

    # Parse arguments
    args = parser.parse_args()

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)

    # Run specific quality checks
    if args.lint:
        success = run_linting()
    elif args.format:
        success = run_formatting()
    elif args.type_check:
        success = run_type_checking()
    elif args.security:
        success = run_security_checks()
    elif args.all_checks:
        success = run_all_checks()
    elif args.database_tests:
        # Run database-agnostic tests
        from run_database_tests import run_all_database_tests

        success = run_all_database_tests(args.test_files, options)
    elif args.database:
        # Run tests with specific database
        from run_database_tests import run_specific_database_test

        success = run_specific_database_test(args.database, args.test_files, options)
    else:
        # Run tests
        success = run_tests_with_options(args)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
