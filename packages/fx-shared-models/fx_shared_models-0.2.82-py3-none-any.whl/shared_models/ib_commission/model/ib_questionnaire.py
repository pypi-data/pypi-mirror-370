from django.db import models
from django.utils import timezone
from shared_models.common.base import BaseModel


class IBQuestionnaire(BaseModel):
    """
    IB business information questionnaire - unified for all flows.
    Can be created from CP (with IBRequest) or CRM (standalone).
    """
    customer = models.OneToOneField(
        'customers.Customer', 
        on_delete=models.CASCADE,
        related_name='ib_questionnaire'
    )
    
    # Business Information
    target_countries = models.JSONField(
        help_text="List of country codes the IB plans to target"
    )
    expected_clients = models.IntegerField(
        help_text="Expected number of clients per month"
    )
    have_site = models.CharField(
        max_length=255,
        help_text="Whether IB has a website/platform"
    )
    get_client = models.TextField(
        help_text="How the IB plans to acquire clients"
    )
    ref_other = models.TextField(
        blank=True,
        help_text="Previous experience or other referral information"
    )
    
    # Metadata
    source = models.CharField(
        max_length=10, 
        choices=[
            ('CP', 'Client Portal'),
            ('CRM', 'CRM')
        ],
        help_text="Where the questionnaire was submitted from"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(
        'users.CRMUser', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        help_text="CRM user who submitted on behalf of IB (if source=CRM)"
    )
    
    class Meta:
        db_table = 'ib_questionnaire'
        app_label = 'ib_commission'
        verbose_name = 'IB Questionnaire'
        verbose_name_plural = 'IB Questionnaires'
        
    def __str__(self):
        return f"IB Questionnaire for {self.customer.email}"