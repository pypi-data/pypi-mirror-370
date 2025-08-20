# Quick CI/CD Setup Guide

This guide will help you set up the CI/CD pipeline for Django Auto Admin in under 5 minutes.

## Prerequisites

- GitHub repository with the code
- PyPI account (for deployment)

## Step 1: Push the Code

The CI/CD workflows are already configured in the `.github/workflows/` directory. Simply push your code to GitHub:

```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

## Step 2: Set Up PyPI Token (Optional)

If you want automatic deployment to PyPI:

1. Go to https://pypi.org/ and create an account
2. Go to Account Settings → API tokens
3. Create a new token with "Entire account" scope
4. Copy the token (starts with `pypi-`)
5. Go to your GitHub repository → Settings → Secrets and variables → Actions
6. Add new repository secret named `PYPI_API_TOKEN`
7. Paste your PyPI token

## Step 3: Test Locally (Recommended)

Before pushing, test the CI setup locally:

```bash
python scripts/test-ci-locally.py
```

This will run all the same checks that the GitHub Actions pipeline will run.

## Step 4: Verify Setup

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. You should see the CI workflow running
4. Check that badges appear in your README

## What's Included

### CI Pipeline (`.github/workflows/ci.yml`)
- ✅ Tests across Django 3.2-5.0 and Python 3.8-3.12
- ✅ Code linting with ruff
- ✅ Security scanning with bandit
- ✅ Automatic badge updates
- ✅ Coverage reporting

### Deployment Pipeline (`.github/workflows/deploy.yml`)
- ✅ Automatic PyPI deployment on releases
- ✅ Package validation
- ✅ TestPyPI deployment (optional)

### Badge Updates (`.github/workflows/update-badges.yml`)
- ✅ Daily badge updates
- ✅ Manual trigger option
- ✅ Coverage and test status badges

## Badges

The pipeline automatically generates these badges:

- **Tests**: ![Tests](.github/badges/tests-badge.svg)
- **Coverage**: ![Coverage](.github/badges/coverage-badge.svg)
- **PyPI Version**: [![PyPI version](https://badge.fury.io/py/django-admin-magic.svg)](https://badge.fury.io/py/django-admin-magic)
- **Python Versions**: [![Python versions](https://img.shields.io/pypi/pyversions/django-admin-magic.svg)](https://pypi.org/project/django-admin-magic/)
- **Django Versions**: [![Django versions](https://img.shields.io/pypi/djversions/django-admin-magic.svg)](https://pypi.org/project/django-admin-magic/)

## Troubleshooting

### Badges Not Updating
- Ensure the main branch is not protected against pushes from Actions
- Check that `GITHUB_TOKEN` has write permissions

### Tests Failing
- Run `python scripts/test-ci-locally.py` to debug locally
- Check Django/Python version compatibility

### Deployment Failing
- Verify `PYPI_API_TOKEN` is set correctly
- Ensure package version is incremented in `pyproject.toml`

## Next Steps

1. **Create a Release**: Go to Releases → Create a new release to trigger deployment
2. **Monitor**: Check the Actions tab regularly to ensure everything is working
3. **Customize**: Modify the workflows in `.github/workflows/` as needed

## Support

For detailed information about the CI/CD setup, see [CI_CD_SETUP.md](CI_CD_SETUP.md). 