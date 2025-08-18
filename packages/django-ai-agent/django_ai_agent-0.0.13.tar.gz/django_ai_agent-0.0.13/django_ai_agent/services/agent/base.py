from .abstract import AbstractAgentService
from django_ai_agent.services.document import BaseDocumentService
from django_ai_agent.services.memory import BaseMemoryService
from django_ai_agent.services.guardrails import BaseGuardrailService


class BaseAgentService(AbstractAgentService):
    document_service_class = BaseDocumentService
    memory_service_class = BaseMemoryService
    guardrail_service_class = BaseGuardrailService
