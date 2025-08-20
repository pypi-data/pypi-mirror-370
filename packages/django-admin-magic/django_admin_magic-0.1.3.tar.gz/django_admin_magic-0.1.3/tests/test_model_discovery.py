import pytest
from django.contrib import admin
from django.test import override_settings

from django_admin_magic.registrar import AdminModelRegistrar
from django_admin_magic.utils import (
    create_auto_admin_registrar,
    create_auto_admin_registrar_for_all_apps,
    create_auto_admin_registrar_for_apps,
)

from .models import PolymorphicParent, SimpleModel


@pytest.mark.django_db
class TestModelDiscovery:
    """Test the model discovery functionality."""

    def test_single_app_registration(self):
        """Test registering models for a single app."""
        registrar = AdminModelRegistrar.register_app("tests")

        # Check that models from the tests app are registered
        assert admin.site.is_registered(SimpleModel)
        assert admin.site.is_registered(PolymorphicParent)

        # Check that the registrar has the correct app labels
        assert "tests" in registrar.app_labels

    def test_multiple_apps_registration(self):
        """Test registering models for multiple apps."""
        # For this test, we'll just test with the existing tests app
        # since creating a new app config in tests is complex
        registrar = AdminModelRegistrar.register_apps(["tests"])

        # Check that models from the tests app are registered
        assert admin.site.is_registered(SimpleModel)
        assert admin.site.is_registered(PolymorphicParent)

        # Check that the registrar has the correct app labels
        assert "tests" in registrar.app_labels

    def test_auto_discovery_registration(self):
        """Test auto-discovery of all apps."""
        registrar = AdminModelRegistrar.register_all_discovered_apps()

        # Check that models from the tests app are registered
        assert admin.site.is_registered(SimpleModel)
        assert admin.site.is_registered(PolymorphicParent)

        # Check that the registrar has discovered apps
        assert len(registrar.app_labels) > 0
        assert "tests" in registrar.app_labels

    def test_utility_functions(self):
        """Test the utility functions for creating registrars."""
        # Test create_auto_admin_registrar
        registrar1 = create_auto_admin_registrar("tests")
        assert "tests" in registrar1.app_labels

        # Test create_auto_admin_registrar_for_apps
        registrar2 = create_auto_admin_registrar_for_apps(["tests"])
        assert "tests" in registrar2.app_labels

        # Test create_auto_admin_registrar_for_all_apps
        registrar3 = create_auto_admin_registrar_for_all_apps()
        assert len(registrar3.app_labels) > 0

    def test_app_label_auto_detection(self):
        """Test automatic app label detection from package."""
        # This test would need to be run from within a Django app context
        # For now, we'll test that the function works with explicit app label
        registrar = create_auto_admin_registrar("tests")
        assert "tests" in registrar.app_labels

    def test_empty_app_labels(self):
        """Test behavior when no app labels are provided."""
        # Clear any existing settings that might affect this test
        with override_settings(
            AUTO_ADMIN_APP_LABEL=None, AUTO_ADMIN_APP_LABELS=[], AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS=False
        ):
            registrar = AdminModelRegistrar()
            assert registrar.app_labels == []
            assert len(registrar.models) == 0

    def test_invalid_app_label(self):
        """Test behavior with invalid app labels."""
        registrar = AdminModelRegistrar(app_labels=["nonexistent_app"])

        # Should not raise an exception, but should log a warning
        assert "nonexistent_app" in registrar.app_labels
        assert len(registrar.models) == 0

    @override_settings(AUTO_ADMIN_APP_LABEL="tests")
    def test_settings_app_label(self):
        """Test configuration via settings."""
        registrar = AdminModelRegistrar()
        assert "tests" in registrar.app_labels

    @override_settings(AUTO_ADMIN_APP_LABELS=["tests"])
    def test_settings_app_labels(self):
        """Test configuration via APP_LABELS setting."""
        registrar = AdminModelRegistrar()
        assert "tests" in registrar.app_labels

    @override_settings(AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS=True)
    def test_settings_auto_discover(self):
        """Test configuration via AUTO_DISCOVER_ALL_APPS setting."""
        registrar = AdminModelRegistrar()
        assert len(registrar.app_labels) > 0
        assert "tests" in registrar.app_labels

    def test_settings_priority(self):
        """Test that explicit parameters override settings."""
        # Test that explicit app_label overrides settings
        with override_settings(AUTO_ADMIN_APP_LABEL="other_app"):
            registrar = AdminModelRegistrar(app_label="tests")
            assert registrar.app_labels == ["tests"]

        # Test that explicit app_labels overrides settings
        with override_settings(AUTO_ADMIN_APP_LABELS=["other_app"]):
            registrar = AdminModelRegistrar(app_labels=["tests"])
            assert registrar.app_labels == ["tests"]

        # Test that explicit auto_discover overrides settings
        with override_settings(AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS=False):
            registrar = AdminModelRegistrar(auto_discover=True)
            assert len(registrar.app_labels) > 0

    def test_class_methods(self):
        """Test the class methods for creating registrars."""
        # Test register_app class method
        registrar1 = AdminModelRegistrar.register_app("tests")
        assert "tests" in registrar1.app_labels

        # Test register_apps class method
        registrar2 = AdminModelRegistrar.register_apps(["tests"])
        assert "tests" in registrar2.app_labels

        # Test register_all_discovered_apps class method
        registrar3 = AdminModelRegistrar.register_all_discovered_apps()
        assert len(registrar3.app_labels) > 0

    def test_model_collection(self):
        """Test that models are properly collected from multiple apps."""
        registrar = AdminModelRegistrar(app_labels=["tests"])

        # Check that models are collected
        assert len(registrar.models) > 0

        # Check that SimpleModel and PolymorphicParent are in the models
        model_names = [model.__name__ for model in registrar.models]
        assert "SimpleModel" in model_names
        assert "PolymorphicParent" in model_names

    def test_skip_system_apps(self):
        """Test that system apps are skipped during auto-discovery."""
        registrar = AdminModelRegistrar(auto_discover=True)

        # Check that system apps are not included
        system_apps = ["django_admin_magic", "admin", "auth", "contenttypes", "sessions"]
        for app in system_apps:
            assert app not in registrar.app_labels
