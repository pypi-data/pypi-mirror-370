# Django Admin Magic

[![Tests](.github/badges/tests-badge.svg)](https://github.com/billthefighter/django-admin-magic/actions)
[![Coverage](.github/badges/coverage-badge.svg)](https://codecov.io/gh/billthefighter/django-admin-magic)
[![Test Matrix](https://img.shields.io/badge/test%20matrix-23%20combinations-brightgreen)](https://github.com/billthefighter/django-admin-magic/actions)
[![PyPI version](https://badge.fury.io/py/django-admin-magic.svg)](https://badge.fury.io/py/django-admin-magic)
[![Python versions](https://img.shields.io/pypi/pyversions/django-admin-magic.svg)](https://pypi.org/project/django-admin-magic/)
[![Django versions](https://img.shields.io/pypi/djversions/django-admin-magic.svg)](https://pypi.org/project/django-admin-magic/)

A simple Django app to automatically register your models with the admin site.

## What?
It auto-generates all your admin pages programatically! It's awesome!

## Why?
Sometimes you're working on a django app and you just wanna see the models, and you don't want to define a brand new admin instance every time, and you just want things to work and look at your data in the admin view. If so, this package is for you!

## Tested Dependencies

This package is thoroughly tested against the following dependency combinations:

| Django Version | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 | Python 3.12 |
|----------------|------------|------------|-------------|-------------|-------------|
| **3.2**        | ✅         | ✅         | ✅          | ✅          | ✅          |
| **4.0**        | ✅         | ✅         | ✅          | ✅          | ✅          |
| **4.1**        | ✅         | ✅         | ✅          | ✅          | ✅          |
| **4.2**        | ✅         | ✅         | ✅          | ✅          | ✅          |
| **5.0**        | ❌         | ❌         | ✅          | ✅          | ✅          |

**Note**: Django 5.0 requires Python 3.10+ and is not compatible with Python 3.8 or 3.9.

### Continuous Integration

The test matrix includes:
- **5 Django versions** (3.2, 4.0, 4.1, 4.2, 5.0)
- **5 Python versions** (3.8, 3.9, 3.10, 3.11, 3.12)
- **Code coverage** reporting
- **Linting** with ruff
- **Security scanning** with bandit



## Installation

Install the package from PyPI:

```bash
pip install django-admin-magic
```

Then, add it to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_admin_magic",
    # ...
]
```

## Demo

A full-featured demo app is included in this repository to showcase all features of Django Admin Magic, including:
- Automatic admin registration for a variety of model types
- Sample data for all models
- Auto-generated superuser for instant login
- Landing page listing all registered models

**Quickstart:**

```bash
python demo_app/setup_demo.py
python demo_app/manage.py runserver
```

- Main demo: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/ (login: `admin` / `admin123`)

See [demo_app/README.md](demo_app/README.md) for full demo instructions, troubleshooting, and customization tips.

## Configuration

Django Auto Admin supports multiple ways to specify which apps to register models for:

### Method 1: Single App Label (Traditional)

Specify a single `app_label` in your `settings.py`:

```python
AUTO_ADMIN_APP_LABEL = "my_app"
```

### Method 2: Multiple App Labels

Specify multiple app labels as a list:

```python
# Option A: Using APP_LABELS setting
AUTO_ADMIN_APP_LABELS = ["my_app", "another_app", "third_app"]

# Option B: Using APP_LABEL as a list
AUTO_ADMIN_APP_LABEL = ["my_app", "another_app", "third_app"]
```

### Method 3: Auto-Discover All Apps

Automatically discover and register all installed apps that have models:

```python
AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS = True
```

### Method 4: Manual Registration in admin.py

If no configuration is provided in settings, you can manually create registrars in your `admin.py` files:

```python
# In your app's admin.py file
from django_admin_magic.utils import create_auto_admin_registrar

# Auto-determine app label from current package
registrar = create_auto_admin_registrar()

# Or specify a specific app label
registrar = create_auto_admin_registrar("my_app")

# Or register multiple apps
from django_admin_magic.utils import create_auto_admin_registrar_for_apps
registrar = create_auto_admin_registrar_for_apps(["my_app", "another_app"])

# Or register all discovered apps
from django_admin_magic.utils import create_auto_admin_registrar_for_all_apps
registrar = create_auto_admin_registrar_for_all_apps()
```

### Configuration Priority

The library follows this priority order for determining which apps to register:

1. Explicitly provided parameters in admin.py files
2. Settings configuration (`AUTO_ADMIN_APP_LABEL`, `AUTO_ADMIN_APP_LABELS`, `AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS`)
3. Auto-discovery if enabled
4. No registration if nothing is configured

### Advanced Configuration

You can override the default settings by adding them to your `settings.py` with the `AUTO_ADMIN_` prefix.

-   `DEFAULT_EXCLUDED_TERMS`: A list of strings to exclude from the `list_display` when it's auto-generated.
-   `DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST`: A list of strings. Any model whose name contains one of these strings will not be registered.
-   `ADMIN_TUPLE_ATTRIBUTES_TO_LIST`: A list of admin attributes that are typically tuples but need to be lists for modification (e.g., `list_display`, `list_filter`).
-   `REORDER_LINKIFY_FIELDS`: Boolean flag (default: `True`) that controls whether linkify fields should be reordered to avoid being the first column in admin changelist views. This prevents issues with clicking on the first column, which is often used for row selection checkboxes.

### Linkify Field Reordering

By default, Django Auto Admin automatically reorders `list_display` fields to ensure that linkify functions (foreign key links) are not the first column in admin changelist views. This is because the first column in Django admin is often used for row selection checkboxes, and having a clickable link there can interfere with the selection functionality.

**Example:**
```python
# Without reordering (problematic):
list_display = [linkify('parent'), 'name', 'created_at']

# With reordering (fixed):
list_display = ['name', linkify('parent'), 'created_at']
```

You can disable this behavior by setting:
```python
AUTO_ADMIN_REORDER_LINKIFY_FIELDS = False
```

## Usage

Once installed and configured, the library will automatically register all the models in the specified app(s) with the admin site.

### Customizing the Admin

You can still customize the admin classes after they've been registered. The `AdminModelRegistrar` instance provides several methods for this purpose. You can get the registrar instance from the `apps` registry.

```python
from django.apps import apps

# Get the registrar instance
registrar = apps.get_app_config("django_admin_magic").registrar

# Get the admin class for a model
MyModelAdmin = registrar.return_admin_class_for_model(MyModel)

# Customize the admin class
MyModelAdmin.list_display.append("my_custom_field")
```

### Available Methods

-   `append_list_display(model, list_display)`
-   `prepend_list_display(model, list_display)`
-   `remove_list_display(model, list_display_to_remove)`
-   `append_filter_display(model, list_filter)`
-   `add_search_fields(model, search_fields)`
-   `update_list_select_related(model, list_select_related)`
-   `add_admin_method(model, method_name, method_func, short_description=None, is_action=False)`
-   `append_inline(model, inline_class)`

## Polymorphic Models

This library automatically detects if `django-polymorphic` is installed and will use the appropriate admin classes for polymorphic models. There is no extra configuration required.

## Development

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- **Tests**: Runs across Django 3.2-5.0 and Python 3.8-3.12
- **Linting**: Code quality checks with ruff
- **Security**: Automated security scanning with bandit
- **Deployment**: Automatic PyPI deployment on releases
- **Badges**: Real-time status badges updated automatically

For setup instructions, see [SETUP_CI_CD.md](SETUP_CI_CD.md).

### Local Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format .

# Test CI locally
python scripts/test-ci-locally.py
``` 