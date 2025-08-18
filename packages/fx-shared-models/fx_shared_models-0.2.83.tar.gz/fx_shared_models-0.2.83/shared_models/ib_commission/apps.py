from django.apps import AppConfig


class IBCommissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.ib_commission'
    label = 'ib_commission'
    verbose_name = "IB Commission"
    
    def ready(self):
        # Import any signals here
        pass 