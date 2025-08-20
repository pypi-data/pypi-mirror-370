import pytest
from django.contrib import admin

from .models import (
    PolymorphicChildA,
    PolymorphicChildB,
    PolymorphicParent,
    SimpleModel,
)


@pytest.mark.django_db
class TestBasicFunctionality:
    """Basic smoke tests to ensure the library works end-to-end."""

    def test_all_models_registered(self):
        """Test that all test models are registered with the admin site."""
        assert admin.site.is_registered(SimpleModel)
        assert admin.site.is_registered(PolymorphicParent)
        assert admin.site.is_registered(PolymorphicChildA)
        assert admin.site.is_registered(PolymorphicChildB)

    def test_admin_classes_have_basic_attributes(self):
        """Test that admin classes have the expected basic attributes."""
        simple_admin = admin.site._registry[SimpleModel]
        polymorphic_admin = admin.site._registry[PolymorphicParent]

        # Check basic attributes
        assert hasattr(simple_admin, "list_display")
        assert hasattr(simple_admin, "list_filter")
        assert hasattr(simple_admin, "search_fields")
        assert hasattr(simple_admin, "readonly_fields")

        # Check polymorphic-specific attributes
        assert hasattr(polymorphic_admin, "get_child_models")

    def test_list_display_contains_expected_fields(self):
        """Test that list_display contains the expected model fields."""
        admin_class = admin.site._registry[SimpleModel]

        # Check that basic fields are included
        assert "name" in admin_class.list_display
        assert "is_active" in admin_class.list_display
        assert "created_at" in admin_class.list_display

    def test_list_filter_contains_expected_fields(self):
        """Test that list_filter contains the expected model fields."""
        admin_class = admin.site._registry[SimpleModel]

        # Check that appropriate fields are included
        assert "is_active" in admin_class.list_filter
        assert "created_at" in admin_class.list_filter
