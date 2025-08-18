from django.db import models
from ...common.base import BaseModel

class AccountType(BaseModel):
    """
    Account type model for managing different trading account configurations
    """
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=50)
    server = models.ForeignKey('system_settings.TradingPlatformServer', 
                             on_delete=models.PROTECT,
                             related_name='account_types')
    
    # Trading Configuration
    min_first_deposit = models.IntegerField(default=0)
    leverages = models.JSONField(default=list)
    default_leverage = models.IntegerField(default=100)

    # Default MT5 Group
    default_group = models.CharField(
        max_length=100,
        help_text="Default MT5 group if no group configuration exists"
    )
    
    # Display Configuration
    is_active = models.BooleanField(default=True)
    show_cp = models.BooleanField(default=False)
    show_crm = models.BooleanField(default=False)
    show_agreement = models.BooleanField(default=False)
    sequence = models.ForeignKey('system_settings.AccountSequence', 
                             on_delete=models.PROTECT,
                             related_name='account_types')
    
    # Account Configuration
    account_type = models.CharField(
        max_length=10,
        choices=[('LIVE', 'LIVE'), ('DEMO', 'DEMO'), ('IB', 'IB')],
        default='LIVE'
    )
    platform = models.CharField(
        max_length=10,
        choices=[('MT5', 'MT5'), ('MT4', 'MT4'), ('VERTEX', 'VERTEX')],
        default='MT5'
    )
    max_unapproved_accounts = models.IntegerField(default=0)
    
    # Demo Account Configuration
    demo_auto_deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10000.00,
        help_text="Auto deposit amount for demo accounts in USD"
    )

    class Meta:
        app_label = 'system_settings'
        db_table = 'account_types'
        verbose_name = 'Account Type'
        verbose_name_plural = 'Account Types'
        unique_together = [['name', 'server']]
        permissions = [
            ('manage_account_type_groups', 'Can manage account type groups'),
        ]

    def __str__(self):
        return f"{self.name} ({self.server.name})" 