from django.db import models
from simple_history.models import HistoricalRecords

from .abstract import TimestampMixin
from ..enums import TranscriptionProvider


class Agent(TimestampMixin):
    class Meta:
        verbose_name = 'agent'
        verbose_name_plural = 'agents'

    name = models.CharField(max_length=255, primary_key=True, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    system_prompt = models.ForeignKey(
        'django_ai_agent.Prompt',
        on_delete=models.CASCADE,
        related_name='agents',
        null=True,
        blank=True,
    )
    model_settings = models.ForeignKey('django_ai_agent.ModelSettings', on_delete=models.CASCADE, related_name='agents')
    guardrail = models.ForeignKey(
        'django_ai_agent.Guardrail',
        on_delete=models.SET_NULL,
        related_name='agents',
        null=True,
        blank=True,
    )
    tools = models.ManyToManyField('django_ai_agent.Tool', related_name='agents', blank=True)
    documents = models.ManyToManyField('django_ai_agent.Document', related_name='agents', blank=True)
    transcription_model = models.ForeignKey(
        'django_ai_agent.TranscriptionModel', on_delete=models.SET_NULL, null=True, blank=True
    )

    history = HistoricalRecords(excluded_fields=['updated_at'], cascade_delete_history=False)

    def __str__(self):
        return self.name

    @property
    def model(self):
        return self.model_settings.model

    def get_system_prompt(self, prompt_variables=None):
        variables = prompt_variables or {}
        return self.system_prompt.format(**variables) if self.system_prompt else None

    def get_model_settings(self):
        return self.model_settings.as_dict()

    @property
    def has_documents(self):
        return self.documents.exists()

    @property
    def transcription_service(self):
        if self.transcription_model:
            return self.transcription_model.service
        return None
