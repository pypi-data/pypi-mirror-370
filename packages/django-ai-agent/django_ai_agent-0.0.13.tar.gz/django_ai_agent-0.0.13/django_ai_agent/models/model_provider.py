import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import OpenAIModel

from .abstract import TimestampMixin


class ModelProvider(TimestampMixin):
    class Provider(models.TextChoices):
        OPENAI = 'OPENAI'
        ANTHROPIC = 'ANTHROPIC'
        GEMINI = 'GEMINI'
        GROQ = 'GROQ'
        GROK = 'GROK'
        MISTRAL = 'MISTRAL'

    provider = models.CharField(choices=Provider.choices, max_length=100, default=Provider.OPENAI)
    base_url = models.CharField(max_length=255, null=True, blank=True)
    api_key_variable = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.provider

    def _get_api_key(self, variable):
        return getattr(settings, variable, os.environ.get(variable))

    @property
    def api_key(self):
        if self.api_key_variable:
            return self._get_api_key(self.api_key_variable)
        return self._get_api_key(f'{self.provider.upper()}_API_KEY')

    @property
    def model(self):
        return {
            self.Provider.OPENAI: OpenAIModel,
            self.Provider.ANTHROPIC: AnthropicModel,
            self.Provider.GEMINI: GeminiModel,
            self.Provider.GROQ: GroqModel,
            self.Provider.GROK: OpenAIModel,
            self.Provider.MISTRAL: MistralModel,
        }.get(self.provider)

    def clean(self):
        if not self.api_key:
            raise ValidationError(f'API key for {self.provider} is not set')
        super().clean()
