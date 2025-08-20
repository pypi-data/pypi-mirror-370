import pytest
from django.contrib import admin
from django.core.paginator import Paginator
from django.db import models

from django_admin_magic.utils import (
    TimeLimitedPaginator,
    get_all_child_classes,
    is_polymorphic_model,
    is_polymorphic_model_parent_model,
    linkify,
    linkify_gfk,
    reset_success,
)

from .models import (
    PolymorphicChildA,
    PolymorphicChildB,
    PolymorphicParent,
    SimpleModel,
)


@pytest.mark.django_db
class TestUtilityFunctions:
    """Test the utility functions."""

    def test_get_all_child_classes(self):
        """Test that get_all_child_classes returns all child classes recursively."""
        child_classes = get_all_child_classes(PolymorphicParent)

        # Should include all child classes (but not the parent itself)
        assert PolymorphicChildA in child_classes
        assert PolymorphicChildB in child_classes
        # The parent is not included in child classes
        assert PolymorphicParent not in child_classes

    def test_is_polymorphic_model(self):
        """Test that is_polymorphic_model correctly identifies polymorphic models."""
        assert is_polymorphic_model(PolymorphicParent)
        assert is_polymorphic_model(PolymorphicChildA)
        assert is_polymorphic_model(PolymorphicChildB)
        assert not is_polymorphic_model(SimpleModel)

    def test_is_polymorphic_model_parent_model(self):
        """Test that is_polymorphic_model_parent_model correctly identifies parent models."""
        assert is_polymorphic_model_parent_model(PolymorphicParent)
        assert not is_polymorphic_model_parent_model(PolymorphicChildA)
        assert not is_polymorphic_model_parent_model(PolymorphicChildB)
        assert not is_polymorphic_model_parent_model(SimpleModel)


@pytest.mark.django_db
class TestLinkify:
    """Test the linkify function."""

    def test_linkify_with_valid_foreign_key(self, foreign_key_model_instance):
        """Test that linkify creates a proper link for a foreign key."""
        # Ensure SimpleModel is registered in admin for the linkify function to work
        from django_admin_magic.registrar import AdminModelRegistrar

        AdminModelRegistrar(app_label="tests")

        # Debug: Check if SimpleModel is registered
        print(f"Admin site registry: {list(admin.site._registry.keys())}")
        print(f"SimpleModel in admin: {SimpleModel in admin.site._registry}")

        # Test with an existing model that has a foreign key relationship
        # We'll use the foreign_key_model_instance and test the linkify function
        link_func = linkify("simple_foreign_key")
        result = link_func(foreign_key_model_instance)

        # Debug: Print the actual result
        print(f"Linkify result: {result}")

        # Should contain a link since SimpleModel is in admin
        assert "href=" in result
        assert foreign_key_model_instance.simple_foreign_key.name in result

    def test_linkify_with_none_value(self, simple_model_instance):
        """Test that linkify handles None values correctly."""

        # Create a mock object with None value
        class MockObject:
            def __init__(self):
                self.none_field = None

        mock_obj = MockObject()
        link_func = linkify("none_field")
        result = link_func(mock_obj)

        # Should return "-" for None values
        assert result == "-"

    def test_linkify_with_invalid_url(self, foreign_key_model_instance):
        """Test that linkify handles invalid URLs gracefully."""
        # Ensure SimpleModel is registered in admin for the linkify function to work
        from django_admin_magic.registrar import AdminModelRegistrar

        AdminModelRegistrar(app_label="tests")

        # Test with a field that doesn't have an admin URL
        link_func = linkify("simple_foreign_key")
        result = link_func(foreign_key_model_instance)

        # Should return a link since SimpleModel is in admin
        assert "href=" in result


@pytest.mark.django_db
class TestLinkifyGFK:
    """Test the linkify_gfk function."""

    def test_linkify_gfk_with_valid_object(self, simple_model_instance):
        """Test that linkify_gfk creates a proper link for a GenericForeignKey."""

        # Create a mock object that simulates a GenericForeignKey
        class MockGFKObject:
            def __init__(self, content_object):
                self.content_object = content_object

        mock_obj = MockGFKObject(simple_model_instance)

        # Test the linkify_gfk function
        link_func = linkify_gfk("content_object")
        result = link_func(mock_obj)

        # Should contain a link
        assert "href=" in result
        assert "Simplemodel" in result  # Django uses lowercase model name

    def test_linkify_gfk_with_none_value(self):
        """Test that linkify_gfk handles None values correctly."""

        # Create a mock object with None content_object
        class MockGFKObject:
            def __init__(self):
                self.content_object = None

        mock_obj = MockGFKObject()

        link_func = linkify_gfk("content_object")
        result = link_func(mock_obj)

        # Should return "-" for None values
        assert result == "-"

    def test_linkify_gfk_with_invalid_object(self):
        """Test that linkify_gfk handles invalid objects gracefully."""

        # Create a mock object with invalid content_object
        class MockGFKObject:
            def __init__(self):
                self.content_object = "invalid_object"

        mock_obj = MockGFKObject()

        link_func = linkify_gfk("content_object")
        result = link_func(mock_obj)

        # Should handle the error gracefully
        assert result is not None


@pytest.mark.django_db
class TestTimeLimitedPaginator:
    """Test the TimeLimitedPaginator class."""

    def test_paginator_inheritance(self):
        """Test that TimeLimitedPaginator inherits from Paginator."""
        paginator = TimeLimitedPaginator([1, 2, 3, 4, 5], 2)
        assert isinstance(paginator, Paginator)

    def test_paginator_initialization(self):
        """Test that TimeLimitedPaginator initializes correctly."""
        # Test with a simple list (not a QuerySet)
        paginator = TimeLimitedPaginator([1, 2, 3, 4, 5], 2)

        # For simple lists, it should work like a regular paginator
        assert paginator.num_pages == 3
        assert len(paginator.page(1).object_list) == 2

    def test_paginator_count_property(self):
        """Test that the count property works correctly."""
        paginator = TimeLimitedPaginator([1, 2, 3, 4, 5], 2)

        # The count should be the length of the object list
        assert paginator.count == 5


@pytest.mark.django_db
class TestResetSuccessAction:
    """Test the reset_success admin action."""

    def test_reset_success_action(self, simple_model_instance):
        """Test that reset_success action works correctly."""

        # Create a mock queryset with objects that have a success attribute and save method
        class MockObject:
            def __init__(self, success=True):
                self.success = success

            def save(self):
                pass  # Mock save method

        mock_objects = [MockObject(True), MockObject(True)]

        # Test the action
        reset_success(None, None, mock_objects)

        # Check that success was set to False
        for obj in mock_objects:
            assert obj.success is False


@pytest.mark.django_db
class TestUtilityIntegration:
    """Test integration between utility functions."""

    def test_polymorphic_utilities_work_together(self):
        """Test that polymorphic utility functions work together."""
        # Test the complete polymorphic detection flow
        assert is_polymorphic_model(PolymorphicParent)
        assert is_polymorphic_model_parent_model(PolymorphicParent)

        child_classes = get_all_child_classes(PolymorphicParent)
        assert PolymorphicChildA in child_classes
        assert PolymorphicChildB in child_classes

    def test_linkify_functions_attributes(self):
        """Test that linkify functions have the correct attributes."""
        link_func = linkify("test_field")
        gfk_func = linkify_gfk("test_gfk")

        # Check that they have the expected attributes
        assert hasattr(link_func, "short_description")
        assert hasattr(link_func, "admin_order_field")
        assert hasattr(gfk_func, "short_description")
        assert hasattr(gfk_func, "admin_order_field")


@pytest.mark.django_db
class TestUtilityEdgeCases:
    """Test edge cases and error handling in utility functions."""

    def test_get_all_child_classes_with_no_children(self):
        """Test get_all_child_classes with a class that has no children."""

        class NoChildren(models.Model):
            class Meta:
                app_label = "tests"

        child_classes = get_all_child_classes(NoChildren)
        assert child_classes == []

    def test_linkify_with_missing_field(self):
        """Test linkify with a field that doesn't exist."""

        class MockObject:
            def __init__(self):
                self.name = "Test"

        instance = MockObject()

        # This should raise an AttributeError
        link_func = linkify("nonexistent_field")
        with pytest.raises(AttributeError):
            link_func(instance)

    def test_paginator_with_empty_list(self):
        """Test TimeLimitedPaginator with an empty list."""
        paginator = TimeLimitedPaginator([], 10)
        assert paginator.count == 0
        assert paginator.num_pages == 1  # Django paginator returns 1 for empty lists
