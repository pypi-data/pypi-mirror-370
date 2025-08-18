from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SharedEmailCampaignConfig(AppConfig):
    """
    App configuration for the Shared EmailCampaign model.
    """
    name = 'shared_models.email_campaigns'
    label = 'shared_email_campaign'  # Changed to avoid conflicts with apps.common.modules.email_log
    verbose_name = _('Shared Email Campaign')