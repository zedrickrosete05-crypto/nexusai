"""Conversation-specific repository for database access."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for all Conversation model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the conversation repository with an active session.

        Args:
            session: The async database session to use for queries.
        """
        super().__init__(model=Conversation, session=session)

    async def create(self, *, user_id: uuid.UUID, title: str = "New Conversation") -> Conversation:
        """Create and persist a new conversation.

        Args:
            user_id: The id of the user who owns this conversation.
            title: An initial display title.

        Returns:
            The newly created Conversation instance.
        """
        conversation = Conversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_id_for_user(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Conversation]:
        """Fetch a conversation by id, scoped to its owning user.

        Args:
            conversation_id: The conversation's id.
            user_id: The requesting user's id, to enforce ownership.

        Returns:
            The matching Conversation with messages eagerly loaded,
            or None if not found or not owned by this user.
        """
        result = await self.session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> List[Conversation]:
        """List all conversations belonging to a user, most recent first.

        Args:
            user_id: The owning user's id.

        Returns:
            A list of the user's Conversation instances.
        """
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())