from django.apps import AppConfig, apps

from .conf import app_settings


class DjangoAutoAdminConfig(AppConfig):
    name = "django_admin_magic"
    verbose_name = "Django Auto Admin"

    def ready(self):
        if "polymorphic" in apps.app_configs:
            from .registrar import PolymorphicAdminModelRegistrar as Registrar
        else:
            from .registrar import AdminModelRegistrar as Registrar

        # Check if we should auto-discover all apps
        if hasattr(app_settings, "AUTO_DISCOVER_ALL_APPS") and app_settings.AUTO_DISCOVER_ALL_APPS:
            self.registrar = Registrar.register_all_discovered_apps()
            return

        # Check for multiple app labels
        if hasattr(app_settings, "APP_LABELS") and app_settings.APP_LABELS:
            self.registrar = Registrar.register_apps(app_settings.APP_LABELS)
            return

        # Check for single app label
        app_label = app_settings.APP_LABEL
        if app_label:
            if isinstance(app_label, list):
                self.registrar = Registrar.register_apps(app_label)
            else:
                self.registrar = Registrar.register_app(app_label)
            return

        # If no configuration is provided, don't create a registrar
        # Users can create one manually in their admin.py files
        self.registrar = None
