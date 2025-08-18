from django.apps import AppConfig


class DrfchelseruConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "drfchelseru"

    def ready(self):
        import drfchelseru.signals
