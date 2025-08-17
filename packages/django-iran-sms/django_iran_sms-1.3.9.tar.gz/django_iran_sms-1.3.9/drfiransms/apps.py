from django.apps import AppConfig


class DrfiransmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drfiransms'

    def ready(self):
        import drfiransms.signals
