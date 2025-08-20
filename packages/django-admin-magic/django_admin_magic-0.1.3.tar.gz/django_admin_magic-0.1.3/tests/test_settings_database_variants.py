"""
Database-specific test settings for Django Auto Admin.

This module provides test settings for different database backends to ensure
the library works correctly with all supported Django databases.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-test-key-for-testing-only"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "polymorphic",
    "django_admin_magic",
    "tests",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tests.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django Auto Admin settings
AUTO_ADMIN_APP_LABEL = "tests"


# Database configurations for different backends
def get_database_config():
    """Get database configuration based on environment variables."""
    db_backend = os.environ.get("DJANGO_TEST_DB", "sqlite")

    if db_backend == "postgresql":
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "django_admin_magic_test"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    elif db_backend == "mysql":
        return {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DB", "django_admin_magic_test"),
            "USER": os.environ.get("MYSQL_USER", "root"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
            "HOST": os.environ.get("MYSQL_HOST", "localhost"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    elif db_backend == "oracle":
        return {
            "ENGINE": "django.db.backends.oracle",
            "NAME": os.environ.get("ORACLE_DB", "localhost:1521/XE"),
            "USER": os.environ.get("ORACLE_USER", "system"),
            "PASSWORD": os.environ.get("ORACLE_PASSWORD", "oracle"),
            "HOST": os.environ.get("ORACLE_HOST", "localhost"),
            "PORT": os.environ.get("ORACLE_PORT", "1521"),
        }
    else:  # sqlite (default)
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }


# Database configuration
DATABASES = {"default": get_database_config()}

# Additional database configurations for multi-database testing
DATABASES.update(
    {
        "sqlite": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_sqlite.sqlite3",
        },
        "postgresql": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "django_admin_magic_test"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        },
        "mysql": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DB", "django_admin_magic_test"),
            "USER": os.environ.get("MYSQL_USER", "root"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", ""),
            "HOST": os.environ.get("MYSQL_HOST", "localhost"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        },
        "oracle": {
            "ENGINE": "django.db.backends.oracle",
            "NAME": os.environ.get("ORACLE_DB", "localhost:1521/XE"),
            "USER": os.environ.get("ORACLE_USER", "system"),
            "PASSWORD": os.environ.get("ORACLE_PASSWORD", "oracle"),
            "HOST": os.environ.get("ORACLE_HOST", "localhost"),
            "PORT": os.environ.get("ORACLE_PORT", "1521"),
        },
    }
)


# Database-specific settings
def get_database_specific_settings():
    """Get database-specific settings based on the current database."""
    db_backend = os.environ.get("DJANGO_TEST_DB", "sqlite")

    if db_backend == "postgresql":
        return {
            # PostgreSQL-specific settings
            "CONN_MAX_AGE": 0,  # Disable connection pooling for tests
        }
    elif db_backend == "mysql":
        return {
            # MySQL-specific settings
            "CONN_MAX_AGE": 0,
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    elif db_backend == "oracle":
        return {
            # Oracle-specific settings
            "CONN_MAX_AGE": 0,
            "OPTIONS": {
                "threaded": True,
            },
        }
    else:  # sqlite
        return {
            # SQLite-specific settings
            "CONN_MAX_AGE": 0,
        }


# Apply database-specific settings
for db_name, db_config in DATABASES.items():
    if db_name != "default":
        db_specific = get_database_specific_settings()
        db_config.update(db_specific)


# Test-specific settings
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Cache settings for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email settings for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Logging for tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django_admin_magic": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
