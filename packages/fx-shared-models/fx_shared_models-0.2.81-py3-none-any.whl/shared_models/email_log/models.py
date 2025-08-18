from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from ..common.base import BaseModel

class EmailLogStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SCHEDULED = 'SCHEDULED', _('Scheduled')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')
    # RETRYING = 'RETRYING', _('Retrying') # Optional, depends on retry implementation

class EmailLog(BaseModel):
    """
    Model to log emails sent through the system.
    """
    recipient_to = models.TextField(
        _('Recipient To'),
        help_text=_('Comma-separated list of main recipients.')
    )
    recipient_cc = models.TextField(
        _('Recipient CC'),
        blank=True,
        help_text=_('Comma-separated list of CC recipients.')
    )
    recipient_bcc = models.TextField(
        _('Recipient BCC'),
        blank=True,
        help_text=_('Comma-separated list of BCC recipients.')
    )
    sender = models.EmailField(
        _('Sender Email')
    )
    subject = models.CharField(
        _('Subject'),
        max_length=255
    )
    body_text = models.TextField(
        _('Body (Text)'),
        blank=True,
        help_text=_('Plain text version of the email body.')
    )
    body_html = models.TextField(
        _('Body (HTML)'),
        blank=True,
        help_text=_('HTML version of the email body.')
    )
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=EmailLogStatus.choices,
        default=EmailLogStatus.PENDING,
        db_index=True
    )
    provider_status = models.CharField(
        _('Provider Status'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Status code or message from the email provider (e.g., SendGrid, SMTP).')
    )
    provider_message = models.TextField(
        _('Provider Message'),
        blank=True,
        null=True,
        help_text=_('Detailed message or error returned by the email provider.')
    )
    retry_count = models.PositiveIntegerField(
        _('Retry Count'),
        default=0
    )
    last_attempt_time = models.DateTimeField(
        _('Last Attempt Time'),
        null=True,
        blank=True
    )
    scheduled_time = models.DateTimeField(
        _('Scheduled Time'),
        null=True,
        blank=True,
        help_text=_('When this email is scheduled to be sent. If set, status should be SCHEDULED.')
    )

    class Meta:
        verbose_name = _('Email Log')
        verbose_name_plural = _('Email Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {str(self.recipient_to)[:50]}... - {str(self.subject)[:50]}... ({self.status})"

    def mark_sent(self, provider_status=None):
        self.status = EmailLogStatus.SENT
        self.provider_status = provider_status
        self.last_attempt_time = timezone.now()
        self.save(update_fields=['status', 'provider_status', 'last_attempt_time', 'updated_at'])

    def mark_failed(self, provider_status=None, provider_message=None):
        self.status = EmailLogStatus.FAILED
        self.provider_status = provider_status
        self.provider_message = provider_message
        self.last_attempt_time = timezone.now()
        self.save(update_fields=['status', 'provider_status', 'provider_message', 'last_attempt_time', 'updated_at'])

    def increment_retry(self):
        self.retry_count += 1
        # self.status = EmailLogStatus.PENDING # Or RETRYING if using that status
        self.last_attempt_time = timezone.now()
        self.save(update_fields=['retry_count', 'last_attempt_time', 'updated_at'])
        
    def schedule(self, scheduled_time):
        """
        Schedule this email to be sent at a future time.
        
        Args:
            scheduled_time: A datetime object representing when the email should be sent
        """
        self.status = EmailLogStatus.SCHEDULED
        self.scheduled_time = scheduled_time
        self.save(update_fields=['status', 'scheduled_time', 'updated_at'])
        
    @classmethod
    def get_emails_to_send(cls):
        """
        Returns emails that are scheduled and whose scheduled time has passed,
        or emails that are in PENDING status.
        
        This method is intended to be called by a task scheduler like Celery.
        """
        now = timezone.now()
        return cls.objects.filter(
            models.Q(status=EmailLogStatus.PENDING) |
            models.Q(
                status=EmailLogStatus.SCHEDULED,
                scheduled_time__lte=now
            )
        ).order_by('scheduled_time', 'created_at')
