import logging
from collections.abc import Callable
from typing import Any, cast

from django.apps import apps
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from polymorphic.models import PolymorphicModel, PolymorphicModelBase

# Django compatibility: AlreadyRegistered moved in Django 4.0
try:
    from django.contrib.admin.exceptions import AlreadyRegistered
except ImportError:
    from django.contrib.admin.sites import AlreadyRegistered

from .conf import app_settings
from .mixins import ListAdmin, PolymorphicChildListAdmin, PolymorphicParentListAdmin
from .utils import is_polymorphic_model, is_polymorphic_model_parent_model

logger = logging.getLogger(__name__)

# Model type definition for all models used in admin class
InclusiveModelType = type[models.Model] | models.Model | PolymorphicModelBase | type[PolymorphicModelBase]

AdminClassType = type[PolymorphicParentListAdmin] | type[PolymorphicChildListAdmin] | type[ListAdmin]


class NoOpRegistrar:
    """
    Registrar that performs no operations.

    Used when auto-registration is disabled (e.g., during migrations or when admin
    is not installed). Provides the same API surface as the real registrar but
    all methods are safe no-ops to avoid import-time side effects.
    """

    def __init__(self, app_label: str | None = None, app_labels: list[str] | None = None, auto_discover: bool = False):
        self.app_labels = []

    @classmethod
    def register_all_discovered_apps(cls) -> "NoOpRegistrar":
        return cls(auto_discover=True)

    @classmethod
    def register_apps(cls, app_labels: list[str]) -> "NoOpRegistrar":
        return cls(app_labels=app_labels)

    @classmethod
    def register_app(cls, app_label: str) -> "NoOpRegistrar":
        return cls(app_label=app_label)

    # Common mutator methods are implemented as no-ops
    def register_models(self):
        return None

    def return_admin_class_for_model(self, model: InclusiveModelType):
        raise KeyError("Auto admin registration is disabled; no admin classes are available.")

    def add_search_fields(self, *args, **kwargs):
        return None

    def append_list_display(self, *args, **kwargs):
        return None

    def prepend_list_display(self, *args, **kwargs):
        return None

    def remove_list_display(self, *args, **kwargs):
        return None

    def append_filter_display(self, *args, **kwargs):
        return None

    def append_inline(self, *args, **kwargs):
        return None


class AdminModelRegistrar:
    """
    Class that handles the registration and configuration of Django admin classes for models.

    This class provides a centralized way to register models with the Django admin site and
    manage their display properties (list_display, list_filter, etc.). It handles both regular
    Django models and polymorphic models.

    General flow:
    1. create prototype models (_admin_class_factory)
    2. register models (register_models)
        2.1. set defaults for fields to show up in admin(__init__ method of listadmin mixin)
    3. Modify fields with append methods once admin classes have been registered.
    #NOTE: This needs a fundamentally different approach. The Sync() idea is good, because
    # we need to make sure the instances and the adminclasses actually have the same
    # attributes or you get errors like this:
    # <class 'django.forms.widgets.AdminClass_ProjectAlternateName'>: (admin.E108) The
    # value of 'list_display[5]' refers to 'created_at', which is not a callable, an
    # attribute of 'AdminClass_ProjectAlternateName', or an attribute or method on
    # 'project_tracker.ProjectAlternateName'.
    # As of right now (this commit) all edits using the methods for the registrar are
    # happenin on the widget, not the admin class.
    # They need to be syncd! And the sync code needs to be updated to sync changes from
    # the instance to the admin class prototype.
    """

    def __init__(self, app_label: str | None = None, app_labels: list[str] | None = None, auto_discover: bool = False):
        """
        Initialize the registrar for specific Django app(s).

        Args:
            app_label (str, optional): The label of a single Django app to register models for.
            app_labels (List[str], optional): List of Django app labels to register models for.
            auto_discover (bool): Whether to auto-discover and register all installed apps.

        """
        self.class_dict: dict[str, tuple[InclusiveModelType, AdminClassType]] = {}
        self.app_labels = self._determine_app_labels(app_label, app_labels, auto_discover)
        self.do_not_register_filter_string_list = app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
        self.models = []
        self._collect_models()
        self.model_iterator()
        self.register_models()

    def _determine_app_labels(
        self, app_label: str | None, app_labels: list[str] | None, auto_discover: bool
    ) -> list[str]:
        """
        Determine which app labels to use based on the provided parameters and settings.

        Priority order:
        1. Explicitly provided app_label or app_labels
        2. Settings configuration (APP_LABEL, APP_LABELS, AUTO_DISCOVER_ALL_APPS)
        3. Auto-discovery if enabled
        """
        # If explicit parameters are provided, use them
        if app_label:
            return [app_label]
        if app_labels:
            return app_labels

        # Check settings
        if hasattr(app_settings, "APP_LABEL") and app_settings.APP_LABEL:
            if isinstance(app_settings.APP_LABEL, list):
                return app_settings.APP_LABEL
            return [app_settings.APP_LABEL]

        if hasattr(app_settings, "APP_LABELS") and app_settings.APP_LABELS:
            return app_settings.APP_LABELS

        # Auto-discovery
        if auto_discover or (hasattr(app_settings, "AUTO_DISCOVER_ALL_APPS") and app_settings.AUTO_DISCOVER_ALL_APPS):
            return self._discover_app_labels()

        # Default to empty list if nothing is configured
        return []

    def _discover_app_labels(self) -> list[str]:
        """
        Discover all Django apps that have models.

        Returns:
            List of app labels that have models.

        """
        discovered_apps = []
        for app_config in apps.get_app_configs():
            # Skip django_admin_magic itself and other Django system apps
            if app_config.label in ["django_admin_magic", "admin", "auth", "contenttypes", "sessions"]:
                continue

            # Check if the app has any models
            models = app_config.get_models()
            if models:
                discovered_apps.append(app_config.label)
                logger.info(f"Auto-discovered app: {app_config.label} with {len(models)} models")

        return discovered_apps

    def _collect_models(self):
        """Collect all models from the specified app labels."""
        for app_label in self.app_labels:
            try:
                app_config = apps.get_app_config(app_label=app_label)
                app_models = list(app_config.get_models())
                self.models.extend(app_models)
                logger.info(f"Collected {len(app_models)} models from app: {app_label}")
            except LookupError:
                logger.warning(f"App '{app_label}' not found in installed apps")

    @classmethod
    def register_all_discovered_apps(cls) -> "AdminModelRegistrar":
        """
        Class method to create a registrar that auto-discovers and registers all apps.

        This is useful for users who want to register all their models automatically
        without specifying individual app labels.

        Returns:
            AdminModelRegistrar instance configured for auto-discovery

        """
        return cls(auto_discover=True)

    @classmethod
    def register_apps(cls, app_labels: list[str]) -> "AdminModelRegistrar":
        """
        Class method to create a registrar for specific app labels.

        Args:
            app_labels: List of app labels to register

        Returns:
            AdminModelRegistrar instance configured for the specified apps

        """
        return cls(app_labels=app_labels)

    @classmethod
    def register_app(cls, app_label: str) -> "AdminModelRegistrar":
        """
        Class method to create a registrar for a single app.

        Args:
            app_label: The app label to register

        Returns:
            AdminModelRegistrar instance configured for the specified app

        """
        return cls(app_label=app_label)

    def model_iterator(self):
        """
        Iterates through models and creates the associated admin class.
        Convenience method to create admin classes for models without
        having to explicitly create them in each app's admin.py file.
        """
        for model in self.models:
            model_name = model.__name__ if isinstance(model, type) else model.__class__.__name__
            model_passes_filter = not any(x in model_name for x in self.do_not_register_filter_string_list)
            if model._meta.abstract is False and model_passes_filter:
                admin_class = self._admin_class_factory(model, admin.site)
                self.class_dict[str(model)] = (model, admin_class)

    def _admin_class_factory(self, model, admin_site):
        """Creates class prototypes for admin_classes depending on the incoming model object."""
        adminclass_name = f"AdminClass_{model.__name__}"
        common_class_kwargs = {"model": model, "admin_site": admin_site}
        return type(
            adminclass_name,
            (ListAdmin,),
            common_class_kwargs,
        )

    def _tuple_list_handler(self, tuple_or_list: list[Any] | tuple[Any, ...]) -> list[Any]:
        """
        Convert a tuple or list to a list, preserving order and removing duplicates.

        This method ensures consistent handling of list-like objects by:
        1. Converting tuples to lists
        2. Removing duplicate entries while preserving order
        3. Handling nested structures recursively

        Args:
            tuple_or_list: The input tuple or list to process

        Returns:
            A list with duplicates removed while preserving order

        """
        if isinstance(tuple_or_list, tuple):
            tuple_or_list = list(tuple_or_list)
        return list(dict.fromkeys(tuple_or_list))

    def _verify_list_display_in_model(
        self,
        model: InclusiveModelType,
        list_display: list[str] | tuple[str],
        admin_class: admin.ModelAdmin,
    ):
        """
        Verify that all fields in list_display exist on the model or the admin class.

        This method checks both model fields and attributes (including properties)
        to ensure that all display fields are valid. It handles:
        1. Field names that exist on the model
        2. Property names that exist on the model
        3. Method names that exist on the model
        4. Callable objects (like linkify or custom display methods)
        5. Single character strings (used for formatting)

        Args:
            model: The model to verify fields against
            list_display: The list of fields to verify
            admin_class: The admin class associated with the model

        Raises:
            FieldDoesNotExist: If a field is not found on the model and doesn't match any valid pattern

        """
        # Cast model to appropriate type
        model_class = cast(
            "type[models.Model | PolymorphicModel]",
            model if isinstance(model, type) else model.__class__,
        )
        model_fields = [field.name for field in model_class._meta.fields]
        model_attributes = dir(model_class)
        # Get attributes from the admin class as well
        admin_class_attributes = dir(admin_class)

        for field in list_display:
            # Skip validation for:
            # 1. Callable objects (custom display methods)
            # 2. Single character strings (often used for formatting)
            # 3. Fields that have a short_description (admin display methods)
            if callable(field) or (isinstance(field, str) and len(field) == 1) or hasattr(field, "short_description"):
                continue

            # Check if the field exists on the model OR the admin class
            if field not in model_fields and field not in model_attributes and field not in admin_class_attributes:
                if isinstance(field, str):
                    admin_class_name = getattr(admin_class, "__name__", f"AdminClass_{model_class.__name__}")
                    msg = (
                        f"Field {field} not found in model {model_class.__name__} or admin class {admin_class_name}\n"
                        f"Model fields: {model_fields}\n"
                        f"Model attributes: {model_attributes}\n"
                        f"Admin class attributes: {admin_class_attributes}\n"
                        f"List display: {list_display}"
                    )
                    raise FieldDoesNotExist(
                        msg,
                    )
                admin_class_name = getattr(admin_class, "__name__", f"AdminClass_{model_class.__name__}")
                logger.debug(
                    f"Field {field} not found in model {model_class.__name__} or admin class {admin_class_name}",
                )

    def _sync_admin_instance(self, model: InclusiveModelType) -> None:
        """
        Sync the admin class with its registered instance.

        This method ensures that any changes made to the admin class prototype
        are reflected in the registered instance. This includes:
        - list_display
        - list_filter
        - inlines
        - actions
        - methods and their attributes
        - search fields
        - custom querysets


        Args:
            model: The model whose admin class needs to be synced

        """
        admin_class = self.return_admin_class_for_model(model)
        # Get the actual model class if we were passed an instance
        model_class = cast("type[models.Model]", model if isinstance(model, type) else model.__class__)
        registered_instance = admin.site._registry.get(model_class)

        if not registered_instance:
            return

        # Sync list_display
        if hasattr(admin_class, "list_display"):
            # Convert list_display to list and filter out any function objects
            list_display = []
            for item in admin_class.list_display:
                if callable(item) and not isinstance(item, type):
                    # For callable items (methods), create a wrapper that preserves attributes
                    def create_wrapper(method):
                        def wrapper(*args, **kwargs):
                            return method(*args, **kwargs)

                        # Copy all attributes from the original method
                        for attr in dir(method):
                            if not attr.startswith("_"):
                                try:
                                    setattr(wrapper, attr, getattr(method, attr))
                                except (AttributeError, TypeError):
                                    continue
                        # Copy special attributes if they exist
                        if hasattr(method, "__func__"):
                            wrapper.__func__ = method.__func__
                        if hasattr(method, "__self__"):
                            wrapper.__self__ = method.__self__
                        return wrapper

                    list_display.append(create_wrapper(item))
                else:
                    list_display.append(item)
            registered_instance.list_display = list_display

        # Sync list_filter
        if hasattr(admin_class, "list_filter"):
            registered_instance.list_filter = admin_class.list_filter

        # Sync search_fields
        if hasattr(admin_class, "search_fields"):
            registered_instance.search_fields = admin_class.search_fields

        # Sync readonly_fields
        if hasattr(admin_class, "readonly_fields"):
            registered_instance.readonly_fields = admin_class.readonly_fields

        # Sync list_select_related
        if hasattr(admin_class, "list_select_related"):
            registered_instance.list_select_related = admin_class.list_select_related

        # Sync inlines
        if hasattr(admin_class, "inlines"):
            if isinstance(admin_class.inlines, tuple):
                registered_instance.inlines = list(admin_class.inlines)
            else:
                registered_instance.inlines = admin_class.inlines

        # Sync actions
        if hasattr(admin_class, "actions"):
            current_actions = []
            if hasattr(registered_instance, "actions") and registered_instance.actions is not None:
                # Start with existing actions from the registered instance
                current_actions = list(registered_instance.actions)

            admin_actions_to_add = []
            if admin_class.actions is not None:
                # Get actions defined on the admin class prototype
                admin_actions_to_add = list(admin_class.actions)

            # Add actions from the admin class prototype if they aren't already present
            # in the registered instance's actions list. We compare by name for callables.
            for action in admin_actions_to_add:
                action_name = action if isinstance(action, str) else getattr(action, "__name__", str(action))
                is_present = False
                for existing_action in current_actions:
                    existing_action_name = (
                        existing_action
                        if isinstance(existing_action, str)
                        else getattr(existing_action, "__name__", str(existing_action))
                    )
                    if action_name == existing_action_name:
                        is_present = True
                        break
                if not is_present:
                    # Append the original action (callable or string)
                    current_actions.append(action)

            # Assign the updated list back to the registered instance
            registered_instance.actions = current_actions

        # Sync methods and their attributes
        for attr_name in dir(admin_class):
            if not attr_name.startswith("_"):  # Skip private methods
                try:
                    attr = getattr(admin_class, attr_name)
                    if callable(attr) and not isinstance(attr, type):
                        # Create a wrapper function that will have the attributes
                        def create_wrapper(method):
                            def wrapper(*args, **kwargs):
                                return method(*args, **kwargs)

                            # Copy all attributes from the original method
                            for method_attr in dir(method):
                                if not method_attr.startswith("_"):
                                    try:
                                        setattr(
                                            wrapper,
                                            method_attr,
                                            getattr(method, method_attr),
                                        )
                                    except (AttributeError, TypeError):
                                        continue
                            # Copy special attributes if they exist
                            if hasattr(method, "__func__"):
                                wrapper.__func__ = method.__func__
                            if hasattr(method, "__self__"):
                                wrapper.__self__ = method.__self__
                            return wrapper

                        wrapped = create_wrapper(attr)
                        # Set the wrapped method on the instance
                        setattr(registered_instance, attr_name, wrapped)
                except (AttributeError, TypeError):
                    # Skip any attributes that can't be accessed or copied
                    continue

    def update_list_select_related(
        self,
        model: InclusiveModelType,
        list_select_related: list[str] | tuple[str, ...] | bool,
    ) -> None:
        """
        Update the list_select_related property for a model's admin class.

        This method allows setting the list_select_related property to optimize
        database queries for the admin changelist view. It can be:
        - True: Select all foreign key relationships
        - False: Don't use any JOINs
        - List/tuple of field names: Only JOIN the specified relationships

        Args:
            model: The model whose admin class should be updated
            list_select_related: The value to set for list_select_related

        Example:
            # To select all foreign keys
            registrar.update_list_select_related(MyModel, True)

            # To select specific foreign keys
            registrar.update_list_select_related(MyModel, ['author', 'category'])

            # To disable all automatic JOINs
            registrar.update_list_select_related(MyModel, False)

        """
        admin_class = self.return_admin_class_for_model(model)
        admin_class.list_select_related = list_select_related
        self._sync_admin_instance(model)

    def add_admin_method(
        self,
        model: InclusiveModelType,
        method_name: str,
        method_func: Callable,
        *,
        short_description: str | None = None,
        is_action: bool = False,
    ) -> None:
        """
        Add a method to the admin class for a model.

        This method allows adding custom methods to the admin class, optionally
        marking them as actions and setting their short descriptions.

        Args:
            model: The model to add the method to
            method_name: The name to give the method
            method_func: The method to add (should be a function)
            short_description: Optional description for the method in admin interface
            is_action: Whether to add this method to the actions list

        Example:
            def mark_as_special(modeladmin, request, queryset):
                queryset.update(is_special=True)

            registrar.add_admin_method(
                MyModel,
                "mark_as_special",
                mark_as_special,
                short_description="Mark selected items as special",
                is_action=True
            )

        """
        # Validate method_name
        if not method_name or not isinstance(method_name, str):
            raise ValueError("method_name must be a non-empty string")

        # Validate method_func
        if method_func is None:
            raise ValueError("method_func cannot be None")

        # Validate method_name format (should be a valid Python identifier)
        if not method_name.replace("_", "").isalnum() or method_name[0].isdigit():
            raise ValueError("method_name must be a valid Python identifier")

        admin_instance = self.return_admin_class_for_model(model)  # This is the actual live instance

        final_wrapped_method: Callable
        if is_action:
            # Wrapper for admin actions
            # method_func signature: (modeladmin_instance, request, queryset)
            # Django calls action as: func(modeladmin, request, queryset)
            # This wrapper ensures the original method_func is called correctly.
            def action_wrapper(modeladmin_param, request_param, queryset_param):
                return method_func(modeladmin_param, request_param, queryset_param)

            final_wrapped_method = action_wrapper
        else:
            # Wrapper for display methods (e.g., in list_display)
            # method_func signature: (modeladmin_instance, model_instance)
            # Django calls display method as: admin_instance.method_name(model_instance)
            # 'admin_instance' (the live model admin instance) is available from the outer scope.
            def display_wrapper(obj_param):  # obj_param is the model_instance passed by Django
                # admin_instance is the ModelAdmin instance captured from the outer scope of add_admin_method
                return method_func(admin_instance, obj_param)

            final_wrapped_method = display_wrapper

        # Set the wrapped method directly on the admin instance
        setattr(admin_instance, method_name, final_wrapped_method)

        # Set short description if provided (on the final_wrapped_method)
        if short_description:
            try:
                final_wrapped_method.short_description = short_description
            except AttributeError:
                logger.warning(f"Could not set short_description on wrapped method {method_name} for model {model}")

        # Add to actions if requested
        if is_action:
            existing_actions = list(getattr(admin_instance, "actions", []) or [])
            action_to_add = final_wrapped_method  # Add the callable wrapper

            already_present = False
            for existing_action in existing_actions:
                if existing_action == action_to_add:
                    already_present = True
                    break
                # Compare by name if functions are different instances but represent the same action
                if hasattr(existing_action, "__name__") and existing_action.__name__ == getattr(
                    action_to_add,
                    "__name__",
                    None,
                ):
                    already_present = True
                    break

            if not already_present:
                existing_actions.append(action_to_add)
            admin_instance.actions = existing_actions

        # Sync the changes to the registered instance
        self._sync_admin_instance(model)

    def register_models(self):
        """
        Register models with the Django admin site.

        This method handles the registration process for all models in the app.
        It ensures that:
        1. Each model gets the correct admin class type (regular or polymorphic)
        2. List display and filter properties are properly initialized
        """
        if not self.class_dict:
            logger.debug(f"No admin classes to register for app {self.app_labels}")
            return

        for name, model_adminclass_tuple in self.class_dict.items():
            logger.debug(f"Registering model {name}")
            model, admin_class = model_adminclass_tuple
            # Check if admin class has a ListAdminMixin as a parent class
            try:
                admin.site.register(model, admin_class)  # type: ignore
                self._sync_admin_instance(model)

            except AlreadyRegistered:
                # If already registered, sync the instance
                self._sync_admin_instance(model)

    def add_search_fields(
        self,
        model: InclusiveModelType,
        search_fields: list[str],
    ):
        admin_class = self.return_admin_class_for_model(model)
        if hasattr(admin_class, "search_fields"):
            # Pass admin_class to verification
            self._verify_list_display_in_model(model, search_fields, admin_class)
            admin_class.search_fields = search_fields  # type: ignore
            self._sync_admin_instance(model)  # Sync after modification

    def append_list_display(
        self,
        model: InclusiveModelType,
        list_display: list[str] | tuple[str],
    ) -> None:
        """
        Add fields to the end of the admin display list.

        This method:
        1. Validates that all fields exist on the model
        2. Maintains field order while preventing duplicates
        3. Updates both the admin class and registered instance

        Args:
            model: The model to modify the admin display for
            list_display: Fields to add to the display list

        """
        admin_class = self.return_admin_class_for_model(model)
        if hasattr(admin_class, "list_display"):
            # Pass admin_class to verification
            self._verify_list_display_in_model(model, list_display, admin_class)
            current_list = self._tuple_list_handler(admin_class.list_display)
            # Add new fields, avoiding duplicates
            for field in list_display:
                if field not in current_list:
                    current_list.append(field)
            admin_class.list_display = current_list
            self._sync_admin_instance(model)

    def prepend_list_display(
        self,
        model: InclusiveModelType,
        list_display: str | list[str] | tuple[str],
    ) -> None:
        """
        Add fields to the start of the admin display list.

        This method:
        1. Validates that all fields exist on the model
        2. Removes any existing instances of the fields
        3. Prepends fields to the start of the list
        4. Updates both the admin class and registered instance

        Args:
            model: The model to modify the admin display for
            list_display: Field(s) to add to the start of the display list.
                         Can be a single string or list/tuple of strings.

        """
        admin_class = self.return_admin_class_for_model(model)
        if hasattr(admin_class, "list_display"):
            # Convert single string to list
            fields_to_add = [list_display] if isinstance(list_display, str) else list(list_display)

            # Pass admin_class to verification
            self._verify_list_display_in_model(model, fields_to_add, admin_class)
            current_list = self._tuple_list_handler(admin_class.list_display)

            # Remove any existing instances of the fields
            for field in fields_to_add:
                if field in current_list:
                    current_list.remove(field)

            # Add new fields at the start
            for field in reversed(fields_to_add):
                current_list.insert(0, field)

            admin_class.list_display = current_list
            self._sync_admin_instance(model)

    def remove_list_display(
        self,
        model: InclusiveModelType,
        list_display_to_remove: list[str] | tuple[str],
    ) -> None:
        admin_class = self.return_admin_class_for_model(model)
        admin_class.list_display = [field for field in admin_class.list_display if field not in list_display_to_remove]
        self._sync_admin_instance(model)

    def append_filter_display(
        self,
        model: type[models.Model] | models.Model | PolymorphicModelBase,
        list_filter: list[str] | tuple[str],
    ) -> None:
        """
        Add filter fields to the admin display.

        This method adds fields to the list_filter property of the admin class.
        It follows the same pattern as list_display management:
        1. Validates fields exist on the model
        2. Maintains field order while preventing duplicates
        3. Updates both admin class and registered instance

        Args:
            model: The model to add filters to
            list_filter: List or tuple of field names to add as filters

        Raises:
            KeyError: If model not found in registered classes
            FieldDoesNotExist: If field doesn't exist on model

        """
        admin_class = self.return_admin_class_for_model(model)
        if hasattr(admin_class, "list_filter"):
            # Pass admin_class to verification (assuming list_filter items should also be valid fields/methods)
            self._verify_list_display_in_model(model, list_filter, admin_class)
            admin_class.list_filter = self._tuple_list_handler(admin_class.list_filter)
            # Ensure no duplicates are added
            for item in list_filter:
                if item not in admin_class.list_filter:
                    admin_class.list_filter.append(item)
            self._sync_admin_instance(model)

    def return_admin_class_for_model(self, model: InclusiveModelType):
        """
        Return the admin class for a model.

        This method retrieves the admin class associated with a model from the
        class dictionary. It handles both class and instance model references.

        The returned admin class can be modified to customize various aspects
        of the admin interface. See Django's ModelAdmin documentation for all
        available options.

        Args:
            model: The model to get the admin class for

        Returns:
            The admin class for the model

        Raises:
            KeyError: If the model is not found in the registered classes

        Example Usage:
            admin_class = registrar.return_admin_class_for_model(MyModel)
            admin_class.list_filter += ["is_custom_component", "category"]
            admin_class.show_full_result_count = False
            admin_class.paginator = TimeLimitedPaginator

        """
        model_class = cast("type[models.Model]", model if isinstance(model, type) else model.__class__)
        registered_instance = admin.site._registry.get(model_class)

        if registered_instance:
            return registered_instance
        msg = f"Model {model_class} not found in registered classes - please register the model first."
        raise KeyError(msg)

    def append_inline(
        self,
        model: InclusiveModelType,
        inline_class: type[admin.TabularInline | admin.StackedInline],
    ) -> None:
        """
        Add an inline class to a model's admin.

        This method:
        1. Gets or creates the inlines list
        2. Converts tuple to list if needed
        3. Appends the new inline
        4. Updates both admin class and registered instance

        Args:
            model: The model to add the inline to
            inline_class: The inline class to add

        """
        admin_class = self.return_admin_class_for_model(model)

        # Initialize or convert inlines to list
        if not hasattr(admin_class, "inlines"):
            admin_class.inlines = []
        elif isinstance(admin_class.inlines, tuple):
            admin_class.inlines = list(admin_class.inlines)

        # Add inline if not already present
        if inline_class not in admin_class.inlines:
            admin_class.inlines.append(inline_class)

        self._sync_admin_instance(model)


class PolymorphicAdminModelRegistrar(AdminModelRegistrar):
    """An extension of AdminModelRegistrar that handles polymorphic models."""

    def _admin_class_factory(self, model, admin_site):
        """
        Creates class prototypes for admin_classes depending on the incoming model object.
        This method handles both regular and polymorphic models.
        """
        adminclass_name = f"AdminClass_{model.__name__}"
        common_class_kwargs = {"model": model, "admin_site": admin_site}
        if is_polymorphic_model(model):
            if is_polymorphic_model_parent_model(model):
                return type(
                    adminclass_name,
                    (PolymorphicParentListAdmin,),
                    common_class_kwargs,
                )
            return type(
                adminclass_name,
                (PolymorphicChildListAdmin,),
                common_class_kwargs,
            )
        return super()._admin_class_factory(model, admin_site)
