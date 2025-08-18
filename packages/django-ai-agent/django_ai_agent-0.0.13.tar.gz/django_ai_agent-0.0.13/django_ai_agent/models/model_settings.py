from django.db import models
from simple_history.models import HistoricalRecords

from django_ai_agent.models.abstract import TimestampMixin


class ModelSettings(TimestampMixin):
    class Meta:
        verbose_name = 'model settings'
        verbose_name_plural = 'model settings'

    provider = models.ForeignKey(
        'django_ai_agent.ModelProvider',
        on_delete=models.CASCADE,
        related_name='model_settings',
    )
    model_name = models.CharField(max_length=100, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    max_tokens = models.IntegerField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    frequency_penalty = models.FloatField(null=True, blank=True)
    presence_penalty = models.FloatField(null=True, blank=True)

    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=False)

    def __str__(self):
        return self.model_name or f'Model Settings {self.id}'

    @property
    def model(self):
        # If there is no base_url, then the model will be inferred when agent initialized
        if not self.base_url:
            return self.model_name
        return self.provider.model(self.model_name, base_url=self.base_url, api_key=self.api_key)

    @property
    def api_key(self):
        return self.provider.api_key

    @property
    def base_url(self):
        return self.provider.base_url

    def as_dict(self):
        return {
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
        }
