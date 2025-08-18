from django.db import models
from ..common.base import BaseModel

class  CompanyBankAccount(BaseModel):
    id = models.AutoField(primary_key=True, editable=False)
    bank_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    iban = models.CharField(max_length=255)
    swift = models.CharField(max_length=255)
    ifsc = models.CharField(max_length=255)
    address = models.TextField(blank=True, default='')
    account_holder_name = models.CharField(max_length=255, default='')

    class Meta:
        app_label = 'company_ba'
        db_table = 'company_bank_accounts'
        verbose_name = 'Company Bank Account'
        verbose_name_plural = 'Company Bank Accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bank_name', 'country']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f"Bank Account {self.bank_name} ({self.account_number})"
