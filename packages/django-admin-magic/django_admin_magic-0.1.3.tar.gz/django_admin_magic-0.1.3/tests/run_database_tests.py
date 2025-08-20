#!/usr/bin/env python3
"""
Database-agnostic test runner for Django Auto Admin.

This script runs the test suite against different database backends to ensure
the library works correctly with all supported Django databases.
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
    if env:
        print(f"Environment: {dict(env)}")
    print(f"{'=' * 60}\n")

    try:
        subprocess.run(cmd, check=True, capture_output=False, env=env)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_tests_with_database(database, test_files=None, options=None):
    """Run tests with a specific database backend."""
    # Set up environment
    env = os.environ.copy()
    env["DJANGO_TEST_DB"] = database
    env["DJANGO_SETTINGS_MODULE"] = "tests.test_settings_database_variants"

    # Base command
    cmd = ["uv", "run", "pytest"]

    # Add test files
    if test_files:
        cmd.extend(test_files)
    else:
        cmd.append("tests/test_database_agnostic.py")

    # Add options
    if options:
        cmd.extend(options)

    # Add database-specific options
    if database == "postgresql":
        cmd.extend(["--tb=short", "--maxfail=10"])
    elif database == "mysql":
        cmd.extend(["--tb=short", "--maxfail=10"])
    elif database == "oracle":
        cmd.extend(["--tb=short", "--maxfail=5"])  # Oracle tests might be slower

    return run_command(cmd, f"Tests with {database.upper()} database", env)


def check_database_availability(database):
    """Check if a database is available for testing."""
    if database == "sqlite":
        return True  # SQLite is always available

    # Check if database-specific environment variables are set
    if database == "postgresql":
        required_vars = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    elif database == "mysql":
        required_vars = ["MYSQL_DB", "MYSQL_USER", "MYSQL_PASSWORD"]
    elif database == "oracle":
        required_vars = ["ORACLE_DB", "ORACLE_USER", "ORACLE_PASSWORD"]
    else:
        return False

    # Check if all required environment variables are set
    for var in required_vars:
        if not os.environ.get(var):
            print(f"⚠️  {database.upper()} not available: {var} environment variable not set")
            return False

    return True


def run_all_database_tests(test_files=None, options=None):
    """Run tests against all available database backends."""
    databases = ["sqlite", "postgresql", "mysql", "oracle"]
    results = {}

    print("🔍 Checking database availability...")

    for database in databases:
        if check_database_availability(database):
            print(f"✅ {database.upper()} is available")
            results[database] = run_tests_with_database(database, test_files, options)
        else:
            print(f"❌ {database.upper()} is not available")
            results[database] = False

    # Print summary
    print(f"\n{'=' * 60}")
    print("DATABASE TEST SUMMARY")
    print(f"{'=' * 60}")

    all_passed = True
    for database, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{database.upper():12} {status}")
        if not success:
            all_passed = False

    print(f"{'=' * 60}")
    if all_passed:
        print("🎉 All database tests passed!")
    else:
        print("⚠️  Some database tests failed. Check the output above.")

    return all_passed


def run_specific_database_test(database, test_files=None, options=None):
    """Run tests with a specific database backend."""
    if not check_database_availability(database):
        print(f"❌ {database.upper()} is not available for testing")
        return False

    return run_tests_with_database(database, test_files, options)


def setup_database_environment(database):
    """Set up environment variables for a specific database."""
    if database == "postgresql":
        env_vars = {
            "POSTGRES_DB": "django_admin_magic_test",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
        }
    elif database == "mysql":
        env_vars = {
            "MYSQL_DB": "django_admin_magic_test",
            "MYSQL_USER": "root",
            "MYSQL_PASSWORD": "",
            "MYSQL_HOST": "localhost",
            "MYSQL_PORT": "3306",
        }
    elif database == "oracle":
        env_vars = {
            "ORACLE_DB": "localhost:1521/XE",
            "ORACLE_USER": "system",
            "ORACLE_PASSWORD": "oracle",
            "ORACLE_HOST": "localhost",
            "ORACLE_PORT": "1521",
        }
    else:
        return

    print(f"Setting up environment for {database.upper()}...")
    for key, value in env_vars.items():
        if not os.environ.get(key):
            os.environ[key] = value
            print(f"  Set {key}={value}")


def main():
    """Main function to parse arguments and run database tests."""
    parser = argparse.ArgumentParser(
        description="Database-agnostic test runner for Django Auto Admin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_database_tests.py                    # Run all database tests
  python run_database_tests.py --database sqlite  # Run SQLite tests only
  python run_database_tests.py --database postgresql  # Run PostgreSQL tests only
  python run_database_tests.py --setup postgresql # Set up PostgreSQL environment
  python run_database_tests.py --verbose          # Run with verbose output
  python run_database_tests.py --coverage         # Run with coverage
        """,
    )

    parser.add_argument(
        "--database",
        choices=["sqlite", "postgresql", "mysql", "oracle", "all"],
        default="all",
        help="Database backend to test against",
    )

    parser.add_argument(
        "--setup",
        choices=["postgresql", "mysql", "oracle"],
        help="Set up environment variables for a specific database",
    )

    parser.add_argument("--test-files", nargs="+", help="Specific test files to run")

    parser.add_argument("--verbose", "-v", action="store_true", help="Run tests with verbose output")

    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")

    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")

    parser.add_argument("--stop-on-failure", "-x", action="store_true", help="Stop on first test failure")

    parser.add_argument("--max-failures", type=int, help="Maximum number of test failures before stopping")

    # Parse arguments
    args = parser.parse_args()

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)

    # Set up environment if requested
    if args.setup:
        setup_database_environment(args.setup)
        return

    # Build test options
    options = []
    if args.verbose:
        options.append("-v")
    if args.coverage:
        options.extend(["--cov=django_admin_magic", "--cov-report=term-missing"])
    if args.parallel:
        options.extend(["-n", "auto"])
    if args.stop_on_failure:
        options.append("-x")
    if args.max_failures:
        options.extend(["--maxfail", str(args.max_failures)])

    # Run tests
    if args.database == "all":
        success = run_all_database_tests(args.test_files, options)
    else:
        success = run_specific_database_test(args.database, args.test_files, options)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
