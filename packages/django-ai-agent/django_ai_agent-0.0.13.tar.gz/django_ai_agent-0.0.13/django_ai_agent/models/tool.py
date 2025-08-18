from django.db import models
from simple_history.models import HistoricalRecords

from .abstract import TimestampMixin


class Tool(TimestampMixin):
    name = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parameters_schema = models.JSONField(
        default=dict, help_text='JSON Schema defining the parameters this tool accepts'
    )
    max_retries = models.IntegerField(default=3)
    strict = models.BooleanField(default=False, help_text='Whether to require all parameters to be present')

    # Circuit breaker fields
    max_calls = models.IntegerField(
        default=5,
        null=True,
        blank=True,
        help_text='Maximum number of times this tool can be called in a single agent run'
    )
    max_identical_calls = models.IntegerField(
        default=3,
        null=True,
        blank=True,
        help_text='Maximum number of times this tool can be called with identical parameters in a single agent run',
    )

    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=False)
