from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.accounts'
    label = 'accounts'
    verbose_name = 'Accounts'

    def ready(self):
        try:
            import shared_models.accounts.signals  # noqa
        except ImportError:
            pass 