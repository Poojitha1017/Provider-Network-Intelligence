from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The user query or question")
    history: Optional[List[ChatMessage]] = Field(default=None, description="Previous message history")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Current page context (e.g. selected area)")


class ChatQueryResponse(BaseModel):
    answer: str
    suggested_actions: Optional[List[str]] = None
    data_summary: Optional[Dict[str, Any]] = None
    timestamp: str
