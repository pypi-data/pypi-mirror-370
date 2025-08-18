from django.db import models
from django.core.validators import RegexValidator
from shared_models.transactions.enums import PaymentMethod, PaymentGateway, CardType
from shared_models.common.base import BaseModel


class PaymentGatewayConfig(BaseModel):
    """Configuration for payment gateways"""
    
    gateway = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[A-Z][A-Z0-9_]*$',
                message='Gateway name must be uppercase and contain only letters, numbers, and underscores'
            )
        ],
        help_text="Unique identifier for the gateway. Must be uppercase with underscores (e.g. NEG_BALANCE_COVERAGE)"
    )
    display_name = models.CharField(max_length=100)
    
    # Core settings
    enable = models.BooleanField(default=True)
    enable_crm = models.BooleanField(default=True)
    enable_cp = models.BooleanField(default=False)
    is_external = models.BooleanField(
        default=False,
        help_text="If True, this is an external payment provider"
    )
    
    # Country restrictions (only for payment gateways)
    enabled_countries = models.JSONField(
        default=list,
        blank=True,
        help_text="List of country codes where this gateway is enabled"
    )
    disabled_countries = models.JSONField(
        default=list,
        blank=True,
        help_text="List of country codes where this gateway is disabled"
    )
    
    # Fee configuration (only for payment gateways)
    charge_fees = models.BooleanField(default=False)
    fixed_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    percentage_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Payment method link (optional, only for actual payment gateways)
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )
    
    # Additional configuration
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration specific to this gateway"
    )
    
    class Meta:
        db_table = 'payment_gateway_configs'
        ordering = ['gateway']
        verbose_name = 'Payment Gateway Configuration'
        verbose_name_plural = 'Payment Gateway Configurations'

    def __str__(self):
        return f"{self.display_name} ({self.gateway})"
    
    def calculate_fees(self, amount):
        """Calculate total fees for a given amount"""
        if not self.charge_fees:
            return 0
        
        total_fee = self.fixed_fee
        if self.percentage_fee > 0:
            total_fee += (amount * self.percentage_fee / 100)
        return total_fee


class PaymentMethodConfig(BaseModel):
    """Configuration for payment methods"""

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices
    )
    is_enabled = models.BooleanField(default=True)
    requires_manual_approval = models.BooleanField(default=True)
    requires_evidence = models.BooleanField(default=True)
    display_name = models.CharField(max_length=100)
    
    # Gateway configuration - all made optional
    default_gateway = models.ForeignKey(
        PaymentGatewayConfig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_methods'
    )
    allowed_gateways = models.ManyToManyField(
        PaymentGatewayConfig,
        related_name='payment_methods',
        blank=True  # Make it optional
    )
    
    # Transaction type specific settings
    allowed_transaction_types = models.JSONField(
        default=list,
        help_text="List of transaction types allowed for this payment method"
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
    
    # Additional configuration
    metadata_schema = models.JSONField(
        default=dict,
        help_text="Required fields and validations for this payment method"
    )
    approval_roles = models.JSONField(
        default=list,
        help_text="Roles that can approve transactions with this payment method"
    )
    
    class Meta:
        db_table = 'payment_method_configs'
        ordering = ['payment_method']

    def __str__(self):
        return f"{self.payment_method} - {self.display_name}"

# KYC Requirement Rules

# KycLevels enum removed as requirements changed to boolean fields
class KycRequirementRule(BaseModel):
    """
    Defines the minimum KYC level required for a specific combination
    of payment method, gateway, and transaction type.
    Rules are checked based on specificity (most specific match wins).
    """
    # Identifiers for the rule scope (nullable to allow broader rules)
    payment_method = models.ForeignKey(
        PaymentMethodConfig,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Apply rule only to this payment method (optional)"
    )
    payment_gateway = models.ForeignKey(
        PaymentGatewayConfig,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Apply rule only to this payment gateway (optional)"
    )
    transaction_type = models.CharField(
        max_length=50, # Adjust size as needed
        null=True,
        blank=True,
        help_text="Apply rule only to this transaction type (e.g., DEPOSIT, WITHDRAWAL) (optional)"
    )
    # Optional: Add a priority field if complex precedence is needed beyond specificity

    # KYC Level Requirements (Hierarchical: L3 implies L2 implies L1)
    requires_level_one = models.BooleanField(
        default=False, help_text="Does this rule require at least KYC Level One?"
    )
    requires_level_two = models.BooleanField(
        default=False, help_text="Does this rule require at least KYC Level Two?"
    )
    requires_level_three = models.BooleanField(
        default=False, help_text="Does this rule require at least KYC Level Three?"
    )

    class Meta:
        db_table = 'system_settings_kycrequirementrule' # More conventional table name
        ordering = ['payment_method', 'payment_gateway', 'transaction_type'] # Example ordering
        verbose_name = "KYC Requirement Rule"
        verbose_name_plural = "KYC Requirement Rules"
        # Consider adding unique_together constraints if appropriate for your logic

    def __str__(self):
        # Safely access related object attributes only if the FK is set
        method_obj = self.payment_method
        gateway_obj = self.payment_gateway
        method = method_obj.payment_method if method_obj else 'Any Method'
        gateway = gateway_obj.gateway if gateway_obj else 'Any Gateway'
        tx_type = self.transaction_type or 'Any Type'
        # Display boolean flags
        flags = []
        if self.requires_level_one: flags.append("L1")
        if self.requires_level_two: flags.append("L2")
        if self.requires_level_three: flags.append("L3")
        req = "+".join(flags) if flags else "None"
        return f"Rule: M={method}, G={gateway}, T={tx_type} -> KYC Req: {req}"
