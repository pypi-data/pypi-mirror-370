from django.apps import AppConfig


class CustomerCryptoWalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.customer_crypto_wallet'
    label = 'shared_customer_crypto_wallet'
    verbose_name = 'Customer Crypto Wallet'
