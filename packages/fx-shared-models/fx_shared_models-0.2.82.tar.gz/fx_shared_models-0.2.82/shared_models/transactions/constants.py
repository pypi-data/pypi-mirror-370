# Default configuration for different transaction types
BONUS_RULES = {
    'valid_reasons': ['welcome_bonus', 'deposit_bonus', 'loyalty_bonus'],
    'expiry_days': 30,  # Bonus validity period
    'can_withdraw': False,  # Whether bonus amount can be withdrawn
}

COMMISSION_RULES = {
    'calculation_basis': ['percentage', 'fixed'],
    'max_percentage': 100,
    'requires_trade_link': True,
}

CORRECTION_RULES = {
    'requires_supervisor_approval': True,
    'requires_documentation': True,
    'valid_reasons': ['system_error', 'manual_error', 'dispute_resolution'],
}

REBATE_RULES = {
    'calculation_methods': ['volume_based', 'fixed'],
    'payment_frequency': ['real_time', 'daily', 'weekly', 'monthly'],
    'minimum_volume': 0.01,
}

# Transaction amount limits
DEFAULT_MIN_AMOUNT = 0.01
DEFAULT_MAX_AMOUNT = 1000000.0

# Evidence requirements
REQUIRED_EVIDENCE_TYPES = {
    'WIRE': ['BANK_SLIP'],
    'CRYPTO': ['CRYPTO_TX_HASH'],
    'CARD': ['CARD_RECEIPT'],
}

# Approval requirements
DEFAULT_APPROVAL_ROLES = ['manager', 'supervisor', 'admin']
HIGH_AMOUNT_APPROVAL_ROLES = ['supervisor', 'admin']  # For amounts above threshold
