# CI/CD Pipeline Setup

This document explains the GitHub Actions CI/CD pipeline setup for Django Auto Admin.

## Overview

The CI/CD pipeline consists of three main workflows:

1. **CI** (`ci.yml`) - Runs on every push and pull request
2. **Deploy** (`deploy.yml`) - Runs when a new release is published
3. **Update Badges** (`update-badges.yml`) - Runs daily to keep badges current

## CI Workflow

The CI workflow runs the following jobs:

### Test Matrix
- **Django versions**: 3.2, 4.0, 4.1, 4.2, 5.0
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Exclusions**: Django 5.0 with Python 3.8/3.9 (incompatible)

### Jobs
1. **test** - Runs pytest with coverage across all Django/Python combinations
2. **lint** - Runs ruff for code formatting and linting
3. **security** - Runs bandit for security analysis
4. **update-badges** - Updates coverage and test badges (main branch only)

## Deployment Workflow

The deployment workflow:
1. Builds the package using `python -m build`
2. Validates the package with `twine check`
3. Publishes to PyPI
4. Optionally publishes to TestPyPI for testing

## Required Secrets

To enable full functionality, add these secrets to your GitHub repository:

### For PyPI Deployment
- `PYPI_API_TOKEN` - Your PyPI API token
- `TEST_PYPI_API_TOKEN` - Your TestPyPI API token (optional)

### For Badge Updates
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## Setting Up PyPI Tokens

1. **Create PyPI Account**: Sign up at https://pypi.org/
2. **Generate API Token**:
   - Go to Account Settings → API tokens
   - Create a new token with "Entire account" scope
   - Copy the token (starts with `pypi-`)
3. **Add to GitHub Secrets**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add new repository secret named `PYPI_API_TOKEN`
   - Paste your PyPI token

## Badge System

The pipeline automatically generates and updates these badges:

- **Tests**: Shows test status (passing/failing)
- **Coverage**: Shows code coverage percentage
- **PyPI Version**: Shows current package version on PyPI
- **Python Versions**: Shows supported Python versions
- **Django Versions**: Shows supported Django versions

Badges are stored in `.github/badges/` and updated:
- After successful CI runs on the main branch
- Daily via scheduled workflow
- Manually via workflow dispatch

## Local Development

To test the CI setup locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=src/django_admin_magic --cov-report=xml --cov-report=term-missing

# Run linting
ruff check .
ruff format --check .

# Run security checks
bandit -r src/

# Build package (test deployment)
python -m build
twine check dist/*
```

## Troubleshooting

### Common Issues

1. **Badge Updates Failing**
   - Ensure `GITHUB_TOKEN` has write permissions
   - Check that the main branch is protected correctly

2. **PyPI Deployment Failing**
   - Verify `PYPI_API_TOKEN` is set correctly
   - Ensure package version is incremented in `pyproject.toml`
   - Check that the release tag matches the version

3. **Test Matrix Failures**
   - Check Django/Python version compatibility
   - Update version exclusions in the matrix if needed

### Manual Badge Update

To manually update badges:

1. Go to Actions tab in GitHub
2. Select "Update Badges" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Customization

### Adding New Test Environments

To add new Django or Python versions:

1. Update the matrix in `.github/workflows/ci.yml`
2. Add any necessary exclusions for incompatible combinations
3. Test locally to ensure compatibility

### Adding New Badges

To add new badges:

1. Generate the badge using appropriate tools
2. Store in `.github/badges/`
3. Update README.md to include the badge
4. Modify CI workflow to generate the badge automatically

### Modifying Deployment

To customize deployment:

1. Edit `.github/workflows/deploy.yml`
2. Add additional validation steps
3. Configure additional deployment targets

## Security Considerations

- API tokens are stored as GitHub secrets
- Tokens have minimal required permissions
- Security scanning runs on every CI build
- Dependencies are cached to reduce attack surface

## Performance Optimization

- Dependencies are cached between runs
- Matrix builds run in parallel
- Only necessary jobs run on each trigger
- Badge updates are batched to reduce API calls 