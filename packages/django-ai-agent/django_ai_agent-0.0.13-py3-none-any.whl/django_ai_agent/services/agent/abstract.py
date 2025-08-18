import asyncio
from abc import ABC
from typing import Union, Any, Optional, Type, Sequence

from asgiref.sync import async_to_sync
from pydantic import BaseModel
from pydantic_ai.agent import AgentRunResult, Agent
from pydantic_ai.messages import UserContent

from django_ai_agent.enums import GuardrailValidationType
from django_ai_agent.exceptions import GuardrailValidationError
from django_ai_agent.models import Agent as AgentModel
from django_ai_agent.services.tools import ToolService
from django_ai_agent.services.document import AbstractDocumentService
from django_ai_agent.services.guardrails import AbstractGuardrailService
from django_ai_agent.services.memory import AbstractMemoryService

from django_ai_agent.utils import get_event_loop


class AbstractAgentService(ABC):
    document_service_class: Type[AbstractDocumentService]
    memory_service_class: Type[AbstractMemoryService]
    guardrail_service_class: Type[AbstractGuardrailService]
    tool_service_class: Type[ToolService] = ToolService

    deps_type: Optional[Type[BaseModel]] = None
    result_type: Type[BaseModel] | str = str

    def __init__(
        self,
        agent_model: AgentModel,
        user,
        prompt_variables: dict = None,
        result_type: Type[BaseModel] = str,
        deps_type: Optional[Type[BaseModel]] = None,
    ):
        self.agent_model = agent_model
        self._result_type = result_type or self.result_type
        self._deps_type = deps_type or self.deps_type

        self.document_service = self.document_service_class(agent_model)
        self.memory_service = self.memory_service_class(agent_model, user)
        self.guardrail_service = self.guardrail_service_class(agent_model)
        self.tool_service = self.tool_service_class(agent_model)

        tools = self.tool_service.get_tools()

        self.agent = Agent(
            agent_model.model,
            instructions=agent_model.get_system_prompt(prompt_variables),
            tools=tools,
            deps_type=self._deps_type,
            result_type=self._result_type,
            instrument=True,
        )

    def add_context(self, query: str | Sequence[UserContent] | None) -> str | Sequence[UserContent] | None:
        if not self.agent_model.has_documents:
            return query

        search_text = self._extract_search_text(query)

        if not search_text:
            return query

        chunks = self.document_service.search(search_text)
        context = "\n".join(f"<chunk>{chunk.content}</chunk>" for chunk in chunks)

        return self._build_context_query(query, context)

    def _extract_search_text(self, query: str | Sequence[UserContent] | None) -> str:
        if query is None:
            return ''

        if isinstance(query, str):
            return query

        if isinstance(query, Sequence):
            text_parts = []
            for item in query:
                if isinstance(item, str):
                    text_parts.append(item)
            return ' '.join(text_parts)

        return ''

    def _build_context_query(
        self, original_query: str | Sequence[UserContent] | None, context: str
    ) -> str | Sequence[UserContent] | None:
        if isinstance(original_query, str):
            return f"""
            <context>
            {context}
            </context>

            {original_query}
            """

        if isinstance(original_query, Sequence):
            context_text = f"<context>\n{context}\n</context>"
            return [context_text] + list(original_query)

        return original_query

    def get_deps(self, **kwargs):
        return self._deps_type(**kwargs) if self._deps_type else None

    def _prepare(self, query: str | Sequence[UserContent] | None, **kwargs):
        contextualized_query = self.add_context(query)
        message_history = self.memory_service.get_message_history()
        deps = self.get_deps(**kwargs)
        return contextualized_query, message_history, deps

    def _process_result(self, result: AgentRunResult):
        return result.output

    def process_result(self, result: AgentRunResult):
        async_to_sync(self.guardrail_service.validate)(result.output, GuardrailValidationType.OUTPUT)
        self.memory_service.save_new_messages(result.new_messages())
        return self._process_result(result)

    def run(self, query: str | Sequence[UserContent] | None = None, **kwargs) -> Union[BaseModel, str]:
        try:
            contextualized_query, message_history, deps = self._prepare(query, **kwargs)
            result, input_guardrail_response = get_event_loop().run_until_complete(
                asyncio.gather(
                    self.agent.run(contextualized_query, deps=deps, message_history=message_history),
                    self.guardrail_service.validate(query, GuardrailValidationType.INPUT),
                )
            )
            return self.process_result(result)
        except GuardrailValidationError as e:
            return self._handle_exception(e)

    def _handle_exception(self, exception) -> Any:
        if isinstance(exception, GuardrailValidationError):
            return exception.message
        raise exception
