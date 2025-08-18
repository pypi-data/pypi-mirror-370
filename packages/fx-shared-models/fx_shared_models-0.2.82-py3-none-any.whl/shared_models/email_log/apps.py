from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SharedEmailLogConfig(AppConfig):
    """
    App configuration for the Shared EmailLog model.
    """
    # Full Python path to the app module, corrected based on structure
    name = 'shared_models.email_log'
    label = 'shared_email_log'  # Changed to avoid conflicts with apps.common.modules.email_log
    # Optional: Human-readable name for the admin
    verbose_name = _('Shared Email Logs')
    # Optional: label used for relations, migrations etc.
    # label = 'shared_email_log' # Uncomment if a specific label is needed