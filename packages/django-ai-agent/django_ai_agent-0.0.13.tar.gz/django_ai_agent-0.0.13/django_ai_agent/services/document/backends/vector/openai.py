from django_ai_agent.services.embedding import OpenAIEmbeddingService

from .abstract import AbstractVectorStoreDocumentBackend


class OpenAIVectorStoreDocumentBackend(AbstractVectorStoreDocumentBackend):
    _embedding_service: OpenAIEmbeddingService
