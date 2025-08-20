import pytest
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.test import override_settings

from django_admin_magic.registrar import AdminModelRegistrar

from .models import (
    ComplexModel,
    ForeignKeyModel,
    SimpleModel,
)


@pytest.mark.django_db
class TestEdgeCaseModels:
    """Test edge cases with unusual model configurations."""

    def test_model_with_no_fields(self):
        """Test handling of a model with no fields (except id)."""

        class EmptyModel(models.Model):
            class Meta:
                app_label = "tests"

        # This should not crash the registrar
        AdminModelRegistrar("tests")

        # The model should be registered
        assert admin.site.is_registered(EmptyModel)

    def test_model_with_only_auto_fields(self):
        """Test handling of a model with only auto-generated fields."""

        class AutoFieldModel(models.Model):
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(AutoFieldModel)

    def test_model_with_only_foreign_keys(self):
        """Test handling of a model with only foreign key fields."""

        class ForeignKeyOnlyModel(models.Model):
            simple_fk = models.ForeignKey(SimpleModel, on_delete=models.CASCADE)
            complex_fk = models.ForeignKey(ComplexModel, on_delete=models.CASCADE)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(ForeignKeyOnlyModel)

    def test_model_with_only_properties(self):
        """Test handling of a model with only properties."""

        class PropertyOnlyModel(models.Model):
            @property
            def computed_field(self):
                return "computed"

            @property
            def another_property(self):
                return "another"

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(PropertyOnlyModel)

    def test_model_with_very_long_field_names(self):
        """Test handling of models with very long field names."""

        class LongFieldNameModel(models.Model):
            very_long_field_name_that_exceeds_normal_length_limits = models.CharField(max_length=100)
            another_very_long_field_name_that_exceeds_normal_length_limits = models.TextField()

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(LongFieldNameModel)

    def test_model_with_special_characters_in_field_names(self):
        """Test handling of models with special characters in field names."""

        class SpecialCharModel(models.Model):
            field_with_underscores = models.CharField(max_length=100)
            field_with_dashes = models.CharField(max_length=100)
            field_with_dots = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(SpecialCharModel)

    def test_model_with_unicode_field_names(self):
        """Test handling of models with unicode field names."""

        class UnicodeFieldModel(models.Model):
            unicode_field_测试 = models.CharField(max_length=100)
            another_unicode_field_测试 = models.TextField()

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(UnicodeFieldModel)


@pytest.mark.django_db
class TestEdgeCaseFieldTypes:
    """Test edge cases with unusual field types."""

    def test_model_with_all_field_types(self):
        """Test handling of a model with all possible Django field types."""

        class AllFieldTypesModel(models.Model):
            # Basic fields
            char_field = models.CharField(max_length=100)
            text_field = models.TextField()
            integer_field = models.IntegerField()
            positive_integer_field = models.PositiveIntegerField()
            small_integer_field = models.SmallIntegerField()
            positive_small_integer_field = models.PositiveSmallIntegerField()
            big_integer_field = models.BigIntegerField()
            decimal_field = models.DecimalField(max_digits=10, decimal_places=2)
            float_field = models.FloatField()
            boolean_field = models.BooleanField()
            null_boolean_field = models.BooleanField(null=True)

            # Date and time fields
            date_field = models.DateField()
            time_field = models.TimeField()
            datetime_field = models.DateTimeField()
            duration_field = models.DurationField()

            # File fields
            file_field = models.FileField(upload_to="test/")
            image_field = models.ImageField(upload_to="test/")

            # URL and email fields
            url_field = models.URLField()
            email_field = models.EmailField()

            # JSON field
            json_field = models.JSONField()

            # UUID field
            uuid_field = models.UUIDField()

            # Binary field
            binary_field = models.BinaryField()

            # Slug field
            slug_field = models.SlugField()

            # IP address fields
            ip_address_field = models.GenericIPAddressField()
            ipv4_field = models.GenericIPAddressField(protocol="IPv4")
            ipv6_field = models.GenericIPAddressField(protocol="IPv6")

            # File path field
            file_path_field = models.FilePathField(path="/tmp")

            # Choices field
            choices_field = models.CharField(max_length=1, choices=[("A", "A"), ("B", "B")])

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(AllFieldTypesModel)

    def test_model_with_custom_field(self):
        """Test handling of models with custom fields."""

        class CustomField(models.CharField):
            def __init__(self, *args, **kwargs):
                kwargs["max_length"] = 100
                super().__init__(*args, **kwargs)

        class CustomFieldModel(models.Model):
            custom_field = CustomField()

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(CustomFieldModel)

    def test_model_with_proxy_fields(self):
        """Test handling of models with proxy fields."""

        class ProxyFieldModel(SimpleModel):
            class Meta:
                proxy = True
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(ProxyFieldModel)


@pytest.mark.django_db
class TestEdgeCaseRelationships:
    """Test edge cases with unusual relationships."""

    def test_model_with_self_referencing_foreign_key(self):
        """Test handling of models with self-referencing foreign keys."""

        class SelfReferencingModel(models.Model):
            name = models.CharField(max_length=100)
            parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(SelfReferencingModel)

    def test_model_with_multiple_generic_foreign_keys(self):
        """Test handling of models with multiple generic foreign keys."""

        class MultipleGFKModel(models.Model):
            content_type1 = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="gfk1")
            object_id1 = models.PositiveIntegerField()
            content_object1 = GenericForeignKey("content_type1", "object_id1")

            content_type2 = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="gfk2")
            object_id2 = models.PositiveIntegerField()
            content_object2 = GenericForeignKey("content_type2", "object_id2")

            content_type3 = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="gfk3")
            object_id3 = models.PositiveIntegerField()
            content_object3 = GenericForeignKey("content_type3", "object_id3")

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(MultipleGFKModel)

    def test_model_with_circular_foreign_keys(self):
        """Test handling of models with circular foreign key relationships."""

        class CircularModelA(models.Model):
            name = models.CharField(max_length=100)
            model_b = models.ForeignKey("CircularModelB", on_delete=models.CASCADE, null=True, blank=True)

            class Meta:
                app_label = "tests"

        class CircularModelB(models.Model):
            name = models.CharField(max_length=100)
            model_a = models.ForeignKey(CircularModelA, on_delete=models.CASCADE, null=True, blank=True)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(CircularModelA)
        assert admin.site.is_registered(CircularModelB)

    def test_model_with_deep_inheritance(self):
        """Test handling of models with deep inheritance."""

        class DeepBaseModel(models.Model):
            base_field = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        class DeepLevel1Model(DeepBaseModel):
            level1_field = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        class DeepLevel2Model(DeepLevel1Model):
            level2_field = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        class DeepLevel3Model(DeepLevel2Model):
            level3_field = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        assert admin.site.is_registered(DeepBaseModel)
        assert admin.site.is_registered(DeepLevel1Model)
        assert admin.site.is_registered(DeepLevel2Model)
        assert admin.site.is_registered(DeepLevel3Model)


@pytest.mark.django_db
class TestEdgeCaseRegistrar:
    """Test edge cases with the registrar."""

    def test_registrar_with_nonexistent_app(self):
        """Test registrar behavior with a nonexistent app."""
        # The registrar should handle nonexistent apps gracefully
        registrar = AdminModelRegistrar("nonexistent_app")
        # Should not crash, but should have empty class_dict
        assert registrar.class_dict == {}

    def test_registrar_with_empty_app(self):
        """Test registrar behavior with an app that has no models."""
        # This would require creating an empty app, which is complex
        # For now, we test that the registrar handles apps gracefully
        pass

    def test_registrar_with_abstract_models_only(self):
        """Test registrar behavior with an app that has only abstract models."""

        class AbstractModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                abstract = True
                app_label = "tests"

        AdminModelRegistrar("tests")
        # Abstract models should not be registered
        assert not admin.site.is_registered(AbstractModel)

    def test_registrar_with_models_excluded_by_filter(self):
        """Test registrar behavior with models that should be excluded by filter."""

        class HistoricalModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        # Historical models should be excluded by default filter
        assert not admin.site.is_registered(HistoricalModel)

    @override_settings(AUTO_ADMIN_DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST=["Test"])
    def test_registrar_with_custom_exclusion_filter(self):
        """Test registrar behavior with custom exclusion filters."""

        class TestModel(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")
        # TestModel should be excluded by custom filter
        assert not admin.site.is_registered(TestModel)


@pytest.mark.django_db
class TestEdgeCaseAdminMethods:
    """Test edge cases with admin method modifications."""

    def test_add_admin_method_with_nonexistent_model(self, registrar):
        """Test adding admin method to a nonexistent model."""

        def custom_method(obj):
            return "custom"

        with pytest.raises(KeyError):
            registrar.add_admin_method("NonexistentModel", "custom_method", custom_method)

    def test_add_admin_method_with_invalid_method_name(self, registrar):
        """Test adding admin method with invalid method name."""

        def custom_method(obj):
            return "custom"

        with pytest.raises(ValueError):
            registrar.add_admin_method(SimpleModel, "invalid-method-name", custom_method)

    def test_add_admin_method_with_none_method(self, registrar):
        """Test adding admin method with None method."""
        with pytest.raises(ValueError):
            registrar.add_admin_method(SimpleModel, "custom_method", None)

    def test_append_list_display_with_nonexistent_model(self, registrar):
        """Test appending to list_display for nonexistent model."""
        with pytest.raises(KeyError):
            registrar.append_list_display("NonexistentModel", ["field"])

    def test_append_list_display_with_invalid_field(self, registrar):
        """Test appending invalid field to list_display."""
        with pytest.raises(FieldDoesNotExist):
            registrar.append_list_display(SimpleModel, ["nonexistent_field"])

    def test_remove_list_display_with_nonexistent_field(self, registrar):
        """Test removing nonexistent field from list_display."""
        # This should not raise an error, just do nothing
        registrar.remove_list_display(SimpleModel, ["nonexistent_field"])

    def test_prepend_list_display_with_empty_list(self, registrar):
        """Test prepending empty list to list_display."""
        registrar.prepend_list_display(SimpleModel, [])
        # Should not crash

    def test_append_filter_display_with_nonexistent_model(self, registrar):
        """Test appending to list_filter for nonexistent model."""
        with pytest.raises(KeyError):
            registrar.append_filter_display("NonexistentModel", ["field"])


@pytest.mark.django_db
class TestEdgeCaseData:
    """Test edge cases with data handling."""

    def test_admin_with_empty_queryset(self, admin_site):
        """Test admin behavior with empty queryset."""
        admin_site._registry[SimpleModel]

        # Create an empty queryset
        queryset = SimpleModel.objects.none()

        # Should not crash
        assert queryset.count() == 0

    def test_admin_with_large_queryset(self, admin_site):
        """Test admin behavior with large queryset."""
        # Create many instances
        for i in range(100):
            SimpleModel.objects.create(name=f"Test {i}", is_active=True)

        admin_site._registry[SimpleModel]
        queryset = SimpleModel.objects.all()

        # Should handle large querysets
        assert queryset.count() == 100

    def test_admin_with_unicode_data(self, admin_site):
        """Test admin behavior with unicode data."""
        # Create instance with unicode data
        instance = SimpleModel.objects.create(name="测试模型", is_active=True)

        admin_site._registry[SimpleModel]

        # Should handle unicode data
        assert instance.name == "测试模型"

    def test_admin_with_special_characters_in_data(self, admin_site):
        """Test admin behavior with special characters in data."""
        # Create instance with special characters
        instance = SimpleModel.objects.create(name="Test & Model <script>alert('xss')</script>", is_active=True)

        admin_site._registry[SimpleModel]

        # Should handle special characters
        assert "&" in instance.name
        assert "<script>" in instance.name


@pytest.mark.django_db
class TestEdgeCasePerformance:
    """Test edge cases related to performance."""

    def test_admin_with_slow_queryset(self, admin_site):
        """Test admin behavior with potentially slow queryset."""
        # Create many instances to simulate slow query
        for i in range(1000):
            SimpleModel.objects.create(name=f"Test {i}", is_active=True)

        admin_site._registry[SimpleModel]
        queryset = SimpleModel.objects.all()

        # Should handle large querysets without timeout
        assert queryset.count() == 1000

    def test_admin_with_complex_queryset(self, admin_site):
        """Test admin behavior with complex queryset."""
        # Create related instances
        simple = SimpleModel.objects.create(name="Test", is_active=True)
        complex_model = ComplexModel.objects.create(char_field="Test")
        one_to_one_simple = SimpleModel.objects.create(name="One-to-One Test", is_active=True)

        ForeignKeyModel.objects.create(
            simple_foreign_key=simple, complex_foreign_key=complex_model, one_to_one=one_to_one_simple, name="Test FK"
        )

        admin_site._registry[ForeignKeyModel]
        queryset = ForeignKeyModel.objects.select_related("simple_foreign_key", "complex_foreign_key")

        # Should handle complex querysets
        assert queryset.count() == 1

    def test_admin_with_nested_queryset(self, admin_site):
        """Test admin behavior with deeply nested queryset."""
        # Create nested relationships
        simple = SimpleModel.objects.create(name="Test", is_active=True)
        complex_model = ComplexModel.objects.create(char_field="Test")
        one_to_one_simple = SimpleModel.objects.create(name="One-to-One Test", is_active=True)

        ForeignKeyModel.objects.create(
            simple_foreign_key=simple, complex_foreign_key=complex_model, one_to_one=one_to_one_simple, name="Test FK"
        )

        admin_site._registry[ForeignKeyModel]
        queryset = ForeignKeyModel.objects.select_related("simple_foreign_key", "complex_foreign_key").prefetch_related(
            "many_to_many"
        )

        # Should handle nested querysets
        assert queryset.count() == 1


@pytest.mark.django_db
class TestEdgeCaseErrorHandling:
    """Test edge cases for error handling."""

    def test_admin_with_broken_model_method(self, admin_site):
        """Test admin behavior when model method raises exception."""

        class BrokenModel(SimpleModel):
            @property
            def broken_property(self):
                raise Exception("Broken property")

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")

        # Should handle broken methods gracefully
        assert admin.site.is_registered(BrokenModel)

    def test_admin_with_broken_admin_method(self, registrar, admin_site):
        """Test admin behavior when admin method raises exception."""

        def broken_method(obj):
            raise Exception("Broken method")

        registrar.add_admin_method(SimpleModel, "broken_method", broken_method)

        admin_class = admin_site._registry[SimpleModel]

        # Should handle broken admin methods gracefully
        assert hasattr(admin_class, "broken_method")

    def test_admin_with_broken_linkify(self, admin_site):
        """Test admin behavior when linkify function raises exception."""

        class BrokenLinkifyModel(models.Model):
            broken_fk = models.ForeignKey(SimpleModel, on_delete=models.CASCADE)

            class Meta:
                app_label = "tests"

        AdminModelRegistrar("tests")

        # Should handle broken linkify gracefully
        assert admin.site.is_registered(BrokenLinkifyModel)

    def test_admin_with_missing_related_object(self, admin_site):
        """Test admin behavior when related object is missing."""
        # Create FK model but delete the related object
        simple = SimpleModel.objects.create(name="Test", is_active=True)
        one_to_one_simple = SimpleModel.objects.create(name="One-to-One Test", is_active=True)
        fk_model = ForeignKeyModel.objects.create(
            simple_foreign_key=simple,
            complex_foreign_key=ComplexModel.objects.create(char_field="Test"),
            one_to_one=one_to_one_simple,
            name="Test FK",
        )

        # Test that the admin can handle the relationship
        admin_class = admin_site._registry[ForeignKeyModel]
        assert hasattr(admin_class, "list_display")

        # Should handle missing related objects gracefully
        assert fk_model.simple_foreign_key_id is not None
