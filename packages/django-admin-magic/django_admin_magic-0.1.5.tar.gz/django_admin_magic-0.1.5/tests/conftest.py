import os

import django
from django.conf import settings

# Configure Django settings before importing any Django modules
if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
    django.setup()

import pytest
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory

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


@pytest.fixture
def request_factory():
    """Provide a Django RequestFactory for testing admin views."""
    return RequestFactory()


@pytest.fixture
def simple_model_instance():
    """Create a SimpleModel instance for testing."""
    return SimpleModel.objects.create(
        name="Test Model",
        is_active=True,
    )


@pytest.fixture
def complex_model_instance():
    """Create a ComplexModel instance for testing all field types."""
    return ComplexModel.objects.create(
        char_field="Test Complex Model",
        text_field="This is a long text field for testing",
        integer_field=123,
        positive_integer_field=456,
        small_integer_field=78,
        positive_small_integer_field=90,
        big_integer_field=9223372036854775806,
        decimal_field=123.45,
        float_field=3.14159,
        boolean_field=True,
        null_boolean_field=None,
        url_field="https://test.example.com",
        email_field="test@example.com",
        json_field={"key": "value", "list": [1, 2, 3]},
        slug_field="test-complex-model",
        ip_address_field="192.168.1.100",
        ipv4_field="10.0.0.1",
        ipv6_field="2001:db8::1",
        choices_field="B",
        nullable_char="Nullable String",
        nullable_int=999,
    )


@pytest.fixture
def foreign_key_model_instance(simple_model_instance, complex_model_instance):
    """Create a ForeignKeyModel instance for testing foreign key relationships."""
    # Create one-to-one relationship first
    one_to_one_simple = SimpleModel.objects.create(
        name="One-to-One Model",
        is_active=True,
    )

    fk_model = ForeignKeyModel.objects.create(
        simple_foreign_key=simple_model_instance,
        complex_foreign_key=complex_model_instance,
        one_to_one=one_to_one_simple,  # Set the one-to-one relationship
        name="Test FK Model",
        description="Testing foreign key relationships",
        is_active=True,
    )

    # Add many-to-many relationship
    fk_model.many_to_many.add(simple_model_instance)

    return fk_model


@pytest.fixture
def generic_foreign_key_model_instance(simple_model_instance, complex_model_instance):
    """Create a GenericForeignKeyModel instance for testing GFK functionality."""
    # Create GFK model pointing to SimpleModel
    gfk_model = GenericForeignKeyModel.objects.create(
        content_type=ContentType.objects.get_for_model(SimpleModel),
        object_id=simple_model_instance.id,
        content_type_2=ContentType.objects.get_for_model(ComplexModel),  # Set the second GFK
        object_id_2=complex_model_instance.id,
        name="Test GFK Model",
        description="Testing generic foreign key",
    )

    return gfk_model


@pytest.fixture
def polymorphic_parent_instance():
    """Create a PolymorphicParent instance for testing."""
    return PolymorphicParent.objects.create(name="Test Parent")


@pytest.fixture
def polymorphic_child_a_instance():
    """Create a PolymorphicChildA instance for testing."""
    return PolymorphicChildA.objects.create(
        name="Test Child A",
        field_a="Test Field A",
        is_special=True,
    )


@pytest.fixture
def polymorphic_child_b_instance():
    """Create a PolymorphicChildB instance for testing."""
    return PolymorphicChildB.objects.create(
        name="Test Child B",
        field_b=42,
        category="test_category",
    )


@pytest.fixture
def model_with_properties_instance():
    """Create a ModelWithProperties instance for testing property detection."""
    return ModelWithProperties.objects.create(
        first_name="John",
        last_name="Doe",
        age=25,
        is_active=True,
    )


@pytest.fixture
def model_with_search_vector_instance():
    """Create a ModelWithSearchVector instance for testing search functionality."""
    return ModelWithSearchVector.objects.create(
        title="Test Article",
        content="This is the content of the test article for search testing.",
        search_vector="test article content search",
        is_published=True,
    )


@pytest.fixture
def model_with_custom_manager_instance():
    """Create a ModelWithCustomManager instance for testing custom managers."""
    return ModelWithCustomManager.objects.create(
        name="Test Manager Model",
        category="test",
        is_featured=True,
    )


@pytest.fixture
def admin_site():
    """Provide access to the Django admin site."""
    return admin.site


@pytest.fixture
def registrar():
    """Provide access to the AdminModelRegistrar instance."""
    from django.apps import apps

    return apps.get_app_config("django_admin_magic").registrar
