from django.apps import AppConfig

class ReferralsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.referrals'
    verbose_name = 'Shared Referrals'
    label = 'referrals'
    
    def ready(self):
        print("DEBUG: Shared Referrals app is being loaded!")