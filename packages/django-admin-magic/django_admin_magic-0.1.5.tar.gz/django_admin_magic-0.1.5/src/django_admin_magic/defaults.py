# The app_label(s) of the app(s) to auto-register models for.
# Can be a single string, a list of strings, or None for auto-discovery
APP_LABEL = None

# List of app labels to auto-register models for (alternative to APP_LABEL)
APP_LABELS = []

# Whether to auto-discover and register all installed apps
# If True, will register models for all Django apps that have models
AUTO_DISCOVER_ALL_APPS = False

# Global kill-switch to disable auto admin registration entirely
DISABLED = False

# Skip auto registration for these Django management commands
# This prevents crashes during migrations and similar non-admin contexts
SKIP_COMMANDS = ["makemigrations", "migrate"]

# If True, disable auto-registration when 'django.contrib.admin' isn't installed
SKIP_IF_ADMIN_NOT_INSTALLED = True

# Terms to exclude from list_display when auto-generating it.
DEFAULT_EXCLUDED_TERMS = ["_ptr", "uuid", "poly", "baseclass", "basemodel", "histo", "pk", "id", "search"]

# Model names to exclude from registration. Useful for excluding historical models.
DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST = ["Historical"]

# Admin attributes that are often tuples but need to be lists for modification.
ADMIN_TUPLE_ATTRIBUTES_TO_LIST = ["list_display", "list_filter", "search_fields", "readonly_fields"]

# Whether to reorder linkify fields to avoid them being first in list_display
# This prevents issues with clicking on the first column in admin changelist views
REORDER_LINKIFY_FIELDS = True
