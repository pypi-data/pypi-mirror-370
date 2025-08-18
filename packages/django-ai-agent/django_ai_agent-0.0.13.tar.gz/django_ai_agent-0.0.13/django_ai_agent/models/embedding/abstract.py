from django.db import models

from ..abstract import TimestampMixin


class AbstractEmbedding(TimestampMixin):
    class Meta:
        abstract = True

    chunk = models.ForeignKey('django_ai_agent.DocumentChunk', on_delete=models.PROTECT)
    model = models.CharField(max_length=255, null=True, blank=True)
