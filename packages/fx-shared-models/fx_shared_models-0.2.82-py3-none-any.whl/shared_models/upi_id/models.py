from django.db import models
from ..common.base import BaseModel

class CompanyUpiId(BaseModel):
    id = models.AutoField(primary_key=True, editable=False)
    upi_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    bank = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    show_only_in_countries = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of country codes where this UPI ID should be shown")
    excluded_countries = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of country codes where this UPI ID should NOT be shown")

    class Meta:
        app_label = 'shared_company_upi_id'
        db_table = 'company_upi_ids'
        verbose_name = 'Company UPI ID'
        verbose_name_plural = 'Company UPI IDs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['upi_id', 'bank']),
            models.Index(fields=['owner_name']),
        ]

    def __str__(self):
        return f"Company UPI ID {self.upi_id} ({self.owner_name})"
