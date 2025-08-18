from abc import ABC, abstractmethod

from django.contrib.auth import get_user_model
from pydantic_ai.messages import ModelMessage

from django_ai_agent.models import Agent as AgentModel


User = get_user_model()


class AbstractMemoryService(ABC):

    def __init__(self, agent_model: AgentModel, user: User):
        self.agent_model = agent_model
        self.user = user

    @abstractmethod
    def get_message_history(self):
        pass

    @abstractmethod
    def save_new_messages(self, messages: list[ModelMessage]):
        pass
