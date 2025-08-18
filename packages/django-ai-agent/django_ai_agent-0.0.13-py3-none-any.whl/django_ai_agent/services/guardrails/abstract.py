from abc import ABC, abstractmethod
from typing import Optional, Sequence

from pydantic_ai.messages import UserContent

from django_ai_agent.models import Guardrail, Agent as AgentModel
from django_ai_agent.entities.guardrail import (
    GuardrailResponse,
    GuardrailValidationType,
)


class AbstractGuardrailService(ABC):
    """Base class for implementing guardrail services."""

    def __init__(self, agent_model: AgentModel):
        self.guardrail: Guardrail = agent_model.guardrail
        self.config = self.guardrail.configuration if self.guardrail else {}

    async def validate(
        self, query: str | Sequence[UserContent] | None, validation_type: GuardrailValidationType
    ) -> Optional[GuardrailResponse]:
        if self.guardrail and self._is_enabled(validation_type):
            return await self._validate(query, validation_type)
        return None

    def _is_enabled(self, validation_type: GuardrailValidationType) -> bool:
        return (self.guardrail.is_input_enabled and validation_type == GuardrailValidationType.INPUT) or (
            self.guardrail.is_output_enabled and validation_type == GuardrailValidationType.OUTPUT
        )

    @abstractmethod
    async def _validate(
        self, query: str | Sequence[UserContent] | None, validation_type: GuardrailValidationType
    ) -> GuardrailResponse:
        pass
