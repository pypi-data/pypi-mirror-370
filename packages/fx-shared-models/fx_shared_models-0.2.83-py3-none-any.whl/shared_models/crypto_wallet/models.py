from django.db import models
from ..common.base import BaseModel

class CompanyCryptoWallet(BaseModel):
    id = models.AutoField(primary_key=True, editable=False)
    address = models.CharField(max_length=255)
    network = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    show_only_in_countries = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of country codes where this wallet should be shown")
    excluded_countries = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of country codes where this wallet should NOT be shown")

    class Meta:
        app_label = 'shared_company_crypto_wallet'
        db_table = 'company_crypto_wallets'
        verbose_name = 'Company Crypto Wallet'
        verbose_name_plural = 'Company Crypto Wallets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['address', 'network']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Company Crypto Wallet {self.address} ({self.network}/{self.token})"
