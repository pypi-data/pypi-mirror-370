from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

from .abstract import TimestampMixin
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python

from .message import Message


class Conversation(TimestampMixin):
    agent = models.ForeignKey('django_ai_agent.Agent', on_delete=models.CASCADE, related_name='conversations')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_conversations',
    )
    title = models.CharField(max_length=255, default='New conversation', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.title or 'Conversation'} between {self.user} and {self.agent}'

    @classmethod
    def get_active_conversation(cls, user, agent):
        timeout_seconds = getattr(settings, 'AI_AGENT_CONVERSATION_TIMEOUT', 60 * 60)  # Default: 1 hour
        timeout_threshold = timezone.now() - timedelta(seconds=timeout_seconds)
        conversation = cls.objects.filter(user=user, agent=agent, is_active=True).first()
        if not conversation:
            return cls.objects.create(user=user, agent=agent, is_active=True)

        last_message = conversation.messages.order_by('-created_at').first()
        if last_message and last_message.created_at < timeout_threshold:
            conversation.is_active = False
            conversation.save(update_fields=['is_active'])
            return cls.objects.create(user=user, agent=agent, is_active=True)

        return conversation

    def get_messages(self):
        messages = self.messages.order_by('created_at').values_list('message_history', flat=True)
        messages = [item for sublist in messages for item in sublist]
        return ModelMessagesTypeAdapter.validate_python(messages)

    def save_new_messages(self, messages):
        return Message.objects.create(conversation=self, message_history=to_jsonable_python(messages))

    @classmethod
    def new(cls, user, agent):
        active_conversation = cls.get_active_conversation(user, agent)
        active_conversation.is_active = False
        active_conversation.save(update_fields=['is_active'])
        return cls.objects.create(user=user, agent=agent, is_active=True)
