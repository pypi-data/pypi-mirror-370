# Database Testing for Django Auto Admin

This document describes how to test Django Auto Admin against different database backends to ensure the library is truly database-agnostic.

## Overview

Django Auto Admin is designed to work with all database backends that Django supports. This includes:

- **SQLite** - Default Django database (always available)
- **PostgreSQL** - Advanced open-source database
- **MySQL** - Popular open-source database
- **Oracle** - Enterprise database system

## Test Coverage

The database testing suite covers:

### Core Functionality
- ✅ Model registration across all backends
- ✅ Admin class creation and configuration
- ✅ Field detection and handling
- ✅ Relationship detection and linkification
- ✅ Property detection and inclusion

### Database-Specific Features
- ✅ JSON field handling (PostgreSQL, MySQL 5.7+)
- ✅ UUID field handling
- ✅ Binary field handling
- ✅ Decimal field precision
- ✅ IP address field handling
- ✅ Text field handling with different encodings

### Database Constraints
- ✅ Unique constraints
- ✅ Foreign key constraints
- ✅ Nullable fields
- ✅ Default values

### Transaction Handling
- ✅ Transaction rollbacks
- ✅ Nested transactions
- ✅ Connection management
- ✅ Multi-database setups

### Query Handling
- ✅ Case sensitivity differences
- ✅ Unicode data handling
- ✅ Special character handling
- ✅ Large dataset performance

### Error Handling
- ✅ Connection errors
- ✅ Constraint violations
- ✅ Timeout handling
- ✅ Database-specific errors

## Running Database Tests

### Quick Start

```bash
# Run tests against all available databases
python run_database_tests.py

# Run tests against a specific database
python run_database_tests.py --database sqlite
python run_database_tests.py --database postgresql
python run_database_tests.py --database mysql
python run_database_tests.py --database oracle
```

### Using Docker (Recommended)

The easiest way to test against different databases is using Docker:

```bash
# Start PostgreSQL for testing
docker-compose -f docker-compose.test.yml --profile postgres up -d

# Start MySQL for testing
docker-compose -f docker-compose.test.yml --profile mysql up -d

# Start Oracle for testing
docker-compose -f docker-compose.test.yml --profile oracle up -d

# Start all databases
docker-compose -f docker-compose.test.yml --profile postgres --profile mysql --profile oracle up -d
```

### Manual Database Setup

If you prefer to use existing database installations:

#### PostgreSQL
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Create test database
createdb django_admin_magic_test

# Set environment variables
export POSTGRES_DB=django_admin_magic_test
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
```

#### MySQL
```bash
# Install MySQL
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS
brew install mysql

# Create test database
mysql -u root -p -e "CREATE DATABASE django_admin_magic_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Set environment variables
export MYSQL_DB=django_admin_magic_test
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
```

#### Oracle
```bash
# Install Oracle Database Express Edition
# Download from Oracle website and follow installation instructions

# Create test database
sqlplus system/oracle@localhost:1521/XE
CREATE USER django_admin_magic_test IDENTIFIED BY test_password;
GRANT CONNECT, RESOURCE TO django_admin_magic_test;
EXIT;

# Set environment variables
export ORACLE_DB=localhost:1521/XE
export ORACLE_USER=system
export ORACLE_PASSWORD=oracle
export ORACLE_HOST=localhost
export ORACLE_PORT=1521
```

## Test Configuration

### Environment Variables

The test runner uses environment variables to configure database connections:

#### PostgreSQL
```bash
POSTGRES_DB=django_admin_magic_test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

#### MySQL
```bash
MYSQL_DB=django_admin_magic_test
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

#### Oracle
```bash
ORACLE_DB=localhost:1521/XE
ORACLE_USER=system
ORACLE_PASSWORD=oracle
ORACLE_HOST=localhost
ORACLE_PORT=1521
```

### Test Settings

The database tests use `tests/test_settings_database_variants.py` which:

- Automatically detects the database backend from `DJANGO_TEST_DB`
- Configures appropriate database settings
- Sets up database-specific optimizations
- Disables migrations for faster tests

## Test Categories

### 1. Core Functionality Tests
Tests that verify basic functionality works across all databases:

```python
def test_model_registration_works_with_all_backends(self):
    """Test that model registration works regardless of database backend."""
    registrar = AdminModelRegistrar("tests")
    assert admin.site.is_registered(SimpleModel)
```

### 2. Database-Specific Feature Tests
Tests that verify features work correctly with each database's capabilities:

```python
def test_json_field_handling(self):
    """Test JSON field handling across different databases."""
    complex_model = ComplexModel.objects.create(
        json_field={"key": "value", "list": [1, 2, 3]}
    )
    assert complex_model.json_field["key"] == "value"
```

### 3. Constraint Tests
Tests that verify database constraints don't interfere with functionality:

```python
def test_unique_constraint_handling(self):
    """Test that unique constraints don't interfere with admin functionality."""
    class UniqueModel(SimpleModel):
        unique_field = models.CharField(max_length=100, unique=True)
    
    registrar = AdminModelRegistrar("tests")
    admin_class = registrar.return_admin_class_for_model(UniqueModel)
    assert hasattr(admin_class, 'list_display')
```

### 4. Performance Tests
Tests that verify performance characteristics across databases:

```python
def test_large_dataset_handling(self):
    """Test handling of large datasets."""
    for i in range(100):
        SimpleModel.objects.create(name=f"Test {i}", is_active=True)
    
    queryset = SimpleModel.objects.all()
    assert queryset.count() == 100
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Database Tests

on: [push, pull_request]

jobs:
  test-sqlite:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run SQLite tests
        run: python run_database_tests.py --database sqlite

  test-postgresql:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: django_admin_magic_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - name: Run PostgreSQL tests
        env:
          POSTGRES_DB: django_admin_magic_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
        run: python run_database_tests.py --database postgresql

  test-mysql:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: django_admin_magic_test
          MYSQL_ROOT_PASSWORD: root
        options: >-
          --health-cmd "mysqladmin ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 3306:3306
    steps:
      - uses: actions/checkout@v3
      - name: Run MySQL tests
        env:
          MYSQL_DB: django_admin_magic_test
          MYSQL_USER: root
          MYSQL_PASSWORD: root
          MYSQL_HOST: localhost
          MYSQL_PORT: 3306
        run: python run_database_tests.py --database mysql
```

### GitLab CI Example

```yaml
stages:
  - test

test-sqlite:
  stage: test
  script:
    - python run_database_tests.py --database sqlite

test-postgresql:
  stage: test
  services:
    - postgres:15
  variables:
    POSTGRES_DB: django_admin_magic_test
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
  script:
    - python run_database_tests.py --database postgresql

test-mysql:
  stage: test
  services:
    - mysql:8.0
  variables:
    MYSQL_DATABASE: django_admin_magic_test
    MYSQL_ROOT_PASSWORD: root
  script:
    - python run_database_tests.py --database mysql
```

## Troubleshooting

### Common Issues

#### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d django_admin_magic_test

# Reset password if needed
sudo -u postgres psql
ALTER USER postgres PASSWORD 'postgres';
```

#### MySQL Connection Issues
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Check connection
mysql -u root -p -h localhost

# Create database if missing
CREATE DATABASE django_admin_magic_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Oracle Connection Issues
```bash
# Check if Oracle is running
sqlplus system/oracle@localhost:1521/XE

# Check listener
lsnrctl status

# Create user if missing
CREATE USER django_admin_magic_test IDENTIFIED BY test_password;
GRANT CONNECT, RESOURCE TO django_admin_magic_test;
```

### Performance Issues

#### Slow Tests
- Use `--parallel` flag for parallel execution
- Disable migrations with `MIGRATION_MODULES = DisableMigrations()`
- Use `--reuse-db` to reuse test database

#### Memory Issues
- Reduce test dataset sizes
- Use `--maxfail` to stop early on failures
- Monitor database connection pooling

### Database-Specific Issues

#### PostgreSQL
- JSON field support requires PostgreSQL 9.4+
- UUID field support requires `uuid-ossp` extension
- Full-text search requires additional configuration

#### MySQL
- JSON field support requires MySQL 5.7+
- UTF8MB4 charset recommended for full Unicode support
- `STRICT_TRANS_TABLES` mode recommended

#### Oracle
- Limited JSON field support
- Different transaction isolation levels
- Case-sensitive object names by default

## Best Practices

### 1. Test All Supported Databases
Always test against all databases that your users might use.

### 2. Use Docker for Consistency
Docker provides consistent database environments across different systems.

### 3. Test Database-Specific Features
Verify that features work correctly with each database's capabilities.

### 4. Monitor Performance
Ensure that performance is acceptable across all databases.

### 5. Handle Database Differences
Use database-agnostic code and handle differences gracefully.

### 6. Test Error Conditions
Verify that error handling works correctly across databases.

### 7. Use Appropriate Test Data
Use realistic test data that exercises database features.

## Conclusion

Database testing ensures that Django Auto Admin works correctly with all supported Django database backends. This comprehensive testing approach helps maintain the library's database agnosticism and provides confidence that it will work in various deployment environments.

The test suite covers core functionality, database-specific features, constraints, transactions, queries, and error handling to provide thorough coverage of all aspects that might be affected by database differences. 