from django.db import models
from simple_history.models import HistoricalRecords

from .abstract import TimestampMixin


class Guardrail(TimestampMixin):
    name = models.CharField(max_length=255)
    is_input_enabled = models.BooleanField(default=True)
    is_output_enabled = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(
        null=True,
        blank=True,
        help_text='A description of what this guardrail checks for',
    )

    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=False)

    def __str__(self):
        return self.name
