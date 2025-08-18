from django.db import models
from ...transactions.enums import TransactionType, TransactionDirection
from ...common.base import BaseModel

class TransactionTypeConfig(BaseModel):
    """Configuration for transaction"""

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    
    # Direction settings
    allows_in = models.BooleanField(default=True)
    allows_out = models.BooleanField(default=True)
    
    # Approval settings
    requires_approval = models.BooleanField(default=True)
    approval_roles = models.JSONField(
        default=list,
        help_text="Roles that can approve this transaction type"
    )
    
    # Amount limits
    min_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Type specific rules
    rules = models.JSONField(
        default=dict,
        help_text="Type-specific configuration and rules"
    )
    
    # Additional settings
    requires_reason = models.BooleanField(default=False)
    requires_documentation = models.BooleanField(default=False)
    auto_approve_threshold = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount below which transactions are auto-approved"
    )
    
    class Meta:
        db_table = 'transaction_type_configs'
        unique_together = ['transaction_type']
        ordering = ['transaction_type']

    def validate_transaction(self, amount, direction, metadata=None):
        """
        Validates a transaction against this configuration
        Returns (bool, str) tuple of (is_valid, error_message)
        """
        if direction == TransactionDirection.IN and not self.allows_in:
            return False, f"{self.transaction_type} does not allow incoming transactions"
            
        if direction == TransactionDirection.OUT and not self.allows_out:
            return False, f"{self.transaction_type} does not allow outgoing transactions"
            
        if self.min_amount and amount < self.min_amount:
            return False, f"Amount {amount} is below minimum {self.min_amount}"
            
        if self.max_amount and amount > self.max_amount:
            return False, f"Amount {amount} is above maximum {self.max_amount}"
            
        return True, ""
