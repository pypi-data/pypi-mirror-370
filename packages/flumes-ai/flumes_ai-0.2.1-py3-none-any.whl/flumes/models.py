from __future__ import annotations

from typing import List, Literal, Optional, Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single chat message."""

    role: Literal["user", "assistant", "system"]
    content: str


class AddMemoryRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1, max_length=50)
    entity_id: Optional[str] = None
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    infer: bool = True


class UpdateMemoryRequest(BaseModel):
    memory: str
    metadata: Optional[dict[str, Any]] = None
