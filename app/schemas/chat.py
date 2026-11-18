from typing import Literal
from pydantic import BaseModel, Field, field_validator

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def no_system_injection(cls, v: str) -> str:
        stripped = v.strip().lower()
        if stripped.startswith("system:") or stripped.startswith("[system]"):
            raise ValueError("Invalid message content")
        return v

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)

    @field_validator("history")
    @classmethod
    def limit_history(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        return v[-6:]

class ChatResponse(BaseModel):
    response: str