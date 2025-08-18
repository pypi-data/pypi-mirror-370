from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re
from shared_models.common.base import BaseModel
from shared_models.system_settings.models.email import EmailTemplate


class ContentType:
    HTML = 'HTML'
    TEXT = 'TEXT'


class EmailCampaign(BaseModel):
    """
    Model for storing email campaign data with flexible filters.
    
    The filters field is implemented as a JSONField to allow for
    a flexible and scalable filtering mechanism that can grow
    from 1 to 10,000+ filters depending on the use case.
    """
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')),
        ('SCHEDULED', _('Scheduled')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(_('Campaign Name'), max_length=255)
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, help_text=_(
        'Email template with placeholders for content sections'
    ))
    schedule_type = models.CharField(_('Schedule Type'), max_length=100)
    schedule_time = models.DateTimeField(_('Schedule Time'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    available_variables = models.JSONField(
        _('Available Variables'),
        help_text=_('Variables that can be used in email content (e.g., ["customer_name", "account_number"])'),
        default=list
    )
    filters = models.JSONField(_('Filters'), default=dict, blank=True, help_text=_(
        'Flexible filtering criteria for targeting email recipients. '
        'Can include country, kycStatus, leadStatus, callStatus, '
        'isFunded, customerType, source, agentId, ibId, createdAtFrom, '
        'createdAtTo, and any other future filter criteria.'
    ))
    
    class Meta:
        app_label = 'shared_email_campaign'
        db_table = 'shared_email_campaign'
        verbose_name = _('Email Campaign')
        verbose_name_plural = _('Email Campaigns')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['schedule_type']),
            models.Index(fields=['schedule_time']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ('manage_emailcampaign_schedule', 'Can schedule and cancel email campaigns'),
            ('send_emailcampaign_test', 'Can send test emails'),
            ('view_emailcampaign_statistics', 'Can view campaign statistics and reports'),
            ('access_emailcampaign_recipient_count', 'Can access recipient count')
        ]
    
    def __str__(self):
        return self.name


class EmailCampaignContent(BaseModel):
    """
    Multi-language content for email campaigns.
    
    Content sections that will be inserted into template placeholders.
    Can use variables like {{ customer_name }} which will be replaced at send time.
    Supports conditional content based on recipient attributes.
    """
    id = models.AutoField(primary_key=True, editable=False)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='contents')
    language_code = models.CharField(_('Language Code'), max_length=10, help_text=_('e.g., "en", "es", "fr"'))
    subject = models.CharField(_('Email Subject'), max_length=255)
    content_sections = models.JSONField(
        _('Content Sections'),
        help_text=_(
            'Dict mapping template placeholders to content structures. '
            'Each structure has "default" content and optional "condition_sets". '
            'Content can include {{ variables }}'
        ),
        default=dict
    )
    content_type = models.CharField(
        _('Content Type'),
        max_length=20,
        choices=[(t, t) for t in [ContentType.HTML, ContentType.TEXT]],
        default=ContentType.HTML
    )
    
    def get_used_variables(self) -> set:
        """Extract all variables used in subject and content sections"""
        pattern = r'{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}'
        variables = set()
        
        # Check subject
        variables.update(re.findall(pattern, self.subject))
        
        # Check all content sections
        for section_data in self.content_sections.values():
            if 'default' in section_data:
                variables.update(re.findall(pattern, section_data['default']))
            
            if 'condition_sets' in section_data and isinstance(section_data['condition_sets'], list):
                for condition_set in section_data['condition_sets']:
                    if isinstance(condition_set, dict) and 'content' in condition_set:
                        variables.update(re.findall(pattern, condition_set['content']))
            
        return variables
    
    def clean(self):
        """Validate the model"""
        super().clean()

        template_placeholders = set(self.campaign.template.content_placeholders)
        content_sections_keys = set(self.content_sections.keys())

        # Check for missing required placeholders
        missing_placeholders = template_placeholders - content_sections_keys
        if missing_placeholders:
            raise ValidationError({
                'content_sections': f'Missing content structure for required placeholders: {", ".join(missing_placeholders)}'
            })

        # Check for extra placeholders that aren't in the template
        extra_placeholders = content_sections_keys - template_placeholders
        if extra_placeholders:
            raise ValidationError({
                'content_sections': f'Content sections contain placeholders not in template: {", ".join(extra_placeholders)}'
            })

        # Validate the structure of each content section
        for placeholder, section_data in self.content_sections.items():
            if not isinstance(section_data, dict):
                raise ValidationError({
                    'content_sections': f"Structure for placeholder '{placeholder}' must be a dictionary."
                })
            if 'default' not in section_data:
                raise ValidationError({
                    'content_sections': f"Structure for placeholder '{placeholder}' must contain a 'default' key."
                })
            if 'condition_sets' in section_data:
                if not isinstance(section_data['condition_sets'], list):
                    raise ValidationError({
                        'content_sections': f"'condition_sets' for placeholder '{placeholder}' must be a list."
                    })
                for i, condition_set in enumerate(section_data['condition_sets']):
                    if not isinstance(condition_set, dict):
                        raise ValidationError({
                            'content_sections': f"Condition set {i+1} for placeholder '{placeholder}' must be a dictionary."
                        })
                    required_keys = {'conditions', 'content'}
                    if not required_keys.issubset(condition_set.keys()):
                        raise ValidationError({
                            'content_sections': f"Condition set {i+1} for placeholder '{placeholder}' is missing required keys: {', '.join(required_keys - set(condition_set.keys()))}."
                        })
                    if not isinstance(condition_set['conditions'], list):
                        raise ValidationError({
                            'content_sections': f"'conditions' in set {i+1} for placeholder '{placeholder}' must be a list."
                        })
    
    class Meta:
        app_label = 'shared_email_campaign'
        db_table = 'shared_email_campaign_content'
        verbose_name = _('Email Campaign Content')
        verbose_name_plural = _('Email Campaign Contents')
        ordering = ['-created_at']
        unique_together = ('campaign', 'language_code', 'content_type')
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['language_code']),
        ]
        permissions = []
    
    def __str__(self):
        return f"{self.campaign.name} - {self.language_code} ({self.content_type})"


class EmailCampaignEvent(BaseModel):
    """
    Model for tracking events in the lifecycle of an email campaign.
    
    Events can include: scheduled, edited, starting, warning, failed, completed, etc.
    This provides a detailed audit trail of what happened during the campaign.
    """
    EVENT_TYPES = [
        ('SCHEDULED', _('Scheduled')),
        ('EDITED', _('Edited')),
        ('STARTING', _('Starting')),
        ('WARNING', _('Warning')),
        ('FAILED', _('Failed')),
        ('COMPLETED', _('Completed')),
    ]
    
    id = models.AutoField(primary_key=True, editable=False)
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(_('Event Type'), max_length=20, choices=EVENT_TYPES)
    details = models.JSONField(_('Event Details'), default=dict, blank=True, help_text=_(
        'Additional details about the event, such as error messages, success counts, etc.'
    ))
    description = models.TextField(_('Description'), blank=True, null=True)
    
    class Meta:
        app_label = 'shared_email_campaign'
        db_table = 'shared_email_campaign_event'
        verbose_name = _('Email Campaign Event')
        verbose_name_plural = _('Email Campaign Events')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['event_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        # Get the display value from the choices
        event_type_display = dict(self.EVENT_TYPES).get(self.event_type, self.event_type)
        return f"{self.campaign.name} - {event_type_display} at {self.created_at}"
