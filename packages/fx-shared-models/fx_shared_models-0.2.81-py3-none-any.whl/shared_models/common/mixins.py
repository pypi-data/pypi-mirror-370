import logging
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

class SensitiveFieldsTrackingMixin:
    """
    Mixin to track changes in sensitive fields and log them appropriately.
    """
    sensitive_fields = []  # List of fields to track
    requires_approval_fields = []  # Fields that require approval before change

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_sensitive_values = self._get_sensitive_values()

    def _get_sensitive_values(self):
        """Get current values of sensitive fields"""
        return {
            field: getattr(self, field)
            for field in self.sensitive_fields
            if hasattr(self, field)
        }

    def _get_sensitive_field_changes(self):
        """Compare current values with original values"""
        current_values = self._get_sensitive_values()
        changes = {}
        
        for field, original_value in self._original_sensitive_values.items():
            current_value = current_values.get(field)
            if current_value != original_value:
                changes[field] = {
                    'from': original_value,
                    'to': current_value
                }
        return changes

    def _get_actor_info(self, request=None):
        """Get actor information from request"""
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            # User is authenticated
            service_name = getattr(settings, 'SERVICE_NAME', '').lower()
            actor_details = {
                'email': getattr(request.user, 'email', None),
                'username': getattr(request.user, 'username', None),
                'first_name': getattr(request.user, 'first_name', None),
                'last_name': getattr(request.user, 'last_name', None)
            }
            logger.debug(f"Found authenticated user: {actor_details['email']}")
            
            if service_name == 'cp':
                return {
                    'type': 'CUSTOMER',
                    'id': request.user.id,
                    'details': actor_details
                }
            return {
                'type': 'USER',
                'id': request.user.id,
                'details': actor_details
            }
        
        logger.debug("No authenticated user found, using SYSTEM actor")
        return {
            'type': 'SYSTEM',
            'id': 0,
            'details': {'system': 'automated'}
        }

    def _get_affected_customer_id(self):
        """Get the affected customer ID"""
        # Import locally to avoid circular imports
        try:
            from shared_models.customers.models import Customer
        except ImportError:
            # Fallback if the import fails
            Customer = None
        
        # If this model is a Customer
        if Customer and isinstance(self, Customer):
            return self.id
            
        # If this model has a customer relation
        if hasattr(self, 'customer_id'):
            return self.customer_id
        if hasattr(self, 'customer'):
            return self.customer.id
            
        return None

    def save(self, *args, **kwargs):
        # Extract request from kwargs if present
        request = kwargs.pop('request', None)
        
        is_new = self._state.adding
        if not is_new:
            changes = self._get_sensitive_field_changes()
            if changes:
                self._handle_sensitive_field_changes(changes, request=request)
        
        result = super().save(*args, **kwargs)
        if not is_new:
            self._original_sensitive_values = self._get_sensitive_values()
        return result

    def _handle_sensitive_field_changes(self, changes, request=None):
        """Handle changes in sensitive fields"""
        # Get actor information using passed request if available
        actor_info = self._get_actor_info(request)
        affected_customer_id = self._get_affected_customer_id()
        
        logger.debug(f"Handling sensitive changes. Actor: {actor_info}, Customer: {affected_customer_id}")
        
        ip_address = None
        user_agent = None
        
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
                
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT')
            
            logger.debug(f"Request context found. IP: {ip_address}, UA: {user_agent}")
        else:
            logger.debug("No request context found")
        
        for field, change in changes.items():
            # Try to import AuditLogService, but make it optional
            try:
                from apps.common.modules.audit.services import AuditLogService
                # Create audit log entry with full context
                AuditLogService.log(
                    actor_type=actor_info['type'],
                    actor_id=actor_info['id'],
                    actor_details=actor_info['details'],
                    action='SENSITIVE_CHANGE',
                    description=f'Sensitive field {field} was changed',
                    customer_description=f'Your {field} information was updated',
                    target_object=self,
                    level='WARNING',
                    changes={
                        'field': field,
                        'changes': change,
                        'field_type': 'sensitive'
                    },
                    metadata={
                        'service': {
                            'name': getattr(settings, 'SERVICE_NAME', 'crm'),
                            'environment': getattr(settings, 'ENVIRONMENT', 'development')
                        },
                        'event': {
                            'dataset': 'sensitive_data',
                            'module': 'customer',
                            'field_name': field
                        },
                        'request': {
                            'ip_address': ip_address,
                            'user_agent': user_agent
                        }
                    },
                    affected_customer_id=affected_customer_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except ImportError:
                # Log that audit service is not available
                logger.warning(f"AuditLogService not available. Sensitive field {field} was changed but not logged.")

            # If field requires approval, handle it
            if field in self.requires_approval_fields:
                self._handle_approval_required_change(field, change)

    def _handle_approval_required_change(self, field, change):
        """Handle changes that require approval"""
        try:
            from apps.common.modules.notifications.services import NotificationService
            
            # Create a notification for admins
            NotificationService.send_notification(
                type='SENSITIVE_DATA',
                subtype='CHANGE_APPROVAL_REQUIRED',
                title=f'Approval Required: {field} Change',
                message=f'A change to {field} requires approval',
                level='WARNING',
                data={
                    'field': field,
                    'changes': change,
                    'model': self._meta.model_name,
                    'object_id': self.pk
                }
            )
        except ImportError:
            # Log that notification service is not available
            logger.warning(f"NotificationService not available. Approval required for {field} change but notification not sent.") 