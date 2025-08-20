# Django Admin Magic Demo

> **Note:** This demo requires the [uv package manager](https://github.com/astral-sh/uv). Install it from the link or with `curl -Ls https://astral.sh/uv/install.sh | sh`.

This demo showcases the `django-admin-magic` package, which automatically registers your Django models with the admin site.

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to the demo directory
cd demo

# Run the automated setup script (installs dependencies with uv)
python setup_demo.py

# Start the development server
python manage.py runserver
```

### Option 2: Manual Setup

```bash
# Navigate to the demo directory
cd demo

# Install dependencies with uv
uv pip install -r requirements.txt

# Run migrations (pre-created)
python manage.py migrate

# Create a superuser (optional - will be created automatically)
python manage.py createsuperuser_auto

# Start the development server
python manage.py runserver
```

## Access the Demo

1. **Main Demo Page**: http://127.0.0.1:8000/
   - Shows all automatically registered models
   - Displays field information for each model
   - Provides links to the admin interface

2. **Django Admin**: http://127.0.0.1:8000/admin/
   - Username: `admin`
   - Password: `admin123`
   - All models are automatically registered and ready to use

## Demo Features

### Models Included

The demo includes various model types to showcase the automatic registration:

- **SimpleModel**: Basic model with standard fields
- **ComplexModel**: Model with all Django field types
- **ForeignKeyModel**: Model with various relationship types
- **GenericForeignKeyModel**: Model with generic foreign keys
- **PolymorphicParent/ChildA/ChildB**: Polymorphic models using django-polymorphic
- **ModelWithProperties**: Model with properties (detected automatically)
- **ModelWithSearchVector**: Model with search functionality
- **ModelWithCustomManager**: Model with custom manager

### Sample Data

The demo includes sample data for all models, including:
- Multiple instances of each model type
- Relationships between models
- Various field values to demonstrate different data types
- Polymorphic model instances

### Admin Features Demonstrated

- **Automatic Registration**: All models appear in the admin without manual registration
- **Field Detection**: Different field types are properly displayed
- **Relationship Handling**: Foreign keys, many-to-many, and one-to-one relationships
- **Polymorphic Support**: Polymorphic models work seamlessly
- **Property Detection**: Model properties can be used in admin lists
- **Search and Filtering**: Built-in search and filtering capabilities

## Configuration

The demo uses the following configuration in `demo/settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'django_admin_magic',
    'demo_app',
]

# Django Admin Magic Configuration
AUTO_ADMIN_APP_LABEL = 'demo_app'
```

## Customization

You can customize the admin classes after they've been registered:

```python
from django.apps import apps

# Get the registrar instance
registrar = apps.get_app_config("django_admin_magic").registrar

# Get the admin class for a model
MyModelAdmin = registrar.return_admin_class_for_model(MyModel)

# Customize the admin class
MyModelAdmin.list_display.append("my_custom_field")
```

## Troubleshooting

### Common Issues

1. **Import Error for django-polymorphic**: Make sure you have installed the requirements:
   ```bash
   uv pip install -r requirements.txt
   ```

2. **Database Errors**: If you encounter database errors, try:
   ```bash
   python manage.py migrate --run-syncdb
   ```

3. **Superuser Already Exists**: The setup script will skip superuser creation if one already exists.

### Reset Demo

To reset the demo to a clean state:

```bash
# Remove the database
rm db.sqlite3

# Re-run setup
python setup_demo.py
```

## Learn More

- [Django Admin Magic Documentation](../README.md)
- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [Django Polymorphic Documentation](https://django-polymorphic.readthedocs.io/) 