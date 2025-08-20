import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from .models import (
    ComplexModel,
    ForeignKeyModel,
    GenericForeignKeyModel,
    ModelWithCustomManager,
    ModelWithProperties,
    ModelWithSearchVector,
    PolymorphicChildA,
    PolymorphicChildB,
    PolymorphicParent,
    SimpleModel,
)


@pytest.mark.django_db
class TestAdminIntegration:
    """Integration tests for the complete Django Auto Admin workflow."""

    def test_admin_site_registration(self, admin_site):
        """Test that all models are properly registered with the admin site."""
        # Check that all our test models are registered
        registered_models = admin_site._registry.keys()

        assert SimpleModel in registered_models
        assert ComplexModel in registered_models
        assert ForeignKeyModel in registered_models
        assert GenericForeignKeyModel in registered_models
        assert PolymorphicParent in registered_models
        assert PolymorphicChildA in registered_models
        assert PolymorphicChildB in registered_models
        assert ModelWithProperties in registered_models
        assert ModelWithSearchVector in registered_models
        assert ModelWithCustomManager in registered_models

    def test_admin_list_views_load(self, admin_site):
        """Test that admin list views are properly configured."""
        # Test that admin classes are properly configured for each model
        models_to_test = [
            SimpleModel,
            ComplexModel,
            ForeignKeyModel,
            GenericForeignKeyModel,
            PolymorphicParent,
            ModelWithProperties,
            ModelWithSearchVector,
            ModelWithCustomManager,
        ]

        for model in models_to_test:
            model_admin = admin_site._registry[model]
            # Test that the admin class has the required attributes
            assert hasattr(model_admin, "list_display")
            assert hasattr(model_admin, "list_filter")
            assert hasattr(model_admin, "search_fields")
            # Test that the admin class can be instantiated
            assert model_admin is not None

    def test_admin_change_views_load(self, admin_site, simple_model_instance):
        """Test that admin change views are properly configured."""
        # Test that the admin class has the required attributes for change views
        admin_class = admin_site._registry[SimpleModel]
        assert hasattr(admin_class, "fields")
        assert hasattr(admin_class, "fieldsets")
        assert hasattr(admin_class, "readonly_fields")
        # Test that the admin class can handle the model instance
        assert admin_class.model == SimpleModel

    def test_admin_add_views_load(self, admin_site):
        """Test that admin add views are properly configured."""
        # Test that the admin class has the required attributes for add views
        admin_class = admin_site._registry[SimpleModel]
        assert hasattr(admin_class, "add_form_template")
        assert hasattr(admin_class, "change_form_template")
        # Test that the admin class can handle model creation
        assert admin_class.model == SimpleModel

    def test_list_display_functionality(self, admin_site, simple_model_instance):
        """Test that list_display fields work correctly in admin."""
        admin_class = admin_site._registry[SimpleModel]

        # Check that list_display contains expected fields
        assert "name" in admin_class.list_display
        assert "is_active" in admin_class.list_display
        assert "created_at" in admin_class.list_display

        # Test that the fields can be accessed on model instances
        assert hasattr(simple_model_instance, "name")
        assert hasattr(simple_model_instance, "is_active")
        assert hasattr(simple_model_instance, "created_at")

    def test_list_filter_functionality(self, admin_site):
        """Test that list_filter fields work correctly in admin."""
        admin_class = admin_site._registry[SimpleModel]

        # Check that list_filter contains expected fields
        assert "is_active" in admin_class.list_filter
        assert "created_at" in admin_class.list_filter

    def test_search_fields_functionality(self, admin_site, model_with_search_vector_instance):
        """Test that search_fields work correctly in admin."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        # Check that search_vector is in search_fields
        assert "search_vector" in admin_class.search_fields

    def test_readonly_fields_functionality(self, admin_site, model_with_search_vector_instance):
        """Test that readonly_fields work correctly in admin."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        # Check that search_vector is in readonly_fields
        assert "search_vector" in admin_class.readonly_fields

    def test_foreign_key_linkification(self, admin_site, foreign_key_model_instance):
        """Test that foreign key fields are properly linkified."""
        admin_class = admin_site._registry[ForeignKeyModel]

        # Check that foreign key fields are linkified
        list_display = admin_class.list_display

        # Find linkified foreign key fields
        linkified_fields = [field for field in list_display if callable(field)]

        # Should have at least one linkified field (the foreign key)
        assert len(linkified_fields) >= 1

    def test_generic_foreign_key_linkification(self, admin_site, generic_foreign_key_model_instance):
        """Test that generic foreign key fields are properly linkified."""
        admin_class = admin_site._registry[GenericForeignKeyModel]

        # Check that generic foreign key fields are linkified
        list_display = admin_class.list_display

        # Find linkified generic foreign key fields
        linkified_fields = [field for field in list_display if callable(field)]

        # Should have at least one linkified field (the generic foreign key)
        assert len(linkified_fields) >= 1

    def test_linkify_reordering_applied(self, admin_site, foreign_key_model_instance):
        """Test that linkify reordering is applied during admin registration."""
        admin_class = admin_site._registry[ForeignKeyModel]
        list_display = admin_class.list_display

        # Check that the first field is not a linkify function
        from django_admin_magic.utils import is_linkify_function

        if len(list_display) > 0:
            first_field = list_display[0]
            # The first field should not be a linkify function
            assert not is_linkify_function(first_field), f"First field {first_field} should not be a linkify function"

        # Check that linkify functions are present but not first
        linkified_fields = [field for field in list_display if is_linkify_function(field)]
        if linkified_fields:
            # At least one linkify field should exist
            assert len(linkified_fields) >= 1
            # The first linkify field should not be at index 0
            first_linkify_index = next(i for i, field in enumerate(list_display) if is_linkify_function(field))
            assert first_linkify_index > 0, "First linkify field should not be at index 0"

    def test_property_detection(self, admin_site, model_with_properties_instance):
        """Test that model properties are detected and included in list_display."""
        admin_class = admin_site._registry[ModelWithProperties]

        # Check that properties are in list_display
        assert "full_name" in admin_class.list_display
        assert "is_adult" in admin_class.list_display
        assert "status" in admin_class.list_display

        # Test that properties work correctly
        assert model_with_properties_instance.full_name == "John Doe"
        assert model_with_properties_instance.is_adult is True
        assert model_with_properties_instance.status == "Adult"

    def test_polymorphic_model_inheritance(self, admin_site):
        """Test that polymorphic models are handled correctly."""
        # Check that polymorphic parent admin has get_child_models method
        parent_admin = admin_site._registry[PolymorphicParent]
        assert hasattr(parent_admin, "get_child_models")

        # Check that child models are included
        child_models = parent_admin.get_child_models()
        assert PolymorphicParent in child_models
        assert PolymorphicChildA in child_models
        assert PolymorphicChildB in child_models

    def test_paginator_functionality(self, admin_site):
        """Test that the TimeLimitedPaginator is used."""
        admin_class = admin_site._registry[SimpleModel]

        from django_admin_magic.utils import TimeLimitedPaginator

        assert admin_class.paginator == TimeLimitedPaginator

    def test_show_full_result_count_setting(self, admin_site):
        """Test that show_full_result_count is set to False."""
        admin_class = admin_site._registry[SimpleModel]

        assert admin_class.show_full_result_count is False

    def test_list_select_related_setting(self, admin_site):
        """Test that list_select_related is set correctly."""
        admin_class = admin_site._registry[SimpleModel]

        # Should be True by default for better performance
        assert admin_class.list_select_related is True

    def test_excluded_terms_respected(self, admin_site):
        """Test that excluded terms are not included in list_display."""
        admin_class = admin_site._registry[SimpleModel]

        excluded_terms = ["_ptr", "uuid", "poly", "baseclass", "basemodel", "histo", "pk", "id", "search"]

        for term in excluded_terms:
            # Check that no field contains excluded terms
            for field in admin_class.list_display:
                if isinstance(field, str):
                    assert term not in field.lower()

    def test_timestamp_fields_at_end(self, admin_site):
        """Test that timestamp fields are placed at the end of list_display."""
        admin_class = admin_site._registry[SimpleModel]

        # Find timestamp fields
        timestamp_fields = [field for field in admin_class.list_display if "_at" in field]

        # Check that timestamp fields are at the end
        for timestamp_field in timestamp_fields:
            field_index = admin_class.list_display.index(timestamp_field)
            # Should be in the last few positions
            assert field_index >= len(admin_class.list_display) - len(timestamp_fields)


@pytest.mark.django_db
class TestAdminActions:
    """Test admin actions functionality."""

    def test_export_csv_action(self, admin_site, simple_model_instance):
        """Test that the export CSV action is available."""
        admin_class = admin_site._registry[SimpleModel]

        # Check that export_as_csv action is available
        assert hasattr(admin_class, "export_as_csv")
        assert "export_as_csv" in admin_class.actions

    def test_export_csv_functionality(self, admin_site, simple_model_instance):
        """Test that the export CSV action works correctly."""
        user = User.objects.create_superuser(username="admin", email="admin@example.com", password="password")

        client = Client()
        client.force_login(user)

        # Get the changelist URL
        changelist_url = reverse(f"admin:{SimpleModel._meta.app_label}_{SimpleModel._meta.model_name}_changelist")

        # Post to the changelist with export action
        response = client.post(
            changelist_url,
            {
                "action": "export_as_csv",
                "_selected_action": [simple_model_instance.pk],
            },
        )

        # Should return a CSV response
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert "attachment" in response["Content-Disposition"]


@pytest.mark.django_db
class TestAdminPerformance:
    """Test admin performance optimizations."""

    def test_time_limited_paginator(self, admin_site):
        """Test that TimeLimitedPaginator is used for performance."""
        admin_class = admin_site._registry[SimpleModel]

        from django_admin_magic.utils import TimeLimitedPaginator

        assert admin_class.paginator == TimeLimitedPaginator

    def test_list_select_related_performance(self, admin_site):
        """Test that list_select_related is enabled for performance."""
        admin_class = admin_site._registry[SimpleModel]

        assert admin_class.list_select_related is True

    def test_show_full_result_count_performance(self, admin_site):
        """Test that show_full_result_count is disabled for performance."""
        admin_class = admin_site._registry[SimpleModel]

        assert admin_class.show_full_result_count is False


@pytest.mark.django_db
class TestAdminCustomization:
    """Test admin customization capabilities."""

    def test_custom_admin_methods(self, registrar, admin_site):
        """Test adding custom admin methods."""

        def custom_display(obj):
            return f"Custom: {obj.name}"

        registrar.add_admin_method(SimpleModel, "custom_display", custom_display, short_description="Custom Display")

        admin_class = admin_site._registry[SimpleModel]
        assert hasattr(admin_class, "custom_display")
        assert admin_class.custom_display.short_description == "Custom Display"

    def test_custom_admin_actions(self, registrar, admin_site):
        """Test adding custom admin actions."""

        def custom_action(modeladmin, request, queryset):
            queryset.update(is_active=False)

        registrar.add_admin_method(
            SimpleModel, "custom_action", custom_action, short_description="Custom Action", is_action=True
        )

        admin_class = admin_site._registry[SimpleModel]
        # Check that the action function is in the actions list
        action_functions = [action for action in admin_class.actions if callable(action)]
        assert len(action_functions) >= 1, "At least one action function should be present"
        # Check that the custom_action method exists on the admin class
        assert hasattr(admin_class, "custom_action")

    def test_list_display_modification(self, registrar, admin_site):
        """Test modifying list_display after registration."""
        admin_class = admin_site._registry[SimpleModel]
        original_length = len(admin_class.list_display)

        # Append a field that doesn't exist yet
        registrar.append_list_display(SimpleModel, ["name"])  # This should be a no-op since it exists
        assert len(admin_class.list_display) == original_length
        assert "name" in admin_class.list_display

        # Prepend a field that doesn't exist yet
        registrar.prepend_list_display(SimpleModel, "name")  # This should move it to the front
        assert admin_class.list_display[0] == "name"

        # Remove a field
        registrar.remove_list_display(SimpleModel, ["name"])
        assert "name" not in admin_class.list_display

    def test_list_filter_modification(self, registrar, admin_site):
        """Test modifying list_filter after registration."""
        admin_class = admin_site._registry[SimpleModel]
        original_length = len(admin_class.list_filter)

        registrar.append_filter_display(SimpleModel, ["is_active"])  # This should be a no-op since it exists
        assert len(admin_class.list_filter) == original_length
        assert "is_active" in admin_class.list_filter

    def test_search_fields_modification(self, registrar, admin_site):
        """Test modifying search_fields after registration."""
        admin_class = admin_site._registry[SimpleModel]

        registrar.add_search_fields(SimpleModel, ["custom_search"])
        assert "custom_search" in admin_class.search_fields

    def test_list_select_related_modification(self, registrar, admin_site):
        """Test modifying list_select_related after registration."""
        admin_class = admin_site._registry[SimpleModel]

        registrar.update_list_select_related(SimpleModel, ["related_field"])
        assert admin_class.list_select_related == ["related_field"]
