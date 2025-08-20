from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render


def index(request):
    """Landing page for the demo app."""
    # Get all models from the demo_app
    demo_app_config = apps.get_app_config("demo_app")
    models = demo_app_config.get_models()

    # Prepare model data for template
    model_data = []
    for model in models:
        # Get model documentation
        doc = getattr(model, "__doc__", "") or ""
        if doc:
            doc = doc.strip()

        model_data.append(
            {
                "name": model._meta.verbose_name_plural.title(),
                "doc": doc,
                "fields": [{"name": field.name, "type": field.get_internal_type()} for field in model._meta.fields]
                + [{"name": field.name, "type": "ManyToMany"} for field in model._meta.many_to_many],
            }
        )

    # Get admin site info
    admin_site = admin.site

    context = {
        "models": model_data,
        "admin_site": admin_site,
        "has_superuser": User.objects.filter(is_superuser=True).exists(),
    }

    return render(request, "demo_app/index.html", context)
