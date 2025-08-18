from openai import OpenAI

from django_ai_agent.models import OpenAIEmbedding
from .abstract import AbstractEmbeddingService


class OpenAIEmbeddingService(AbstractEmbeddingService):
    _embedding_model = OpenAIEmbedding
    _model: str = 'text-embedding-ada-002'

    def __init__(self):
        self.client = OpenAI()

    def get_embedding(self, query: str):
        embedding_response = self.client.embeddings.create(input=query, model=self._model)
        return embedding_response.data[0].embedding
