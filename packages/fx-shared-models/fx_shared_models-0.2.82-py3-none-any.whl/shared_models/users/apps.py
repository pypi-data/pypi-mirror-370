from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.users'
    verbose_name = 'Shared Users'
    label = 'users'
    
    def ready(self):
        print("DEBUG: Shared Users app is being loaded!")