from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

import logfire

if TYPE_CHECKING:
    from django_ai_agent.models import TranscriptionModel


class AbstractTranscriptionService(ABC):
    def __init__(self, transcription_model: 'TranscriptionModel'):
        self.transcription_model = transcription_model

    def get_transcription(self, audio):
        with logfire.span(
            'audio transcription {service} {model}',
            service=self.transcription_model.provider,
            model=self.transcription_model.model_name,
        ):
            return self._get_transcription(audio, self.transcription_model.model_name)

    @abstractmethod
    def _get_transcription(self, audio, model_name):
        pass
