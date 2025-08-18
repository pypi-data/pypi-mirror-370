from django.apps import AppConfig

class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.transactions'
    verbose_name = 'Transactions'

    def ready(self):
        try:
            import shared_models.transactions.signals  # noqa
        except ImportError:
            pass 