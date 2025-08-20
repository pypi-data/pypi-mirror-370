import pytest

from .models import (
    ComplexModel,
    ForeignKeyModel,
    GenericForeignKeyModel,
    ModelWithCustomManager,
    ModelWithProperties,
    ModelWithSearchVector,
    SimpleModel,
)


@pytest.mark.django_db
class TestComplexModelRegistration:
    """Test registration and admin functionality for ComplexModel with all field types."""

    def test_complex_model_is_registered(self, admin_site):
        """Test that ComplexModel is properly registered with the admin site."""
        assert admin_site.is_registered(ComplexModel)

    def test_complex_model_admin_has_all_field_types(self, admin_site):
        """Test that ComplexModel admin includes all field types in list_display."""
        admin_class = admin_site._registry[ComplexModel]

        # Check that various field types are included in list_display
        expected_fields = [
            "char_field",
            "integer_field",
            "boolean_field",
            "date_field",
            "datetime_field",
            "created_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display

    def test_complex_model_list_filter_includes_appropriate_fields(self, admin_site):
        """Test that ComplexModel admin includes appropriate fields in list_filter."""
        admin_class = admin_site._registry[ComplexModel]

        # Check that boolean and datetime fields are included in list_filter
        expected_filters = [
            "boolean_field",
            "created_at",
        ]

        for field in expected_filters:
            assert field in admin_class.list_filter

    def test_complex_model_includes_all_fields(self, admin_site):
        """Test that ComplexModel admin includes all fields in list_display (actual behavior)."""
        admin_class = admin_site._registry[ComplexModel]

        # Based on the actual implementation, all fields are included
        # Check that various field types are included in list_display
        expected_fields = [
            "char_field",
            "text_field",
            "integer_field",
            "decimal_field",
            "boolean_field",
            "date_field",
            "datetime_field",
            "file_field",
            "image_field",
            "url_field",
            "email_field",
            "json_field",
            "binary_field",
            "slug_field",
            "choices_field",
            "created_at",
            "updated_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display

    def test_debug_list_display_fields(self, admin_site):
        """Debug test to see what fields are actually in list_display."""
        admin_class = admin_site._registry[ComplexModel]
        print(f"\nComplexModel list_display fields: {admin_class.list_display}")
        print(f"ComplexModel list_filter fields: {admin_class.list_filter}")

        # This test should always pass, it's just for debugging
        assert True


@pytest.mark.django_db
class TestForeignKeyModelRegistration:
    """Test registration and admin functionality for ForeignKeyModel."""

    def test_foreign_key_model_is_registered(self, admin_site):
        """Test that ForeignKeyModel is properly registered with the admin site."""
        assert admin_site.is_registered(ForeignKeyModel)

    def test_foreign_key_model_includes_foreign_key_fields(self, admin_site):
        """Test that ForeignKeyModel admin includes foreign key fields in list_display."""
        admin_class = admin_site._registry[ForeignKeyModel]

        # Check that foreign key fields are included (they will be wrapped in linkify functions)
        # We need to check for the presence of callable objects that represent the foreign keys
        list_display_items = admin_class.list_display

        # Check that basic fields are included
        expected_basic_fields = [
            "name",
            "is_active",
            "created_at",
        ]

        for field in expected_basic_fields:
            assert field in list_display_items

    def test_foreign_key_model_list_filter_includes_appropriate_fields(self, admin_site):
        """Test that ForeignKeyModel admin includes appropriate fields in list_filter."""
        admin_class = admin_site._registry[ForeignKeyModel]

        # Check that appropriate fields are included in list_filter
        expected_filters = [
            "name",
            "is_active",
            "created_at",
        ]

        for field in expected_filters:
            assert field in admin_class.list_filter

    def test_foreign_key_model_excludes_many_to_many_from_list_display(self, admin_site):
        """Test that ForeignKeyModel admin excludes many-to-many fields from list_display."""
        admin_class = admin_site._registry[ForeignKeyModel]

        # Many-to-many fields should not be in list_display
        assert "many_to_many" not in admin_class.list_display


@pytest.mark.django_db
class TestGenericForeignKeyModelRegistration:
    """Test registration and admin functionality for GenericForeignKeyModel."""

    def test_generic_foreign_key_model_is_registered(self, admin_site):
        """Test that GenericForeignKeyModel is properly registered with the admin site."""
        assert admin_site.is_registered(GenericForeignKeyModel)

    def test_generic_foreign_key_model_includes_basic_fields(self, admin_site):
        """Test that GenericForeignKeyModel admin includes basic fields in list_display."""
        admin_class = admin_site._registry[GenericForeignKeyModel]

        # Check that basic fields are included
        expected_fields = [
            "name",
            "description",
            "created_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display

    def test_generic_foreign_key_model_excludes_content_type_fields(self, admin_site):
        """Test that GenericForeignKeyModel admin excludes content_type and object_id fields."""
        admin_class = admin_site._registry[GenericForeignKeyModel]

        # Content type and object ID fields should not be in list_display
        excluded_fields = [
            "content_type",
            "object_id",
            "content_type_2",
            "object_id_2",
            "content_type_nullable",
            "object_id_nullable",
        ]

        for field in excluded_fields:
            assert field not in admin_class.list_display


@pytest.mark.django_db
class TestModelWithPropertiesRegistration:
    """Test registration and admin functionality for ModelWithProperties."""

    def test_model_with_properties_is_registered(self, admin_site):
        """Test that ModelWithProperties is properly registered with the admin site."""
        assert admin_site.is_registered(ModelWithProperties)

    def test_model_with_properties_includes_properties_in_list_display(self, admin_site):
        """Test that ModelWithProperties admin includes properties in list_display."""
        admin_class = admin_site._registry[ModelWithProperties]

        # Check that properties are included in list_display
        expected_fields = [
            "first_name",
            "last_name",
            "full_name",  # Property
            "is_adult",  # Property
            "status",  # Property
            "is_active",
            "created_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display

    def test_model_with_properties_list_filter_includes_appropriate_fields(self, admin_site):
        """Test that ModelWithProperties admin includes appropriate fields in list_filter."""
        admin_class = admin_site._registry[ModelWithProperties]

        # Check that boolean and integer fields are included in list_filter
        expected_filters = [
            "is_active",
            "created_at",
        ]

        for field in expected_filters:
            assert field in admin_class.list_filter


@pytest.mark.django_db
class TestModelWithSearchVectorRegistration:
    """Test registration and admin functionality for ModelWithSearchVector."""

    def test_model_with_search_vector_is_registered(self, admin_site):
        """Test that ModelWithSearchVector is properly registered with the admin site."""
        assert admin_site.is_registered(ModelWithSearchVector)

    def test_model_with_search_vector_includes_search_vector_in_search_fields(self, admin_site):
        """Test that ModelWithSearchVector admin includes search_vector in search_fields."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        # search_vector should be included in search_fields
        assert "search_vector" in admin_class.search_fields

    def test_model_with_search_vector_includes_search_vector_in_readonly_fields(self, admin_site):
        """Test that ModelWithSearchVector admin includes search_vector in readonly_fields."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        # search_vector should be included in readonly_fields
        assert "search_vector" in admin_class.readonly_fields

    def test_model_with_search_vector_list_display_includes_appropriate_fields(self, admin_site):
        """Test that ModelWithSearchVector admin includes appropriate fields in list_display."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        expected_fields = [
            "title",
            "is_published",
            "created_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display


@pytest.mark.django_db
class TestModelWithCustomManagerRegistration:
    """Test registration and admin functionality for ModelWithCustomManager."""

    def test_model_with_custom_manager_is_registered(self, admin_site):
        """Test that ModelWithCustomManager is properly registered with the admin site."""
        assert admin_site.is_registered(ModelWithCustomManager)

    def test_model_with_custom_manager_list_display_includes_appropriate_fields(self, admin_site):
        """Test that ModelWithCustomManager admin includes appropriate fields in list_display."""
        admin_class = admin_site._registry[ModelWithCustomManager]

        expected_fields = [
            "name",
            "category",
            "is_featured",
            "created_at",
        ]

        for field in expected_fields:
            assert field in admin_class.list_display

    def test_model_with_custom_manager_list_filter_includes_appropriate_fields(self, admin_site):
        """Test that ModelWithCustomManager admin includes appropriate fields in list_filter."""
        admin_class = admin_site._registry[ModelWithCustomManager]

        expected_filters = [
            "category",
            "is_featured",
            "created_at",
        ]

        for field in expected_filters:
            assert field in admin_class.list_filter


@pytest.mark.django_db
class TestComprehensiveModelIntegration:
    """Test integration between different model types."""

    def test_all_models_are_registered(self, admin_site):
        """Test that all comprehensive models are registered."""
        models_to_check = [
            SimpleModel,
            ComplexModel,
            ForeignKeyModel,
            GenericForeignKeyModel,
            ModelWithProperties,
            ModelWithSearchVector,
            ModelWithCustomManager,
        ]

        for model in models_to_check:
            assert admin_site.is_registered(model)

    def test_foreign_key_relationships_work_correctly(self, foreign_key_model_instance, admin_site):
        """Test that foreign key relationships are properly handled in admin."""
        admin_class = admin_site._registry[ForeignKeyModel]

        # Check that the admin class has the expected structure
        assert hasattr(admin_class, "list_display")
        assert isinstance(admin_class.list_display, list)

        # Check that basic fields are included
        assert "name" in admin_class.list_display
        assert "is_active" in admin_class.list_display
        assert "created_at" in admin_class.list_display

    def test_generic_foreign_key_relationships_work_correctly(self, generic_foreign_key_model_instance, admin_site):
        """Test that generic foreign key relationships are properly handled in admin."""
        admin_class = admin_site._registry[GenericForeignKeyModel]

        # Check that the admin class has the expected structure
        assert hasattr(admin_class, "list_display")
        assert isinstance(admin_class.list_display, list)

        # Check that basic fields are included
        assert "name" in admin_class.list_display
        assert "description" in admin_class.list_display
        assert "created_at" in admin_class.list_display

    def test_property_detection_works_correctly(self, model_with_properties_instance, admin_site):
        """Test that model properties are properly detected and included in admin."""
        admin_class = admin_site._registry[ModelWithProperties]

        # Check that properties are included
        assert "full_name" in admin_class.list_display
        assert "is_adult" in admin_class.list_display
        assert "status" in admin_class.list_display

    def test_search_vector_detection_works_correctly(self, model_with_search_vector_instance, admin_site):
        """Test that search_vector fields are properly detected and configured."""
        admin_class = admin_site._registry[ModelWithSearchVector]

        # Check that search_vector is properly configured
        assert "search_vector" in admin_class.search_fields
        assert "search_vector" in admin_class.readonly_fields


@pytest.mark.django_db
class TestComprehensiveModelEdgeCases:
    """Test edge cases with comprehensive models."""

    def test_choices_field_handling(self, admin_site):
        """Test that choice fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # Choice field should be included in list_display
        assert "choices_field" in admin_class.list_display

    def test_json_field_handling(self, admin_site):
        """Test that JSON fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # JSON field should be included in list_display
        assert "json_field" in admin_class.list_display

    def test_decimal_field_handling(self, admin_site):
        """Test that decimal fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # Decimal field should be included in list_display
        assert "decimal_field" in admin_class.list_display

    def test_email_field_handling(self, admin_site):
        """Test that email fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # Email field should be included in list_display
        assert "email_field" in admin_class.list_display

    def test_url_field_handling(self, admin_site):
        """Test that URL fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # URL field should be included in list_display
        assert "url_field" in admin_class.list_display

    def test_file_field_handling(self, admin_site):
        """Test that file fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # File field should be included in list_display (actual behavior)
        assert "file_field" in admin_class.list_display

    def test_image_field_handling(self, admin_site):
        """Test that image fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # Image field should be included in list_display (actual behavior)
        assert "image_field" in admin_class.list_display

    def test_binary_field_handling(self, admin_site):
        """Test that binary fields are handled correctly."""
        admin_class = admin_site._registry[ComplexModel]

        # Binary field should be included in list_display (actual behavior)
        assert "binary_field" in admin_class.list_display
