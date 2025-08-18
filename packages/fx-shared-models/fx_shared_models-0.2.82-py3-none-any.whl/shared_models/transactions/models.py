from django.db import models
from django.conf import settings
from .enums import (
    TransactionDirection,
    TransactionType,
    TransactionStatus,
    PaymentMethod,
)
from ..common.base import BaseModel


class Transaction(BaseModel):
    # Core transaction fields
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)  # ISO 4217 currency code
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    direction = models.CharField(
        max_length=3,
        choices=TransactionDirection.choices
    )
    status = models.CharField(
        max_length=10,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )
    
    # MT5 details
    mt5_ticket = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="MT5 ticket number for the transaction"
    )
    
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    # Payment details

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )
    payment_gateway = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    
    # Gateway response
    gateway_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    
    # Relationships
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    # order = models.ForeignKey(
    #     'orders.Order',
    #     on_delete=models.PROTECT,
    #     related_name='transactions',
    #     null=True,
    #     blank=True
    # )
    
    # User tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_transactions',
         null=True,
         blank=True
     )
    approved_at = models.DateTimeField(
         null=True,
         blank=True,
         help_text="Timestamp when the transaction was approved"
    )
    approved_by = models.ForeignKey(
        'users.CRMUser',
        on_delete=models.PROTECT,
        related_name='approved_transactions',
        null=True,
        blank=True
    )
    assigned_user = models.ForeignKey(
        'users.CRMUser',
        on_delete=models.PROTECT,
        related_name='assigned_transactions',
        null=True,
        blank=True,
        help_text="The CRM user assigned to this transaction's customer at the time of creation."
    )
    
    # Additional fields
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_type', 'status']),
            models.Index(fields=['account', 'created_at']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['payment_gateway']),
            models.Index(fields=['assigned_user']),
        ]
        permissions = [
            ("approve_transaction", "Can approve transactions"),
            ("reject_transaction", "Can reject transactions"),
        ]


class CommissionRebateTransaction(Transaction):
    # Additional fields specific to Commission/Rebate
    ib_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.PROTECT,
        related_name='commission_rebate_transactions'
    )
    # trade = models.ForeignKey(
    #     'trades.Trade',
    #     on_delete=models.PROTECT,
    #     related_name='commission_rebate_transactions'
    # )
    calculation_basis = models.JSONField(
        help_text="Parameters used for calculation"
    )
    
    class Meta:
        db_table = 'commission_rebate_transactions'


class TransactionEvidence(BaseModel):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='evidences'
    )
    file = models.FileField(upload_to='transaction_evidences/%Y/%m/%d/')
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'transaction_evidences'
        ordering = ['-created_at']
