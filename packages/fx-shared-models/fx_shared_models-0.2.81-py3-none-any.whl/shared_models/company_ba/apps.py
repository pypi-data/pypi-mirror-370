from django.apps import AppConfig

class CompanyBankAccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.company_ba'
    verbose_name = 'Company Bank Accounts'

    def ready(self):
        pass
