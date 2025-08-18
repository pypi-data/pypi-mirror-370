from django.db import models
# Attempting to import from one level up, assuming common/base.py exists there
from ..common.base import BaseModel 

class DashboardTip(BaseModel):
    """Model to store actionable tips for the dashboard."""
    text = models.TextField(help_text="The content of the tip.")
    icon = models.CharField(max_length=50, blank=True, help_text="Optional FontAwesome icon class (e.g., 'faLightbulb').")
    link = models.URLField(blank=True, null=True, help_text="Optional URL for the user to click for more info.")
    is_active = models.BooleanField(default=True, help_text="Whether the tip should be displayed.")

    class Meta:
        app_label = 'ui_elements'
        db_table = 'ui_dashboard_tips'
        verbose_name = 'Dashboard Tip'
        verbose_name_plural = 'Dashboard Tips'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text

class MotivationalQuote(BaseModel):
    """Model to store motivational quotes for the dashboard."""
    text = models.TextField(help_text="The content of the quote.")
    author = models.CharField(max_length=100, blank=True, help_text="The author of the quote.")
    link = models.URLField(blank=True, null=True, help_text="Optional URL related to the quote or author.")
    is_active = models.BooleanField(default=True, help_text="Whether the quote should be displayed.")

    class Meta:
        app_label = 'ui_elements'
        db_table = 'ui_motivational_quotes'
        verbose_name = 'Motivational Quote'
        verbose_name_plural = 'Motivational Quotes'
        ordering = ['-created_at']

    def __str__(self):
        base = self.text[:50] + '...' if len(self.text) > 50 else self.text
        if self.author:
            return f'"{base}" - {self.author}'
        return f'"{base}"' 