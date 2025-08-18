from enum import Enum

from django.db.models import TextChoices


class ApprovalStatus(TextChoices):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class GuardrailValidationType(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"


class TranscriptionProvider(TextChoices):
    OPENAI = 'OPENAI'
    GROQ = 'GROQ'
