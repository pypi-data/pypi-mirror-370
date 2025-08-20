# Django Auto Admin Test Suite

This directory contains a comprehensive test suite for the Django Auto Admin package. The tests are designed to ensure the reliability, functionality, and performance of all components.

## Test Organization

The test suite is organized into several categories:

### Core Component Tests

- **`test_registrar.py`** - Tests for the `AdminModelRegistrar` class
- **`test_mixins.py`** - Tests for admin mixins (`ListAdminMixin`, `AdminDefaultsMixin`, etc.)
- **`test_utils.py`** - Tests for utility functions (`linkify`, `linkify_gfk`, etc.)
- **`test_config.py`** - Tests for configuration system
- **`test_settings.py`** - Tests for Django settings integration

### Comprehensive Tests

- **`test_integration.py`** - Integration tests covering the complete workflow
- **`test_utils_comprehensive.py`** - Comprehensive tests for utility functions
- **`test_config_comprehensive.py`** - Comprehensive tests for configuration
- **`test_comprehensive_models.py`** - Tests for complex model scenarios
- **`test_edge_cases.py`** - Tests for edge cases and error handling

### Model Tests

- **`test_simple_model.py`** - Tests for simple model scenarios
- **`models.py`** - Test models used across the test suite

## Test Models

The test suite includes a variety of models to test different scenarios:

### Basic Models
- **`SimpleModel`** - Basic model with standard fields
- **`ComplexModel`** - Model with all Django field types
- **`ModelWithProperties`** - Model with computed properties
- **`ModelWithSearchVector`** - Model with search functionality
- **`ModelWithCustomManager`** - Model with custom manager

### Relationship Models
- **`ForeignKeyModel`** - Model with various foreign key relationships
- **`GenericForeignKeyModel`** - Model with generic foreign keys
- **`PolymorphicParent`** - Base polymorphic model
- **`PolymorphicChildA`** - First polymorphic child
- **`PolymorphicChildB`** - Second polymorphic child

## Test Categories

### Unit Tests
- Test individual components in isolation
- Mock dependencies where appropriate
- Focus on specific functionality

### Integration Tests
- Test component interactions
- Test complete workflows
- Test real Django admin functionality

### Edge Case Tests
- Test unusual model configurations
- Test error conditions
- Test performance scenarios
- Test data handling edge cases

### Configuration Tests
- Test settings overrides
- Test default values
- Test configuration validation

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run tests with verbose output
python run_tests.py -v

# Run tests with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py tests/test_registrar.py

# Run specific test class
python run_tests.py -k TestRegistrar

# Run tests in parallel
python run_tests.py --parallel

# Run quality checks
python run_tests.py --all-checks
```

### Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=django_admin_magic --cov-report=html tests/

# Run specific test file
pytest tests/test_registrar.py

# Run specific test class
pytest -k TestRegistrar tests/

# Run tests with specific marker
pytest -m "django_db" tests/
```

### Test Markers

The test suite uses several pytest markers:

- **`@pytest.mark.django_db`** - Tests that require database access
- **`@pytest.mark.slow`** - Tests that are slow to run
- **`@pytest.mark.integration`** - Integration tests

## Test Fixtures

The test suite provides several fixtures in `conftest.py`:

### Model Fixtures
- `simple_model_instance` - SimpleModel instance
- `complex_model_instance` - ComplexModel instance
- `foreign_key_model_instance` - ForeignKeyModel instance
- `generic_foreign_key_model_instance` - GenericForeignKeyModel instance
- `polymorphic_parent_instance` - PolymorphicParent instance
- `polymorphic_child_a_instance` - PolymorphicChildA instance
- `polymorphic_child_b_instance` - PolymorphicChildB instance
- `model_with_properties_instance` - ModelWithProperties instance
- `model_with_search_vector_instance` - ModelWithSearchVector instance
- `model_with_custom_manager_instance` - ModelWithCustomManager instance

### System Fixtures
- `request_factory` - Django RequestFactory
- `admin_site` - Django admin site
- `registrar` - AdminModelRegistrar instance

## Test Coverage

The test suite aims to achieve comprehensive coverage of:

### Core Functionality
- ✅ Model registration with Django admin
- ✅ Automatic list_display generation
- ✅ Automatic list_filter generation
- ✅ Foreign key linkification
- ✅ Generic foreign key linkification
- ✅ Property detection and inclusion
- ✅ Polymorphic model handling
- ✅ Search vector field handling

### Configuration
- ✅ Settings overrides
- ✅ Default values
- ✅ Configuration validation
- ✅ App-specific configuration

### Utilities
- ✅ linkify function
- ✅ linkify_gfk function
- ✅ TimeLimitedPaginator
- ✅ Polymorphic model detection
- ✅ Child class discovery

### Edge Cases
- ✅ Models with no fields
- ✅ Models with only auto fields
- ✅ Models with only foreign keys
- ✅ Models with only properties
- ✅ Models with very long field names
- ✅ Models with unicode field names
- ✅ Models with special characters
- ✅ Self-referencing foreign keys
- ✅ Circular foreign keys
- ✅ Deep inheritance
- ✅ Multiple generic foreign keys

### Error Handling
- ✅ Missing related objects
- ✅ Broken model methods
- ✅ Invalid field names
- ✅ Nonexistent models
- ✅ Configuration errors

### Performance
- ✅ Large querysets
- ✅ Complex relationships
- ✅ Nested querysets
- ✅ Timeout handling

## Continuous Integration

The test suite is designed to work with CI/CD systems:

### GitHub Actions
```yaml
- name: Run tests
  run: |
    python run_tests.py --coverage --parallel
```

### GitLab CI
```yaml
test:
  script:
    - python run_tests.py --coverage
```

### Local Development
```bash
# Run tests before committing
python run_tests.py --all-checks

# Run tests with coverage
python run_tests.py --coverage

# Run tests in parallel for speed
python run_tests.py --parallel
```

## Debugging Tests

### Running Individual Tests
```bash
# Run specific test method
pytest tests/test_registrar.py::TestRegistrar::test_append_list_display -v

# Run with debugger
pytest tests/test_registrar.py --pdb

# Run with print statements
pytest tests/test_registrar.py -s
```

### Database Debugging
```bash
# Use existing database
pytest --reuse-db tests/

# Create new database
pytest --create-db tests/
```

### Coverage Analysis
```bash
# Generate HTML coverage report
pytest --cov=django_admin_magic --cov-report=html tests/

# View coverage in browser
open htmlcov/index.html
```

## Test Data

The test suite includes sample data generation:

### Sample Data Migration
- `0002_populate_sample_data.py` - Creates sample data for testing

### Fixture Data
- All fixtures create realistic test data
- Data includes edge cases and unusual values
- Data covers all field types and relationships

## Best Practices

### Writing Tests
1. **Use descriptive test names** - Test names should clearly describe what is being tested
2. **Test one thing at a time** - Each test should focus on a single behavior
3. **Use appropriate fixtures** - Reuse fixtures for common test data
4. **Test edge cases** - Include tests for unusual scenarios
5. **Test error conditions** - Ensure error handling works correctly

### Test Organization
1. **Group related tests** - Use test classes to organize related tests
2. **Use consistent naming** - Follow consistent naming conventions
3. **Add docstrings** - Document what each test does
4. **Use markers appropriately** - Mark tests with appropriate pytest markers

### Performance
1. **Use database transactions** - Use `@pytest.mark.django_db` appropriately
2. **Reuse test data** - Use fixtures to avoid recreating data
3. **Test efficiently** - Avoid unnecessary database operations
4. **Use parallel execution** - Use `--parallel` for faster test runs

## Troubleshooting

### Common Issues

#### Database Issues
```bash
# Reset test database
pytest --create-db tests/

# Use existing database
pytest --reuse-db tests/
```

#### Import Issues
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use pytest with pythonpath
pytest --pythonpath=src tests/
```

#### Coverage Issues
```bash
# Install coverage dependencies
pip install pytest-cov

# Run with coverage
pytest --cov=django_admin_magic tests/
```

### Getting Help

If you encounter issues with the test suite:

1. Check the test output for specific error messages
2. Ensure all dependencies are installed
3. Verify the Django settings are correct
4. Check that the database is properly configured
5. Review the test documentation and examples

## Contributing

When adding new tests:

1. Follow the existing test organization
2. Use appropriate fixtures
3. Add comprehensive docstrings
4. Test both success and failure cases
5. Include edge cases where appropriate
6. Update this documentation if needed

## Test Dependencies

The test suite requires:

- `pytest` - Test framework
- `pytest-django` - Django integration
- `pytest-cov` - Coverage reporting
- `pytest-xdist` - Parallel execution
- `django-polymorphic` - Polymorphic model support

Install with:
```bash
pip install -e ".[dev]"
``` 