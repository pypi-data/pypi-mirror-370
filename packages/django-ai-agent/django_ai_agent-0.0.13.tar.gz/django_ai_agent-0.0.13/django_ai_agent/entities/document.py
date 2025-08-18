from typing import Optional

from pydantic import BaseModel


class DocumentEntity(BaseModel):
    name: str
    source: Optional[str]
    author: Optional[str]
    url: Optional[str]
    content: str
    metadata: Optional[dict]
