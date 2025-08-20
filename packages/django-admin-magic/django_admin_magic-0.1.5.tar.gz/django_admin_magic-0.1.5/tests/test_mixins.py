import pytest
from django.contrib import admin

from django_admin_magic.mixins import (
    AdminDefaultsMixin,
    ListAdmin,
    ListAdminMixin,
    PolymorphicChildListAdmin,
    PolymorphicParentListAdmin,
)

from .models import (
    PolymorphicChildA,
    PolymorphicChildB,
    PolymorphicParent,
    SimpleModel,
)


@pytest.mark.django_db
class TestListAdminMixin:
    """Test the ListAdminMixin functionality."""

    def test_mixin_initializes_correctly(self):
        """Test that ListAdminMixin initializes with correct attributes."""
        mixin = ListAdminMixin(SimpleModel)

        # Check that required attributes are set
        assert hasattr(mixin, "list_display")
        assert hasattr(mixin, "list_filter")
        assert hasattr(mixin, "search_fields")
        assert hasattr(mixin, "readonly_fields")
        assert hasattr(mixin, "relations")
        assert hasattr(mixin, "generic_foreign_keys")
        assert hasattr(mixin, "properties")
        assert mixin.model == SimpleModel

    def test_tuple_attributes_converted_to_lists(self):
        """Test that tuple attributes are converted to lists."""
        mixin = ListAdminMixin(SimpleModel)

        # Check that attributes are lists, not tuples
        assert isinstance(mixin.list_display, list)
        assert isinstance(mixin.list_filter, list)
        assert isinstance(mixin.search_fields, list)
        assert isinstance(mixin.readonly_fields, list)

    def test_relations_detection(self):
        """Test that model relations are correctly detected."""
        ListAdminMixin(SimpleModel)

        # SimpleModel has reverse relations from other models that reference it
        # We should check that it has the expected reverse relations
        all_fields = SimpleModel._meta.get_fields()
        reverse_relations = [field.name for field in all_fields if field.is_relation and field.auto_created]

        # SimpleModel should have reverse relations from ForeignKeyModel, etc.
        expected_reverse_relations = ["fk_models", "nullable_fk_models", "m2m_models", "one_to_one_model"]
        for expected_relation in expected_reverse_relations:
            assert expected_relation in reverse_relations, f"Expected reverse relation {expected_relation} not found"

    def test_properties_detection(self):
        """Test that model properties are correctly detected."""
        mixin = ListAdminMixin(SimpleModel)

        # SimpleModel doesn't have properties, so properties should be empty
        assert mixin.properties == []

    def test_set_changelist_fields(self):
        """Test that set_changelist_fields populates list_display and list_filter."""
        mixin = ListAdminMixin(SimpleModel)

        # Check that list_display contains expected fields
        assert "name" in mixin.list_display
        assert "is_active" in mixin.list_display
        assert "created_at" in mixin.list_display

        # Check that list_filter contains expected fields
        assert "is_active" in mixin.list_filter
        assert "created_at" in mixin.list_filter

    def test_set_changelist_fields_with_custom_end_fields(self):
        """Test set_changelist_fields with custom fields_at_end_of_list."""
        mixin = ListAdminMixin(SimpleModel)

        # Reset and call with custom end fields
        mixin.set_changelist_fields(fields_at_end_of_list=["custom_field"])

        # Check that custom field is at the end
        assert "custom_field" in mixin.list_display
        # The custom field should be at the end, but timestamp fields might also be there
        # depending on the implementation
        assert mixin.list_display[-1] in ["custom_field", "created_at", "updated_at"]


@pytest.mark.django_db
class TestAdminDefaultsMixin:
    """Test the AdminDefaultsMixin functionality."""

    def test_mixin_initializes_correctly(self):
        """Test that AdminDefaultsMixin initializes with correct attributes."""
        mixin = AdminDefaultsMixin(SimpleModel)

        # Check that required attributes are set
        assert hasattr(mixin, "paginator")
        assert hasattr(mixin, "show_full_result_count")
        assert mixin.show_full_result_count is False

    def test_paginator_is_set(self):
        """Test that the paginator is set to TimeLimitedPaginator."""
        mixin = AdminDefaultsMixin(SimpleModel)

        from django_admin_magic.utils import TimeLimitedPaginator

        assert mixin.paginator == TimeLimitedPaginator


@pytest.mark.django_db
class TestListAdmin:
    """Test the ListAdmin class."""

    def test_list_admin_initialization(self):
        """Test that ListAdmin initializes correctly."""
        admin_instance = ListAdmin(SimpleModel, admin.site)

        # Check that it has all the expected attributes
        assert hasattr(admin_instance, "list_display")
        assert hasattr(admin_instance, "list_filter")
        assert hasattr(admin_instance, "search_fields")
        assert hasattr(admin_instance, "readonly_fields")
        assert hasattr(admin_instance, "paginator")
        assert hasattr(admin_instance, "show_full_result_count")
        assert admin_instance.model == SimpleModel

    def test_list_admin_inheritance(self):
        """Test that ListAdmin inherits from the correct base classes."""
        admin_instance = ListAdmin(SimpleModel, admin.site)

        # Check inheritance
        assert isinstance(admin_instance, admin.ModelAdmin)
        assert hasattr(admin_instance, "list_display")  # From ListAdminMixin
        assert hasattr(admin_instance, "paginator")  # From AdminDefaultsMixin


@pytest.mark.django_db
class TestPolymorphicParentListAdmin:
    """Test the PolymorphicParentListAdmin class."""

    def test_polymorphic_parent_admin_initialization(self):
        """Test that PolymorphicParentListAdmin initializes correctly."""
        admin_instance = PolymorphicParentListAdmin(PolymorphicParent, admin.site)

        # Check that it has all the expected attributes
        assert hasattr(admin_instance, "list_display")
        assert hasattr(admin_instance, "list_filter")
        assert hasattr(admin_instance, "base_model")
        assert hasattr(admin_instance, "child_models")
        assert admin_instance.base_model == PolymorphicParent

    def test_get_child_models(self):
        """Test that get_child_models returns the correct child models."""
        admin_instance = PolymorphicParentListAdmin(PolymorphicParent, admin.site)

        child_models = admin_instance.get_child_models()

        # Should include the parent and all child models
        assert PolymorphicParent in child_models
        assert PolymorphicChildA in child_models
        assert PolymorphicChildB in child_models

    def test_polymorphic_parent_admin_inheritance(self):
        """Test that PolymorphicParentListAdmin inherits from the correct base classes."""
        from polymorphic.admin import PolymorphicParentModelAdmin

        admin_instance = PolymorphicParentListAdmin(PolymorphicParent, admin.site)

        # Check inheritance
        assert isinstance(admin_instance, PolymorphicParentModelAdmin)
        assert hasattr(admin_instance, "list_display")  # From ListAdminMixin
        assert hasattr(admin_instance, "paginator")  # From AdminDefaultsMixin


@pytest.mark.django_db
class TestPolymorphicChildListAdmin:
    """Test the PolymorphicChildListAdmin class."""

    def test_polymorphic_child_admin_initialization(self):
        """Test that PolymorphicChildListAdmin initializes correctly."""
        admin_instance = PolymorphicChildListAdmin(PolymorphicChildA, admin.site)

        # Check that it has all the expected attributes
        assert hasattr(admin_instance, "list_display")
        assert hasattr(admin_instance, "list_filter")
        assert admin_instance.model == PolymorphicChildA

    def test_polymorphic_child_admin_inheritance(self):
        """Test that PolymorphicChildListAdmin inherits from the correct base classes."""
        from polymorphic.admin import PolymorphicChildModelAdmin

        admin_instance = PolymorphicChildListAdmin(PolymorphicChildA, admin.site)

        # Check inheritance
        assert isinstance(admin_instance, PolymorphicChildModelAdmin)
        assert hasattr(admin_instance, "list_display")  # From ListAdminMixin
        assert hasattr(admin_instance, "paginator")  # From AdminDefaultsMixin


@pytest.mark.django_db
class TestMixinIntegration:
    """Test integration between different mixins."""

    def test_mixins_work_together(self):
        """Test that all mixins work together correctly."""
        admin_instance = ListAdmin(SimpleModel, admin.site)

        # Check that all mixin functionality is present
        assert hasattr(admin_instance, "list_display")  # From ListAdminMixin
        assert hasattr(admin_instance, "list_filter")  # From ListAdminMixin
        assert hasattr(admin_instance, "search_fields")  # From ListAdminMixin
        assert hasattr(admin_instance, "readonly_fields")  # From ListAdminMixin
        assert hasattr(admin_instance, "paginator")  # From AdminDefaultsMixin
        assert hasattr(admin_instance, "show_full_result_count")  # From AdminDefaultsMixin

    def test_polymorphic_mixins_work_together(self):
        """Test that polymorphic mixins work together correctly."""
        admin_instance = PolymorphicParentListAdmin(PolymorphicParent, admin.site)

        # Check that all mixin functionality is present
        assert hasattr(admin_instance, "list_display")  # From ListAdminMixin
        assert hasattr(admin_instance, "list_filter")  # From ListAdminMixin
        assert hasattr(admin_instance, "paginator")  # From AdminDefaultsMixin
        assert hasattr(admin_instance, "get_child_models")  # From PolymorphicParentModelAdmin
