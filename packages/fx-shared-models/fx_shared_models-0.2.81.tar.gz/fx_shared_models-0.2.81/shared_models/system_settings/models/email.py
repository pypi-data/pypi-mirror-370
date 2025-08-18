from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ...constants import EmailProvider, SettingType, ContentType, BaseEmailVariables, SystemEmailTrigger
from .base import SystemSetting
import re

class EmailConfiguration(SystemSetting):
    """
    Email provider configuration for the system.
    Credentials are stored in Azure Key Vault.
    """
    provider = models.CharField(
        max_length=50,
        choices=[(p.value, p.value) for p in EmailProvider],
        default=EmailProvider.SMTP
    )
    from_email = models.EmailField(validators=[validate_email])
    reply_to = models.EmailField(validators=[validate_email], null=True, blank=True)
    
    # SMTP specific settings
    use_tls = models.BooleanField(
        default=True,
        help_text="Use TLS encryption for SMTP"
    )
    use_ssl = models.BooleanField(
        default=False,
        help_text="Use SSL encryption for SMTP. Don't enable both TLS and SSL."
    )
    timeout = models.IntegerField(
        default=30,
        help_text="Connection timeout in seconds"
    )
    debug_level = models.IntegerField(
        default=0,
        help_text="SMTP debug level (0-2). Higher values for more verbose logging."
    )

    def clean(self):
        """Validate the model"""
        super().clean()
        
        if self.use_tls and self.use_ssl:
            raise ValidationError({
                'use_ssl': "Cannot use both TLS and SSL simultaneously",
                'use_tls': "Cannot use both TLS and SSL simultaneously"
            })

    def save(self, *args, **kwargs):
        self.clean()
        self.setting_type = SettingType.EMAIL.value
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'system_email_configuration'
        app_label = 'system_settings'
        verbose_name = 'Email Configuration'
        verbose_name_plural = 'Email Configurations'

    def __str__(self):
        return f"{self.name} ({self.provider})"

class EmailTemplate(SystemSetting):
    """
    HTML email template with placeholders for content sections.
    Example:
    <div>___header___</div>
    <div>___content1___</div>
    <button>___button1Title___</button>
    """
    html_template = models.TextField(
        help_text="HTML template with placeholders like ___content1___, ___button1Title___",
        default="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div>___header___</div>
    <div>___main_content___</div>
    <div>___footer___</div>
</body>
</html>
        """.strip()
    )
    content_placeholders = models.JSONField(
        help_text="List of content placeholders in the template (e.g., ['content1', 'button1Title'])",
        default=list
    )

    def save(self, *args, **kwargs):
        # Extract placeholders from html_template using regex
        pattern = r'___([a-zA-Z][a-zA-Z0-9_]*)___'
        placeholders = re.findall(pattern, self.html_template)
        
        # Handle the case where html_template might have extra whitespace
        if not placeholders:
            # Try with stripped template
            placeholders = re.findall(pattern, self.html_template.strip())
        
        self.content_placeholders = list(set(placeholders))  # Remove duplicates
        self.setting_type = SettingType.EMAIL.value
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'system_email_template'
        app_label = 'system_settings'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

class SystemEmail(SystemSetting):
    """
    System email configuration that defines when and how emails are sent.
    Links a template with its content and trigger events.
    """
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT)
    available_variables = models.JSONField(
        help_text="Additional variables specific to this type of system email (e.g., ['order_number', 'amount']). Base variables are automatically included.",
        default=list
    )
    cc = models.JSONField(default=list)  # List of email addresses
    bcc = models.JSONField(default=list)  # List of email addresses
    trigger_event = models.CharField(
        max_length=255,
        help_text="Event that triggers this email. Must be one of the predefined trigger events."
    )

    @property
    def all_available_variables(self) -> list:
        """Get all available variables including base variables"""
        return BaseEmailVariables.get_all_variables() + self.available_variables

    def clean(self):
        """Validate the model"""
        super().clean()
        
        # Validate trigger event
        valid_triggers = SystemEmailTrigger.get_all_triggers()
        if self.trigger_event not in valid_triggers:
            raise ValidationError({
                'trigger_event': f'Invalid trigger event. Must be one of: {", ".join(valid_triggers)}'
            })

        # Get required variables for this trigger
        required_vars = SystemEmailTrigger.get_trigger_variables().get(self.trigger_event, [])
        # Check if all required variables are available
        available_vars = set(self.all_available_variables)
        missing_vars = set(required_vars) - available_vars
        if missing_vars:
            raise ValidationError({
                'available_variables': f'Missing required variables for trigger {self.trigger_event}: {", ".join(missing_vars)}'
            })
        
        # Validate CC and BCC email addresses
        for email in self.cc + self.bcc:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError({
                    'cc' if email in self.cc else 'bcc': f'Invalid email address: {email}'
                })

    def save(self, *args, **kwargs):
        self.clean()
        self.setting_type = SettingType.EMAIL.value
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'system_email'
        app_label = 'system_settings'
        verbose_name = 'System Email'
        verbose_name_plural = 'System Emails'

class EmailContent(SystemSetting):
    """
    Multi-language content for system emails.
    Content sections that will be inserted into template placeholders.
    Can use variables like {{ user_name }} which will be replaced at send time.
    Variables are not restricted to predefined ones - any variable in the context_data will be replaced.
    """
    system_email = models.ForeignKey(SystemEmail, on_delete=models.CASCADE, related_name='contents')
    language_code = models.CharField(max_length=10)  # e.g., 'en', 'es', 'fr'
    subject = models.CharField(max_length=255)  # Email subject line
    content_sections = models.JSONField(
        help_text="Dict mapping template placeholders to content structures. Each structure has 'default' content and optional 'condition_sets'. Content can include {{ variables }}.",
        default=dict  # Default remains dict, but structure inside will change
    )
    content_type = models.CharField(
        max_length=20,
        choices=[(t.value, t.value) for t in ContentType],
        default=ContentType.HTML
    )

    def get_used_variables(self) -> set:
        """Extract all variables used in subject and content sections"""
        pattern = r'{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}'
        variables = set()
        
        # Check subject
        variables.update(re.findall(pattern, self.subject))
        
        # Check all content sections
        for content in self.content_sections.values():
            variables.update(re.findall(pattern, content))
            
        return variables

    def clean(self):
        """Validate the model"""
        super().clean()

        template_placeholders = set(self.system_email.template.content_placeholders)
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
                    # Basic validation for individual conditions can be added here if needed
                    # e.g., check if each condition is a dict with a 'type' key

        # REMOVED: Variable availability check - too complex with conditional logic
        # used_variables = self.get_used_variables() # This method might need adjustment too if we want to check variables within conditions
        # available_variables = set(self.system_email.all_available_variables)
        # missing_variables = used_variables - available_variables
        # if missing_variables:
        #     raise ValidationError({
        #         'content_sections': f'Content uses variables that are not available: {", ".join(missing_variables)}'
        #     })

    def save(self, *args, **kwargs):
        # Clean is called automatically by Django's save process if not disabled
        self.setting_type = SettingType.EMAIL.value
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'system_email_content'
        app_label = 'system_settings'
        verbose_name = 'Email Content'
        verbose_name_plural = 'Email Contents'
        unique_together = ('system_email', 'language_code', 'content_type')
