import json
from dataclasses import asdict, is_dataclass
from typing import Sequence

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import UserContent

from django_ai_agent.exceptions import GuardrailValidationError
from django_ai_agent.models import Agent as AgentModel
from django_ai_agent.enums import GuardrailValidationType
from django_ai_agent.entities.guardrail import GuardrailResponse

from .abstract import AbstractGuardrailService


class BaseGuardrailService(AbstractGuardrailService):
    """Base implementation of a guardrail service.

    This service provides both synchronous and asynchronous methods for validating
    inputs and outputs against configured guardrails.
    """

    def __init__(self, agent_model: AgentModel):
        super().__init__(agent_model)
        self.input_validation_prompt = self.config.get("input_validation_prompt", "")
        self.output_validation_prompt = self.config.get("output_validation_prompt", "")
        self.default_model = self.config.get("model", "openai:gpt-4.1-mini")
        self.validation_agent = Agent(model=self.default_model, result_type=GuardrailResponse)

    async def _validate(
        self, query: str | Sequence[UserContent] | None, validation_type: GuardrailValidationType
    ) -> GuardrailResponse:
        """Validate a query asynchronously.

        Args:
            query: The query to validate, which can be a string, sequence of UserContent, or None
            validation_type: The type of validation to perform

        Returns:
            GuardrailResponse containing validation result
        """
        self.validation_agent.system_prompt = self._get_system_prompt(validation_type)

        if query is None:
            query = ""
        elif isinstance(query, BaseModel):
            query = query.model_dump_json()
        elif is_dataclass(query):
            query = json.dumps(asdict(query))
        elif isinstance(query, Sequence):
            pass

        result = await self.validation_agent.run(query)

        if not result.data.is_valid:
            raise GuardrailValidationError(result.data.error_message or "Validation failed")

        return result.data

    def _get_system_prompt(self, validation_type: GuardrailValidationType) -> str:
        return (
            self.input_validation_prompt
            if validation_type == GuardrailValidationType.INPUT
            else self.output_validation_prompt
        )
