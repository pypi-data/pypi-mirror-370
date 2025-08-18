from .abstract import AbstractDocumentService
from .mixins import ContextualizeChunkMixin

from .backends import OpenAIVectorStoreDocumentBackend


class BaseDocumentService(ContextualizeChunkMixin, AbstractDocumentService):
    @property
    def _document_backends(self):
        return (OpenAIVectorStoreDocumentBackend,)
