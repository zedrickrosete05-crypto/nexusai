"""Pydantic schemas for conversation and message API requests/responses."""

import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    """Schema for returning a single message in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    total_tokens: int
    created_at: datetime


class ConversationResponse(BaseModel):
    """Schema for returning conversation summary data (no messages)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    """Schema for returning a conversation including its full message history."""

    messages: List[MessageResponse] = Field(default_factory=list)


class SendMessageRequest(BaseModel):
    """Request body for sending a new message in a conversation."""

    content: str = Field(min_length=1, max_length=10000)


class CreateConversationRequest(BaseModel):
    """Request body for creating a new conversation."""

    title: str = Field(default="New Conversation", max_length=255)