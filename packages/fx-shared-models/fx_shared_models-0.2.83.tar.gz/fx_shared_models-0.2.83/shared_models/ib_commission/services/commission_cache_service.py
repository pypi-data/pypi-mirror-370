import logging
from django.forms.models import model_to_dict

logger = logging.getLogger('commission_cache')


class CachedObject:
    """
    A simple object to hold cached data without Django model constraints.
    This allows us to cache complex objects with relationships without
    triggering Django's foreign key validation.
    """
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict) and '_cached_object' in value:
                # Nested cached object
                setattr(self, key, CachedObject(value))
            else:
                setattr(self, key, value)

def get_cache():
    """
    Lazy import of Django cache to ensure it uses the consuming application's cache configuration.
    This prevents using the dummy cache from library_settings.py.
    """
    from django.core.cache import cache
    return cache

class CommissionCacheService:
    """Service for caching commission-related data using Django's cache framework"""
    
    # Cache key patterns (use consistent patterns across projects)
    # NOTE: Symbol not included in key to support comma-separated symbols
    RULE_CACHE_KEY = "commission_rule:{agreement_id}:{commission_type}"
    AGREEMENT_CACHE_KEY = "ib_agreement:{customer_id}"
    HIERARCHY_CACHE_KEY = "ib_hierarchy:{customer_id}"
    CLIENT_MAPPING_CACHE_KEY = "client_mapping:{mt5_login}:{customer_id}"
    ACCOUNT_CACHE_KEY = "account:{mt5_login}"
    
    # Cache expiration times (in seconds)
    RULE_CACHE_EXPIRY = 3600 * 24  # 24 hours
    AGREEMENT_CACHE_EXPIRY = 3600 * 24  # 24 hours
    HIERARCHY_CACHE_EXPIRY = 3600 * 24  # 24 hours
    CLIENT_MAPPING_CACHE_EXPIRY = 3600 * 24  # 24 hours
    ACCOUNT_CACHE_EXPIRY = 3600 * 24  # 24 hours
    
    # Flag to enable/disable cache
    CACHE_ENABLED = True
    
    @classmethod
    def get_account(cls, mt5_login):
        """
        Get account from cache or database
        
        Args:
            mt5_login: The MT5 login
            
        Returns:
            Account object or None
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching account from database")
            return cls._get_account_from_db(mt5_login)
            
        cache_key = cls.ACCOUNT_CACHE_KEY.format(mt5_login=mt5_login)
        
        logger.info(f"Looking for account cache key: {cache_key}")
        
        # Try to get from cache first
        cached_data = get_cache().get(cache_key)
        if cached_data:
            logger.info(f"Account cache hit for {cache_key}")
            # Return a CachedObject instead of trying to reconstruct Django model
            return CachedObject(cached_data)
        
        logger.info(f"Account cache miss for {cache_key}")
        
        # If not in cache, get from database
        account = cls._get_account_from_db(mt5_login)
        
        if account:
            # Prepare comprehensive data for caching
            cache_data = {
                '_cached_object': True,
                'id': account.id,
                'login': account.login,
                'is_active': account.is_active,
            }
            
            # Add related objects data
            if account.customer:
                cache_data['customer'] = {
                    '_cached_object': True,
                    'id': account.customer.id,
                    'email': account.customer.email,
                    'first_name': account.customer.first_name,
                    'last_name': account.customer.last_name,
                }
                cache_data['customer_id'] = account.customer.id
            
            if account.account_type:
                cache_data['account_type'] = {
                    '_cached_object': True,
                    'id': account.account_type.id,
                    'account_type': account.account_type.account_type,
                }
            
            if account.server:
                cache_data['server'] = {
                    '_cached_object': True,
                    'id': account.server.id,
                    'name': account.server.name,
                }
            
            logger.info(f"Storing account in cache: {cache_key}")
            get_cache().set(cache_key, cache_data, cls.ACCOUNT_CACHE_EXPIRY)
        
        return account
    
    @classmethod
    def _get_account_from_db(cls, mt5_login):
        """Get account directly from database"""
        from shared_models.accounts.models import Account
        
        logger.info(f"Fetching account from DB for mt5_login={mt5_login}")
        
        # Use select_related to fetch account_type and customer in single query
        account = Account.objects.filter(
            login=mt5_login, 
            is_active=True
        ).select_related('account_type', 'customer').first()
        
        logger.info(f"Found account in database: {account is not None}")
        return account
    
    @classmethod
    def invalidate_account_cache(cls, mt5_login):
        """
        Invalidate account cache
        
        Args:
            mt5_login: The MT5 login
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping account invalidation")
            return
            
        cache_key = cls.ACCOUNT_CACHE_KEY.format(mt5_login=mt5_login)
        logger.info(f"Invalidating account cache key: {cache_key}")
        get_cache().delete(cache_key)
    
    @classmethod
    def get_commission_rules(cls, agreement_id, symbol, commission_type, account_type_id=None):
        """
        Get commission rules from cache or database
        
        Args:
            agreement_id: The agreement ID
            symbol: The trading symbol
            commission_type: The commission type (COMMISSION or REBATE)
            account_type_id: Optional account type ID for more specific caching
            
        Returns:
            List of commission rules
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_commission_rules_from_db(agreement_id, symbol, commission_type, account_type_id)
            
        # Build cache key without symbol to support comma-separated symbols
        cache_key = cls.RULE_CACHE_KEY.format(
            agreement_id=agreement_id,
            commission_type=commission_type
        )
        
        logger.info(f"Looking for cache key: {cache_key} (will filter for symbol: {symbol})")
        
        # Try to get from cache first
        cached_rules = get_cache().get(cache_key)
        if cached_rules is not None:
            logger.info(f"Cache hit for {cache_key}")
            # Convert dicts back to objects that support attribute access and filter
            rules = []
            for rule_dict in cached_rules:
                # Create a simple object with attributes
                rule_obj = type('CachedRule', (), rule_dict)()
                
                # Filter by account type if specified
                if account_type_id:
                    # Include rules with matching account type or no account type (wildcard)
                    if rule_obj.account_type_id and rule_obj.account_type_id != account_type_id:
                        continue
                
                # Filter by symbol
                if symbol and symbol != '*':
                    if not rule_obj.symbol or rule_obj.symbol == '*':
                        # Wildcard rules always match
                        rules.append(rule_obj)
                    elif ',' in rule_obj.symbol:
                        # Check if our symbol is in the comma-separated list
                        rule_symbols = [s.strip().upper() for s in rule_obj.symbol.split(',')]
                        if symbol.upper() in rule_symbols:
                            rules.append(rule_obj)
                    elif rule_obj.symbol.upper() == symbol.upper():
                        # Exact match
                        rules.append(rule_obj)
                else:
                    # No symbol filter or wildcard requested
                    rules.append(rule_obj)
            
            return rules
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get ALL rules for this agreement/commission_type from database
        all_rules = cls._get_all_commission_rules_from_db(agreement_id, commission_type)
        
        # Convert ALL rules to serializable format for caching
        serialized_rules = []
        for rule in all_rules:
            rule_dict = model_to_dict(rule)
            # Add account_type_id explicitly since model_to_dict uses 'account_type' for FK
            rule_dict['account_type_id'] = rule.account_type_id
            # Add account_type name if exists
            if rule.account_type:
                rule_dict['account_type_name'] = rule.account_type.name
            serialized_rules.append(rule_dict)
        
        # Store ALL rules in cache
        logger.info(f"Storing {len(serialized_rules)} rules in cache: {cache_key}")
        get_cache().set(cache_key, serialized_rules, cls.RULE_CACHE_EXPIRY)
        
        # Now filter the rules based on the requested criteria
        filtered_rules = []
        for rule in all_rules:
            # Filter by account type if specified
            if account_type_id:
                # Include rules with matching account type or no account type (wildcard)
                if rule.account_type_id and rule.account_type_id != account_type_id:
                    continue
            
            # Filter by symbol
            if symbol and symbol != '*':
                if not rule.symbol or rule.symbol == '*':
                    # Wildcard rules always match
                    filtered_rules.append(rule)
                elif ',' in rule.symbol:
                    # Check if our symbol is in the comma-separated list
                    rule_symbols = [s.strip().upper() for s in rule.symbol.split(',')]
                    if symbol.upper() in rule_symbols:
                        filtered_rules.append(rule)
                elif rule.symbol.upper() == symbol.upper():
                    # Exact match
                    filtered_rules.append(rule)
            else:
                # No symbol filter or wildcard requested
                filtered_rules.append(rule)
        
        return filtered_rules
    
    @classmethod
    def _get_all_commission_rules_from_db(cls, agreement_id, commission_type):
        """Get ALL commission rules for an agreement from database (no filtering)"""
        from shared_models.ib_commission.models import IBCommissionRule
        
        logger.info(f"Fetching ALL rules from DB for agreement_id={agreement_id}, commission_type={commission_type}")
        
        rules = IBCommissionRule.objects.filter(
            agreement_id=agreement_id,
            commission_type=commission_type
        ).select_related('account_type').order_by('priority')
        
        rules = list(rules)
        logger.info(f"Found {len(rules)} total rules in database")
        return rules
    
    @classmethod
    def _get_commission_rules_from_db(cls, agreement_id, symbol, commission_type, account_type_id=None):
        """Get commission rules directly from database with better query optimization"""
        from shared_models.ib_commission.models import IBCommissionRule
        from django.db import models
        
        logger.info(f"Fetching rules from DB for agreement_id={agreement_id}, symbol={symbol}, commission_type={commission_type}, account_type_id={account_type_id}")
        
        rules_query = IBCommissionRule.objects.filter(
            agreement_id=agreement_id,
            commission_type=commission_type
        )
        
        # Smart filtering based on symbol
        if symbol and symbol != '*':
            # Build Q object for symbol matching (including comma-separated symbols)
            symbol_q = models.Q(symbol__iexact=symbol)
            # Also check if the symbol is contained in comma-separated lists
            symbol_q |= models.Q(symbol__icontains=f"{symbol},")  # Symbol at start or middle
            symbol_q |= models.Q(symbol__icontains=f",{symbol}")  # Symbol at end or middle
            # Also include wildcards
            symbol_q |= models.Q(symbol='*') | models.Q(symbol__isnull=True)
            
            rules_query = rules_query.filter(symbol_q)
        
        # Filter by account type if provided
        if account_type_id:
            rules_query = rules_query.filter(
                models.Q(account_type_id=account_type_id) | models.Q(account_type__isnull=True)
            )
        
        rules = list(rules_query.select_related('account_type').order_by('priority'))
        
        # Post-process to ensure exact symbol matches for comma-separated values
        if symbol and symbol != '*':
            filtered_rules = []
            for rule in rules:
                if not rule.symbol or rule.symbol == '*':
                    # Wildcard rules always match
                    filtered_rules.append(rule)
                elif ',' in rule.symbol:
                    # Check if our symbol is in the comma-separated list (case-insensitive)
                    rule_symbols = [s.strip().upper() for s in rule.symbol.split(',')]
                    if symbol.upper() in rule_symbols:
                        filtered_rules.append(rule)
                elif rule.symbol.upper() == symbol.upper():
                    # Exact match for non-comma-separated symbols
                    filtered_rules.append(rule)
            rules = filtered_rules
        
        logger.info(f"Found {len(rules)} rules in database")
        return rules
    
    @classmethod
    def get_ib_agreements(cls, customer_id):
        """
        Get IB agreements from cache or database
        
        Args:
            customer_id: The customer ID
            
        Returns:
            List of agreement memberships
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_ib_agreements_from_db(customer_id)
            
        cache_key = cls.AGREEMENT_CACHE_KEY.format(customer_id=customer_id)
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        cached_agreements = get_cache().get(cache_key)
        if cached_agreements:
            logger.info(f"Cache hit for {cache_key}")
            # Convert dicts back to objects that support attribute access
            agreements = []
            for agr_dict in cached_agreements:
                agr_obj = type('CachedAgreementMember', (), agr_dict)()
                agreements.append(agr_obj)
            return agreements
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        agreements = cls._get_ib_agreements_from_db(customer_id)
        
        # Convert to serializable format for caching
        serialized_agreements = []
        for agr in agreements:
            agr_dict = model_to_dict(agr)
            # Add agreement details if exists
            if agr.agreement:
                agr_dict['agreement_name'] = agr.agreement.name
            serialized_agreements.append(agr_dict)
        
        # Store in cache for future use
        logger.info(f"Storing in cache: {cache_key}")
        get_cache().set(cache_key, serialized_agreements, cls.AGREEMENT_CACHE_EXPIRY)
        
        return agreements
    
    @classmethod
    def _get_ib_agreements_from_db(cls, customer_id):
        """Get IB agreements directly from database"""
        from shared_models.ib_commission.models import IBAgreementMember
        
        logger.info(f"Fetching agreements from DB for customer_id={customer_id}")
        
        agreements = list(IBAgreementMember.objects.filter(
            customer_id=customer_id,
            is_active=True
        ).select_related('agreement'))
        
        logger.info(f"Found {len(agreements)} agreements in database")
        return agreements
    
    @classmethod
    def get_ib_hierarchy(cls, customer_id):
        """
        Get IB hierarchy from cache or database
        
        Args:
            customer_id: The customer ID
            
        Returns:
            IBHierarchy object
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_ib_hierarchy_from_db(customer_id)
            
        cache_key = cls.HIERARCHY_CACHE_KEY.format(customer_id=customer_id)
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        cached_data = get_cache().get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            # Return a CachedObject instead of trying to reconstruct Django model
            return CachedObject(cached_data)
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        hierarchy = cls._get_ib_hierarchy_from_db(customer_id)
        
        if hierarchy:
            # Prepare comprehensive data for caching
            cache_data = {
                '_cached_object': True,
                'id': hierarchy.id,
                'customer_id': hierarchy.customer_id,
                'path': hierarchy.path,
                'level': hierarchy.level,
                'mt5_login': hierarchy.mt5_login,
                'is_active': hierarchy.is_active,
                'default_agreement_id': hierarchy.default_agreement_id if hasattr(hierarchy, 'default_agreement_id') else None,
            }
            
            # Add ib_account data if exists
            if hierarchy.ib_account:
                cache_data['ib_account'] = {
                    '_cached_object': True,
                    'id': hierarchy.ib_account.id,
                    'login': hierarchy.ib_account.login,
                }
                
                # Add server data if exists
                if hierarchy.ib_account.server:
                    cache_data['ib_account']['server'] = {
                        '_cached_object': True,
                        'id': hierarchy.ib_account.server.id,
                        'name': hierarchy.ib_account.server.name,
                    }
            
            logger.info(f"Storing in cache: {cache_key}")
            get_cache().set(cache_key, cache_data, cls.HIERARCHY_CACHE_EXPIRY)
        
        return hierarchy
    
    @classmethod
    def _get_ib_hierarchy_from_db(cls, customer_id):
        """Get IB hierarchy directly from database"""
        from shared_models.ib_commission.models import IBHierarchy
        
        logger.info(f"Fetching hierarchy from DB for customer_id={customer_id}")
        
        hierarchy = IBHierarchy.objects.filter(
            customer_id=customer_id,
            is_active=True
        ).select_related('ib_account', 'ib_account__server').first()
        
        logger.info(f"Found hierarchy in database: {hierarchy is not None}")
        return hierarchy
    
    @classmethod
    def get_client_mapping(cls, mt5_login, customer_id):
        """
        Get client mapping from cache or database
        
        Args:
            mt5_login: The MT5 login
            customer_id: The customer ID
            
        Returns:
            ClientIBMapping object
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, fetching from database")
            return cls._get_client_mapping_from_db(mt5_login, customer_id)
            
        cache_key = cls.CLIENT_MAPPING_CACHE_KEY.format(
            mt5_login=mt5_login or "none",
            customer_id=customer_id
        )
        
        logger.info(f"Looking for cache key: {cache_key}")
        
        # Try to get from cache first
        cached_data = get_cache().get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            # Return a CachedObject instead of trying to reconstruct Django model
            return CachedObject(cached_data)
        
        logger.info(f"Cache miss for {cache_key}")
        
        # If not in cache, get from database
        mapping = cls._get_client_mapping_from_db(mt5_login, customer_id)
        
        if mapping:
            # Prepare comprehensive data for caching
            cache_data = {
                '_cached_object': True,
                'id': mapping.id,
                'customer_id': mapping.customer_id,
                'direct_ib_customer_id': mapping.direct_ib_customer_id,
                'master_ib_customer_id': mapping.master_ib_customer_id,
                'agreement_id': mapping.agreement_id,
                'agreement_path': mapping.agreement_path if hasattr(mapping, 'agreement_path') else None,
                'ib_path': mapping.ib_path,
                'mt5_login': mapping.mt5_login,
            }
            
            # Add related objects data if they exist
            if mapping.direct_ib_customer:
                cache_data['direct_ib_customer'] = {
                    '_cached_object': True,
                    'id': mapping.direct_ib_customer.id,
                    'email': mapping.direct_ib_customer.email,
                    'first_name': mapping.direct_ib_customer.first_name,
                    'last_name': mapping.direct_ib_customer.last_name,
                }
            
            if mapping.agreement:
                cache_data['agreement'] = {
                    '_cached_object': True,
                    'id': mapping.agreement.id,
                    'name': mapping.agreement.name,
                }
            else:
                cache_data['agreement'] = None
            
            logger.info(f"Storing in cache: {cache_key}")
            get_cache().set(cache_key, cache_data, cls.CLIENT_MAPPING_CACHE_EXPIRY)
        
        return mapping
    
    @classmethod
    def _get_client_mapping_from_db(cls, mt5_login, customer_id):
        """Get client mapping directly from database"""
        from shared_models.ib_commission.models import ClientIBMapping
        
        logger.info(f"Fetching client mapping from DB for mt5_login={mt5_login}, customer_id={customer_id}")
        
        mapping = None
        if mt5_login:
            mapping = ClientIBMapping.objects.filter(
                mt5_login=mt5_login,
                customer_id=customer_id
            ).select_related('direct_ib_customer', 'agreement').first()
        
        if not mapping and customer_id:
            # Try to find by customer only
            mapping = ClientIBMapping.objects.filter(
                customer_id=customer_id
            ).select_related('direct_ib_customer', 'agreement').first()
        
        logger.info(f"Found client mapping in database: {mapping is not None}")
        return mapping
    
    @classmethod
    def invalidate_rule_cache(cls, agreement_id=None):
        """
        Invalidate rule cache for an agreement
        
        Args:
            agreement_id: The agreement ID (if None, invalidate all rule caches)
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        if agreement_id:
            # With the new caching strategy, we only need to invalidate 2 keys per agreement
            # (one for COMMISSION and one for REBATE)
            invalidated_count = 0
            for commission_type in ['COMMISSION', 'REBATE']:
                cache_key = cls.RULE_CACHE_KEY.format(
                    agreement_id=agreement_id,
                    commission_type=commission_type
                )
                logger.debug(f"Invalidating cache key: {cache_key}")
                get_cache().delete(cache_key)
                invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} cache keys for agreement {agreement_id}")
        else:
            # This is a more aggressive approach - clear the entire cache
            # Only use this if absolutely necessary
            logger.warning("Clearing entire cache")
            get_cache().clear()
    
    @classmethod
    def invalidate_agreement_cache(cls, customer_id):
        """
        Invalidate agreement cache for a customer
        
        Args:
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        cache_key = cls.AGREEMENT_CACHE_KEY.format(customer_id=customer_id)
        logger.info(f"Invalidating cache key: {cache_key}")
        get_cache().delete(cache_key)
    
    @classmethod
    def invalidate_hierarchy_cache(cls, customer_id):
        """
        Invalidate hierarchy cache for a customer
        
        Args:
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        cache_key = cls.HIERARCHY_CACHE_KEY.format(customer_id=customer_id)
        logger.info(f"Invalidating cache key: {cache_key}")
        get_cache().delete(cache_key)
    
    @classmethod
    def invalidate_client_mapping_cache(cls, mt5_login=None, customer_id=None):
        """
        Invalidate client mapping cache
        
        Args:
            mt5_login: The MT5 login
            customer_id: The customer ID
        """
        if not cls.CACHE_ENABLED:
            logger.info("Cache disabled, skipping invalidation")
            return
            
        if mt5_login and customer_id:
            cache_key = cls.CLIENT_MAPPING_CACHE_KEY.format(
                mt5_login=mt5_login,
                customer_id=customer_id
            )
            logger.info(f"Invalidating cache key: {cache_key}")
            get_cache().delete(cache_key)
        elif customer_id:
            # Get all mt5_logins for this customer from the database
            from shared_models.ib_commission.models import ClientIBMapping
            
            # Find all mt5_logins associated with this customer
            mt5_logins = ClientIBMapping.objects.filter(
                customer_id=customer_id
            ).values_list('mt5_login', flat=True).distinct()
            
            # Invalidate cache for each mt5_login
            invalidated_count = 0
            for mt5_login in mt5_logins:
                if mt5_login:  # Skip None values
                    cache_key = cls.CLIENT_MAPPING_CACHE_KEY.format(
                        mt5_login=mt5_login,
                        customer_id=customer_id
                    )
                    logger.info(f"Invalidating cache key: {cache_key}")
                    get_cache().delete(cache_key)
                    invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} client mapping cache keys for customer {customer_id}")
        else:
            logger.warning("Cannot invalidate client mapping cache without customer_id")
    
    @classmethod
    def list_all_cache_keys(cls):
        """
        List all cache keys (if possible)
        
        Returns:
            List of cache keys or None if not supported
        """
        try:
            # This only works with some cache backends like Redis
            cache = get_cache()
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'keys'):
                try:
                    all_keys = cache._cache.keys('*')
                    logger.info(f"Found {len(all_keys)} keys in cache")
                    return all_keys
                except:
                    logger.warning("Could not retrieve keys from cache")
                    return None
            else:
                logger.warning("Cache backend does not support listing keys")
                return None
        except Exception as e:
            logger.exception(f"Error listing cache keys: {e}")
            return None 