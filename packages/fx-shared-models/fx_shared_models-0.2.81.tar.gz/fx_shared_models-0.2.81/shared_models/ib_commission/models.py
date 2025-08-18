"""
Models for the IB (Introducing Broker) Commission System.

This module contains models for managing IB hierarchies, agreements, commission rules,
and tracking of commission distribution as detailed in the IB Commission Implementation Guide.
"""
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from shared_models.common.base import BaseModel
from shared_models.trading.models import Deal


logger = logging.getLogger(__name__)


class IBHierarchy(BaseModel):
    """
    Tracks the hierarchical relationships between IBs (Introducing Brokers).
    
    This model maintains the parent-child relationships between IBs,
    allowing for multi-level IB structures and commission distribution.
    """
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='ib_hierarchy')
    parent_customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, 
                                       blank=True, related_name='child_ibs')
    level = models.IntegerField(help_text='0 for master IB, increments for each level down')
    path = models.TextField(help_text='Stored as dot-separated customer ids, e.g., "1001.1002.1003"')
    
    # Add account reference while keeping mt5_login for backward compatibility
    ib_account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT, 
                                 related_name='ib_hierarchy_entry', null=True, blank=True,
                                 help_text='IB account that receives commissions')
    mt5_login = models.IntegerField(help_text='MT5 login for deal processing')
    
    default_agreement = models.ForeignKey(
        'IBAgreement', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='default_for_hierarchies',
        help_text='Default agreement when not specified in client mapping'
    )
    
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Override save to keep ib_account and mt5_login in sync.
        If ib_account is provided, update mt5_login to match.
        """
        if self.ib_account and self.ib_account.login != self.mt5_login:
            self.mt5_login = self.ib_account.login
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_hierarchy'
        verbose_name = 'IB Hierarchy'
        verbose_name_plural = 'IB Hierarchies'
        indexes = [
            models.Index(fields=['mt5_login']),
            models.Index(fields=['path']),
            models.Index(fields=['customer', 'is_active'], name='idx_hierarchy_lookup'),
            models.Index(fields=['path'], name='idx_hierarchy_path'),  # For path__contains queries
        ]
        constraints = [
            models.UniqueConstraint(fields=['customer'], name='unique_customer_in_hierarchy')
        ]


class IBAgreement(BaseModel):
    """
    Represents an IB commission agreement.
    
    This is the base agreement model that contains general information about the agreement.
    Specific commission rules are defined in the IBCommissionRule model.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_agreements'
        verbose_name = 'IB Agreement'
        verbose_name_plural = 'IB Agreements'

class ClientIBMapping(BaseModel):
    """
    Maps clients to their IBs in the hierarchy.
    
    This model maintains the relationship between clients and their IBs,
    including information about the direct IB and the master IB.
    """
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                               related_name='client_ib_mappings')
    direct_ib_customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                                        related_name='direct_clients')
    master_ib_customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                                        related_name='all_hierarchy_clients')
    agreement = models.ForeignKey(IBAgreement, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='client_mappings', 
                               help_text='Default agreement for this client-IB relationship')
    ib_path = models.TextField(help_text='Full path of IBs using customer ids')
    mt5_login = models.IntegerField(help_text="Client's MT5 login", null=True, blank=True)
    agreement_path = models.TextField(
        null=True, 
        blank=True,
        help_text='Agreement IDs for each IB level in hierarchy (dot-separated). Empty positions use IB default.'
    )

    class Meta:
        app_label = 'ib_commission'
        db_table = 'client_ib_mapping'
        verbose_name = 'Client IB Mapping'
        verbose_name_plural = 'Client IB Mappings'
        indexes = [
            models.Index(fields=['mt5_login']),
            models.Index(fields=['customer']),
            models.Index(fields=['mt5_login', 'customer'], name='idx_client_mapping_lookup'),
            models.Index(fields=['customer', 'direct_ib_customer'], name='idx_client_mapping_ib'),
        ]


class IBAgreementMember(BaseModel):
    """
    Links customers (IBs) to agreements.
    
    This model associates IBs with specific agreements and tracks
    when the agreement is active for that IB.
    """
    agreement = models.ForeignKey(IBAgreement, on_delete=models.CASCADE, related_name='members')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                               related_name='ib_agreements')
    is_self_rebate = models.BooleanField(default=False, 
                                       help_text='Whether the IB can receive rebates from their own trading')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_agreement_members'
        verbose_name = 'IB Agreement Member'
        verbose_name_plural = 'IB Agreement Members'
        indexes = [
            models.Index(fields=['customer', 'is_active'], name='idx_agreement_member_lookup'),
            models.Index(fields=['agreement', 'is_active'], name='idx_agreement_member_reverse'),
        ]


class IBAccountAgreement(BaseModel):
    """
    Account-specific agreement assignments.
    
    This model allows for assigning specific agreements to individual
    trading accounts, overriding the default agreement for a client.
    """
    agreement = models.ForeignKey(IBAgreement, on_delete=models.PROTECT, related_name='account_agreements')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                               related_name='account_ib_agreements')
    
    # Add account reference while keeping mt5_login for backward compatibility
    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT,
                             related_name='ib_agreement_overrides', null=True, blank=True,
                             help_text='Client account with agreement override')
    mt5_login = models.IntegerField(help_text='Specific MT5 account login')
    
    ib_customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                                  related_name='ib_account_agreements')
    is_self_rebate = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        Override save to keep account and mt5_login in sync.
        If account is provided, update mt5_login to match.
        """
        if self.account and self.account.mt5_login != self.mt5_login:
            self.mt5_login = self.account.mt5_login
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_account_agreements'
        verbose_name = 'IB Account Agreement'
        verbose_name_plural = 'IB Account Agreements'
        indexes = [
            models.Index(fields=['mt5_login']),
            models.Index(fields=['customer']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['mt5_login', 'ib_customer'], name='unique_account_ib_agreement')
        ]


class IBCommissionRule(BaseModel):
    """
    Defines rules for commission calculations.
    
    This model contains the rules for calculating commissions based on
    various factors such as account type, symbol, and calculation method.
    """
    CALCULATION_TYPES = [
        ('LOT_BASED', 'Lot Based'),
        ('PERCENTAGE', 'Percentage'),
        ('PIP_VALUE', 'Pip Value'),
        ('TIERED', 'Tiered Volume'),
    ]
    
    COMMISSION_TYPES = [
        ('REBATE', 'Rebate'),  # Broker pays IB
        ('COMMISSION', 'Commission'),  # Client pays IB
    ]
    
    agreement = models.ForeignKey(IBAgreement, on_delete=models.CASCADE, related_name='commission_rules')
    commission_type = models.CharField(max_length=10, choices=COMMISSION_TYPES, 
                                    help_text='Whether this rule applies to rebates or commissions')
    account_type = models.ForeignKey(
        'system_settings.AccountType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commission_rules',
        help_text='NULL means all account types'
    )
    symbol = models.CharField(max_length=50, null=True, blank=True, 
                            help_text='NULL means all symbols')
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES)
    value = models.DecimalField(max_digits=20, decimal_places=5, 
                              help_text='Amount per lot/percentage/pip')
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, default=1.00,
                                 help_text='Number of lots this value applies to (for LOT_BASED calculation)')
    min_volume = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                   help_text='Minimum volume (in lots) required to qualify for this rule')
    keep_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00,
                                      help_text='Percentage of commission to keep (0-100)')
    pass_up_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                         help_text='Percentage of commission to pass up to parent IB (0-100)')
    min_amount = models.DecimalField(max_digits=20, decimal_places=5, 
                                   help_text='Minimum commission amount')
    max_amount = models.DecimalField(max_digits=20, decimal_places=5, 
                                   help_text='Maximum commission amount')
    min_trade_time = models.IntegerField(default=0, 
                                       help_text='Minimum trade duration in seconds (anti-scalping)')
    conditions = models.JSONField(default=dict, blank=True, 
                                help_text='Additional conditions (volume ranges, etc)')
    priority = models.IntegerField(default=10, 
                                 help_text='Rule priority (lower number = higher priority)')

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_commission_rules'
        verbose_name = 'IB Commission Rule'
        verbose_name_plural = 'IB Commission Rules'
        indexes = [
            models.Index(fields=['agreement', 'priority']),
            models.Index(fields=['account_type', 'symbol']),
            models.Index(fields=['commission_type']),
            models.Index(fields=['agreement', 'commission_type', 'symbol'], name='idx_rule_lookup'),
            models.Index(fields=['agreement', 'commission_type', 'priority'], name='idx_rule_priority'),
            models.Index(fields=['agreement', 'account_type'], name='idx_rule_account_type'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['agreement', 'commission_type', 'account_type', 'symbol', 'calculation_type'],
                name='unique_commission_rule_config'
            ),
        ]


class CommissionTracking(BaseModel):
    """
    Tracks all commission operations.
    
    This model records the details of each commission transaction,
    including the client, IB, and commission amount.
    """
    COMMISSION_TYPES = [
        ('REBATE', 'Rebate'),
        ('COMMISSION', 'Commission'),
    ]
    deal = models.OneToOneField(Deal, on_delete=models.CASCADE, related_name='commission_tracking')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='commissions_generated')
    direct_ib_customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='direct_commissions')
    commission_type = models.CharField(max_length=10, choices=COMMISSION_TYPES)
    rule = models.ForeignKey(IBCommissionRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions')
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    processed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'commission_tracking'
        verbose_name = 'Commission Tracking'
        verbose_name_plural = 'Commission Tracking'
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['direct_ib_customer']),
            models.Index(fields=['rule']),
            models.Index(fields=['processed_time']),
        ]


class CommissionDistribution(BaseModel):
    """
    Records commission distributions to IBs.
    
    This model tracks how commissions are distributed through the IB hierarchy,
    recording the amount each IB receives from a transaction.
    """
    DISTRIBUTION_TYPES = [
        ('REBATE', 'Rebate'),
        ('COMMISSION', 'Commission'),
    ]

    PROCESSING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('DELAYED', 'Delayed - Pending Open Deal'),
        ('SKIPPED', 'Skipped'),
    ]

    DELAYED_REASON_CHOICES = [
        ('MISSING_OPEN_DEAL', 'Missing Opening Deal'),
    ]
    
    commission_tracking = models.ForeignKey(
        CommissionTracking,
        on_delete=models.PROTECT, # Or CASCADE? Consider lifecycle. PROTECT is safer initially.
        related_name='distributions',
        db_index=True # Explicitly add index if not added automatically by PROTECT/FK
    )
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='commission_distributions')
    ib_account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT, related_name='received_distributions', null=True, blank=True, help_text="IB's account receiving commissions")
    mt5_login = models.IntegerField(help_text="IB's MT5 login")
    amount = models.DecimalField(max_digits=20, decimal_places=5)
    level = models.IntegerField(help_text='IB level in the hierarchy')
    distribution_type = models.CharField(max_length=10, choices=DISTRIBUTION_TYPES)
    is_pass_up = models.BooleanField(default=False, help_text='Whether this distribution is passed up to parent IB')
    processed_time = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False, help_text='Whether this distribution has been processed by the financial system')
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='PENDING', help_text='Current status of the distribution processing')
    processing_notes = models.TextField(blank=True, null=True, help_text='Additional notes about processing status')
    transaction = models.ForeignKey('transactions.CommissionRebateTransaction', on_delete=models.SET_NULL, related_name='distributions', null=True, blank=True, help_text='Associated financial transaction record')
    rule = models.ForeignKey(IBCommissionRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='distributions')
    retry_count = models.IntegerField(default=0, help_text='Number of times processing has been retried for delayed distributions')
    delayed_reason = models.CharField(max_length=50, null=True, blank=True, choices=DELAYED_REASON_CHOICES, help_text='Reason why processing is delayed')

    def save(self, *args, **kwargs):
        """
        Override save to keep ib_account and mt5_login in sync.
        If ib_account is provided, update mt5_login to match.
        """
        if self.ib_account and self.ib_account.login != self.mt5_login:
            self.mt5_login = self.ib_account.login
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'ib_commission'
        db_table = 'commission_distribution'
        verbose_name = 'Commission Distribution'
        verbose_name_plural = 'Commission Distributions'
        indexes = [
            models.Index(fields=['mt5_login']),
            models.Index(fields=['customer']),
            models.Index(fields=['processed_time']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['commission_tracking']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['commission_tracking', 'customer', 'rule', 'is_pass_up'], 
                name='unique_distribution_per_ib_rule_type'
            )
        ]


class IBViewPermission(BaseModel):
    """
    Controls hierarchy viewing permissions for IBs.
    
    This model defines which IBs can view the full hierarchy
    and which are restricted to their own sub-hierarchy.
    """
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, 
                               related_name='ib_view_permissions')
    can_view_full_hierarchy = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.CRMUser', on_delete=models.SET_NULL, 
                                 null=True, related_name='created_ib_permissions')

    class Meta:
        app_label = 'ib_commission'
        db_table = 'ib_view_permissions'
        verbose_name = 'IB View Permission'
        verbose_name_plural = 'IB View Permissions'


# Import the onboarding model
from .model.ib_onboarding import IBOnboardingStatus
from .model.ib_questionnaire import IBQuestionnaire