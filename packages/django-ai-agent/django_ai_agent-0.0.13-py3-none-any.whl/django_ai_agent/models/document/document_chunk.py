from django.db import models


class DocumentChunk(models.Model):
    document = models.ForeignKey('django_ai_agent.Document', on_delete=models.PROTECT, related_name='chunks')
    index = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    @property
    def score(self):
        if hasattr(self, '_score'):
            return self._score
        raise ValueError('DocumentChunk: _score field is not annotated')
