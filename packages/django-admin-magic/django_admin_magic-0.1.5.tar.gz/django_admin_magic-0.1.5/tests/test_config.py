import pytest
from django.conf import settings
from django.test import override_settings

from django_admin_magic import defaults
from django_admin_magic.conf import AppSettings, app_settings
from django_admin_magic.utils import (
    linkify,
    reorder_list_display_to_avoid_linkify_first,
)


@pytest.mark.django_db
class TestAppSettings:
    """Test the AppSettings class."""

    def test_app_settings_initialization(self):
        """Test that AppSettings initializes correctly."""
        settings_obj = AppSettings(prefix="TEST_")
        assert settings_obj.prefix == "TEST_"

    def test_getattr_with_prefixed_setting(self):
        """Test that getattr retrieves prefixed settings from Django settings."""
        with override_settings(TEST_CUSTOM_SETTING="test_value"):
            settings_obj = AppSettings(prefix="TEST_")
            assert settings_obj.CUSTOM_SETTING == "test_value"

    def test_getattr_with_default_setting(self):
        """Test that getattr falls back to defaults when setting not found."""
        settings_obj = AppSettings(prefix="NONEXISTENT_")

        # Should fall back to the default
        assert settings_obj.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS

    def test_getattr_with_nonexistent_setting(self):
        """Test that getattr raises AttributeError for nonexistent settings."""
        settings_obj = AppSettings(prefix="TEST_")

        with pytest.raises(AttributeError):
            _ = settings_obj.NONEXISTENT_SETTING

    def test_getattr_with_empty_prefix(self):
        """Test that getattr works with empty prefix."""
        settings_obj = AppSettings(prefix="")

        # Should work the same way
        assert settings_obj.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS


@pytest.mark.django_db
class TestAppSettingsIntegration:
    """Test integration of AppSettings with Django settings."""

    def test_app_settings_with_auto_admin_prefix(self):
        """Test that app_settings uses the correct AUTO_ADMIN_ prefix."""
        # Test with a custom setting
        with override_settings(AUTO_ADMIN_CUSTOM_SETTING="custom_value"):
            assert app_settings.CUSTOM_SETTING == "custom_value"

    def test_app_settings_fallback_to_defaults(self):
        """Test that app_settings falls back to defaults when setting not found."""
        # Remove any existing setting to test fallback
        if hasattr(settings, "AUTO_ADMIN_DEFAULT_EXCLUDED_TERMS"):
            delattr(settings, "AUTO_ADMIN_DEFAULT_EXCLUDED_TERMS")

        # Should use the default
        assert app_settings.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS

    def test_app_settings_override_defaults(self):
        """Test that app_settings can override defaults."""
        custom_excluded_terms = ["custom1", "custom2"]

        with override_settings(AUTO_ADMIN_DEFAULT_EXCLUDED_TERMS=custom_excluded_terms):
            assert app_settings.DEFAULT_EXCLUDED_TERMS == custom_excluded_terms

    def test_app_settings_app_label(self):
        """Test that APP_LABEL is correctly retrieved."""
        # Should get the value from test_settings.py
        assert app_settings.APP_LABEL == "tests"


@pytest.mark.django_db
class TestDefaults:
    """Test the defaults module."""

    def test_defaults_has_required_settings(self):
        """Test that defaults module has all required settings."""
        assert hasattr(defaults, "APP_LABEL")
        assert hasattr(defaults, "DEFAULT_EXCLUDED_TERMS")
        assert hasattr(defaults, "DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST")
        assert hasattr(defaults, "ADMIN_TUPLE_ATTRIBUTES_TO_LIST")

    def test_default_excluded_terms_is_list(self):
        """Test that DEFAULT_EXCLUDED_TERMS is a list."""
        assert isinstance(defaults.DEFAULT_EXCLUDED_TERMS, list)
        assert len(defaults.DEFAULT_EXCLUDED_TERMS) > 0

    def test_default_do_not_register_filter_string_list_is_list(self):
        """Test that DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST is a list."""
        assert isinstance(defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST, list)

    def test_admin_tuple_attributes_to_list_is_list(self):
        """Test that ADMIN_TUPLE_ATTRIBUTES_TO_LIST is a list."""
        assert isinstance(defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST, list)
        assert len(defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST) > 0

    def test_admin_tuple_attributes_to_list_contains_expected_attributes(self):
        """Test that ADMIN_TUPLE_ATTRIBUTES_TO_LIST contains expected attributes."""
        expected_attributes = ["list_display", "list_filter", "search_fields", "readonly_fields"]
        for attr in expected_attributes:
            assert attr in defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST


@pytest.mark.django_db
class TestConfigurationEdgeCases:
    """Test edge cases in configuration handling."""

    def test_app_settings_with_none_value(self):
        """Test that app_settings handles None values correctly."""
        with override_settings(AUTO_ADMIN_NONE_SETTING=None):
            assert app_settings.NONE_SETTING is None

    def test_app_settings_with_false_value(self):
        """Test that app_settings handles False values correctly."""
        with override_settings(AUTO_ADMIN_FALSE_SETTING=False):
            assert app_settings.FALSE_SETTING is False

    def test_app_settings_with_empty_list(self):
        """Test that app_settings handles empty lists correctly."""
        with override_settings(AUTO_ADMIN_EMPTY_LIST=[]):
            assert app_settings.EMPTY_LIST == []

    def test_app_settings_with_complex_objects(self):
        """Test that app_settings handles complex objects correctly."""
        complex_object = {"key": "value", "list": [1, 2, 3]}

        with override_settings(AUTO_ADMIN_COMPLEX_OBJECT=complex_object):
            assert app_settings.COMPLEX_OBJECT == complex_object

    def test_app_settings_case_sensitivity(self):
        """Test that app_settings is case sensitive."""
        with override_settings(AUTO_ADMIN_CASE_TEST="lowercase"):
            assert app_settings.CASE_TEST == "lowercase"

            # Different case should not match
            with pytest.raises(AttributeError):
                _ = app_settings.case_test


@pytest.mark.django_db
class TestConfigurationIntegration:
    """Test integration between configuration components."""

    def test_app_settings_with_multiple_prefixes(self):
        """Test that different prefixes work independently."""
        settings1 = AppSettings(prefix="PREFIX1_")
        settings2 = AppSettings(prefix="PREFIX2_")

        with override_settings(PREFIX1_CUSTOM_SETTING="value1", PREFIX2_CUSTOM_SETTING="value2"):
            assert settings1.CUSTOM_SETTING == "value1"
            assert settings2.CUSTOM_SETTING == "value2"

    def test_app_settings_shared_defaults(self):
        """Test that different AppSettings instances share the same defaults."""
        settings1 = AppSettings(prefix="PREFIX1_")
        settings2 = AppSettings(prefix="PREFIX2_")

        # Both should get the same default value
        assert settings1.DEFAULT_EXCLUDED_TERMS == settings2.DEFAULT_EXCLUDED_TERMS
        assert settings1.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS

    def test_app_settings_override_chain(self):
        """Test the override chain: Django settings -> defaults -> AttributeError."""
        settings_obj = AppSettings(prefix="TEST_")

        # Test with setting in Django settings
        with override_settings(TEST_CUSTOM_SETTING="django_value"):
            assert settings_obj.CUSTOM_SETTING == "django_value"

        # Test with setting only in defaults
        assert settings_obj.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS

        # Test with setting in neither
        with pytest.raises(AttributeError):
            _ = settings_obj.NONEXISTENT_SETTING


@pytest.mark.django_db
class TestConfiguration:
    """Test configuration settings."""

    def test_default_excluded_terms(self):
        """Test that DEFAULT_EXCLUDED_TERMS is properly configured."""
        excluded_terms = app_settings.DEFAULT_EXCLUDED_TERMS
        assert isinstance(excluded_terms, list)
        assert "_ptr" in excluded_terms
        assert "uuid" in excluded_terms

    def test_do_not_register_filter_string_list(self):
        """Test that DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST is properly configured."""
        filter_list = app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
        assert isinstance(filter_list, list)
        assert "Historical" in filter_list

    def test_admin_tuple_attributes_to_list(self):
        """Test that ADMIN_TUPLE_ATTRIBUTES_TO_LIST is properly configured."""
        attributes = app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST
        assert isinstance(attributes, list)
        assert "list_display" in attributes
        assert "list_filter" in attributes

    def test_reorder_linkify_fields_default(self):
        """Test that REORDER_LINKIFY_FIELDS defaults to True."""
        assert app_settings.REORDER_LINKIFY_FIELDS is True

    @override_settings(AUTO_ADMIN_REORDER_LINKIFY_FIELDS=False)
    def test_reorder_linkify_fields_can_be_disabled(self):
        """Test that REORDER_LINKIFY_FIELDS can be disabled via settings."""
        # Re-import to get updated settings
        from django_admin_magic.conf import app_settings as updated_settings

        assert updated_settings.REORDER_LINKIFY_FIELDS is False

    @override_settings(AUTO_ADMIN_REORDER_LINKIFY_FIELDS=True)
    def test_reorder_linkify_fields_can_be_enabled(self):
        """Test that REORDER_LINKIFY_FIELDS can be enabled via settings."""
        # Re-import to get updated settings
        from django_admin_magic.conf import app_settings as updated_settings

        assert updated_settings.REORDER_LINKIFY_FIELDS is True

    def test_reorder_linkify_fields_functionality(self):
        """Test that the reordering function works correctly."""
        linkify_func = linkify("parent")

        # Test with linkify first
        original_list = [linkify_func, "name", "created_at"]
        reordered = reorder_list_display_to_avoid_linkify_first(original_list)

        # Should reorder to move linkify after first non-linkify field
        assert reordered == ["name", linkify_func, "created_at"]

        # Test with linkify not first (should not change)
        original_list2 = ["name", linkify_func, "created_at"]
        reordered2 = reorder_list_display_to_avoid_linkify_first(original_list2)
        assert reordered2 == original_list2
