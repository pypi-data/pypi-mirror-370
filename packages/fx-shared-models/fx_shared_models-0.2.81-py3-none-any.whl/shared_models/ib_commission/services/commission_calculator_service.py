"""
Service for calculating IB commissions based on rules and deal tickets.
"""
from shared_models.ib_commission.models import IBCommissionRule, CommissionDistribution, IBAgreement, IBAgreementMember
from shared_models.ib_commission.models import IBHierarchy, ClientIBMapping, IBAccountAgreement, CommissionTracking
from shared_models.accounts.models import Account
from shared_models.transactions.models import CommissionRebateTransaction
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Q, Prefetch
from django.db import models
from django.utils import timezone
from django.core.cache import cache
import logging

# Import the Deal model
from shared_models.trading.models import Deal

logger = logging.getLogger(__name__)


class CommissionCalculatorService:
    """
    Service for calculating IB commissions based on rules and deal tickets.
    """
    
    COMMISSION_TYPE = "COMMISSION"
    REBATE_TYPE = "REBATE"
    
    # MT5 entry types
    ENTRY_IN = 0      # Entering the market or adding volume
    ENTRY_OUT = 1     # Exit from the market or partial closure
    ENTRY_INOUT = 2   # Deal that closed an existing position and opened a new one in the opposite direction
    ENTRY_OUT_BY = 3  # Close by - simultaneous closure of two opposite positions
    
    @classmethod
    def calculate_distribution(cls, deal_instance: Deal):
        """
        Calculate commission distribution for a deal.
        
        Args:
            deal_instance: The Deal model instance.
            
        Returns:
            Dictionary containing:
            - distributions: List of calculated distributions (saved or unsaved depending on status)
            - client_deduction: Total amount to deduct from client (for entry positions)
            - client_server_id: Server ID for the client account (for MT5 processing)
            - is_processed: Whether distributions have already been processed (True if deal was already processed, False otherwise)
        """
        # Extract data from deal_instance
        deal_ticket = deal_instance.deal_ticket
        mt5_login = deal_instance.login
        action = deal_instance.action  # 0=buy, 1=sell
        entry = deal_instance.entry    # 0=in, 1=out, 2=inout, 3=out_by
        symbol = deal_instance.symbol
        volume = deal_instance.volume
        price = deal_instance.price
        profit = deal_instance.profit
        volume_closed = deal_instance.volume_closed or volume # Use volume if volume_closed is None
        position_id = deal_instance.position_id
        trade_time = deal_instance.time # Already a datetime object

        # Basic validation
        if action not in [0, 1]:
            logger.warning(f"Invalid action: {action} for deal {deal_ticket}. Skipping calculation.")
            return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': True} # Indicate skip
            logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
            return return_value

        # Check if this is a close by deal with zero profit
        if entry == cls.ENTRY_OUT_BY and profit is not None:
            # Convert to string with 2 decimal places to check if it starts with 0.00
            profit_str = f"{profit:.2f}"
            if profit_str.startswith('0.00') or profit_str.startswith('-0.00'):
                logger.info(f"Deal ({deal_ticket}) is a close by and profit is 0 ({profit}), skipping")
                return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': True} # Indicate skip
                logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
                return return_value

        # Check if commission already processed (excluding DELAYED)
        # This check prevents reprocessing successful or skipped/failed deals but allows retrying delayed ones.
        if CommissionDistribution.objects.filter(
            commission_tracking__deal=deal_instance
        ).exclude(
            processing_status='DELAYED'
        ).exists():
            logger.info(f"Deal {deal_ticket} has already been processed or skipped/failed. Skipping calculation.")
            return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': True}
            logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
            return return_value

        # Get linked account from the Deal instance
        account = deal_instance.account
        if not account:
            # If the deal wasn't linked to an account during saving, try to find it now.
            # This might happen if the account wasn't created yet when the deal arrived.
            try:
                from shared_models.ib_commission.services.commission_cache_service import CommissionCacheService
                account = CommissionCacheService.get_account(mt5_login)
                logger.info(f"Got account for login {mt5_login} from cache/DB (post-deal): {account is not None}")
            except (ImportError, Exception) as e:
                logger.warning(f"Could not use CommissionCacheService for fallback account lookup: {e}")
                account = Account.objects.filter(login=mt5_login, is_active=True).first()
                logger.info(f"Got account for login {mt5_login} from direct DB query (post-deal): {account is not None}")

            if not account:
                logger.warning(f"Cannot find active account for login {mt5_login} associated with deal {deal_ticket}. Skipping calculation.")
                # We don't create a distribution here, as we can't link it properly.
                # This might need monitoring or a separate retry mechanism if account creation is delayed.
                return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
                logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
                return return_value
            else:
                # Link the found account to the deal instance for consistency
                deal_instance.account = account
                # Note: Consider saving the deal_instance here if this link is critical to persist immediately.
                # deal_instance.save(update_fields=['account']) # Optional: persist the link

        # Get customer from account
        customer = account.customer
        
        # Check if this is a DEMO account and if demo commissions are disabled
        if account.account_type and account.account_type.account_type == 'DEMO':
            from django.conf import settings
            if not getattr(settings, 'ENABLE_DEMO_COMMISSIONS', False):
                logger.info(f"Skipping commission calculation for DEMO account {mt5_login} (ENABLE_DEMO_COMMISSIONS=False)")
                return {
                    'distributions': [], 
                    'client_deduction': 0, 
                    'client_server_id': account.server.id if account.server else None,
                    'is_processed': True  # Mark as processed to avoid retries
                }
            else:
                logger.info(f"Processing commission for DEMO account {mt5_login} (ENABLE_DEMO_COMMISSIONS=True)")

        # Determine which rules to apply based on entry type
        is_entry = entry in [cls.ENTRY_IN, cls.ENTRY_INOUT]  # Entry or InOut
        is_exit = entry in [cls.ENTRY_OUT, cls.ENTRY_OUT_BY]  # Exit or OutBy

        # Determine commission type based on entry/exit
        commission_type_filter = {}
        current_commission_type = None
        if is_entry:
            commission_type_filter = {'commission_type': cls.COMMISSION_TYPE}
            current_commission_type = cls.COMMISSION_TYPE
        elif is_exit:
            commission_type_filter = {'commission_type': cls.REBATE_TYPE}
            current_commission_type = cls.REBATE_TYPE
        else:
             logger.warning(f"Unknown entry type {entry} for deal {deal_ticket}. Skipping calculation.")
             return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
             print(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
             return return_value

        # Find applicable rules for the client's direct IB
        applicable_rules_result = cls._find_applicable_rules(
            ib_id=None, # Will be determined from client mapping
            mt5_account_id=mt5_login,
            symbol=symbol,
            order_type=None, # 'buy'/'sell' isn't used for rule filtering directly
            customer=customer,
            account=account,
            **commission_type_filter
        )

        if not applicable_rules_result or not applicable_rules_result.get('rules'):
            logger.info(f"No applicable {current_commission_type} rules found for deal {deal_ticket}, account {mt5_login}, symbol {symbol}.")
            return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
            print(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
            return return_value

        client_mapping = applicable_rules_result.get('client_mapping')
        direct_ib_rules = applicable_rules_result.get('rules') # Rules applicable to the direct IB for this client/deal

        if not client_mapping:
            logger.warning(f"Client mapping not found for customer {customer.id if customer else 'N/A'} / login {mt5_login}. Skipping calculation.")
            return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
            logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
            return return_value

        distributions = []
        client_deduction = Decimal('0.0')
        opening_deal = None # Initialize opening_deal variable

        # --- Handle Min Trade Time for Exit Deals ---
        delay_distribution = False
        skip_distribution = False
        delay_reason = None
        skip_reason = None

        if is_exit:
            # Check if any applicable rule requires min_trade_time check
            rules_requiring_check = [rule for rule in direct_ib_rules if rule.min_trade_time is not None and rule.min_trade_time > 0]

            if rules_requiring_check:
                logger.info(f"Deal {deal_ticket} is an exit deal, checking min_trade_time for rules: {[r.id for r in rules_requiring_check]}")
                # Attempt to find the corresponding opening deal
                try:
                    # Cache opening deals by position
                    opening_deal_cache_key = f"opening_deal:{position_id}:{mt5_login}"
                    opening_deal = cache.get(opening_deal_cache_key)
                    
                    if opening_deal is False:  # Explicitly cached as not found
                        opening_deal = None
                    elif opening_deal is None:  # Not in cache
                        opening_deal = Deal.objects.filter(
                            position_id=position_id,
                            login=mt5_login, # Ensure it's the same account
                            # entry__in=[cls.ENTRY_IN, cls.ENTRY_INOUT] # Original opening deals
                            entry=cls.ENTRY_IN # Strict check for only ENTRY_IN as opener
                        ).order_by('time').first() # Get the earliest opening deal for the position
                        
                        # Cache even if None to avoid repeated queries
                        cache.set(opening_deal_cache_key, opening_deal or False, 3600)
                    
                    if not opening_deal:
                        logger.warning(f"Opening deal not found for closing deal {deal_ticket} (position_id: {position_id}). Setting status to DELAYED.")
                        delay_distribution = True
                        delay_reason = 'MISSING_OPEN_DEAL'
                    else:
                        # Calculate trade duration
                        duration = deal_instance.time - opening_deal.time
                        duration_seconds = duration.total_seconds()
                        logger.info(f"Found opening deal {opening_deal.deal_ticket} for closing deal {deal_ticket}. Duration: {duration_seconds}s")

                        # Check against rule min_trade_time (use the strictest rule if multiple apply)
                        # Using max() because we skip if duration is LESS than *any* rule's requirement
                        min_required_duration = max(rule.min_trade_time for rule in rules_requiring_check if rule.min_trade_time is not None)

                        if duration_seconds < min_required_duration:
                            logger.warning(f"Trade duration {duration_seconds}s for deal {deal_ticket} is below minimum requirement of {min_required_duration}s. Setting status to SKIPPED.")
                            skip_distribution = True
                            skip_reason = f"Trade duration {duration_seconds:.2f}s < rule minimum {min_required_duration}s"
                        else:
                            logger.info(f"Trade duration {duration_seconds}s meets minimum requirement {min_required_duration}s for deal {deal_ticket}.")

                except Deal.DoesNotExist:
                    logger.warning(f"Opening deal not found for closing deal {deal_ticket} (position_id: {position_id}). Setting status to DELAYED.")
                    delay_distribution = True
                    delay_reason = 'MISSING_OPEN_DEAL'
                except Exception as e:
                    logger.error(f"Error finding opening deal for {deal_ticket}: {e}", exc_info=True)
                    # Decide how to handle: maybe delay or fail? Delaying is safer.
                    delay_distribution = True
                    delay_reason = 'MISSING_OPEN_DEAL'
                    # Alternatively, raise the exception if this shouldn't happen

        # --- Create Records within a Transaction ---
        with transaction.atomic():
            # Create or update CommissionTracking record first
            # Using update_or_create handles potential retries where tracking might exist but distributions failed/delayed.
            commission_tracking, created = CommissionTracking.objects.update_or_create(
                deal=deal_instance, # Use the deal instance as the PK
                defaults={
                    'customer_id': customer.id if customer else None,
                    'direct_ib_customer_id': client_mapping.direct_ib_customer_id,
                    'commission_type': current_commission_type,
                    'rule_id': direct_ib_rules[0].id if direct_ib_rules else None, # Track based on first applicable rule
                    'amount': Decimal('0.0'), # Placeholder, will be updated later
                    'processed_time': timezone.now(), # Update time on each calculation attempt using UTC
                    # Removed redundant fields (symbol, volume, etc.) - they are in deal_instance
                }
            )
            if created:
                logger.info(f"Created CommissionTracking for deal {deal_ticket}.")
            else:
                logger.info(f"Updated existing CommissionTracking for deal {deal_ticket}.")


            # --- Determine Processing Status for Distributions ---
            processing_status = 'PENDING'
            processing_notes = None

            if delay_distribution:
                processing_status = 'DELAYED'
                processing_notes = f"Opening deal {position_id} not found yet."
                # Reset retry count if we are setting to DELAYED status again
                # Note: This update might be redundant if _calculate_rule_based_distribution handles updates
                CommissionDistribution.objects.filter(
                    commission_tracking__deal=deal_instance
                ).update(retry_count=0)
            elif skip_distribution:
                processing_status = 'SKIPPED'
                processing_notes = skip_reason or "Skipped due to rule condition."

            # If status is PENDING, proceed to calculate and create distributions
            if processing_status == 'PENDING':
                # Get all IBs in the hierarchy path
                ib_hierarchy = IBHierarchy.objects.filter(
                    customer_id=client_mapping.direct_ib_customer_id,
                    is_active=True
                ).first()

                if not ib_hierarchy:
                    logger.error(f"IB Hierarchy not found for direct IB {client_mapping.direct_ib_customer_id} linked to deal {deal_ticket}. Cannot calculate distribution.")
                    # Fail the tracking record? Or just return empty? Let's return empty for now.
                    return_value = {'distributions': [], 'client_deduction': 0, 'client_server_id': None, 'is_processed': False}
                    logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
                    return return_value

                # Get all ancestor IB IDs from the path
                path_parts = ib_hierarchy.path.split('.') # Includes the direct IB's ID

                # Parse agreement_path if available (with backward compatibility check)
                agreement_ids = []
                if hasattr(client_mapping, 'agreement_path') and client_mapping.agreement_path:
                    agreement_ids = client_mapping.agreement_path.split('.')
                    
                    # Validate agreement_path structure matches ib_path
                    if len(agreement_ids) != len(path_parts):
                        logger.warning(f"Agreement path length ({len(agreement_ids)}) doesn't match IB path length ({len(path_parts)}) for client {client_mapping.customer_id}")

                # Get all relevant IB agreements (cache this if possible)
                ib_agreements = {}
                
                # Determine commission type for prefetching rules
                current_commission_type = cls.COMMISSION_TYPE if entry in [cls.ENTRY_IN, cls.ENTRY_INOUT] else cls.REBATE_TYPE
                
                # Get ALL agreements with their rules in ONE query
                agreement_members = IBAgreementMember.objects.filter(
                    customer_id__in=path_parts,
                    is_active=True
                ).select_related('agreement').prefetch_related(
                    Prefetch(
                        'agreement__commission_rules',
                        queryset=IBCommissionRule.objects.filter(
                            commission_type=current_commission_type
                        ).select_related('account_type').order_by('priority')
                    )
                )

                # Build ib_agreements respecting agreement_path
                for i, ib_id in enumerate(path_parts):
                    if i < len(agreement_ids) and agreement_ids[i]:
                        # Use specified agreement from agreement_path
                        member = next((m for m in agreement_members 
                                      if str(m.customer_id) == ib_id 
                                      and str(m.agreement_id) == agreement_ids[i]), None)
                        if member:
                            ib_agreements[ib_id] = member.agreement
                        else:
                            logger.warning(f"Agreement {agreement_ids[i]} not found for IB {ib_id}, skipping this IB")
                    else:
                        # Try to use default agreement from IBHierarchy
                        hierarchy = IBHierarchy.objects.filter(
                            customer_id=ib_id, is_active=True
                        ).first()
                        if hierarchy and hasattr(hierarchy, 'default_agreement') and hierarchy.default_agreement:
                            ib_agreements[ib_id] = hierarchy.default_agreement
                        else:
                            # Fallback: use any agreement for this IB (current behavior)
                            member = next((m for m in agreement_members 
                                          if str(m.customer_id) == ib_id), None)
                            if member:
                                ib_agreements[ib_id] = member.agreement

                # Calculate rule-based distribution for the hierarchy
                distributions = cls._calculate_rule_based_distribution(
                    deal_instance=deal_instance, # Pass the Deal instance
                    client_mapping=client_mapping,
                    ib_agreements=ib_agreements,
                    # volume=volume, # Get from deal_instance inside the method
                    # commission_usd=Decimal('0.0'), # Pass relevant data if needed by rules
                    # customer=customer, # Get from deal_instance
                    # account=account, # Get from deal_instance
                    # symbol=symbol, # Get from deal_instance
                    processing_status=processing_status, # Pass determined status
                    processing_notes=processing_notes,
                    commission_tracking=commission_tracking # Pass the tracking object
                )

                # Calculate total distribution amount
                distribution_total = sum(dist.amount for dist in distributions if dist.amount) # Ensure amount is not None

                # Update commission tracking with total amount
                commission_tracking.amount = distribution_total
                commission_tracking.save(update_fields=['amount', 'processed_time'])

                # Calculate client deduction (only for COMMISSIONS on entry trades)
                if is_entry and current_commission_type == cls.COMMISSION_TYPE:
                    client_deduction = sum(
                        d.amount for d in distributions
                        if d.distribution_type == cls.COMMISSION_TYPE and d.amount
                    )
            else:
                # If DELAYED or SKIPPED, create placeholder/status distributions if none exist
                # Or update existing ones if this is a retry
                existing_distributions = CommissionDistribution.objects.filter(
                    commission_tracking__deal=deal_instance
                )
                if not existing_distributions.exists():
                    # Need to create dummy distributions to record the status
                    # Create one for the direct IB to mark the status
                    logger.info(f"Creating placeholder distribution for deal {deal_ticket} with status {processing_status}")
                    # Ensure ib_hierarchy is available if possible
                    ib_hierarchy = None
                    if 'ib_hierarchy' in locals(): # Check if fetched earlier
                        ib_hierarchy = locals()['ib_hierarchy']
                    elif client_mapping: # Fallback: fetch hierarchy for direct IB
                        ib_hierarchy = IBHierarchy.objects.filter(customer_id=client_mapping.direct_ib_customer_id, is_active=True).first()
                        
                    dist = CommissionDistribution.objects.create(
                        commission_tracking=commission_tracking, # Link to the tracking record
                        customer_id=client_mapping.direct_ib_customer_id, # Assign to direct IB
                        ib_account=ib_hierarchy.ib_account if ib_hierarchy else None,
                        mt5_login=ib_hierarchy.mt5_login if ib_hierarchy else 0, # Need a default if no hierarchy
                        distribution_type=current_commission_type, # Mark as commission or rebate
                        amount=Decimal('0.0'), # No amount calculated
                        level=ib_hierarchy.level if ib_hierarchy else 0, # Best guess level
                        rule=direct_ib_rules[0] if direct_ib_rules else None, # Link to a rule if possible
                        is_processed=False, # Not processed yet
                        processed_time=timezone.now(), # Record time of status setting using UTC
                        processing_status=processing_status,
                        processing_notes=processing_notes,
                        delayed_reason=delay_reason if delay_distribution else None,
                        retry_count=0 # Initial attempt
                    )
                    distributions = [dist] # Return this placeholder
                else:
                     # If distributions exist (e.g., from a previous DELAYED state), update them
                     logger.info(f"Updating existing distributions for deal {deal_ticket} to status {processing_status}")
                     num_updated = existing_distributions.update(
                         processing_status=processing_status,
                         processing_notes=processing_notes,
                         delayed_reason=delay_reason if delay_distribution else None,
                         # Optionally update retry_count here if needed based on logic
                     )
                     logger.info(f"Updated {num_updated} distributions.")
                     distributions = list(existing_distributions) # Return the updated distributions

        # --- Return Results ---
        client_server_id = account.server.id if account and account.server else None

        # Batch enrich distributions with server information
        customer_ids_needing_server = [
            d.customer_id for d in distributions 
            if d.customer_id and not (hasattr(d, 'server_id') and d.server_id)
        ]
        
        if customer_ids_needing_server:
            # Get all server IDs in one query
            server_info = IBHierarchy.objects.filter(
                customer_id__in=customer_ids_needing_server,
                is_active=True
            ).select_related('ib_account__server').values_list(
                'customer_id', 'ib_account__server__id'
            )
            
            server_map = dict(server_info)
            
            # Apply to distributions
            for dist in distributions:
                if not hasattr(dist, 'server_id'):
                    ib_account = dist.ib_account # Assuming ib_account FK is populated
                    if ib_account and ib_account.server:
                        dist.server_id = ib_account.server.id
                    elif dist.customer_id in server_map:
                        dist.server_id = server_map[dist.customer_id]

        return_value = {
            'distributions': distributions, # These are saved objects now
            'client_deduction': client_deduction,
            'client_server_id': client_server_id,
            'is_processed': False # Indicate calculation was attempted (not necessarily successful/final)
        }
        logger.debug(f"[CalcDist Return Check] Returning type {type(return_value)}: {return_value}")
        return return_value

    @classmethod
    def process_distributions(cls, deal_ticket, mt5_processing_success=True, processing_notes=None):
        """
        Process distributions after MT5 side has been processed.
        
        Args:
            deal_ticket: The deal ticket ID
            mt5_processing_success: Whether MT5 processing was successful
            processing_notes: Optional notes about the processing status
            
        Returns:
            Dictionary containing:
            - success: Whether processing was successful
            - transactions: List of created transactions
            - message: Status message
        """
        if not mt5_processing_success:
            # If MT5 processing failed, mark distributions with failed status
            # but don't mark them as processed since they weren't actually credited/debited
            CommissionDistribution.objects.filter(
                commission_tracking__deal__deal_ticket=deal_ticket
            ).update(
                processing_status='FAILED',
                processing_notes=processing_notes or 'MT5 processing failed'
            )
            return {
                'success': False,
                'transactions': [],
                'message': 'MT5 processing failed, distributions marked as failed but not processed'
            }
        
        # Get distributions for this deal ticket that are still pending
        distributions = CommissionDistribution.objects.filter(
            commission_tracking__deal__deal_ticket=deal_ticket,
            processing_status='PENDING'
        ).select_related('deal_ticket__customer')
        
        if not distributions:
            return {
                'success': False,
                'transactions': [],
                'message': 'No pending distributions found for this deal ticket'
            }
        
        # Get deal data from the first distribution's deal ticket
        deal_data = {
            'deal': deal_ticket,
            # Add other deal data if available
        }
        
        # Get customer from the first distribution's deal ticket
        customer = distributions.first().deal_ticket.customer
        
        # Create transactions
        transactions = cls._create_transactions(distributions, deal_data, customer)
        
        return {
            'success': True,
            'transactions': transactions,
            'message': f'Successfully processed {len(transactions)} transactions'
        }

    @classmethod
    def _calculate_rule_based_distribution(cls, deal_instance: Deal, client_mapping,
                                         ib_agreements,
                                         # Remove redundant args, get from deal_instance
                                         processing_status, # Pass status determined earlier
                                         processing_notes, # Pass notes determined earlier
                                         commission_tracking: CommissionTracking # Pass tracking record
                                         ):
        """
        Calculate distribution based on individual rules for the entire hierarchy.

        Args:
            deal_instance: The Deal instance containing trade details.
            client_mapping: The ClientIBMapping object for the direct IB.
            ib_agreements: Dictionary of IB agreements keyed by IB ID string.
            processing_status: The determined status ('PENDING', 'DELAYED', 'SKIPPED').
            processing_notes: Notes corresponding to the status.
            commission_tracking: The parent CommissionTracking record.

        Returns:
            List of created CommissionDistribution objects.
        """
        # Extract data from deal_instance
        symbol = deal_instance.symbol
        volume = deal_instance.volume
        # commission_usd might be needed if using PERCENTAGE rules, but requires calculation/lookup first.
        # Assuming LOT_BASED for now, or that commission_usd comes from elsewhere if needed.
        commission_usd = deal_instance.commission # Use the deal's commission field? Or needs separate calculation?
                                                 # Let's assume deal_instance.commission is the basis if needed.

        distributions = []
        calculated_for_ib = set() # Track which IBs have received a distribution for this deal/rule type
        pass_up_amounts = {} # Store amounts to be passed up {parent_ib_id: amount}

        # Get hierarchy info (cache this if possible)
        direct_ib_id = str(client_mapping.direct_ib_customer_id)
        try:
            # Fetch hierarchy for all IBs in the agreements dictionary keys + direct IB
            all_ib_ids = list(map(int, ib_agreements.keys())) # Convert keys to int for query
            if client_mapping.direct_ib_customer_id not in all_ib_ids:
                 all_ib_ids.append(client_mapping.direct_ib_customer_id)

            # Get all IB hierarchies in one query with caching
            hierarchy_cache_key = f"ib_hierarchies_batch:{':'.join(sorted(str(id) for id in all_ib_ids))}"
            hierarchy_info = cache.get(hierarchy_cache_key)
            
            if not hierarchy_info:
                hierarchies = IBHierarchy.objects.filter(
                    customer_id__in=all_ib_ids,
                    is_active=True
                ).select_related('ib_account__server', 'customer') # Preload server info
                hierarchy_info = {
                    str(h.customer_id): { # Use string keys to match ib_agreements
                        'level': h.level,
                        'parent_id': str(h.parent_customer_id) if h.parent_customer_id else None,
                        'ib_account_id': h.ib_account.id if h.ib_account else None,
                        'mt5_login': h.mt5_login,
                        'server_id': h.ib_account.server.id if h.ib_account and h.ib_account.server else None
                    } for h in hierarchies
                }
                cache.set(hierarchy_cache_key, hierarchy_info, 3600)
            logger.debug(f"Hierarchy info fetched for deal {deal_instance.deal_ticket}: {hierarchy_info}")
        except Exception as e:
            logger.error(f"Failed to fetch hierarchy info for deal {deal_instance.deal_ticket}: {e}", exc_info=True)
            return [] # Cannot proceed without hierarchy

        # Start from the direct IB and go up the hierarchy defined by hierarchy_info parent_id links
        # This requires iterating based on the path or levels. Let's process level by level or iterate through agreements.

        # Iterate through involved IBs based on agreements found earlier
        for ib_id_str, agreement in ib_agreements.items():
            if ib_id_str not in hierarchy_info:
                 logger.warning(f"Hierarchy info missing for IB {ib_id_str} with agreement {agreement.id}. Skipping.")
                 continue

            ib_info = hierarchy_info[ib_id_str]
            ib_level = ib_info['level']
            parent_id_str = ib_info['parent_id']

            # *** FIX: Determine commission_type INSIDE the loop for rule filtering ***
            commission_type = cls.COMMISSION_TYPE if deal_instance.entry in [cls.ENTRY_IN, cls.ENTRY_INOUT] else cls.REBATE_TYPE
            rule_filter = {'commission_type': commission_type}

            # Use prefetched rules from the agreement if available
            if hasattr(agreement, 'commission_rules') and hasattr(agreement.commission_rules, 'all'):
                # Rules were prefetched - use them directly
                prefetched_rules = agreement.commission_rules.all()
                account_type_id = deal_instance.account.account_type.id if deal_instance.account and hasattr(deal_instance.account, 'account_type') else None
                
                # Filter rules based on symbol and account type
                applicable_rules = []
                for rule in prefetched_rules:
                    # Check symbol match (supports comma-separated symbols)
                    if rule.symbol and rule.symbol != '*':
                        # Split by comma and check if any match
                        rule_symbols = [s.strip().upper() for s in rule.symbol.split(',')]
                        if symbol.upper() not in rule_symbols:
                            continue
                    # Check account type match
                    if rule.account_type_id and rule.account_type_id != account_type_id:
                        continue
                    applicable_rules.append(rule)
                
                # Sort by priority (should already be sorted from prefetch)
                applicable_rules.sort(key=lambda r: r.priority)
                result = {'rules': applicable_rules}
            else:
                # Fallback to existing method if rules weren't prefetched
                result = cls._find_applicable_rules(
                    ib_id=int(ib_id_str), # Pass the specific IB ID as int
                    mt5_account_id=None,
                    symbol=symbol,
                    order_type=None,
                    customer=None,
                    account=deal_instance.account, # Pass account for context (e.g., account_type filtering)
                    **rule_filter # Apply COMMISSION or REBATE filter
                )

            applicable_rules = result.get('rules', [])
            if not applicable_rules:
                # logger.info(f"No applicable {commission_type} rules found for IB {ib_id_str} / Agreement {agreement.id} / Symbol {symbol}")
                continue

            logger.debug(f"Processing IB {ib_id_str} (Level {ib_level}) for deal {deal_instance.deal_ticket} with {len(applicable_rules)} rules.")

            # Process the highest priority applicable rule for this IB
            # Assuming rules are already sorted by priority in _find_applicable_rules
            rule = applicable_rules[0]
            logger.debug(f"Using rule {rule.id} (Priority {rule.priority}) for IB {ib_id_str}")

            # --- Calculate Base Amount ---
            base_amount = cls._calculate_amount_from_rule(
                rule=rule,
                volume=volume,
                commission_usd=commission_usd # Pass the deal's commission
            )

            if base_amount <= 0:
                logger.debug(f"Rule {rule.id} yielded base amount {base_amount}. Skipping distribution for IB {ib_id_str}.")
                continue

            # --- Calculate Keep Amount ---
            keep_percentage = rule.keep_percentage if rule.keep_percentage is not None else Decimal('100.0') # Default to 100% keep if null
            keep_amount = (base_amount * keep_percentage / Decimal('100.0'))

            if keep_amount > 0 and ib_id_str not in calculated_for_ib:
                logger.debug(f"IB {ib_id_str} keeps {keep_amount} based on rule {rule.id}")
                keep_distribution = CommissionDistribution(
                    commission_tracking=commission_tracking, # Link to tracking record (Corrected FK name)
                    customer_id=int(ib_id_str),
                    ib_account_id=ib_info.get('ib_account_id'),
                    mt5_login=ib_info.get('mt5_login'),
                    distribution_type=commission_type,
                    amount=keep_amount,
                    level=ib_level,
                    rule=rule,
                    is_pass_up=False,
                    is_processed=False, # Will be set later by processing logic
                    processed_time=timezone.now(), # Record time of status setting using UTC
                    processing_status=processing_status, # Set status determined earlier
                    processing_notes=processing_notes,
                    # delayed_reason = set earlier if status is DELAYED
                    # retry_count = set earlier if status is DELAYED
                )
                 # Add server_id for convenience if available
                if ib_info.get('server_id'):
                    keep_distribution.server_id = ib_info['server_id']

                distributions.append(keep_distribution)
                calculated_for_ib.add(ib_id_str) # Mark IB as having received commission/rebate

            # --- Calculate Pass-Up Amount ---
            pass_up_percentage = rule.pass_up_percentage if rule.pass_up_percentage is not None else Decimal('0.0') # Default to 0% pass-up if null
            if parent_id_str and pass_up_percentage > 0:
                pass_up_amount = (base_amount * pass_up_percentage / Decimal('100.0'))
                if pass_up_amount > 0:
                     logger.debug(f"IB {ib_id_str} passes up {pass_up_amount} to parent {parent_id_str} based on rule {rule.id}")
                     # Store pass-up amount for the parent to receive later
                     pass_up_amounts[parent_id_str] = pass_up_amounts.get(parent_id_str, Decimal('0.0')) + pass_up_amount

        # --- Process Pass-Up Amounts ---
        # Add distributions for accumulated pass-up amounts
        for parent_ib_id_str, total_pass_up_amount in pass_up_amounts.items():
            if parent_ib_id_str not in hierarchy_info:
                 logger.warning(f"Hierarchy info missing for parent IB {parent_ib_id_str} receiving pass-up. Skipping pass-up distribution.")
                 continue
            if parent_ib_id_str in calculated_for_ib:
                logger.warning(f"Parent IB {parent_ib_id_str} already received a direct distribution. Skipping pass-up distribution to avoid double payment.")
                continue # Avoid double-paying if parent also had a direct rule match

            parent_info = hierarchy_info[parent_ib_id_str]
            logger.debug(f"Creating pass-up distribution for IB {parent_ib_id_str} (Level {parent_info['level']}) amount {total_pass_up_amount}")

            pass_up_distribution = CommissionDistribution(
                commission_tracking=commission_tracking, # Link to tracking record (Corrected FK name)
                customer_id=int(parent_ib_id_str),
                ib_account_id=parent_info.get('ib_account_id'),
                mt5_login=parent_info.get('mt5_login'),
                distribution_type=commission_type, # Should be same type as originated
                amount=total_pass_up_amount,
                level=parent_info['level'],
                rule=None, # Pass-up doesn't directly associate with one rule? Or use the child's rule? Clarify. Let's use None.
                is_pass_up=True,
                is_processed=False,
                processed_time=timezone.now(), # Record time of status setting using UTC
                processing_status=processing_status, # Pass-up inherits status
                processing_notes=f"Pass-up received. {processing_notes or ''}".strip(),
                # delayed_reason, retry_count also inherit status
            )
            if parent_info.get('server_id'):
                pass_up_distribution.server_id = parent_info['server_id']

            distributions.append(pass_up_distribution)
            calculated_for_ib.add(parent_ib_id_str) # Mark parent as calculated (for pass-up)

        # --- Save Distributions ---
        # Only save if the status is NOT PENDING, as PENDING will be processed later.
        # Or, always save and let the processing logic query PENDING ones?
        # Let's save all created distributions regardless of status.
        # The calling function handles the transaction atomicity.
        if distributions:
            try:
                # Bulk create might be efficient, but need to handle potential conflicts if retrying DELAYED
                # Let's loop and save individually, using update_or_create if needed?
                # No, the initial check prevents re-entry unless DELAYED.
                # So, if we are here and status is DELAYED/SKIPPED, we might be updating.
                # If status is PENDING, we are creating new ones.
                # Let's stick to creating within the transaction block of the caller.
                # The caller should handle saving. This function just returns the list.
                # Correction: Let's save them here to ensure they exist before returning.
                # The caller's transaction.atomic() will wrap this.
                saved_distributions = []
                for dist in distributions:
                    # If status is DELAYED or SKIPPED, check if a distribution for this IB/deal already exists
                    # This handles retries or updates.
                    if dist.processing_status != 'PENDING':
                         existing_dist = CommissionDistribution.objects.filter(
                             commission_tracking=dist.commission_tracking, # Corrected FK filter
                             customer_id=dist.customer_id,
                             # distribution_type=dist.distribution_type # Maybe too specific?
                         ).first()
                         if existing_dist:
                             # Update existing record
                             existing_dist.ib_account = dist.ib_account
                             existing_dist.mt5_login = dist.mt5_login
                             existing_dist.amount = dist.amount # Update amount if recalculated
                             existing_dist.level = dist.level
                             existing_dist.rule = dist.rule
                             existing_dist.is_pass_up = dist.is_pass_up
                             existing_dist.processing_status = dist.processing_status
                             existing_dist.processing_notes = dist.processing_notes
                             # Update delay/retry info if applicable
                             if dist.processing_status == 'DELAYED':
                                 # Get reason from the parent tracking record's FIRST distribution (might be fragile)
                                 first_dist = dist.commission_tracking.distributions.order_by('pk').first()
                                 existing_dist.delayed_reason = first_dist.delayed_reason if first_dist else None
                                 # Retry count handled by Celery task
                             existing_dist.save()
                             saved_distributions.append(existing_dist)
                             logger.debug(f"Updated existing distribution {existing_dist.id} for IB {dist.customer_id} deal {deal_instance.deal_ticket} to status {dist.processing_status}")
                             continue # Skip creating new one

                    # If no existing record found or status is PENDING, create new one
                    dist.save()
                    saved_distributions.append(dist)
                    logger.debug(f"Saved new distribution {dist.id} for IB {dist.customer_id} deal {deal_instance.deal_ticket} with status {dist.processing_status}")

                logger.info(f"Saved {len(saved_distributions)} distributions for deal {deal_instance.deal_ticket}")
                return saved_distributions
            except Exception as e:
                 logger.error(f"Error saving distributions for deal {deal_instance.deal_ticket}: {e}", exc_info=True)
                 # Re-raise the exception to rollback the transaction in the caller? Yes.
                 raise
        else:
            logger.info(f"No distributions calculated for deal {deal_instance.deal_ticket}")
            return []

    @classmethod
    def _calculate_amount_from_rule(cls, rule: IBCommissionRule, volume, commission_usd):
        """
        Calculate amount from a single rule.
        
        Args:
            rule: The IBCommissionRule instance
            volume: The trading volume
            commission_usd: The commission in USD
            
        Returns:
            Decimal value representing the calculated amount
        """
        logger.info(f"[COMMISSION_CALC] _calculate_amount_from_rule called with:")
        logger.info(f"  - Rule ID: {rule.id}, Type: {rule.calculation_type}, Value: {rule.value}")
        logger.info(f"  - Volume: {volume} (type: {type(volume)})")
        logger.info(f"  - Commission USD: {commission_usd}")
        logger.info(f"  - Min Volume: {rule.min_volume}, Min Amount: {rule.min_amount}, Max Amount: {rule.max_amount}")
        
        # Check minimum volume requirement
        min_volume = getattr(rule, 'min_volume', Decimal('0.00')) or Decimal('0.00')
        if Decimal(str(volume)) < min_volume:
            logger.info(f"  - Volume {volume} is below minimum required {min_volume}, returning 0")
            return Decimal('0.0')
        
        if rule.calculation_type == 'LOT_BASED':
            # Get lot size, default to 1 if not specified
            lot_size = getattr(rule, 'lot_size', Decimal('1.00')) or Decimal('1.00')
            # Calculate amount based on lot size
            amount = (Decimal(str(volume)) / lot_size) * rule.value
            logger.info(f"  - LOT_BASED calculation: ({volume} / {lot_size}) * {rule.value} = {amount}")
        elif rule.calculation_type == 'PERCENTAGE':
            amount = (rule.value / Decimal('100.0')) * Decimal(str(commission_usd))
            logger.info(f"  - PERCENTAGE calculation: ({rule.value}/100) * {commission_usd} = {amount}")
        elif rule.calculation_type == 'PIP_VALUE':
            # Implementation for pip value calculation
            amount = Decimal('0.0')
            logger.info(f"  - PIP_VALUE calculation not implemented, returning 0")
        else:  # TIERED
            amount = Decimal('0.0')
            logger.info(f"  - TIERED calculation not implemented, returning 0")
            
        # Apply min/max constraints
        original_amount = amount
        if amount < rule.min_amount:
            amount = rule.min_amount
            logger.info(f"  - Amount {original_amount} below minimum, adjusted to {amount}")
        elif amount > rule.max_amount:
            amount = rule.max_amount
            logger.info(f"  - Amount {original_amount} above maximum, adjusted to {amount}")
            
        logger.info(f"  - Final amount: {amount}")
        return amount
    
    @classmethod
    def _symbol_matches(cls, rule_symbol, deal_symbol):
        """
        Check if a deal symbol matches a rule symbol.
        Supports comma-separated symbols in rule (e.g., "XAUUSD,XAUUSD.v")
        
        Args:
            rule_symbol: The symbol from the rule (can be comma-separated)
            deal_symbol: The symbol from the deal
            
        Returns:
            bool: True if match found
        """
        if not rule_symbol or rule_symbol == '*':
            return True
            
        # Split by comma and check if any match (case-insensitive)
        rule_symbols = [s.strip().upper() for s in rule_symbol.split(',')]
        return deal_symbol.upper() in rule_symbols
    
    @classmethod
    def _find_applicable_rules(cls, ib_id, mt5_account_id, symbol, order_type, customer=None, account=None, **kwargs):
        """
        Find applicable commission rules for a given deal using Django's cache framework
        
        Args:
            ib_id: The IB ID (can be None, will be determined from client mapping)
            mt5_account_id: The MT5 account ID
            symbol: The trading symbol
            order_type: The order type (not used for filtering)
            customer: The customer who made the trade
            account: The account used for the trade
            **kwargs: Additional filters for rules (e.g., commission_type='REBATE')
            
        Returns:
            Dictionary containing:
            - rules: A list of applicable rules
            - client_mapping: The client mapping used to find the rules
        """
        # Import the cache service
        try:
            from shared_models.ib_commission.services.commission_cache_service import CommissionCacheService
            logger.info("Using CommissionCacheService for rule lookups")
        except ImportError:
            logger.warning("CommissionCacheService not available, falling back to database queries")
            CommissionCacheService = None
        
        client_mapping = None
        commission_type = kwargs.get('commission_type')
        account_type_id = account.account_type.id if account and hasattr(account, 'account_type') else None
        
        # If ib_id is provided, we're looking for rules for a specific IB
        if ib_id:
            logger.info(f"Finding rules for specific IB: {ib_id}")
            
            # Get all active agreement memberships for this IB from cache or database
            if CommissionCacheService:
                agreement_members = CommissionCacheService.get_ib_agreements(ib_id)
                logger.info(f"Got {len(agreement_members) if agreement_members else 0} agreement members from cache/DB")
            else:
                agreement_members = IBAgreementMember.objects.filter(
                    customer_id=ib_id,
                    is_active=True
                )
                logger.info(f"Got {agreement_members.count()} agreement members from DB")
            
            if not agreement_members:
                logger.info(f"No active agreements found for IB {ib_id}")
                return {
                    'rules': [],
                    'client_mapping': None
                }
            
            # Find applicable rules for this IB
            for agreement_member in agreement_members:
                # Using caching service
                if CommissionCacheService:
                    # Get all rules for this agreement
                    all_rules = CommissionCacheService.get_commission_rules(
                        agreement_id=agreement_member.agreement_id,
                        symbol=symbol,
                        commission_type=commission_type
                    )
                    
                    logger.info(f"Got {len(all_rules) if all_rules else 0} rules from cache/DB for agreement {agreement_member.agreement_id}")
                    
                    # Rule search order:
                    # 1. Exact symbol + exact account type match
                    # 2. Exact symbol match (any account type)
                    # 3. Any symbol + exact account type match
                    # 4. Wildcard rules (any symbol, any account type)
                    
                    # 1. Exact symbol + exact account type match
                    if account_type_id:
                        exact_symbol_account_type_rules = [
                            rule for rule in all_rules 
                            if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                            and rule.account_type_id == account_type_id
                        ]
                        
                        if exact_symbol_account_type_rules:
                            logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules")
                            # Sort by priority before returning
                            exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                            return {
                                'rules': exact_symbol_account_type_rules,
                                'client_mapping': None
                            }
                    
                    # 2. Exact symbol match (any account type)
                    exact_symbol_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                        and (rule.account_type_id is None)
                    ]
                    
                    if exact_symbol_rules:
                        logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules")
                        # Sort by priority before returning
                        exact_symbol_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_rules,
                            'client_mapping': None
                        }
                    
                    # 3. Any symbol + exact account type match
                    if account_type_id:
                        account_type_rules = [
                            rule for rule in all_rules 
                            if (rule.symbol is None or rule.symbol == '*') 
                            and rule.account_type_id == account_type_id
                        ]
                        
                        if account_type_rules:
                            logger.info(f"Found {len(account_type_rules)} account type rules")
                            # Sort by priority before returning
                            account_type_rules.sort(key=lambda x: x.priority)
                            return {
                                'rules': account_type_rules,
                                'client_mapping': None
                            }
                    
                    # 4. Wildcard rules (any symbol, any account type)
                    wildcard_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and (rule.account_type_id is None)
                    ]
                    
                    if wildcard_rules:
                        logger.info(f"Found {len(wildcard_rules)} wildcard rules")
                        # Sort by priority before returning
                        wildcard_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': wildcard_rules,
                            'client_mapping': None
                        }
                    
                # Using direct database queries
                else:
                    # 1. Exact symbol + exact account type match
                    if account_type_id:
                        # Get all rules with specific symbols (not wildcard)
                        all_symbol_rules = IBCommissionRule.objects.filter(
                            agreement_id=agreement_member.agreement_id,
                            account_type_id=account_type_id
                        ).exclude(symbol__isnull=True).exclude(symbol='*')
                        
                        # Apply additional filters if provided
                        if kwargs:
                            all_symbol_rules = all_symbol_rules.filter(**kwargs)
                        
                        # Order by priority
                        all_symbol_rules = all_symbol_rules.order_by('priority')
                        
                        # Filter in Python to support comma-separated symbols
                        exact_symbol_account_type_rules = [
                            rule for rule in all_symbol_rules
                            if cls._symbol_matches(rule.symbol, symbol)
                        ]
                        
                        if exact_symbol_account_type_rules:
                            logger.info(f"Found exact symbol and account type rules for IB {ib_id}")
                            return {
                                'rules': list(exact_symbol_account_type_rules),
                                'client_mapping': None
                            }
                    
                    # 2. Exact symbol match (any account type)
                    # Get all rules with specific symbols (not wildcard)
                    all_symbol_rules = IBCommissionRule.objects.filter(
                        agreement_id=agreement_member.agreement_id,
                        account_type__isnull=True
                    ).exclude(symbol__isnull=True).exclude(symbol='*')
                    
                    # Apply additional filters if provided
                    if kwargs:
                        all_symbol_rules = all_symbol_rules.filter(**kwargs)
                    
                    # Order by priority
                    all_symbol_rules = all_symbol_rules.order_by('priority')
                    
                    # Filter in Python to support comma-separated symbols
                    exact_symbol_rules = [
                        rule for rule in all_symbol_rules
                        if cls._symbol_matches(rule.symbol, symbol)
                    ]
                    
                    if exact_symbol_rules:
                        logger.info(f"Found exact symbol rules for IB {ib_id}")
                        return {
                            'rules': list(exact_symbol_rules),
                            'client_mapping': None
                        }
                    
                    # 3. Any symbol + exact account type match
                    if account_type_id:
                        account_type_rules = IBCommissionRule.objects.filter(
                            agreement_id=agreement_member.agreement_id,
                            account_type_id=account_type_id
                        ).filter(
                            models.Q(symbol='*') | models.Q(symbol__isnull=True)
                        )
                        
                        # Apply additional filters if provided
                        if kwargs:
                            account_type_rules = account_type_rules.filter(**kwargs)
                        
                        # Order by priority
                        account_type_rules = account_type_rules.order_by('priority')
                        
                        if account_type_rules.exists():
                            logger.info(f"Found account type rules for IB {ib_id}")
                            return {
                                'rules': list(account_type_rules),
                                'client_mapping': None
                            }
                    
                    # 4. Wildcard rules (any symbol, any account type)
                    wildcard_rules = IBCommissionRule.objects.filter(
                        agreement_id=agreement_member.agreement_id,
                        account_type__isnull=True
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        wildcard_rules = wildcard_rules.filter(**kwargs)
                    
                    # Order by priority
                    wildcard_rules = wildcard_rules.order_by('priority')
                    
                    if wildcard_rules.exists():
                        logger.info(f"Found wildcard rules for IB {ib_id}")
                        return {
                            'rules': list(wildcard_rules),
                            'client_mapping': None
                        }
            
            logger.info(f"No applicable rules found for IB {ib_id}")
            return {
                'rules': [],
                'client_mapping': None
            }
        
        # If ib_id is not provided, we're looking for rules for a client's direct IB
        # Get client mapping from cache or database
        if mt5_account_id and customer:
            if CommissionCacheService:
                client_mapping = CommissionCacheService.get_client_mapping(mt5_account_id, customer.id)
                logger.info(f"Got client mapping from cache/DB for mt5_login={mt5_account_id}, customer_id={customer.id}: {client_mapping is not None}")
            else:
                # PRIORITY 1: Find client mapping with account and mt5_login
                client_mapping = ClientIBMapping.objects.filter(
                    mt5_login=mt5_account_id,
                    customer=customer
                ).first()
                logger.info(f"Got client mapping from DB for mt5_login={mt5_account_id}, customer_id={customer.id}: {client_mapping is not None}")
        
        # PRIORITY 2: If no account-specific mapping, try to find customer mapping
        if not client_mapping and customer:
            if CommissionCacheService:
                client_mapping = CommissionCacheService.get_client_mapping(None, customer.id)
                logger.info(f"Got client mapping from cache/DB for customer_id={customer.id}: {client_mapping is not None}")
            else:
                client_mapping = ClientIBMapping.objects.filter(
                    customer=customer
                ).first()
                logger.info(f"Got client mapping from DB for customer_id={customer.id}: {client_mapping is not None}")
        
        # If no client mapping found, return empty result
        if not client_mapping:
            logger.warning("No client mapping found")
            return {
                'rules': [],
                'client_mapping': None
            }
        
        # Get the IB ID from the client mapping if not provided
        ib_id = client_mapping.direct_ib_customer_id
        logger.info(f"Using IB ID from client mapping: {ib_id}")
        
        # PRIORITY 1: Check for account-specific agreement overrides
        account_agreements = IBAccountAgreement.objects.filter(
            mt5_login=mt5_account_id,
            ib_customer_id=ib_id,
        ).values_list('agreement_id', flat=True)
        logger.info(f"Account-specific agreements: {list(account_agreements)}")
        
        # If account-specific agreements exist, use those
        if account_agreements:
            if CommissionCacheService:
                all_rules = []
                for agreement_id in account_agreements:
                    # Get all rules for this agreement
                    rules = CommissionCacheService.get_commission_rules(
                        agreement_id=agreement_id,
                        symbol=symbol,
                        commission_type=commission_type
                    )
                    
                    logger.info(f"Got {len(rules) if rules else 0} rules from cache/DB for account-specific agreement {agreement_id}")
                    
                    if rules:
                        all_rules.extend(rules)
                
                # Apply the same rule search order as above
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_symbol_account_type_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if exact_symbol_account_type_rules:
                        logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules for account-specific agreements")
                        # Sort by priority before returning
                        exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = [
                    rule for rule in all_rules 
                    if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                    and (rule.account_type_id is None)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules for account-specific agreements")
                    # Sort by priority before returning
                    exact_symbol_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if account_type_rules:
                        logger.info(f"Found {len(account_type_rules)} account type rules for account-specific agreements")
                        # Sort by priority before returning
                        account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = [
                    rule for rule in all_rules 
                    if (rule.symbol is None or rule.symbol == '*') 
                    and (rule.account_type_id is None)
                ]
                
                if wildcard_rules:
                    logger.info(f"Found {len(wildcard_rules)} wildcard rules for account-specific agreements")
                    # Sort by priority before returning
                    wildcard_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': wildcard_rules,
                        'client_mapping': client_mapping
                    }
            else:
                # Direct database queries with the same rule search order
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    # Get all rules with specific symbols (not wildcard)
                    all_symbol_rules = IBCommissionRule.objects.filter(
                        agreement_id__in=account_agreements,
                        account_type_id=account_type_id
                    ).exclude(symbol__isnull=True).exclude(symbol='*')
                    
                    # Apply additional filters if provided
                    if kwargs:
                        all_symbol_rules = all_symbol_rules.filter(**kwargs)
                    
                    # Order by priority
                    all_symbol_rules = all_symbol_rules.order_by('priority')
                    
                    # Filter in Python to support comma-separated symbols
                    exact_rules = [
                        rule for rule in all_symbol_rules
                        if cls._symbol_matches(rule.symbol, symbol)
                    ]
                    
                    if exact_rules:
                        logger.info(f"Found exact symbol and account type rules for account-specific agreements")
                        return {
                            'rules': exact_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                # Get all rules with specific symbols (not wildcard)
                all_symbol_rules = IBCommissionRule.objects.filter(
                    agreement_id__in=account_agreements,
                    account_type__isnull=True
                ).exclude(symbol__isnull=True).exclude(symbol='*')
                
                # Apply additional filters if provided
                if kwargs:
                    all_symbol_rules = all_symbol_rules.filter(**kwargs)
                
                # Order by priority
                all_symbol_rules = all_symbol_rules.order_by('priority')
                
                # Filter in Python to support comma-separated symbols
                exact_symbol_rules = [
                    rule for rule in all_symbol_rules
                    if cls._symbol_matches(rule.symbol, symbol)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found exact symbol rules for account-specific agreements")
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = IBCommissionRule.objects.filter(
                        agreement_id__in=account_agreements,
                        account_type_id=account_type_id
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        account_type_rules = account_type_rules.filter(**kwargs)
                    
                    # Order by priority
                    account_type_rules = account_type_rules.order_by('priority')
                    
                    if account_type_rules.exists():
                        logger.info(f"Found account type rules for account-specific agreements")
                        return {
                            'rules': list(account_type_rules),
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = IBCommissionRule.objects.filter(
                    agreement_id__in=account_agreements,
                    account_type__isnull=True
                ).filter(
                    models.Q(symbol='*') | models.Q(symbol__isnull=True)
                )
                
                # Apply additional filters if provided
                if kwargs:
                    wildcard_rules = wildcard_rules.filter(**kwargs)
                
                # Order by priority
                wildcard_rules = wildcard_rules.order_by('priority')
                
                if wildcard_rules.exists():
                    logger.info(f"Found wildcard rules for account-specific agreements")
                    return {
                        'rules': list(wildcard_rules),
                        'client_mapping': client_mapping
                    }
        
        logger.info(f"Client mapping agreement: {getattr(client_mapping, 'agreement', None)}")
        logger.info(f"Client mapping agreement ID: {client_mapping.agreement.id if hasattr(client_mapping, 'agreement') and client_mapping.agreement else 'None'}")
        logger.info(f"Client mapping agreement_id: {client_mapping.agreement_id}")
        
        # If client mapping exists and has a specific agreement, use that
        if client_mapping and client_mapping.agreement_id:
            if CommissionCacheService:
                # Get all rules for this agreement
                all_rules = CommissionCacheService.get_commission_rules(
                    agreement_id=client_mapping.agreement_id,
                    symbol=symbol,
                    commission_type=commission_type
                )
                
                logger.info(f"Got {len(all_rules) if all_rules else 0} rules from cache/DB for client mapping agreement {client_mapping.agreement_id}")
                
                # Apply the same rule search order as above
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    exact_symbol_account_type_rules = [
                        rule for rule in all_rules 
                        if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if exact_symbol_account_type_rules:
                        logger.info(f"Found {len(exact_symbol_account_type_rules)} exact symbol and account type rules for client mapping agreement")
                        # Sort by priority before returning
                        exact_symbol_account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': exact_symbol_account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                exact_symbol_rules = [
                    rule for rule in all_rules 
                    if rule.symbol and cls._symbol_matches(rule.symbol, symbol)
                    and (rule.account_type_id is None)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found {len(exact_symbol_rules)} exact symbol rules for client mapping agreement")
                    # Sort by priority before returning
                    exact_symbol_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = [
                        rule for rule in all_rules 
                        if (rule.symbol is None or rule.symbol == '*') 
                        and rule.account_type_id == account_type_id
                    ]
                    
                    if account_type_rules:
                        logger.info(f"Found {len(account_type_rules)} account type rules for client mapping agreement")
                        # Sort by priority before returning
                        account_type_rules.sort(key=lambda x: x.priority)
                        return {
                            'rules': account_type_rules,
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = [
                    rule for rule in all_rules 
                    if (rule.symbol is None or rule.symbol == '*') 
                    and (rule.account_type_id is None)
                ]
                
                if wildcard_rules:
                    logger.info(f"Found {len(wildcard_rules)} wildcard rules for client mapping agreement")
                    # Sort by priority before returning
                    wildcard_rules.sort(key=lambda x: x.priority)
                    return {
                        'rules': wildcard_rules,
                        'client_mapping': client_mapping
                    }
                
                return {
                    'rules': [],
                    'client_mapping': client_mapping
                }
            else:
                # Direct database queries with the same rule search order
                # 1. Exact symbol + exact account type match
                if account_type_id:
                    # Get all rules with specific symbols (not wildcard)
                    all_symbol_rules = IBCommissionRule.objects.filter(
                        agreement_id=client_mapping.agreement_id,
                        account_type_id=account_type_id
                    ).exclude(symbol__isnull=True).exclude(symbol='*')
                    
                    # Apply additional filters if provided
                    if kwargs:
                        all_symbol_rules = all_symbol_rules.filter(**kwargs)
                    
                    # Order by priority
                    all_symbol_rules = all_symbol_rules.order_by('priority')
                    
                    # Filter in Python to support comma-separated symbols
                    exact_rules = [
                        rule for rule in all_symbol_rules
                        if cls._symbol_matches(rule.symbol, symbol)
                    ]
                    
                    if exact_rules:
                        logger.info(f"Found exact symbol and account type rules for client mapping agreement")
                        return {
                            'rules': exact_rules,
                            'client_mapping': client_mapping
                        }
                
                # 2. Exact symbol match (any account type)
                # Get all rules with specific symbols (not wildcard)
                all_symbol_rules = IBCommissionRule.objects.filter(
                    agreement_id=client_mapping.agreement_id,
                    account_type__isnull=True
                ).exclude(symbol__isnull=True).exclude(symbol='*')
                
                # Apply additional filters if provided
                if kwargs:
                    all_symbol_rules = all_symbol_rules.filter(**kwargs)
                
                # Order by priority
                all_symbol_rules = all_symbol_rules.order_by('priority')
                
                # Filter in Python to support comma-separated symbols
                exact_symbol_rules = [
                    rule for rule in all_symbol_rules
                    if cls._symbol_matches(rule.symbol, symbol)
                ]
                
                if exact_symbol_rules:
                    logger.info(f"Found exact symbol rules for client mapping agreement")
                    return {
                        'rules': exact_symbol_rules,
                        'client_mapping': client_mapping
                    }
                
                # 3. Any symbol + exact account type match
                if account_type_id:
                    account_type_rules = IBCommissionRule.objects.filter(
                        agreement_id=client_mapping.agreement_id,
                        account_type_id=account_type_id
                    ).filter(
                        models.Q(symbol='*') | models.Q(symbol__isnull=True)
                    )
                    
                    # Apply additional filters if provided
                    if kwargs:
                        account_type_rules = account_type_rules.filter(**kwargs)
                    
                    # Order by priority
                    account_type_rules = account_type_rules.order_by('priority')
                    
                    if account_type_rules.exists():
                        logger.info(f"Found account type rules for client mapping agreement")
                        return {
                            'rules': list(account_type_rules),
                            'client_mapping': client_mapping
                        }
                
                # 4. Wildcard rules (any symbol, any account type)
                wildcard_rules = IBCommissionRule.objects.filter(
                    agreement_id=client_mapping.agreement_id,
                    account_type__isnull=True
                ).filter(
                    models.Q(symbol='*') | models.Q(symbol__isnull=True)
                )
                
                # Apply additional filters if provided
                if kwargs:
                    wildcard_rules = wildcard_rules.filter(**kwargs)
                
                # Order by priority
                wildcard_rules = wildcard_rules.order_by('priority')
                
                if wildcard_rules.exists():
                    logger.info(f"Found wildcard rules for client mapping agreement")
                    return {
                        'rules': list(wildcard_rules),
                        'client_mapping': client_mapping
                    }
                
                logger.info(f"No applicable rules found for agreement {client_mapping.agreement_id}")
                
                return {
                    'rules': [],
                    'client_mapping': client_mapping
                }
        
        # If we get here, no applicable rules were found
        logger.info("No applicable rules were found")
        return {
            'rules': [],
            'client_mapping': client_mapping
        }
    
    @classmethod
    def _calculate_client_deduction(cls, distributions):
        """
        Calculate the total amount to deduct from the client.
        
        Args:
            distributions: List of CommissionDistribution objects
            
        Returns:
            Decimal value of total client deduction
        """
        # Sum up all commission distributions (not rebates)
        return sum(
            d.amount for d in distributions 
            if d.distribution_type == cls.COMMISSION_TYPE
        )
    
    @classmethod
    def _create_transactions(cls, distributions, deal_data, customer):
        """
        Create CommissionRebateTransaction records for distributions.
        
        Args:
            distributions: List of CommissionDistribution objects
            deal_data: Original MT5 deal data
            customer: Customer model instance
            
        Returns:
            List of created transaction records
        """
        transactions = []
        
        with transaction.atomic():
            for dist in distributions:
                # Create transaction record
                tx = CommissionRebateTransaction.objects.create(
                    ib_account=dist.ib_account,
                    account=dist.ib_account,
                    amount=dist.amount,
                    customer_id=customer.id if customer else None,
                    transaction_type=dist.distribution_type,
                    status='APPROVED',
                    calculation_basis={
                        'deal_ticket': dist.deal_ticket_id,
                        'distribution_id': dist.id,
                        'rule_id': dist.rule_id,
                        'mt5_data': deal_data
                    }
                )
                transactions.append(tx)
                
                # Update distribution with transaction reference and mark as processed
                dist.transaction = tx
                dist.is_processed = True
                dist.processing_status = 'PROCESSED'
                dist.processing_notes = 'Successfully processed and transaction created'
                dist.save()
        
        return transactions
    
    @classmethod
    def _create_distribution_from_rule(cls, deal_ticket, rule, client_id, ib_id, volume, commission_usd):
        """
        Create a commission distribution based on a rule.
        
        Args:
            deal_ticket: The deal ticket ID
            rule: The IBCommissionRule instance
            client_id: The client ID
            ib_id: The IB ID
            volume: The trading volume
            commission_usd: The commission in USD
            
        Returns:
            The created CommissionDistribution instance
        """
        # Calculate amount based on rule type
        amount = Decimal('0.0')
        
        if rule.calculation_method == 'fixed':
            amount = rule.value
        elif rule.calculation_method == 'percentage':
            amount = (rule.value / Decimal('100.0')) * Decimal(str(commission_usd))
        elif rule.calculation_method == 'per_lot':
            amount = rule.value * Decimal(str(volume))
        
        # Determine distribution type
        distribution_type = cls.REBATE_TYPE if rule.is_rebate else cls.COMMISSION_TYPE
        
        # Create the distribution
        if amount > Decimal('0.0'):
            return CommissionDistribution.objects.create(
                deal_ticket=deal_ticket,
                customer_id=ib_id,
                client_customer_id=client_id,
                distribution_type=distribution_type,
                amount=amount,
                rule=rule,
                is_processed=False,
                processed_time=timezone.now()
            )
        
        return None 