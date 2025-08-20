import uuid
from datetime import timedelta

from django.db import migrations


def create_sample_data(apps, schema_editor):
    """Create sample data for all models."""
    # Get model classes
    SimpleModel = apps.get_model("demo_app", "SimpleModel")
    ComplexModel = apps.get_model("demo_app", "ComplexModel")
    ForeignKeyModel = apps.get_model("demo_app", "ForeignKeyModel")
    PolymorphicParent = apps.get_model("demo_app", "PolymorphicParent")
    PolymorphicChildA = apps.get_model("demo_app", "PolymorphicChildA")
    PolymorphicChildB = apps.get_model("demo_app", "PolymorphicChildB")
    ModelWithProperties = apps.get_model("demo_app", "ModelWithProperties")
    ModelWithSearchVector = apps.get_model("demo_app", "ModelWithSearchVector")
    ModelWithCustomManager = apps.get_model("demo_app", "ModelWithCustomManager")

    # Create SimpleModel instances
    simple1 = SimpleModel.objects.create(name="Sample Item 1", is_active=True)
    simple2 = SimpleModel.objects.create(name="Sample Item 2", is_active=False)
    simple3 = SimpleModel.objects.create(name="Sample Item 3", is_active=True)

    # Create one-to-one SimpleModel first
    one_to_one_simple = SimpleModel.objects.create(name="One-to-One Sample", is_active=True)

    # Create ComplexModel instances
    complex1 = ComplexModel.objects.create(
        char_field="Complex Sample 1",
        text_field="This is a complex model with many field types",
        integer_field=100,
        positive_integer_field=200,
        small_integer_field=50,
        positive_small_integer_field=75,
        big_integer_field=9223372036854775800,
        decimal_field=123.45,
        float_field=3.14159,
        boolean_field=True,
        null_boolean_field=None,
        duration_field=timedelta(hours=2),
        url_field="https://example.org",
        email_field="sample1@example.com",
        json_field={"key": "value", "nested": {"data": "test"}},
        uuid_field=uuid.uuid4(),
        binary_field=b"sample_binary_data",
        slug_field="complex-sample-1",
        ip_address_field="192.168.1.100",
        ipv4_field="10.0.0.1",
        ipv6_field="2001:db8::1",
        choices_field="A",
        nullable_char="Optional text",
        nullable_int=42,
        nullable_date=None,
    )

    complex2 = ComplexModel.objects.create(
        char_field="Complex Sample 2",
        text_field="Another complex model instance",
        integer_field=500,
        positive_integer_field=1000,
        small_integer_field=25,
        positive_small_integer_field=100,
        big_integer_field=9223372036854775000,
        decimal_field=999.99,
        float_field=2.71828,
        boolean_field=False,
        null_boolean_field=True,
        duration_field=timedelta(days=7),
        url_field="https://django.org",
        email_field="sample2@example.com",
        json_field={"status": "active", "tags": ["demo", "test"]},
        uuid_field=uuid.uuid4(),
        binary_field=b"another_binary_data",
        slug_field="complex-sample-2",
        ip_address_field="172.16.0.1",
        ipv4_field="192.168.0.1",
        ipv6_field="::ffff:192.168.0.1",
        choices_field="B",
        nullable_char=None,
        nullable_int=None,
        nullable_date=None,
    )

    # Create ForeignKeyModel instances with one_to_one field
    fk1 = ForeignKeyModel.objects.create(
        simple_foreign_key=simple1,
        nullable_foreign_key=simple2,
        complex_foreign_key=complex1,
        one_to_one=one_to_one_simple,
        name="FK Model 1",
        description="First foreign key model",
        is_active=True,
    )

    fk2 = ForeignKeyModel.objects.create(
        simple_foreign_key=simple3,
        nullable_foreign_key=None,
        complex_foreign_key=complex2,
        one_to_one=simple1,  # Use simple1 for the second FK model
        name="FK Model 2",
        description="Second foreign key model",
        is_active=False,
    )

    # Add many-to-many relationships
    fk1.many_to_many.add(simple1, simple2)
    fk2.many_to_many.add(simple3)

    # Create self-referencing relationships
    fk1.parent = None  # Root level
    fk2.parent = fk1  # Child of fk1
    fk1.save()
    fk2.save()

    # Create Polymorphic models
    PolymorphicParent.objects.create(name="Polymorphic Parent 1")

    PolymorphicChildA.objects.create(name="Child A 1", field_a="Special field A1", is_special=True)

    PolymorphicChildA.objects.create(name="Child A 2", field_a="Regular field A2", is_special=False)

    PolymorphicChildB.objects.create(name="Child B 1", field_b=42, category="premium")

    PolymorphicChildB.objects.create(name="Child B 2", field_b=100, category="standard")

    # Create ModelWithProperties instances
    ModelWithProperties.objects.create(first_name="John", last_name="Doe", age=25, is_active=True)

    ModelWithProperties.objects.create(first_name="Jane", last_name="Smith", age=16, is_active=True)

    ModelWithProperties.objects.create(first_name="Bob", last_name="Johnson", age=30, is_active=False)

    # Create ModelWithSearchVector instances
    ModelWithSearchVector.objects.create(
        title="Introduction to Django",
        content=(
            "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design."
        ),
        is_published=True,
    )

    ModelWithSearchVector.objects.create(
        title="Advanced Django Patterns",
        content="Learn about advanced patterns and best practices for Django development.",
        is_published=False,
    )

    ModelWithSearchVector.objects.create(
        title="Django Admin Customization",
        content="How to customize the Django admin interface for better user experience.",
        is_published=True,
    )

    # Create ModelWithCustomManager instances
    ModelWithCustomManager.objects.create(name="Featured Item 1", category="Technology", is_featured=True)

    ModelWithCustomManager.objects.create(name="Regular Item 1", category="Technology", is_featured=False)

    ModelWithCustomManager.objects.create(name="Featured Item 2", category="Design", is_featured=True)

    ModelWithCustomManager.objects.create(name="Regular Item 2", category="Design", is_featured=False)


def remove_sample_data(apps, schema_editor):
    """Remove sample data."""
    # Get model classes
    SimpleModel = apps.get_model("demo_app", "SimpleModel")
    ComplexModel = apps.get_model("demo_app", "ComplexModel")
    ForeignKeyModel = apps.get_model("demo_app", "ForeignKeyModel")
    PolymorphicParent = apps.get_model("demo_app", "PolymorphicParent")
    ModelWithProperties = apps.get_model("demo_app", "ModelWithProperties")
    ModelWithSearchVector = apps.get_model("demo_app", "ModelWithSearchVector")
    ModelWithCustomManager = apps.get_model("demo_app", "ModelWithCustomManager")

    # Delete all instances
    ModelWithCustomManager.objects.all().delete()
    ModelWithSearchVector.objects.all().delete()
    ModelWithProperties.objects.all().delete()
    PolymorphicParent.objects.all().delete()
    ForeignKeyModel.objects.all().delete()
    ComplexModel.objects.all().delete()
    SimpleModel.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("demo_app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_sample_data, remove_sample_data),
    ]
