from django.apps import AppConfig


class PortmanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portman'  # Make sure this matches the folder name (case-sensitive)

    def ready(self):
        from . import signals  # Import signals here
