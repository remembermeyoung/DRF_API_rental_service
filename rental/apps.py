from django.apps import AppConfig


class RentalV2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rental'

    def ready(self):
        from . import signals