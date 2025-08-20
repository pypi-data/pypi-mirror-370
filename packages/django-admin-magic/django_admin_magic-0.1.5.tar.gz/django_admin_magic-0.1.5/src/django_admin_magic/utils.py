import inspect
import logging
import os
import sys

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.paginator import Paginator
from django.db import OperationalError, connection, transaction
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html
from polymorphic.models import PolymorphicModel

from .conf import app_settings

logger = logging.getLogger(__name__)


def get_all_child_classes(cls: type) -> list[type]:
    """
    Recursively retrieves all child classes of a given class.

    Args:
        cls (Type): The class to inspect for child classes.

    Returns:
        List[Type]: A list of all direct and indirect subclasses of the given class.

    """
    child_classes = cls.__subclasses__()  # Get direct subclasses
    all_children = child_classes[:]  # Start with direct subclasses

    for child in child_classes:
        # Recursively add subclasses of each child
        all_children.extend(get_all_child_classes(child))

    return all_children


def is_polymorphic_model(model_class):
    if model_class is None:
        return False
    return issubclass(model_class, PolymorphicModel)


def is_polymorphic_model_parent_model(cls):
    if cls is None:
        return False
    return PolymorphicModel in cls.__bases__


def is_linkify_function(field):
    """
    Check if a field is a linkify function (either linkify or linkify_gfk).

    Args:
        field: The field to check

    Returns:
        bool: True if the field is a linkify function, False otherwise

    """
    if not callable(field):
        return False

    # Check if it's a linkify function by examining its function name or attributes
    # Both linkify and linkify_gfk functions have specific patterns
    func_name = getattr(field, "__name__", "")

    # Check for the specific function names used in linkify functions
    if func_name in ("_linkify", "_linkify_gfk"):
        return True

    # Additional check: look for the short_description attribute which is set on linkify functions
    if hasattr(field, "short_description") and hasattr(field, "admin_order_field"):
        return True

    # Check if the function was created by our linkify functions by examining the closure
    try:
        # Get the function's code object to check if it contains linkify-specific patterns
        if hasattr(field, "__code__"):
            # This is a more robust way to detect our linkify functions
            # We can check if the function has the expected attributes
            if hasattr(field, "short_description") and hasattr(field, "admin_order_field"):
                return True
    except (AttributeError, TypeError):
        pass

    return False


def reorder_list_display_to_avoid_linkify_first(list_display):
    """
    Reorder list_display to ensure the first field is not a linkify function.
    Moves all leading linkify functions after the first non-linkify field.
    """
    if not list_display or len(list_display) < 2:
        return list_display

    # Find the index of the first non-linkify field
    first_non_linkify_index = None
    for i, field in enumerate(list_display):
        if not is_linkify_function(field):
            first_non_linkify_index = i
            break

    if first_non_linkify_index is None or first_non_linkify_index == 0:
        # No non-linkify field found, or already starts with non-linkify
        return list_display

    # Move all leading linkify functions (from start up to first non-linkify) after the first non-linkify
    leading_linkify = list_display[:first_non_linkify_index]
    rest = list_display[first_non_linkify_index:]
    reordered = [rest[0]] + leading_linkify + rest[1:]
    logger.debug(f"Reordered list_display to avoid linkify field being first: {reordered}")
    return reordered


def create_auto_admin_registrar(app_label: str = None):
    """
    Create an auto admin registrar for the current app.

    This function is designed to be used in admin.py files to automatically
    register all models in the current app with the admin site.

    Args:
        app_label (str, optional): The app label to register. If None, will be
                                 automatically determined from the current package.

    Returns:
        AdminModelRegistrar: The registrar instance

    Example:
        # In your app's admin.py file:
        from django_admin_magic.utils import create_auto_admin_registrar

        registrar = create_auto_admin_registrar()
        # All models in this app are now registered with the admin site

    """
    from .registrar import AdminModelRegistrar, NoOpRegistrar

    if autoreg_disabled():
        return NoOpRegistrar()

    inferred_app_label = app_label
    if inferred_app_label is None:
        inferred_app_label = infer_current_app_label()

    if not inferred_app_label:
        logger.debug("Unable to infer app label for auto admin registrar; skipping registration.")
        return NoOpRegistrar()

    return AdminModelRegistrar.register_app(inferred_app_label)


def create_auto_admin_registrar_for_apps(app_labels: list[str]):
    """
    Create an auto admin registrar for multiple apps.

    Args:
        app_labels (list[str]): List of app labels to register

    Returns:
        AdminModelRegistrar: The registrar instance

    Example:
        # In your admin.py file:
        from django_admin_magic.utils import create_auto_admin_registrar_for_apps

        registrar = create_auto_admin_registrar_for_apps(['myapp1', 'myapp2'])

    """
    from .registrar import AdminModelRegistrar, NoOpRegistrar

    if autoreg_disabled():
        return NoOpRegistrar()

    return AdminModelRegistrar.register_apps(app_labels)


def create_auto_admin_registrar_for_all_apps():
    """
    Create an auto admin registrar that discovers and registers all apps.

    Returns:
        AdminModelRegistrar: The registrar instance

    Example:
        # In your admin.py file:
        from django_admin_magic.utils import create_auto_admin_registrar_for_all_apps

        registrar = create_auto_admin_registrar_for_all_apps()

    """
    from .registrar import AdminModelRegistrar, NoOpRegistrar

    if autoreg_disabled():
        return NoOpRegistrar()

    return AdminModelRegistrar.register_all_discovered_apps()


def infer_current_app_label() -> str | None:
    """
    Infer the current Django app label from the caller's module using Django's app registry.

    This is safer than relying on '__package__' which may not be set during certain
    management commands (e.g., migrations) or when imported in unusual contexts.
    """
    module_name = None
    module = None
    try:
        current_frame = inspect.currentframe()
        if current_frame is not None and current_frame.f_back is not None:
            module = inspect.getmodule(current_frame.f_back)
            if module is not None:
                module_name = module.__name__
    finally:
        # Help GC with frame references
        del current_frame

    if module_name:
        try:
            app_config = django_apps.get_containing_app_config(module_name)
            if app_config is not None:
                return app_config.label
        except Exception:
            pass

        # Fallback: try prefix match with installed app configs
        for config in django_apps.get_app_configs():
            if module_name.startswith(config.name):
                return config.label

    # Secondary fallback using module.__package__ if available
    try:
        if module is not None and getattr(module, "__package__", None):
            pkg = module.__package__
            for config in django_apps.get_app_configs():
                if pkg.startswith(config.name):
                    return config.label
    except Exception:
        pass

    return None


def autoreg_disabled() -> bool:
    """
    Determine whether auto admin registration should be disabled for the current context.

    Disables for:
    - Explicit project setting/env flag
    - Migrations (makemigrations/migrate) and other configured skip commands
    - When django.contrib.admin is not installed and configured to skip
    """
    # Explicit setting toggle
    try:
        if getattr(app_settings, "DISABLED", False):
            return True
    except Exception:
        # If settings are not ready, continue with other checks
        pass

    # Environment variable overrides
    if os.environ.get("DJANGO_ADMIN_MAGIC_DISABLE") == "1" or os.environ.get("AUTO_ADMIN_DISABLE") == "1":
        return True

    # Skip specific management commands
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    skip_commands = set(getattr(app_settings, "SKIP_COMMANDS", []))
    if cmd in skip_commands:
        return True

    # Skip when admin not installed (based on config)
    try:
        if getattr(app_settings, "SKIP_IF_ADMIN_NOT_INSTALLED", True) and not django_apps.is_installed(
            "django.contrib.admin"
        ):
            return True
    except Exception:
        # apps registry may not be ready yet; fallback to settings
        try:
            from django.conf import settings as dj_settings

            if getattr(app_settings, "SKIP_IF_ADMIN_NOT_INSTALLED", True) and (
                not hasattr(dj_settings, "INSTALLED_APPS") or "django.contrib.admin" not in dj_settings.INSTALLED_APPS
            ):
                return True
        except Exception:
            pass

    return False


class TimeLimitedPaginator(Paginator):
    """
    Paginator that enforces a timeout on the count operation.
    If the operations times out, a fake bogus value is
    returned instead.
    """

    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        # Validate per_page
        if per_page is not None and (not isinstance(per_page, int) or per_page <= 0):
            raise ValueError("per_page must be a positive integer or None")
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)

    @cached_property
    def count(self):
        # We set the timeout in a db transaction to prevent it from
        # affecting other transactions.
        try:
            with transaction.atomic(), connection.cursor() as cursor:
                # Only set statement_timeout for PostgreSQL
                if connection.vendor == "postgresql":
                    cursor.execute("SET LOCAL statement_timeout TO 1000;")
                return super().count
        except OperationalError:
            with transaction.atomic(), connection.cursor() as cursor:
                # Obtain estimated values (only valid with PostgreSQL)
                if not self.object_list.query.model:  # type: ignore
                    raise

                # Only use PostgreSQL-specific query for PostgreSQL
                if connection.vendor == "postgresql":
                    cursor.execute(
                        "SELECT reltuples FROM pg_class WHERE relname = %s",
                        [self.object_list.query.model._meta.db_table],  # type: ignore
                    )
                    res = cursor.fetchone()
                    if res:
                        return int(res[0])

                # For non-PostgreSQL databases, return a reasonable estimate
                # or fall back to the actual count (which might be slow)
                logger.warning(
                    f"Count operation failed for {self.object_list.query.model._meta.db_table}. "
                    f"Database vendor: {connection.vendor}. Falling back to actual count."
                )
                return super().count


@admin.action(description="Mark task as unsuccessful")
def reset_success(modeladmin, request, queryset):
    # Handle both QuerySet and list objects
    if hasattr(queryset, "update"):
        queryset.update(success=False)
    else:
        # For list objects, update each item individually
        for item in queryset:
            if hasattr(item, "success"):
                item.success = False
                item.save()


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """

    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return "-"
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f"admin:{app_label}_{model_name}_change"
        # Add try-except block for cases where reverse fails (e.g., model not in admin)
        try:
            link_url = reverse(view_name, args=[linked_obj.pk])
            return format_html('<a href="{}">{}</a>', link_url, linked_obj)
        except Exception:
            # Fallback: Display object representation without a link
            logger.debug(f"Could not reverse admin URL for {app_label}.{model_name} with pk {linked_obj.pk}")
            return str(linked_obj)

    desc = field_name.replace("_", " ").title()
    try:
        _linkify.short_description = desc  # Sets column name
        _linkify.admin_order_field = field_name  # Allow sorting by this field
    except AttributeError:
        logger.warning(f"Could not set admin attributes on linkify function for {field_name}")
    return _linkify


def linkify_gfk(field_name):
    """
    Converts a GenericForeignKey value into clickable links in the admin.

    Args:
        field_name (str): The name of the GenericForeignKey field on the model.

    Returns:
        Callable: A function suitable for Django admin's list_display.

    """

    def _linkify_gfk(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return "-"

        # GFK target object could be anything, so we need its ContentType info
        try:
            # Ensure the linked object has a _meta attribute and pk
            if not hasattr(linked_obj, "_meta") or not hasattr(linked_obj, "pk") or linked_obj.pk is None:
                # Fallback if it's not a standard model instance or has no pk
                return str(linked_obj)

            # Get metadata directly from the linked object instance
            obj_id = linked_obj.pk
            app_label = linked_obj._meta.app_label
            model_name = linked_obj._meta.model_name

            view_name = f"admin:{app_label}_{model_name}_change"
            link_url = reverse(view_name, args=[obj_id])
            # Use a simplified representation, perhaps just the model name and PK
            display_text = f"{model_name.capitalize()} {obj_id}"
            return format_html('<a href="{}">{}</a>', link_url, display_text)
        except Exception as e:
            # Fallback if URL cannot be reversed or any other error occurs
            logger.debug(f"Could not reverse admin URL for GFK target {linked_obj}: {e}")
            return str(linked_obj)  # Display the object's string representation

    # Use the GFK field name for description and ordering
    desc = field_name.replace("_", " ").title()
    try:
        _linkify_gfk.short_description = desc
        _linkify_gfk.admin_order_field = field_name  # Attempt sorting - may depend on GFK setup
    except AttributeError:
        logger.warning(f"Could not set admin attributes on linkify_gfk function for {field_name}")
    return _linkify_gfk
