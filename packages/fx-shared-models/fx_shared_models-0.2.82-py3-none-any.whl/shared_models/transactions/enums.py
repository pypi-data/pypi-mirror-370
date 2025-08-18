from django.db import models

class TransactionDirection(models.TextChoices):
    IN = 'IN', 'Credit/Incoming'
    OUT = 'OUT', 'Debit/Outgoing'

class TransactionType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', 'Deposit'
    WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'
    BONUS = 'BONUS', 'Bonus'
    REBATE = 'REBATE', 'Rebate'
    COMMISSION = 'COMMISSION', 'Commission'
    CORRECTION = 'CORRECTION', 'Correction'
    INTERNAL_TRANSFER = 'INTERNAL_TRANSFER', 'Internal Transfer'
    CREDIT = 'CREDIT', 'Credit'
    CHARGE = 'CHARGE', 'Charge'
    COMPENSATION = 'COMPENSATION', 'Compensation'

class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'
    FAILED = 'FAILED', 'Failed'
    PROCESSED = 'PROCESSED', 'Processed'

class PaymentMethod(models.TextChoices):
    WIRE = 'WIRE', 'Wire Transfer'
    CRYPTO = 'CRYPTO', 'Cryptocurrency'
    CARD = 'CARD', 'Credit/Debit Card'
    MANUAL = 'MANUAL', 'Manual Entry' 
    SYSTEM = 'SYSTEM', 'System Generated' # For Bonus, Rebate, Internal Transfers etc.
    UPI = 'UPI', 'UPI Payment'
    # Example: Add e-wallets if they are distinct high-level methods
    SKRILL = 'SKRILL', 'Skrill'
    NETELLER = 'NETELLER', 'Neteller'

class PaymentGateway(models.TextChoices):
    STRIPE = 'STRIPE', 'Stripe'
    MYFATOORAH = 'MYFATOORAH', 'MyFatoorah'
    MANUAL = 'MANUAL', 'Manual Processing'
    CRYPTO = 'CRYPTO', 'Crypto Payment'
    WIRE = 'WIRE', 'Wire Transfer'
    SYSTEM = 'SYSTEM', 'System Internal'
    QUBEPAY = 'QUBEPAY', 'QubePay'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    CASH = 'CASH', 'Cash'
    PAYPAL = 'PAYPAL', 'PayPal'
    RAZORPAY = 'RAZORPAY', 'Razorpay'
    UPI = 'UPI', 'UPI'
    
class CardType(models.TextChoices):
    VISA = 'VISA', 'Visa'
    MASTERCARD = 'MASTERCARD', 'Mastercard'
    AMEX = 'AMEX', 'American Express'

class EvidenceType(models.TextChoices):
    BANK_SLIP = 'BANK_SLIP', 'Bank Slip'
    CRYPTO_TX_HASH = 'CRYPTO_TX_HASH', 'Crypto Transaction Hash'
    CARD_RECEIPT = 'CARD_RECEIPT', 'Card Receipt'
    OTHER = 'OTHER', 'Other Document'
