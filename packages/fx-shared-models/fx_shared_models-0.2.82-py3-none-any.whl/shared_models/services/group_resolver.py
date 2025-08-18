class MT5GroupResolverService:
    """Service for resolving MT5 group paths based on account and customer attributes"""
    
    @staticmethod
    def resolve_group(account, customer=None):
        """
        Resolve the MT5 group path for an account based on its attributes and customer.
        
        Args:
            account: The Account instance
            customer: Optional Customer instance. If not provided, will use account.customer
        
        Returns:
            str: The resolved group path
        """
        if not customer:
            customer = account.customer
            
        # Try to find a matching group configuration
        try:
            # First check for IB custom configuration
            if customer.ib:
                ib_config = account.account_type.group_configs.filter(
                    country=customer.country,
                    ib_custom_configs__ib=customer.ib
                ).first()
                
                if ib_config:
                    return ib_config.get_group_path(account, customer)
            
            # Then check for country-specific configuration
            config = account.account_type.group_configs.filter(
                country=customer.country
            ).first()
            
            if config:
                return config.get_group_path(account, customer)
            
            # Finally check for default configuration
            config = account.account_type.group_configs.filter(
                country='*'
            ).first()
            
            if config:
                return config.get_group_path(account, customer)
            
        except Exception as e:
            # Log the error if needed
            pass
        
        # Fallback to default group from account type
        return account.account_type.default_group 