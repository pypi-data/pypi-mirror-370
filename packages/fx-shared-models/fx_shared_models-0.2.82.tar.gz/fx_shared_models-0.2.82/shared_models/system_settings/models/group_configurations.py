from django.db import models
from django.core.exceptions import ValidationError
from ...common.base import BaseModel

class GroupConfiguration(BaseModel):
    """
    Configuration for MT5 groups linked to account types
    """
    account_type = models.ForeignKey('system_settings.AccountType', 
                                   on_delete=models.CASCADE,
                                   related_name='group_configs')
    country = models.CharField(
        max_length=2, 
        default='*',
        help_text="Country code or '*' for default configuration"
    )
    
    # Group Paths
    groups = models.JSONField(
        default=dict,
        help_text="""
        Group paths configuration. Example:
        {
            "default": "\\MT5_LIVE\\Standard",
            "swap_free": "\\MT5_LIVE\\Standard_SwapFree",
            "bonus": "\\MT5_LIVE\\Standard_Bonus",
            "bonus_swap_free": "\\MT5_LIVE\\Standard_Bonus_SwapFree",
            "markup": "\\MT5_LIVE\\Standard_Markup",
            "ib": "\\MT5_LIVE\\Standard_IB"
        }
        The presence of a key (e.g., "swap_free") indicates that feature is allowed.
        """
    )
    
    class Meta:
        app_label = 'system_settings'
        db_table = 'group_configurations'
        unique_together = [['account_type', 'country']]
        verbose_name = 'Group Configuration'
        verbose_name_plural = 'Group Configurations'
    
    def __str__(self):
        return f"{self.account_type.name} - {self.country if self.country != '*' else 'Default'}"
    
    def clean(self):
        """Validate the configuration"""
        super().clean()
        
        # Validate groups JSON
        if 'default' not in self.groups:
            raise ValidationError("Groups configuration must contain a 'default' group")
        
        # Validate group paths
        for key, path in self.groups.items():
            if not path.startswith('\\'):
                raise ValidationError(f"Group path '{path}' must start with '\\'")
            
            if not path.replace('\\', '').strip():
                raise ValidationError(f"Group path '{path}' cannot be empty")
    
    def get_group_path(self, account: 'Account', customer: 'Customer') -> str:
        """
        Get the appropriate group path based on account and customer attributes.
        Features (swap_free, bonus, etc.) are allowed if their corresponding group paths exist.
        """
        # Check for bonus + swap_free combination first
        if account.has_bonus and account.is_swap_free and 'bonus_swap_free' in self.groups:
            return self.groups['bonus_swap_free']
        
        # Then check individual conditions
        if account.is_swap_free and 'swap_free' in self.groups:
            return self.groups['swap_free']
        
        if account.has_bonus and 'bonus' in self.groups:
            return self.groups['bonus']
        
        if account.has_markup and 'markup' in self.groups:
            return self.groups['markup']
        
        if customer.ib and 'ib' in self.groups:
            return self.groups['ib']
        
        return self.groups['default']

class IBCustomGroupConfiguration(BaseModel):
    """
    Custom group configurations for specific IBs.
    This allows IBs to have their own specific group paths for their clients.
    """
    group_config = models.ForeignKey(GroupConfiguration, 
                                   on_delete=models.CASCADE,
                                   related_name='ib_custom_configs')
    ib = models.ForeignKey('customers.Customer', 
                          on_delete=models.CASCADE,
                          related_name='custom_group_configs')
    
    # Custom group paths for this IB
    groups = models.JSONField(
        default=dict,
        help_text="""
        Custom group paths for this IB's clients. Example:
        {
            "default": "\\MT5_LIVE\\Standard_IB_123",
            "swap_free": "\\MT5_LIVE\\Standard_IB_123_SwapFree",
            "bonus": "\\MT5_LIVE\\Standard_IB_123_Bonus",
            "bonus_swap_free": "\\MT5_LIVE\\Standard_IB_123_Bonus_SwapFree"
        }
        Only need to specify the groups that are different from the base configuration.
        Features (swap_free, bonus, etc.) are allowed if their corresponding group paths exist.
        """
    )
    
    class Meta:
        app_label = 'system_settings'
        db_table = 'ib_custom_group_configurations'
        unique_together = [['group_config', 'ib']]
        verbose_name = 'IB Custom Group Configuration'
        verbose_name_plural = 'IB Custom Group Configurations'
    
    def __str__(self):
        return f"Custom config for {self.ib.email} - {self.group_config}"
    
    def clean(self):
        """Validate the configuration"""
        super().clean()
        
        # Validate groups JSON
        if 'default' not in self.groups:
            raise ValidationError("Groups configuration must contain a 'default' group")
        
        # Validate group paths
        for key, path in self.groups.items():
            if not path.startswith('\\'):
                raise ValidationError(f"Group path '{path}' must start with '\\'")
            
            if not path.replace('\\', '').strip():
                raise ValidationError(f"Group path '{path}' cannot be empty")
            
        # Validate that all specified groups are allowed in base configuration
        for key in self.groups.keys():
            if key not in self.group_config.groups:
                raise ValidationError(
                    f"Group type '{key}' is not allowed in base configuration"
                )
    
    def get_group_path(self, account: 'Account') -> str:
        """
        Get the appropriate custom group path based on account attributes.
        Falls back to base configuration's group paths if a specific type isn't customized.
        """
        # Check for bonus + swap_free combination first
        if account.has_bonus and account.is_swap_free:
            return self.groups.get('bonus_swap_free', self.group_config.groups.get('bonus_swap_free', self.groups['default']))
        
        # Then check individual conditions
        if account.is_swap_free:
            return self.groups.get('swap_free', self.group_config.groups.get('swap_free', self.groups['default']))
        
        if account.has_bonus:
            return self.groups.get('bonus', self.group_config.groups.get('bonus', self.groups['default']))
        
        return self.groups['default'] 