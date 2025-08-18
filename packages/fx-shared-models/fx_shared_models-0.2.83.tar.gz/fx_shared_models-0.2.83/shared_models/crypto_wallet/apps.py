from django.apps import AppConfig


class CompanyCryptoWalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared_models.crypto_wallet'
    verbose_name = 'Company Crypto Wallets'
    label = 'shared_company_crypto_wallet'
