from django.conf import settings

from . import defaults


class AppSettings:
    """A settings object that allows overriding default settings from the Django project's settings."""

    def __init__(self, prefix="AUTO_ADMIN_"):
        self.prefix = prefix

    def __getattr__(self, name):
        # Check for the setting in the project's settings.py
        prefixed_name = self.prefix + name
        if hasattr(settings, prefixed_name):
            return getattr(settings, prefixed_name)

        # Fallback to the default settings
        if hasattr(defaults, name):
            return getattr(defaults, name)

        # If the setting is not found, raise an AttributeError
        raise AttributeError(f"'AppSettings' object has no attribute '{name}'")


app_settings = AppSettings()
