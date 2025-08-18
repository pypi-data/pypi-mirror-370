from groq import Groq

from .abstract import AbstractTranscriptionService


class GroqTranscriptionService(AbstractTranscriptionService):
    def __init__(self, transcription_model):
        super().__init__(transcription_model)
        self.wrapper = Groq(api_key=self.transcription_model.api_key)

    def _get_transcription(self, audio_file, model_name):
        transcription = self.wrapper.audio.transcriptions.create(
            file=audio_file, model=model_name, response_format='verbose_json'
        )
        return transcription.text
