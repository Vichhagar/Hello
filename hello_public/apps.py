from django.apps import AppConfig


class HelloPublicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hello_public'

    def ready(self):
        print('signals import...')
        import hello_public.signals  # noqa
