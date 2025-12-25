from django.apps import AppConfig


class MuseumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'museum'
    verbose_name = 'Музейный комплекс'

    def ready(self):
        import museum.signals
