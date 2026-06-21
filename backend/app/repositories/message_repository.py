"""Message-specific repository for database access."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for all Message model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the message repository with an active session.

        Args:
            session: The async database session to use for queries.
        """
        super().__init__(model=Message, session=session)

    async def create(
        self,
        *,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        total_tokens: int = 0,
    ) -> Message:
        """Create and persist a new message.

        Args:
            conversation_id: The parent conversation's id.
            role: Either "user" or "assistant".
            content: The message text.
            total_tokens: Token usage for this message, if applicable.

        Returns:
            The newly created Message instance.
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            total_tokens=total_tokens,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message