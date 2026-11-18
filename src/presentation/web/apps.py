from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.presentation.web"
    label = "web"
    verbose_name = "Web"
