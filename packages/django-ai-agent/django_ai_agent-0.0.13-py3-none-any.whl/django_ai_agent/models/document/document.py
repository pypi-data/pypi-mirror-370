from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
