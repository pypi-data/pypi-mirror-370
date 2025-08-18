from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ...common.base import BaseModel


class BrokerConfiguration(BaseModel):
    """
    Global broker configuration settings.
    This model stores broker-wide settings that can be managed through the CRM
    after initial setup. Critical values are also synced to environment variables.
    """
    
    # Basic Information (Broker Editable)
    broker_name = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Internal broker identifier (e.g., 'mybroker')"
    )
    company_display_name = models.CharField(
        max_length=255,
        help_text="Company name shown to clients"
    )
    
    # Logo Configuration (Store as public URLs)
    logo_light_url = models.URLField(
        blank=True,
        help_text="Public URL for light theme logo"
    )
    logo_dark_url = models.URLField(
        blank=True,
        help_text="Public URL for dark theme logo"
    )
    favicon_light_url = models.URLField(
        blank=True,
        help_text="Public URL for light favicon"
    )
    favicon_dark_url = models.URLField(
        blank=True,
        help_text="Public URL for dark favicon"
    )
    
    # Contact Information (Broker Editable)
    support_email = models.EmailField(
        blank=True,
        help_text="Primary support email address"
    )
    support_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Primary support phone number"
    )
    company_address = models.TextField(
        blank=True,
        help_text="Company address for emails and legal"
    )
    
    # System Limits (Superadmin Only)
    max_ib_levels = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Maximum depth of IB hierarchy (1-10)"
    )
    max_active_clients_per_broker = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum number of active clients (null for unlimited)"
    )
    
    # Branding (Broker Editable)
    primary_color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text="Primary brand color (hex)"
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#6c757d',
        help_text="Secondary brand color (hex)"
    )
    
    # Regulatory Information (Broker Editable)
    regulatory_region = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Regulatory jurisdiction (e.g., 'CySEC', 'FCA', 'ASIC')"
    )
    license_number = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Regulatory license number"
    )
    
    # Cache invalidation tracking
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time configuration was updated"
    )
    
    class Meta:
        app_label = 'system_settings'
        db_table = 'broker_configuration'
        verbose_name = 'Broker Configuration'
        verbose_name_plural = 'Broker Configurations'
    
    def __str__(self):
        return f"{self.company_display_name} ({self.broker_name})"
    
    def save(self, *args, **kwargs):
        """Override save to ensure single instance per broker"""
        if not self.pk and BrokerConfiguration.objects.exists():
            # If trying to create a new one when one already exists
            # This ensures only one configuration per deployment
            raise ValueError("Only one broker configuration allowed per system")
        return super().save(*args, **kwargs)
    
    @classmethod
    def get_current(cls):
        """
        Get the current broker configuration.
        If none exists, create a default one.
        """
        config = cls.objects.first()
        if not config:
            # Create default configuration
            config = cls.objects.create(
                broker_name='default',
                company_display_name='Financial Trading Platform',
                support_email='support@example.com',
                support_phone='+1234567890',
                company_address='123 Main Street, City, Country',
                primary_color='#1976d2',
                secondary_color='#dc004e',
                max_ib_levels=3,
                max_active_clients_per_broker=500
            )
        return config
    
    def get_logo_for_theme(self, is_dark=False):
        """Get appropriate logo URL for theme"""
        if is_dark:
            return self.logo_dark_url or self.logo_light_url
        return self.logo_light_url
    
    def get_favicon_for_theme(self, is_dark=False):
        """Get appropriate favicon URL for theme"""
        if is_dark:
            return self.favicon_dark_url or self.favicon_light_url
        return self.favicon_light_url
    
    def get_env_mappings(self):
        """
        Get environment variable mappings for critical settings.
        These are synced to environment variables for system-wide access.
        """
        return {
            'BROKER_NAME': self.broker_name,
            'COMPANY_NAME': self.company_display_name,
            'COMPANY_LOGO_URL': self.logo_light_url or '',
            'MAX_IB_LEVELS': str(self.max_ib_levels),
            'MAX_ACTIVE_CLIENTS': str(self.max_active_clients_per_broker or ''),
            'SUPPORT_EMAIL': self.support_email or '',
            'SUPPORT_PHONE': self.support_phone or '',
            'REGULATORY_REGION': self.regulatory_region or '',
            'PRIMARY_COLOR': self.primary_color,
            'SECONDARY_COLOR': self.secondary_color,
        }