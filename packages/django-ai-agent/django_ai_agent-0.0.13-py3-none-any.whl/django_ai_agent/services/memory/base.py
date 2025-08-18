from pydantic_ai.messages import ModelMessage

from .abstract import AbstractMemoryService
from ...models import Conversation


class BaseMemoryService(AbstractMemoryService):
    _conversation_model = Conversation

    def __init__(self, agent_model, user):
        super().__init__(agent_model, user)
        self.active_conversation = self._conversation_model.get_active_conversation(user, agent_model)

    def get_message_history(self) -> list[ModelMessage]:
        return self.active_conversation.get_messages()

    def save_new_messages(self, messages: list[ModelMessage]):
        self.active_conversation.save_new_messages(messages)
