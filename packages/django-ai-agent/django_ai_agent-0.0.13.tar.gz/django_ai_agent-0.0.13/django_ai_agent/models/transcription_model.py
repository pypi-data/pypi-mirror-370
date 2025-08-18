import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_ai_agent.enums import TranscriptionProvider


class TranscriptionModel(models.Model):
    class Model(models.TextChoices):
        GPT_4O = 'gpt-4o-transcribe', 'gpt-4o-transcribe'
        GRT_4O_MINI = 'gpt-4o-mini-transcribe', 'gpt-4o-mini-transcribe'
        WHISPER_1 = 'whisper-1', 'whisper-1'
        WHISPER_V3_TURBO = 'whisper-large-v3-turbo', 'whisper-large-v3-turbo'

    provider = models.CharField(
        choices=TranscriptionProvider.choices, max_length=100, default=TranscriptionProvider.GROQ
    )
    model_name = models.CharField(choices=Model.choices, max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.provider} - {self.model_name}'

    def clean(self):
        if (self.provider == TranscriptionProvider.OPENAI and self.model_name == self.Model.WHISPER_V3_TURBO) or (
            self.provider == TranscriptionProvider.GROQ
            and self.model_name in [self.Model.GPT_4O, self.Model.GRT_4O_MINI]
        ):
            raise ValidationError(f'{self.model_name} is not available on {self.provider}')
        super().clean()

    @property
    def api_key(self):
        if api_key := getattr(
            settings, f'{self.provider.upper()}_API_KEY', os.environ.get(f'{self.provider.upper()}_API_KEY')
        ):
            return api_key
        raise ValidationError(f'API key for {self.provider} is not set')

    @property
    def service(self):
        from django_ai_agent.services.transcription import OpenAITranscriptionService, GroqTranscriptionService

        return {
            TranscriptionProvider.OPENAI.value: OpenAITranscriptionService,
            TranscriptionProvider.GROQ.value: GroqTranscriptionService,
        }.get(self.provider, GroqTranscriptionService)(self)
