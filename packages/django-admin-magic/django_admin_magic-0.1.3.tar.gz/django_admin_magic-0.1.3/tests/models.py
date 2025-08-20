import uuid
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from polymorphic.models import PolymorphicModel


class SimpleModel(models.Model):
    """Simple model for basic testing."""

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional fields for testing
    custom_field = models.CharField(max_length=100, blank=True)
    custom_filter = models.CharField(max_length=100, blank=True)
    custom_search = models.CharField(max_length=100, blank=True)
    prepended_field = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class ComplexModel(models.Model):
    """Model with all types of Django fields for comprehensive testing."""

    # Basic fields
    char_field = models.CharField(max_length=100, default="Default")
    text_field = models.TextField(default="Long text content")
    integer_field = models.IntegerField(default=42)
    positive_integer_field = models.PositiveIntegerField(default=100)
    small_integer_field = models.SmallIntegerField(default=10)
    positive_small_integer_field = models.PositiveSmallIntegerField(default=50)
    big_integer_field = models.BigIntegerField(default=9223372036854775807)

    # Decimal and float fields
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    float_field = models.FloatField(default=3.14159)

    # Boolean fields
    boolean_field = models.BooleanField(default=True)
    null_boolean_field = models.BooleanField(null=True, blank=True)

    # Date and time fields
    date_field = models.DateField(auto_now_add=True)
    time_field = models.TimeField(auto_now_add=True)
    datetime_field = models.DateTimeField(auto_now_add=True)
    duration_field = models.DurationField(default=timedelta(days=1))

    # File and image fields
    file_field = models.FileField(upload_to="test_files/", null=True, blank=True)
    image_field = models.ImageField(upload_to="test_images/", null=True, blank=True)

    # URL and email fields
    url_field = models.URLField(default="https://example.com")
    email_field = models.EmailField(default="test@example.com")

    # JSON field
    json_field = models.JSONField(default=dict)

    # UUID field
    uuid_field = models.UUIDField(default=uuid.uuid4)

    # Binary field
    binary_field = models.BinaryField(default=b"binary_data")

    # Slug field
    slug_field = models.SlugField(default="test-slug")

    # IP address fields
    ip_address_field = models.GenericIPAddressField(default="127.0.0.1")
    ipv4_field = models.GenericIPAddressField(protocol="IPv4", default="192.168.1.1")
    ipv6_field = models.GenericIPAddressField(protocol="IPv6", default="::1")

    # File path field
    file_path_field = models.FilePathField(path="/tmp", null=True, blank=True)

    # Choices field
    CHOICES = [
        ("A", "Choice A"),
        ("B", "Choice B"),
        ("C", "Choice C"),
    ]
    choices_field = models.CharField(max_length=1, choices=CHOICES, default="A")

    # Nullable fields
    nullable_char = models.CharField(max_length=100, null=True, blank=True)
    nullable_int = models.IntegerField(null=True, blank=True)
    nullable_date = models.DateField(null=True, blank=True)

    # Auto fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ComplexModel {self.id}: {self.char_field}"


class ForeignKeyModel(models.Model):
    """Model with various foreign key relationships for testing."""

    # Basic foreign key
    simple_foreign_key = models.ForeignKey(SimpleModel, on_delete=models.CASCADE, related_name="fk_models")

    # Nullable foreign key
    nullable_foreign_key = models.ForeignKey(
        SimpleModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="nullable_fk_models"
    )

    # Self-referencing foreign key
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    # Foreign key to complex model
    complex_foreign_key = models.ForeignKey(ComplexModel, on_delete=models.CASCADE, related_name="fk_models")

    # Many-to-many relationship
    many_to_many = models.ManyToManyField(SimpleModel, related_name="m2m_models")

    # One-to-one relationship
    one_to_one = models.OneToOneField(SimpleModel, on_delete=models.CASCADE, related_name="one_to_one_model")

    # Basic fields
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FKModel {self.id}: {self.name}"


class GenericForeignKeyModel(models.Model):
    """Model with generic foreign key for testing GFK functionality."""

    # Content type and object ID for generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # Generic foreign key
    content_object = GenericForeignKey("content_type", "object_id")

    # Multiple generic foreign keys
    content_type_2 = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="gfk_models_2")
    object_id_2 = models.PositiveIntegerField()
    content_object_2 = GenericForeignKey("content_type_2", "object_id_2")

    # Nullable generic foreign key
    content_type_nullable = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="gfk_models_nullable"
    )
    object_id_nullable = models.PositiveIntegerField(null=True, blank=True)
    content_object_nullable = GenericForeignKey("content_type_nullable", "object_id_nullable")

    # Basic fields
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GFKModel {self.id}: {self.name}"


# Polymorphic models (existing)
class PolymorphicParent(PolymorphicModel):
    """Base polymorphic model for testing."""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"


class PolymorphicChildA(PolymorphicParent):
    """First polymorphic child model."""

    field_a = models.CharField(max_length=100)
    is_special = models.BooleanField(default=False)

    def __str__(self):
        return f"ChildA: {self.name} ({self.field_a})"


class PolymorphicChildB(PolymorphicParent):
    """Second polymorphic child model."""

    field_b = models.IntegerField()
    category = models.CharField(max_length=50, default="default")

    def __str__(self):
        return f"ChildB: {self.name} ({self.field_b})"


# Model with properties for testing property detection
class ModelWithProperties(models.Model):
    """Model with properties to test property detection in admin."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        """Property that returns full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_adult(self):
        """Property that checks if person is adult."""
        return self.age >= 18

    @property
    def status(self):
        """Property that returns status based on age and active status."""
        if not self.is_active:
            return "Inactive"
        return "Adult" if self.is_adult else "Minor"

    def __str__(self):
        return self.full_name


# Model with search vector for testing search functionality
class ModelWithSearchVector(models.Model):
    """Model with search vector field for testing search functionality."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    search_vector = models.TextField(editable=False, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Model with custom manager for testing
class ModelWithCustomManager(models.Model):
    """Model with custom manager for testing manager functionality."""

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom manager
    objects = models.Manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class UniqueModel(SimpleModel):
    """Model with unique fields for testing constraint handling."""

    unique_field = models.CharField(max_length=100, unique=True)
    unique_together_field1 = models.CharField(max_length=100)
    unique_together_field2 = models.CharField(max_length=100)

    class Meta:
        unique_together = [("unique_together_field1", "unique_together_field2")]

    def __str__(self):
        return f"UniqueModel {self.id}: {self.name}"


class ModelWithAddedField(models.Model):
    """Model with added field for testing field addition functionality."""

    name = models.CharField(max_length=100)
    added_field = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ModelWithAddedField {self.id}: {self.name}"
