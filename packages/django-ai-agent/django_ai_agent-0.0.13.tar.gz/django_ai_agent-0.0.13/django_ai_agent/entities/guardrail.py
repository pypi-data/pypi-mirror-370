from typing import Optional

from pydantic import BaseModel

from django_ai_agent.enums import GuardrailValidationType


class GuardrailRequest(BaseModel):
    query: str
    validation_type: GuardrailValidationType


class GuardrailResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str]
