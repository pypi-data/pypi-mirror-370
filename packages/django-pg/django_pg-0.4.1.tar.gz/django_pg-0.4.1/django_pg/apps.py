from django.apps import AppConfig

class GatewaysConfig(AppConfig):
    name = 'django_pg'

    def ready(self):
        import django_pg.signals
