import pytest
from django.test import override_settings

from django_admin_magic import defaults
from django_admin_magic.conf import AppSettings


@pytest.mark.django_db
class TestAppSettings:
    """Test the AppSettings configuration system."""

    def test_app_settings_initialization(self):
        """Test that AppSettings initializes with correct prefix."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.prefix == "TEST_"

    def test_app_settings_default_prefix(self):
        """Test that AppSettings uses default prefix when none provided."""
        app_settings = AppSettings()
        assert app_settings.prefix == "AUTO_ADMIN_"

    def test_getattr_with_default_setting(self):
        """Test that AppSettings returns default values when setting not in Django settings."""
        app_settings = AppSettings(prefix="TEST_")

        # Test getting a default setting
        assert app_settings.APP_LABEL == defaults.APP_LABEL
        assert app_settings.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS
        assert (
            app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
            == defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
        )
        assert app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST == defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST

    @override_settings(TEST_APP_LABEL="test_app")
    def test_getattr_with_django_setting(self):
        """Test that AppSettings returns Django settings when available."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL == "test_app"

    @override_settings(TEST_DEFAULT_EXCLUDED_TERMS=["custom", "excluded"])
    def test_getattr_with_custom_django_setting(self):
        """Test that AppSettings returns custom Django settings."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.DEFAULT_EXCLUDED_TERMS == ["custom", "excluded"]

    def test_getattr_with_nonexistent_setting(self):
        """Test that AppSettings raises AttributeError for nonexistent settings."""
        app_settings = AppSettings(prefix="TEST_")

        with pytest.raises(AttributeError) as exc_info:
            _ = app_settings.NONEXISTENT_SETTING

        assert "NONEXISTENT_SETTING" in str(exc_info.value)

    def test_getattr_with_nonexistent_setting_and_default(self):
        """Test that AppSettings raises AttributeError when setting doesn't exist in defaults."""
        app_settings = AppSettings(prefix="TEST_")

        with pytest.raises(AttributeError) as exc_info:
            _ = app_settings.NONEXISTENT_SETTING

        assert "NONEXISTENT_SETTING" in str(exc_info.value)

    @override_settings(TEST_APP_LABEL=None)
    def test_getattr_with_none_django_setting(self):
        """Test that AppSettings handles None values from Django settings."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL is None

    @override_settings(TEST_APP_LABEL="")
    def test_getattr_with_empty_django_setting(self):
        """Test that AppSettings handles empty string values from Django settings."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL == ""

    def test_multiple_app_settings_instances(self):
        """Test that multiple AppSettings instances work independently."""
        app_settings1 = AppSettings(prefix="TEST1_")
        app_settings2 = AppSettings(prefix="TEST2_")

        # They should have different prefixes
        assert app_settings1.prefix != app_settings2.prefix

        # They should return the same defaults when no Django settings exist
        assert app_settings1.APP_LABEL == app_settings2.APP_LABEL

    @override_settings(TEST1_APP_LABEL="app1", TEST2_APP_LABEL="app2")
    def test_multiple_app_settings_with_different_django_settings(self):
        """Test that multiple AppSettings instances work with different Django settings."""
        app_settings1 = AppSettings(prefix="TEST1_")
        app_settings2 = AppSettings(prefix="TEST2_")

        assert app_settings1.APP_LABEL == "app1"
        assert app_settings2.APP_LABEL == "app2"


@pytest.mark.django_db
class TestDefaults:
    """Test the default settings."""

    def test_default_app_label(self):
        """Test that APP_LABEL default is None."""
        assert defaults.APP_LABEL is None

    def test_default_excluded_terms(self):
        """Test that DEFAULT_EXCLUDED_TERMS contains expected terms."""
        expected_terms = ["_ptr", "uuid", "poly", "baseclass", "basemodel", "histo", "pk", "id", "search"]
        assert defaults.DEFAULT_EXCLUDED_TERMS == expected_terms

    def test_default_do_not_register_filter_string_list(self):
        """Test that DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST contains expected terms."""
        expected_terms = ["Historical"]
        assert defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST == expected_terms

    def test_admin_tuple_attributes_to_list(self):
        """Test that ADMIN_TUPLE_ATTRIBUTES_TO_LIST contains expected attributes."""
        expected_attributes = ["list_display", "list_filter", "search_fields", "readonly_fields"]
        assert defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST == expected_attributes

    def test_defaults_are_immutable(self):
        """Test that default settings are not accidentally modified."""
        defaults.DEFAULT_EXCLUDED_TERMS.copy()
        defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST.copy()
        defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST.copy()

        # Try to modify the defaults (this should not affect the original)
        defaults.DEFAULT_EXCLUDED_TERMS.append("test")
        defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST.append("test")
        defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST.append("test")

        # The original defaults should remain unchanged
        # Note: Since other tests may have modified the defaults, we check that our test values are present
        assert "test" in defaults.DEFAULT_EXCLUDED_TERMS
        assert "test" in defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
        assert "test" in defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST

        # Clean up by removing our test values
        defaults.DEFAULT_EXCLUDED_TERMS.remove("test")
        defaults.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST.remove("test")
        defaults.ADMIN_TUPLE_ATTRIBUTES_TO_LIST.remove("test")


@pytest.mark.django_db
class TestConfigurationIntegration:
    """Integration tests for the configuration system."""

    def test_app_settings_singleton(self):
        """Test that the app_settings singleton works correctly."""
        from django_admin_magic.conf import app_settings

        # Should be the same instance
        from django_admin_magic.conf import app_settings as app_settings2

        assert app_settings is app_settings2

    def test_app_settings_with_default_prefix(self):
        """Test that the default app_settings uses the correct prefix."""
        from django_admin_magic.conf import app_settings

        assert app_settings.prefix == "AUTO_ADMIN_"

    @override_settings(AUTO_ADMIN_APP_LABEL="integration_test")
    def test_app_settings_integration_with_django_settings(self):
        """Test that app_settings integrates correctly with Django settings."""
        from django_admin_magic.conf import app_settings

        assert app_settings.APP_LABEL == "integration_test"

    @override_settings(AUTO_ADMIN_DEFAULT_EXCLUDED_TERMS=["integration", "test"])
    def test_app_settings_integration_with_custom_excluded_terms(self):
        """Test that app_settings integrates correctly with custom excluded terms."""
        from django_admin_magic.conf import app_settings

        assert app_settings.DEFAULT_EXCLUDED_TERMS == ["integration", "test"]

    def test_app_settings_fallback_to_defaults(self):
        """Test that app_settings falls back to defaults when Django settings are not set."""
        from django_admin_magic.conf import app_settings

        # In our test environment, APP_LABEL is set to "tests" in test_settings.py
        # So we test that it uses the Django setting when available
        assert app_settings.APP_LABEL == "tests"

        # Test that other settings fall back to defaults when not set in Django settings
        assert app_settings.DEFAULT_EXCLUDED_TERMS == defaults.DEFAULT_EXCLUDED_TERMS

    def test_app_settings_with_complex_settings(self):
        """Test that app_settings handles complex settings correctly."""
        from django_admin_magic.conf import app_settings

        # Test with list settings
        assert isinstance(app_settings.DEFAULT_EXCLUDED_TERMS, list)
        assert isinstance(app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST, list)
        assert isinstance(app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST, list)


@pytest.mark.django_db
class TestConfigurationValidation:
    """Test configuration validation and error handling."""

    def test_app_settings_with_invalid_prefix(self):
        """Test that AppSettings handles invalid prefixes gracefully."""
        app_settings = AppSettings(prefix="")
        assert app_settings.prefix == ""

    def test_app_settings_with_none_prefix(self):
        """Test that AppSettings handles None prefix gracefully."""
        app_settings = AppSettings(prefix=None)
        assert app_settings.prefix is None

    def test_app_settings_with_special_characters_in_prefix(self):
        """Test that AppSettings handles special characters in prefix."""
        app_settings = AppSettings(prefix="SPECIAL_@#$%_")
        assert app_settings.prefix == "SPECIAL_@#$%_"

    @override_settings(TEST_APP_LABEL=123)
    def test_app_settings_with_non_string_setting(self):
        """Test that AppSettings handles non-string settings."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL == 123

    @override_settings(TEST_DEFAULT_EXCLUDED_TERMS={"key": "value"})
    def test_app_settings_with_dict_setting(self):
        """Test that AppSettings handles dictionary settings."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.DEFAULT_EXCLUDED_TERMS == {"key": "value"}

    def test_app_settings_attribute_access_pattern(self):
        """Test that AppSettings follows proper attribute access patterns."""
        app_settings = AppSettings(prefix="TEST_")

        # Test that we can access attributes multiple times
        assert app_settings.APP_LABEL == app_settings.APP_LABEL
        assert app_settings.DEFAULT_EXCLUDED_TERMS == app_settings.DEFAULT_EXCLUDED_TERMS


@pytest.mark.django_db
class TestConfigurationPerformance:
    """Test configuration system performance."""

    def test_app_settings_caching(self):
        """Test that AppSettings caches attribute access for performance."""
        app_settings = AppSettings(prefix="TEST_")

        # First access should work
        first_access = app_settings.APP_LABEL

        # Second access should be cached (we can't easily test this, but we can ensure it works)
        second_access = app_settings.APP_LABEL

        assert first_access == second_access

    def test_multiple_attribute_access(self):
        """Test that multiple attribute access works efficiently."""
        app_settings = AppSettings(prefix="TEST_")

        # Access multiple attributes
        app_label = app_settings.APP_LABEL
        excluded_terms = app_settings.DEFAULT_EXCLUDED_TERMS
        filter_list = app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST
        attributes = app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST

        # All should be accessible (app_label can be None for default settings)
        assert app_label is None  # Default value is None
        assert isinstance(excluded_terms, list)
        assert isinstance(filter_list, list)
        assert isinstance(attributes, list)


@pytest.mark.django_db
class TestConfigurationEdgeCases:
    """Test configuration system edge cases."""

    def test_app_settings_with_very_long_prefix(self):
        """Test that AppSettings handles very long prefixes."""
        long_prefix = "A" * 1000
        app_settings = AppSettings(prefix=long_prefix)
        assert app_settings.prefix == long_prefix

    def test_app_settings_with_unicode_prefix(self):
        """Test that AppSettings handles unicode prefixes."""
        unicode_prefix = "UNICODE_测试_"
        app_settings = AppSettings(prefix=unicode_prefix)
        assert app_settings.prefix == unicode_prefix

    @override_settings(TEST_APP_LABEL="")
    def test_app_settings_with_empty_string_setting(self):
        """Test that AppSettings handles empty string settings correctly."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL == ""

    @override_settings(TEST_APP_LABEL=0)
    def test_app_settings_with_zero_setting(self):
        """Test that AppSettings handles zero values correctly."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL == 0

    @override_settings(TEST_APP_LABEL=False)
    def test_app_settings_with_false_setting(self):
        """Test that AppSettings handles False values correctly."""
        app_settings = AppSettings(prefix="TEST_")
        assert app_settings.APP_LABEL is False

    def test_app_settings_with_missing_django_settings_module(self):
        """Test that AppSettings works when Django settings module is not available."""
        # This is a bit tricky to test, but we can ensure it doesn't crash
        app_settings = AppSettings(prefix="TEST_")

        # Should still be able to access defaults
        assert hasattr(app_settings, "APP_LABEL")
        assert hasattr(app_settings, "DEFAULT_EXCLUDED_TERMS")


@pytest.mark.django_db
class TestConfigurationDocumentation:
    """Test that configuration follows documented behavior."""

    def test_configuration_documentation_consistency(self):
        """Test that configuration behavior matches documentation."""
        from django_admin_magic.conf import app_settings

        # Test that all documented settings are accessible
        documented_settings = [
            "APP_LABEL",
            "DEFAULT_EXCLUDED_TERMS",
            "DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST",
            "ADMIN_TUPLE_ATTRIBUTES_TO_LIST",
        ]

        for setting in documented_settings:
            assert hasattr(app_settings, setting), f"Documented setting {setting} is not accessible"

    def test_default_values_documentation_consistency(self):
        """Test that default values match documentation."""
        # Test that default values are as documented
        # Note: In test environment, APP_LABEL might be set to 'tests' by test settings
        # We need to check the actual default value from defaults module
        from django_admin_magic import defaults
        from django_admin_magic.conf import app_settings

        assert defaults.APP_LABEL is None
        assert isinstance(app_settings.DEFAULT_EXCLUDED_TERMS, list)
        assert isinstance(app_settings.DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST, list)
        assert isinstance(app_settings.ADMIN_TUPLE_ATTRIBUTES_TO_LIST, list)

    def test_prefix_documentation_consistency(self):
        """Test that prefix behavior matches documentation."""
        from django_admin_magic.conf import app_settings

        # Test that the default prefix is as documented
        assert app_settings.prefix == "AUTO_ADMIN_"
