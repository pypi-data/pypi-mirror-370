from abc import ABC, abstractmethod

from django.db.models import QuerySet
from pgvector.django import CosineDistance

from django_ai_agent.models import AbstractEmbedding, DocumentChunk


class AbstractEmbeddingService(ABC):
    """Base class for embedding services."""

    _embedding_model = AbstractEmbedding
    """The model used to store embeddings"""
    _model: str
    """Provider model name for generating embeddings"""

    def create(self, chunk: DocumentChunk) -> AbstractEmbedding:
        embedding = self.get_embedding(chunk.content)
        return self._embedding_model.objects.create(chunk=chunk, model=self._model, embedding=embedding)

    def search(self, query: str, k: int = None) -> QuerySet[AbstractEmbedding]:
        embedded_query = self.get_embedding(query)
        embeddings = self._embedding_model.objects.annotate(
            distance=CosineDistance("embedding", embedded_query)
        ).order_by("distance")
        if k:
            embeddings = embeddings[:k]
        return embeddings

    @abstractmethod
    def get_embedding(self, query: str):
        pass
