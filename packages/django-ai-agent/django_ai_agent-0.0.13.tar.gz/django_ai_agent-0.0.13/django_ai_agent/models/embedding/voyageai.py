from pgvector.django import VectorField, HnswIndex
from .abstract import AbstractEmbedding


class VoyageAIEmbedding(AbstractEmbedding):
    class Meta:
        indexes = [
            HnswIndex(
                name='voaygeai_l1024_vectors_index',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            )
        ]

    embedding = VectorField(dimensions=1024, null=True, blank=True)
