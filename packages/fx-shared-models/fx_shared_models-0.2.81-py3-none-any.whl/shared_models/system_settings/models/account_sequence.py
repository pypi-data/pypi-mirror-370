from django.db import models
from ...common.base import BaseModel

class AccountSequence(BaseModel):
    """
    Manages sequences for account creation
    """
    id = models.AutoField(primary_key=True, editable=False)
    current_sequence = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'system_settings'
        db_table = 'account_sequences'
        verbose_name = 'Account Sequence'
        verbose_name_plural = 'Account Sequences'

    def __str__(self):
        return f"Sequence {self.current_sequence}"

    def get_next_sequence(self):
        """Get next sequence number and increment if not zero"""
        from django.db import transaction
        
        with transaction.atomic():
            # Re-fetch the sequence with select_for_update to prevent race conditions
            sequence = AccountSequence.objects.select_for_update().get(id=self.id)
            current = sequence.current_sequence
            
            # Only increment if not zero
            if current != 0:
                sequence.current_sequence += 1
                sequence.save()
            
            return current 