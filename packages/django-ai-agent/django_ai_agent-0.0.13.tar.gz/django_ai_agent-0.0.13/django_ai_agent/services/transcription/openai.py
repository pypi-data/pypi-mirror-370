from openai import OpenAI

from .abstract import AbstractTranscriptionService


class OpenAITranscriptionService(AbstractTranscriptionService):
    def __init__(self, transcription_model):
        super().__init__(transcription_model)
        self.wrapper = OpenAI(api_key=self.transcription_model.api_key)

    def _get_transcription(self, audio, model_name):
        transcription = self.wrapper.audio.transcriptions.create(model=model_name, file=audio)
        return transcription.text
