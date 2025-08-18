from abc import ABC, abstractmethod

from django.db.models import QuerySet

from django_ai_agent.models import DocumentChunk


class AbstractDocumentBackend(ABC):
    @abstractmethod
    def search(self, query: str, k: int) -> QuerySet[DocumentChunk]:
        pass

    @abstractmethod
    def load(self, chunk: DocumentChunk):
        pass
