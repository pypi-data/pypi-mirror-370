from django.apps import AppConfig


class CustomerUPIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.customer_upi'
    label = 'shared_customer_upi'
    verbose_name = 'Customer UPI'
