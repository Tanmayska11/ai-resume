from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    label: str
    url: Optional[str] = None
    source: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
