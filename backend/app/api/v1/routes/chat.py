"""Chat API routes.

Thin HTTP layer for creating conversations, listing history, and
sending messages. All business logic is delegated to ChatService.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationResponse,
    CreateConversationRequest,
    MessageResponse,
    SendMessageRequest,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    payload: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """Create a new conversation for the authenticated user.

    Args:
        payload: The conversation creation request body.
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        The newly created conversation's summary data.
    """
    service = ChatService(db)
    conversation = await service.create_conversation(user_id=current_user.id, title=payload.title)
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ConversationResponse]:
    """List all conversations belonging to the authenticated user.

    Args:
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        A list of the user's conversation summaries, most recent first.
    """
    service = ChatService(db)
    conversations = await service.list_conversations(user_id=current_user.id)
    return [ConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationDetailResponse:
    """Fetch a single conversation with its full message history.

    Args:
        conversation_id: The conversation's id.
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        The conversation's details, including all messages.
    """
    service = ChatService(db)
    conversation = await service.get_conversation(
        conversation_id=conversation_id, user_id=current_user.id
    )
    return ConversationDetailResponse.model_validate(conversation)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send a message in a conversation and get the AI's full response.

    Args:
        conversation_id: The conversation to send the message in.
        payload: The message content.
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        The AI assistant's response message.
    """
    service = ChatService(db)
    assistant_message = await service.send_message(
        conversation_id=conversation_id, user_id=current_user.id, content=payload.content
    )
    return MessageResponse.model_validate(assistant_message)
@router.post(
    "/conversations/{conversation_id}/agent-messages", response_model=MessageResponse
)
async def send_agent_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send a message routed through the full multi-agent pipeline.

    Runs the query through the Router, a specialist agent (Research,
    Coding, Writing, or Summarization), and the Critic's revision loop
    before returning the final answer.

    Args:
        conversation_id: The conversation to send the message in.
        payload: The message content.
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        The AI assistant's agent-generated response message.
    """
    service = ChatService(db)
    assistant_message = await service.send_agent_message(
        conversation_id=conversation_id, user_id=current_user.id, content=payload.content
    )
    return MessageResponse.model_validate(assistant_message)