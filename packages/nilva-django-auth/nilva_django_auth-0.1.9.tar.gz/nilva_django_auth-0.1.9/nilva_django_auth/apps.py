from django.apps import AppConfig


class NilvaDjangoAuthConfig(AppConfig):
    name = 'nilva_django_auth'
    verbose_name = 'Nilva Django Authentication'
    
    def ready(self):
        # Import signal handlers or perform other initialization
        pass
