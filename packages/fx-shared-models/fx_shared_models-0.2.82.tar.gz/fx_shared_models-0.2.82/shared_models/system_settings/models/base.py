from django.db import models
from shared_models.common.base import BaseModel
from ...constants import SettingType, SettingStatus

class SystemSetting(BaseModel):
    """
    Base model for all system settings. Each setting type can have multiple configurations
    but only one active configuration at a time.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    setting_type = models.CharField(max_length=50, choices=[(t.value, t.value) for t in SettingType])
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in SettingStatus],
        default=SettingStatus.INACTIVE
    )
    is_active = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'system_settings'
        app_label = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['-created_at']
        permissions = [
            ('add_system_setting', 'Can add system setting'),
            ('change_system_setting', 'Can change system setting'),
            ('delete_system_setting', 'Can delete system setting'),
            ('view_system_setting', 'Can view system setting'),
        ]

    def __str__(self):
        return f"{self.setting_type} - {self.name}" 