from django.db import models
from django.utils.translation import gettext_lazy as _

class KycStatus(models.TextChoices):
    NOT_UPLOADED = 'not_uploaded', _('Not Uploaded')
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')
    RECHECK_PENDING = 'recheck_pending', _('Recheck Pending')

class IbStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')

class LeadStatus(models.TextChoices):
    NEW = 'new', _('New')
    CONTACTED = 'contacted', _('Contacted')
    QUALIFIED = 'qualified', _('Qualified')
    CONVERTED = 'converted', _('Converted')
    LOST = 'lost', _('Lost')

# Note: DECLARATION_CHOICES might not fit well as a TextChoices enum
# if it's just used for storing a list of accepted strings in a JSONField.
# Keeping it in models.py for now unless a different usage is intended.

# Add other customer-related enums here if needed in the future.
