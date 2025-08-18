import voyageai
from django.conf import settings

from .abstract import AbstractEmbeddingService
from django_ai_agent.models import VoyageAIEmbedding


class VoyageAIEmbeddingService(AbstractEmbeddingService):
    _embedding_model = VoyageAIEmbedding
    _model: str = "voyage-3"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.VOYAGEAI_API_KEY
        self.client = voyageai.Client(api_key=self.api_key)

    def get_embedding(self, query: str):
        embedding_response = self.client.embed([query], model=self._model)
        return embedding_response.embeddings[0]
