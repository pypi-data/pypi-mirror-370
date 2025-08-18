from django.db import models

from .abstract import TimestampMixin


class Message(TimestampMixin):
    conversation = models.ForeignKey('django_ai_agent.Conversation', on_delete=models.CASCADE, related_name='messages')
    message_history = models.JSONField()
