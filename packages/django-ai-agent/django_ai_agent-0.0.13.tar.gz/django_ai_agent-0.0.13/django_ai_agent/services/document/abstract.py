from typing import List, Type

from django.db.models import QuerySet

from django_ai_agent.models import DocumentChunk, Document, Agent as AgentModel

from .backends.abstract import AbstractDocumentBackend
from django_ai_agent.entities import DocumentEntity


class AbstractDocumentService:
    top_k: int = 20
    _document_backends: List[Type[AbstractDocumentBackend]]

    def __init__(self, agent_model: AgentModel):
        self.agent_model = agent_model

    def search(self, query) -> QuerySet[DocumentChunk]:
        results = []
        for backend in self._document_backends:
            results += backend().search(query, self.top_k)
        results = self.rank_results(results)
        return results

    def load(self, documents: List[DocumentEntity]):
        for doc in documents:
            document = self.create_document(doc)
            for index, chunk in enumerate(self.get_chunks(document.content)):
                self.create_chunk(document, index, chunk)

    @classmethod
    def rank_results(cls, results: QuerySet[DocumentChunk]) -> QuerySet[DocumentChunk]:
        return results.order_by("-score").distinct()[: cls.top_k]

    def create_document(self, document: DocumentEntity):
        document = Document.objects.create(**document.model_dump())
        self.agent_model.documents.add(document)
        return document

    @classmethod
    def create_chunk(cls, document, index: int, chunk: str):
        prepared_content = cls._prepare_content(document, index, chunk)
        document_chunk = DocumentChunk.objects.create(document=document, index=index, content=prepared_content)
        for backend in cls._document_backends:
            backend().load(document_chunk)

    @classmethod
    async def _prepare_content(cls, document: dict, index: int, chunk: str) -> str:
        return chunk

    def get_chunks(self, text: str, similarity_threshold: float = 0.85) -> List[str]:
        """Split text into chunks based on similarity to pre-trained embeddings."""
        return text.split(".")
        # # Tokenize text into sentences
        # sentences = sent_tokenize(text)
        #
        # # Load pre-trained embedding model
        # model = SentenceTransformer("all-MiniLM-L6-v2")
        #
        # # Encode sentences into embeddings
        # embeddings = model.encode(sentences, convert_to_tensor=True)
        #
        # chunks = []
        # current_chunk = [sentences[0]]
        #
        # # Compare sentence similarity to decide chunk boundaries
        # for i in range(1, len(sentences)):
        #     similarity = util.pytorch_cos_sim(embeddings[i - 1], embeddings[i]).item()
        #     if similarity > similarity_threshold:
        #         current_chunk.append(sentences[i])
        #     else:
        #         chunks.append(" ".join(current_chunk))
        #         current_chunk = [sentences[i]]
        #
        # # Add the last chunk
        # if current_chunk:
        #     chunks.append(" ".join(current_chunk))
        #
        # return chunks
