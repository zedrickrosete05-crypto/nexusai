"""Pydantic schemas for chat/LLM message structures.

Defines a provider-agnostic message format used internally by
AIService, decoupled from any specific SDK's message shape.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a conversation, in OpenAI-compatible format.

    Attributes:
        role: Who sent the message — system, user, or assistant.
        content: The text content of the message.
    """

    role: Literal["system", "user", "assistant"]
    content: str


class CompletionRequest(BaseModel):
    """Internal request shape for requesting an LLM completion.

    Attributes:
        messages: The conversation history to send to the model.
        model: Optional model override (defaults to settings.OPENAI_MODEL).
        temperature: Sampling temperature, higher = more random.
        max_tokens: Optional cap on the response length.
    """

    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None


class CompletionResponse(BaseModel):
    """Internal response shape returned by AIService after a completion.

    Attributes:
        content: The generated text response.
        model: The model that actually generated the response.
        prompt_tokens: Number of tokens in the input.
        completion_tokens: Number of tokens in the output.
        total_tokens: Sum of prompt and completion tokens.
    """

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0