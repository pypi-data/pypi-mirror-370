from .abstract import AbstractEmbedding
from pgvector.django import VectorField, HnswIndex


class OpenAIEmbedding(AbstractEmbedding):
    class Meta:
        indexes = [
            HnswIndex(
                name='openai_l1536_vectors_index',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            )
        ]

    embedding = VectorField(dimensions=1536, null=True, blank=True)
