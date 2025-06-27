from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_des_resultats'
    verbose_name = "GESTION DES RESULTATS"


def ready(self):
    import gestion_des_resultats.signals
