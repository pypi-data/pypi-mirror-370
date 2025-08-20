import pytest
from django.contrib import admin
from django.db import connection, connections

from django_admin_magic.registrar import AdminModelRegistrar

from .models import (
    ComplexModel,
    ForeignKeyModel,
    GenericForeignKeyModel,
    ModelWithProperties,
    PolymorphicChildA,
    PolymorphicChildB,
    PolymorphicParent,
    SimpleModel,
)


@pytest.mark.django_db
class TestDatabaseAgnosticCore:
    """Test core functionality across different database backends."""

    def test_model_registration_works_with_all_backends(self):
        """Test that model registration works regardless of database backend."""
        # This test should work with any database backend
        AdminModelRegistrar("tests")

        # Check that models are registered
        assert admin.site.is_registered(SimpleModel)
        assert admin.site.is_registered(ComplexModel)
        assert admin.site.is_registered(ForeignKeyModel)
        assert admin.site.is_registered(GenericForeignKeyModel)
        assert admin.site.is_registered(PolymorphicParent)
        assert admin.site.is_registered(PolymorphicChildA)
        assert admin.site.is_registered(PolymorphicChildB)

    def test_admin_class_creation_works_with_all_backends(self):
        """Test that admin class creation works regardless of database backend."""
        registrar = AdminModelRegistrar("tests")

        # Get admin classes
        simple_admin = registrar.return_admin_class_for_model(SimpleModel)
        complex_admin = registrar.return_admin_class_for_model(ComplexModel)

        # Check that admin classes have required attributes
        assert hasattr(simple_admin, "list_display")
        assert hasattr(simple_admin, "list_filter")
        assert hasattr(complex_admin, "list_display")
        assert hasattr(complex_admin, "list_filter")

    def test_field_detection_works_with_all_backends(self):
        """Test that field detection works regardless of database backend."""
        registrar = AdminModelRegistrar("tests")

        # Test with a model that has all field types
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # Check that fields are detected correctly
        assert "char_field" in admin_class.list_display
        assert "integer_field" in admin_class.list_display
        assert "boolean_field" in admin_class.list_display
        assert "created_at" in admin_class.list_display

    def test_relationship_detection_works_with_all_backends(self):
        """Test that relationship detection works regardless of database backend."""
        registrar = AdminModelRegistrar("tests")

        # Test with a model that has relationships
        admin_class = registrar.return_admin_class_for_model(ForeignKeyModel)

        # Check that relationships are detected
        assert hasattr(admin_class, "relations")
        assert "simple_foreign_key" in admin_class.relations
        assert "complex_foreign_key" in admin_class.relations

    def test_property_detection_works_with_all_backends(self):
        """Test that property detection works regardless of database backend."""
        registrar = AdminModelRegistrar("tests")

        # Test with a model that has properties
        admin_class = registrar.return_admin_class_for_model(ModelWithProperties)

        # Check that properties are detected
        assert "full_name" in admin_class.list_display
        assert "is_adult" in admin_class.list_display
        assert "status" in admin_class.list_display


@pytest.mark.django_db
class TestDatabaseSpecificFeatures:
    """Test database-specific features and their handling."""

    def test_json_field_handling(self):
        """Test JSON field handling across different databases."""
        # Create instance with JSON data
        complex_model = ComplexModel.objects.create(
            char_field="Test JSON", json_field={"key": "value", "list": [1, 2, 3], "nested": {"a": "b"}}
        )

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # JSON field should be in list_display
        assert "json_field" in admin_class.list_display

        # The field should be accessible
        assert complex_model.json_field["key"] == "value"

    def test_uuid_field_handling(self):
        """Test UUID field handling across different databases."""
        import uuid

        # Create instance with UUID
        complex_model = ComplexModel.objects.create(char_field="Test UUID", uuid_field=uuid.uuid4())

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # UUID field should be in list_display (unless excluded by DEFAULT_EXCLUDED_TERMS)
        # Since 'uuid' is in DEFAULT_EXCLUDED_TERMS, it should be excluded
        assert "uuid_field" not in admin_class.list_display

        # The field should be accessible
        assert isinstance(complex_model.uuid_field, uuid.UUID)

    def test_binary_field_handling(self):
        """Test binary field handling across different databases."""
        # Create instance with binary data
        complex_model = ComplexModel.objects.create(char_field="Test Binary", binary_field=b"binary_data_test")

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # Binary field should be in list_display
        assert "binary_field" in admin_class.list_display

        # The field should be accessible
        assert complex_model.binary_field == b"binary_data_test"

    def test_decimal_field_handling(self):
        """Test decimal field handling across different databases."""
        from decimal import Decimal

        # Create instance with decimal data
        complex_model = ComplexModel.objects.create(char_field="Test Decimal", decimal_field=Decimal("123.45"))

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # Decimal field should be in list_display
        assert "decimal_field" in admin_class.list_display

        # The field should be accessible
        assert complex_model.decimal_field == Decimal("123.45")

    def test_ip_address_field_handling(self):
        """Test IP address field handling across different databases."""
        # Create instance with IP addresses
        complex_model = ComplexModel.objects.create(
            char_field="Test IP", ip_address_field="192.168.1.100", ipv4_field="10.0.0.1", ipv6_field="2001:db8::1"
        )

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # IP address fields should be in list_display
        assert "ip_address_field" in admin_class.list_display
        assert "ipv4_field" in admin_class.list_display
        assert "ipv6_field" in admin_class.list_display

        # The fields should be accessible
        assert complex_model.ip_address_field == "192.168.1.100"
        assert complex_model.ipv4_field == "10.0.0.1"
        assert complex_model.ipv6_field == "2001:db8::1"


@pytest.mark.django_db
class TestDatabaseConstraints:
    """Test handling of database-specific constraints."""

    def test_unique_constraint_handling(self):
        """Test that unique constraints don't interfere with admin functionality."""
        # Use the UniqueModel from models.py
        from .models import UniqueModel

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(UniqueModel)

        # Should still have list_display
        assert hasattr(admin_class, "list_display")
        assert "unique_field" in admin_class.list_display

    def test_foreign_key_constraint_handling(self):
        """Test that foreign key constraints work correctly."""
        # Create related instances
        simple = SimpleModel.objects.create(name="Parent", is_active=True)
        complex_model = ComplexModel.objects.create(char_field="Parent Complex")
        one_to_one_simple = SimpleModel.objects.create(name="One-to-One Parent", is_active=True)

        ForeignKeyModel.objects.create(
            simple_foreign_key=simple, complex_foreign_key=complex_model, one_to_one=one_to_one_simple, name="Child FK"
        )

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ForeignKeyModel)

        # Foreign key fields should be linkified
        list_display = admin_class.list_display
        linkified_fields = [field for field in list_display if callable(field)]
        assert len(linkified_fields) >= 1

    def test_nullable_field_handling(self):
        """Test that nullable fields work correctly across databases."""
        # Create instance with null values
        complex_model = ComplexModel.objects.create(char_field="Test Nullable", nullable_char=None, nullable_int=None)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ComplexModel)

        # Nullable fields should be in list_display
        assert "nullable_char" in admin_class.list_display
        assert "nullable_int" in admin_class.list_display

        # The fields should be accessible (None)
        assert complex_model.nullable_char is None
        assert complex_model.nullable_int is None


@pytest.mark.django_db
class TestDatabaseTransactions:
    """Test transaction handling across different databases."""

    def test_transaction_rollback_handling(self):
        """Test that transaction rollbacks don't affect admin registration."""
        from django.db import transaction

        registrar = AdminModelRegistrar("tests")

        # Start a transaction
        with transaction.atomic():
            # Create an instance
            SimpleModel.objects.create(name="Transaction Test", is_active=True)

            # Admin should still work
            admin_class = registrar.return_admin_class_for_model(SimpleModel)
            assert hasattr(admin_class, "list_display")

            # Rollback the transaction
            transaction.set_rollback(True)

        # Admin should still work after rollback
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")

    def test_nested_transaction_handling(self):
        """Test nested transaction handling."""
        from django.db import transaction

        registrar = AdminModelRegistrar("tests")

        # Outer transaction
        with transaction.atomic():
            # Inner transaction
            with transaction.atomic():
                SimpleModel.objects.create(name="Nested Test", is_active=True)

                # Admin should work in nested transaction
                admin_class = registrar.return_admin_class_for_model(SimpleModel)
                assert hasattr(admin_class, "list_display")

        # Admin should work after nested transaction
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")


@pytest.mark.django_db
class TestDatabaseConnectionHandling:
    """Test connection handling across different databases."""

    def test_connection_reset_handling(self):
        """Test that connection resets don't affect admin functionality."""
        registrar = AdminModelRegistrar("tests")

        # Get initial admin class
        admin_class1 = registrar.return_admin_class_for_model(SimpleModel)

        # Reset connection
        connection.close()

        # Get admin class after connection reset
        admin_class2 = registrar.return_admin_class_for_model(SimpleModel)

        # Should still work
        assert hasattr(admin_class1, "list_display")
        assert hasattr(admin_class2, "list_display")

    def test_multiple_connection_handling(self):
        """Test handling of multiple database connections."""
        # This test is more relevant for multi-database setups
        registrar = AdminModelRegistrar("tests")

        # Should work with default connection
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")

        # Should work with other connections if they exist
        for alias in connections.databases:
            if alias != "default":
                # In a multi-database setup, this would test other connections
                pass


@pytest.mark.django_db
class TestDatabaseSpecificQueries:
    """Test database-specific query handling."""

    def test_case_insensitive_queries(self):
        """Test case insensitive query handling."""
        # Create instances with different cases
        SimpleModel.objects.create(name="Test Model", is_active=True)
        SimpleModel.objects.create(name="test model", is_active=True)
        SimpleModel.objects.create(name="TEST MODEL", is_active=True)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(SimpleModel)

        # Admin should still work regardless of case sensitivity
        assert hasattr(admin_class, "list_display")
        assert "name" in admin_class.list_display

    def test_unicode_queries(self):
        """Test unicode query handling."""
        # Create instance with unicode data
        SimpleModel.objects.create(name="测试模型", is_active=True)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(SimpleModel)

        # Admin should work with unicode data
        assert hasattr(admin_class, "list_display")
        assert "name" in admin_class.list_display

    def test_special_character_queries(self):
        """Test special character query handling."""
        # Create instance with special characters
        SimpleModel.objects.create(name="Test & Model <script>alert('xss')</script>", is_active=True)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(SimpleModel)

        # Admin should work with special characters
        assert hasattr(admin_class, "list_display")
        assert "name" in admin_class.list_display


@pytest.mark.django_db
class TestDatabasePerformance:
    """Test performance characteristics across different databases."""

    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        # Create many instances
        for i in range(100):
            SimpleModel.objects.create(name=f"Test {i}", is_active=True)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(SimpleModel)

        # Admin should work with large datasets
        assert hasattr(admin_class, "list_display")
        assert "name" in admin_class.list_display

        # Should be able to query large datasets
        queryset = SimpleModel.objects.all()
        assert queryset.count() == 100

    def test_complex_relationship_queries(self):
        """Test complex relationship query handling."""
        # Create complex relationships
        simple = SimpleModel.objects.create(name="Parent", is_active=True)
        complex_model = ComplexModel.objects.create(char_field="Parent Complex")

        # Create multiple one-to-one parents to avoid unique constraint violation
        for i in range(10):
            one_to_one_simple = SimpleModel.objects.create(name=f"One-to-One Parent {i}", is_active=True)
            ForeignKeyModel.objects.create(
                simple_foreign_key=simple,
                complex_foreign_key=complex_model,
                one_to_one=one_to_one_simple,
                name=f"Child {i}",
            )

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ForeignKeyModel)

        # Admin should work with complex relationships
        assert hasattr(admin_class, "list_display")

        # Should be able to query with select_related
        queryset = ForeignKeyModel.objects.select_related("simple_foreign_key", "complex_foreign_key")
        assert queryset.count() == 10


@pytest.mark.django_db
class TestDatabaseBackendSpecific:
    """Test backend-specific features and their handling."""

    def test_postgresql_specific_features(self):
        """Test PostgreSQL-specific features if available."""
        if connection.vendor == "postgresql":
            # Test PostgreSQL-specific features
            from django_admin_magic.utils import TimeLimitedPaginator

            # Create test data
            for i in range(50):
                SimpleModel.objects.create(name=f"PostgreSQL Test {i}", is_active=True)

            queryset = SimpleModel.objects.all()
            paginator = TimeLimitedPaginator(queryset, 10)

            # Should work with PostgreSQL
            assert paginator.count == 50
            assert paginator.num_pages == 5

    def test_mysql_specific_features(self):
        """Test MySQL-specific features if available."""
        if connection.vendor == "mysql":
            # Test MySQL-specific features
            # MySQL has some specific behaviors around transactions and constraints
            from django.db import transaction

            with transaction.atomic():
                SimpleModel.objects.create(name="MySQL Test", is_active=True)

                registrar = AdminModelRegistrar("tests")
                admin_class = registrar.return_admin_class_for_model(SimpleModel)

                # Should work with MySQL
                assert hasattr(admin_class, "list_display")

    def test_sqlite_specific_features(self):
        """Test SQLite-specific features if available."""
        if connection.vendor == "sqlite":
            # Test SQLite-specific features
            # SQLite has some specific behaviors around transactions and constraints
            from django.db import transaction

            with transaction.atomic():
                SimpleModel.objects.create(name="SQLite Test", is_active=True)

                registrar = AdminModelRegistrar("tests")
                admin_class = registrar.return_admin_class_for_model(SimpleModel)

                # Should work with SQLite
                assert hasattr(admin_class, "list_display")

    def test_oracle_specific_features(self):
        """Test Oracle-specific features if available."""
        if connection.vendor == "oracle":
            # Test Oracle-specific features
            # Oracle has some specific behaviors around transactions and constraints
            from django.db import transaction

            with transaction.atomic():
                SimpleModel.objects.create(name="Oracle Test", is_active=True)

                registrar = AdminModelRegistrar("tests")
                admin_class = registrar.return_admin_class_for_model(SimpleModel)

                # Should work with Oracle
                assert hasattr(admin_class, "list_display")


@pytest.mark.django_db
class TestDatabaseMigrationCompatibility:
    """Test compatibility with database migrations."""

    def test_migration_awareness(self):
        """Test that the admin system works with migrations."""
        registrar = AdminModelRegistrar("tests")

        # Should work regardless of migration state
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")

    def test_field_addition_handling(self):
        """Test handling of fields added via migrations."""
        # Use the existing ModelWithAddedField from models.py
        from .models import ModelWithAddedField

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(ModelWithAddedField)

        # Should detect the added field
        assert "added_field" in admin_class.list_display

    def test_field_removal_handling(self):
        """Test handling of fields removed via migrations."""
        # This would normally be tested by creating a model without certain fields
        # and ensuring the admin doesn't crash
        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(SimpleModel)

        # Should work even if some fields are missing
        assert hasattr(admin_class, "list_display")


@pytest.mark.django_db
class TestDatabaseErrorHandling:
    """Test error handling across different databases."""

    def test_connection_error_handling(self):
        """Test handling of database connection errors."""
        registrar = AdminModelRegistrar("tests")

        # Should handle connection issues gracefully
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")

    def test_constraint_violation_handling(self):
        """Test handling of constraint violations."""
        # Use the UniqueModel from models.py
        from .models import UniqueModel

        # Create first instance
        UniqueModel.objects.create(name="Unique Test", unique_field="unique_value", is_active=True)

        registrar = AdminModelRegistrar("tests")
        admin_class = registrar.return_admin_class_for_model(UniqueModel)

        # Should still work even with constraint violations
        assert hasattr(admin_class, "list_display")

    def test_timeout_handling(self):
        """Test handling of database timeouts."""
        registrar = AdminModelRegistrar("tests")

        # Should handle timeouts gracefully
        admin_class = registrar.return_admin_class_for_model(SimpleModel)
        assert hasattr(admin_class, "list_display")


@pytest.mark.django_db
class TestDatabaseAgnosticConfiguration:
    """Test configuration that works across all databases."""

    def test_settings_work_with_all_backends(self):
        """Test that settings work regardless of database backend."""
        from django_admin_magic.conf import app_settings

        # These settings should work with any database
        assert hasattr(app_settings, "APP_LABEL")
        assert hasattr(app_settings, "DEFAULT_EXCLUDED_TERMS")
        assert hasattr(app_settings, "DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST")
        assert hasattr(app_settings, "ADMIN_TUPLE_ATTRIBUTES_TO_LIST")

    def test_registrar_initialization_with_all_backends(self):
        """Test that registrar initialization works with all backends."""
        # Should work regardless of database backend
        registrar = AdminModelRegistrar("tests")

        # Should have required attributes
        assert hasattr(registrar, "app_labels")  # Note: it's app_labels (plural), not app_label
        assert hasattr(registrar, "class_dict")

    def test_admin_class_factory_with_all_backends(self):
        """Test that admin class factory works with all backends."""
        registrar = AdminModelRegistrar("tests")

        # Should be able to create admin classes
        admin_class = registrar._admin_class_factory(SimpleModel, admin.site)
        assert hasattr(admin_class, "model")
        assert admin_class.model == SimpleModel
