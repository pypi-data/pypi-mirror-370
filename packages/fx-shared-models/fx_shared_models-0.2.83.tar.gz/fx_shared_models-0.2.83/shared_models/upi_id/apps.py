from django.apps import AppConfig


class CompanyUpiIdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.upi_id'
    verbose_name = 'Company UPI IDs'
    label = 'shared_company_upi_id'
