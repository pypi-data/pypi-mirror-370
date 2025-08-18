from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from shared_models.common.base import BaseModel
from .managers import UserManager

class CRMUser(AbstractUser):
    """
    Custom CRM User extending Django's AbstractUser
    """
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Explicitly define groups and user_permissions with unique related_names
    # to resolve clashes with the default Django User model.
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="crmuser_groups", # Unique related name
        related_query_name="crmuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="crmuser_permissions", # Unique related name
        related_query_name="crmuser",
    )
    
    # Temporary field to force migration
    temp_field = models.CharField(max_length=1, default='x')

    # Use custom manager
    objects = UserManager()

    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        app_label = 'users'
        db_table = 'crm_users'
        permissions = [
            ("change_access_crmuser", "Can block/unblock user"),
            ("reset_password_crmuser", "Can reset user passwords"),
            ("can_assign_users", "Can assign users to customers"),
            ("can_be_assigned", "Can be assigned to customers"),
            # Dashboard permissions
            ('view_own_dashboard', 'Can view own dashboard metrics'),
            ('view_all_users_activity', 'Can view all users activity analytics'),
            ('view_team_analytics', 'Can view team analytics'),
            ('view_customer_analytics', 'Can view customer analytics'),
            ('view_transaction_analytics', 'Can view transaction analytics'),
            ('view_ib_analytics', 'Can view IB analytics'),
            ('view_support_analytics', 'Can view support analytics'),
            ('view_request_analytics', 'Can view request analytics'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
        
    @property
    def blocked_customer_count(self):
        """
        Returns the count of customers blocked by this user
        """
        return self.blocked_customers.count()
        
    @property
    def unblocked_customer_count(self):
        """
        Returns the count of customers unblocked by this user
        """
        return self.unblocked_customers.count()

class UserProfile(BaseModel):
    """
    Additional profile information for CRM Users
    """
    user = models.OneToOneField(CRMUser, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    reporting_manager = models.ForeignKey(CRMUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    profile_picture = models.CharField(max_length=500, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'users'
        db_table = 'crm_user_profiles'

    def __str__(self):
        return f"Profile of {self.user}"

class UserSettings(BaseModel):
    """
    User-specific settings and preferences
    """
    user = models.OneToOneField(CRMUser, on_delete=models.CASCADE, related_name='settings')
    
    # Security Settings
    is_2fa_enabled = models.BooleanField(default=False)
    active_2fa_methods = models.JSONField(default=dict, blank=True, null=True)  # Dict of active 2FA methods and their configs
    two_factor_secret = models.CharField(max_length=255, null=True, blank=True)  # For TOTP
    backup_codes = models.JSONField(default=list, blank=True, null=True)  # List of one-time use backup codes
    security_keys = models.JSONField(default=list, blank=True, null=True)  # List of registered security keys
    default_2fa_method = models.CharField(  # Method to use by default during login
        max_length=20,
        choices=[
            ('totp', 'Authenticator App'),
            ('security_key', 'Security Key'),
            ('sms', 'SMS'),
        ],
        default='totp',
        blank=True,
        null=True
    )
    
    # Temporary fields for WebAuthn
    temp_webauthn_challenge = models.CharField(max_length=512, null=True, blank=True)  # Temporary storage for WebAuthn challenge
    
    # Notification Settings
    notification_preferences = models.JSONField(default=dict)
    
    # UI Settings
    dashboard_layout = models.JSONField(default=dict)
    theme_preference = models.CharField(max_length=20, default='light')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')

    class Meta:
        app_label = 'users'
        db_table = 'crm_user_settings'
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize 2FA methods if not set
        if not self.active_2fa_methods:
            self.active_2fa_methods = {
                'totp': {
                    'enabled': False,
                    'verified': False
                },
                'security_key': {
                    'enabled': False,
                    'verified': False
                },
                'sms': {
                    'enabled': False,
                    'verified': False
                }
            }
        
        # Initialize notification preferences if not set
        if not self.notification_preferences:
            self.notification_preferences = {
                "web": {  # WebSocket notifications
                    "enabled": True,
                    "types": {
                        "LEAD": True,
                        "CLIENT": True,
                        "IB": True,
                        "ACCOUNT": True,
                        "TRANSACTION": True,
                        "SETTINGS": True,
                        "SECURITY": True,
                        "KYC": True,
                        "SUPPORT": True
                    },
                    "levels": {
                        "INFO": True,
                        "SUCCESS": True,
                        "WARNING": True,
                        "ERROR": True
                    }
                },
                "web_push": {  # Browser push notifications
                    "enabled": True,
                    "subscriptions": [],  # List of browser push subscriptions (endpoint, keys, etc)
                    "types": {
                        "LEAD": True,
                        "CLIENT": True,
                        "IB": True,
                        "ACCOUNT": True,
                        "TRANSACTION": True,
                        "SETTINGS": True,
                        "SECURITY": True,
                        "KYC": True,
                        "SUPPORT": True
                    },
                    "levels": {
                        "WARNING": True,
                        "ERROR": True  # By default, only send important web push notifications
                    }
                },
                "mobile_push": {  # Mobile app push notifications
                    "enabled": True,
                    "devices": [],  # List of mobile device tokens
                    "types": {
                        "LEAD": True,
                        "CLIENT": True,
                        "IB": True,
                        "ACCOUNT": True,
                        "TRANSACTION": True,
                        "SETTINGS": True,
                        "SECURITY": True,
                        "KYC": True,
                        "SUPPORT": True
                    },
                    "levels": {
                        "WARNING": True,
                        "ERROR": True  # By default, only send important push notifications
                    }
                },
                "email": {  # Email notifications
                    "enabled": True,
                    "types": {
                        "LEAD": True,
                        "CLIENT": True,
                        "IB": True,
                        "ACCOUNT": True,
                        "TRANSACTION": True,
                        "SETTINGS": True,
                        "SECURITY": True,
                        "KYC": True,
                        "SUPPORT": True
                    },
                    "levels": {
                        "WARNING": True,
                        "ERROR": True  # By default, only send important emails
                    }
                }
            }

    def has_2fa_method(self, method: str) -> bool:
        """Check if a specific 2FA method is enabled and verified"""
        method_config = self.active_2fa_methods.get(method, {})
        return method_config.get('enabled', False) and method_config.get('verified', False)

    def enable_2fa_method(self, method: str):
        """Enable a specific 2FA method"""
        if method not in self.active_2fa_methods:
            self.active_2fa_methods[method] = {'enabled': True, 'verified': False}
        else:
            self.active_2fa_methods[method]['enabled'] = True
        
        # If this is the first method being enabled, make it the default
        if not self.default_2fa_method:
            self.default_2fa_method = method
        
        self.is_2fa_enabled = True
        self.save()

    def verify_2fa_method(self, method: str):
        """Mark a 2FA method as verified"""
        if method in self.active_2fa_methods:
            self.active_2fa_methods[method]['verified'] = True
            self.save()

    def disable_2fa_method(self, method: str):
        """Disable a specific 2FA method"""
        if method in self.active_2fa_methods:
            self.active_2fa_methods[method]['enabled'] = False
            self.active_2fa_methods[method]['verified'] = False
            
            # If this was the default method, try to set another verified method as default
            if self.default_2fa_method == method:
                for other_method, config in self.active_2fa_methods.items():
                    if config['enabled'] and config['verified'] and other_method != method:
                        self.default_2fa_method = other_method
                        break
                else:
                    self.default_2fa_method = None
            
            # Check if any 2FA methods remain enabled
            any_enabled = any(
                config['enabled'] and config['verified']
                for config in self.active_2fa_methods.values()
            )
            self.is_2fa_enabled = any_enabled
            self.save()

    def get_active_2fa_methods(self) -> list:
        """Get list of active and verified 2FA methods"""
        return [
            method
            for method, config in self.active_2fa_methods.items()
            if config['enabled'] and config['verified']
        ]

    def __str__(self):
        return f"Settings for {self.user}"

    def should_notify(self, notification_type: str, level: str, channel: str = 'web') -> bool:
        """
        Check if a notification should be sent based on user preferences
        """
        prefs = self.notification_preferences.get(channel, {})
        if not prefs.get('enabled', True):
            return False
            
        # Check for registered devices/subscriptions
        if channel == 'mobile_push' and not prefs.get('devices'):
            return False
        elif channel == 'web_push' and not prefs.get('subscriptions'):
            return False

        type_allowed = prefs.get('types', {}).get(notification_type, True)
        level_allowed = prefs.get('levels', {}).get(level, True)
        
        return type_allowed and level_allowed

    def register_device(self, device_token: str, channel: str = 'mobile_push'):
        """
        Register a mobile device for push notifications
        """
        prefs = self.notification_preferences.get(channel, {})
        devices = prefs.get('devices', [])
        if device_token not in devices:
            devices.append(device_token)
            prefs['devices'] = devices
            self.save()

    def register_web_push(self, subscription_info: dict):
        """
        Register a browser for web push notifications
        subscription_info should contain:
        {
            'endpoint': 'https://push-service.com/...',
            'keys': {
                'p256dh': 'public key',
                'auth': 'auth secret'
            }
        }
        """
        prefs = self.notification_preferences.get('web_push', {})
        subscriptions = prefs.get('subscriptions', [])
        
        # Check if subscription already exists by endpoint
        exists = any(sub['endpoint'] == subscription_info['endpoint'] for sub in subscriptions)
        if not exists:
            subscriptions.append(subscription_info)
            prefs['subscriptions'] = subscriptions
            self.save()

    def unregister_web_push(self, endpoint: str):
        """
        Unregister a browser from web push notifications
        """
        prefs = self.notification_preferences.get('web_push', {})
        subscriptions = prefs.get('subscriptions', [])
        prefs['subscriptions'] = [sub for sub in subscriptions if sub['endpoint'] != endpoint]
        self.save()