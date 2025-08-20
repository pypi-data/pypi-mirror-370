import csv
import logging

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.http import HttpResponse
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from .conf import app_settings
from .utils import (
    TimeLimitedPaginator,
    get_all_child_classes,
    linkify,
    linkify_gfk,
    reorder_list_display_to_avoid_linkify_first,
)

logger = logging.getLogger(__name__)


class ExportCsvMixin:
    @admin.action(
        description="Export Selected to CSV",
    )
    def export_as_csv(self, request, queryset):
        meta = self.model._meta  # type: ignore
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response


class ListAdminMixin:
    def __init__(self, model):
        """
        Initialize the admin mixin with empty lists for display and filter.

        Args:
            model: The model this admin class is for

        """
        # After registration, admin classes are instantiated with tuples in these attributes. We want to modify those,
        # So we need to recast the fields we want to modify as lists.
        for attr_name in app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST:
            if not hasattr(self, attr_name) or not getattr(self, attr_name):
                setattr(self, attr_name, [])
            else:
                attr_val = getattr(self, attr_name)
                if isinstance(attr_val, tuple):
                    setattr(self, attr_name, list(attr_val))

        self.list_select_related = True
        self.model = model
        # Separate relations and GFKs
        self.relations = []
        self.generic_foreign_keys = []
        self.gfk_constituent_fields = set()  # To track fields used by GFKs
        self.properties = []  # Track properties on the model

        for field in model._meta.get_fields():
            if isinstance(field, GenericForeignKey):
                self.generic_foreign_keys.append(field.name)
                # Store the names of the fields that make up this GFK
                self.gfk_constituent_fields.add(field.ct_field)
                self.gfk_constituent_fields.add(field.fk_field)
            elif field.many_to_one or field.one_to_one or field.many_to_many:
                self.relations.append(field.name)

        # Find property attributes on the model class
        for attr_name in dir(model):
            if attr_name.startswith("_"):
                continue
            # Skip 'pk' and 'id' properties
            if attr_name in ("pk", "id"):
                continue
            if attr_name in ("relation_fields", "non_relation_fields"):
                continue
            try:
                attr = getattr(model, attr_name)
                if isinstance(attr, property):
                    self.properties.append(attr_name)
            except (AttributeError, TypeError):
                continue

        # Automatically add search_vector to search_fields if it exists
        try:
            model._meta.get_field("search_vector")
            if "search_vector" not in self.search_fields:
                self.search_fields.append("search_vector")
            if "search_vector" not in self.readonly_fields:
                self.readonly_fields.append("search_vector")
        except FieldDoesNotExist:
            pass  # The model does not have a search_vector field

        # Ensure list_filter is always a list
        if not hasattr(self, "list_filter"):
            self.list_filter = []
        elif not isinstance(self.list_filter, list):
            self.list_filter = list(self.list_filter)

        self.set_changelist_fields()

    def set_changelist_fields(self, fields_at_end_of_list: list[str] | None = None):
        """
        Set up the list_display and list_filter fields for the admin class.

        Args:
            fields_at_end_of_list: Optional list of fields to append at the end of list_display

        """
        fields_at_end_of_list = fields_at_end_of_list or []
        modelfields = self.model._meta.fields
        logger.debug("Starting set_changelist_fields")
        logger.debug(f"Model fields are {modelfields}")

        # Reset list_display and list_filter to avoid duplicates
        self.list_display = []
        self.list_filter = []

        excluded_terms = app_settings.DEFAULT_EXCLUDED_TERMS

        # Add GenericForeignKeys first, using linkify_gfk
        for gfk_name in self.generic_foreign_keys:
            if not any(term in gfk_name.casefold() for term in excluded_terms):
                self.list_display.append(linkify_gfk(gfk_name))

        # Add other fields
        for field in modelfields:
            # Skip fields that are part of a GFK we just added
            if field.name in self.gfk_constituent_fields:
                continue

            if not any(term in field.name.casefold() for term in excluded_terms):
                # Hack to filter created at / updated at fields to end of list
                if "_at" in field.name:
                    if field.name not in fields_at_end_of_list:
                        fields_at_end_of_list.append(field.name)
                elif field.name in self.relations:
                    self.list_display.append(linkify(field.name))
                else:
                    self.list_display.append(field.name)

                # Add boolean fields and foreign keys to list_filter by default
                if isinstance(
                    field,
                    models.BooleanField | models.DateTimeField | models.CharField,
                ):
                    self.list_filter.append(field.name)

        # Add properties to list_display
        for prop_name in self.properties:
            if not any(term in prop_name.casefold() for term in excluded_terms):
                # Only add properties that aren't already in the list
                if prop_name not in self.list_display:
                    self.list_display.append(prop_name)

        # Add fields_at_end_of_list only if they're not already in list_display
        for field in fields_at_end_of_list:
            if field not in self.list_display:
                self.list_display.append(field)

        # Apply linkify reordering if enabled
        if app_settings.REORDER_LINKIFY_FIELDS:
            self.list_display = reorder_list_display_to_avoid_linkify_first(self.list_display)

        # Ensure export_as_csv action is available
        if not hasattr(self, "actions"):
            self.actions = []
        if not isinstance(self.actions, list):
            self.actions = list(self.actions)

        # Add export_as_csv action if it's not already there
        if hasattr(self, "export_as_csv") and "export_as_csv" not in self.actions:
            self.actions.append("export_as_csv")

        logger.debug(f"after set_changelist_fields, List display is {self.list_display}")
        logger.debug(f"list_filter is {self.list_filter}")


class AdminDefaultsMixin:
    """Sensible defaults for database queries in admin classes."""

    def __init__(self, model):
        # logger.info(f"Initializing AdminDefaultsMixin for {model.__name__}")
        self.paginator = TimeLimitedPaginator
        # self.list_select_related = True
        self.show_full_result_count = False  # Prevent slow COUNT(*) for "Show all" link


class ListAdmin(admin.ModelAdmin, ListAdminMixin, AdminDefaultsMixin, ExportCsvMixin):
    def __init__(self, model, admin_site):
        admin.ModelAdmin.__init__(self, model, admin_site)
        ListAdminMixin.__init__(self, model)
        AdminDefaultsMixin.__init__(self, model)


class PolymorphicParentListAdmin(PolymorphicParentModelAdmin, ListAdminMixin, AdminDefaultsMixin):
    def __init__(self, model, admin_site=None):
        self.base_model = model
        self.child_models = (model, *tuple(get_all_child_classes(model)))
        ListAdminMixin.__init__(self, model)
        PolymorphicParentModelAdmin.__init__(self, model=model, admin_site=admin_site)
        AdminDefaultsMixin.__init__(self, model)

    def get_child_models(self):
        """Return child models for this admin."""
        return self.child_models


class PolymorphicChildListAdmin(PolymorphicChildModelAdmin, ListAdminMixin, AdminDefaultsMixin):
    def __init__(self, model, admin_site):
        super().__init__(model=model, admin_site=admin_site)
        ListAdminMixin.__init__(self, model)
        AdminDefaultsMixin.__init__(self, model)
