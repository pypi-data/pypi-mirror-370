from django.db.models import QuerySet, Subquery, OuterRef, F

from django_ai_agent.models import DocumentChunk
from django_ai_agent.services.embedding import AbstractEmbeddingService

from ..abstract import AbstractDocumentBackend


class AbstractVectorStoreDocumentBackend(AbstractDocumentBackend):
    _embedding_service: AbstractEmbeddingService

    def search(self, query: str, k: int) -> QuerySet[DocumentChunk]:
        subquery = self._embedding_service.search(query)
        return DocumentChunk.objects.annotate(
            distance=Subquery(
                subquery.filter(
                    chunk_id=OuterRef("id"),
                ).values_list(
                    "distance", flat=True
                )[:1]
            ),
            _score=1 - F("distance"),
        )[:k]

    def load(self, chunk: DocumentChunk):
        return self._embedding_service.create(chunk)
