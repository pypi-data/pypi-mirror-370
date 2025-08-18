from django.apps import AppConfig

class SystemSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.system_settings'
    verbose_name = 'System Settings'
    
    def ready(self):
        try:
            import shared_models.system_settings.signals  # noqa
        except ImportError:
            pass 