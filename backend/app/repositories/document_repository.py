"""Document-specific repository for database access."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for all Document model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the document repository with an active session.

        Args:
            session: The async database session to use for queries.
        """
        super().__init__(model=Document, session=session)

    async def create(self, *, user_id: uuid.UUID, filename: str, file_type: str) -> Document:
        """Create and persist a new document record with pending status.

        Args:
            user_id: The owning user's id.
            filename: The original uploaded filename.
            file_type: The file extension/type.

        Returns:
            The newly created Document instance.
        """
        document = Document(
            user_id=user_id, filename=filename, file_type=file_type, status="pending"
        )
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def update_status(
        self, *, document: Document, status: str, chunk_count: int = 0
    ) -> Document:
        """Update a document's processing status and chunk count.

        Args:
            document: The document instance to update.
            status: The new status — pending, processing, completed, or failed.
            chunk_count: The number of chunks generated, if completed.

        Returns:
            The updated Document instance.
        """
        document.status = status
        document.chunk_count = chunk_count
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def get_by_id_for_user(
        self, document_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Document]:
        """Fetch a document by id, scoped to its owning user.

        Args:
            document_id: The document's id.
            user_id: The requesting user's id, to enforce ownership.

        Returns:
            The matching Document, or None if not found or not owned.
        """
        result = await self.session.execute(
            select(Document).where(Document.id == document_id, Document.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> List[Document]:
        """List all documents belonging to a user, most recent first.

        Args:
            user_id: The owning user's id.

        Returns:
            A list of the user's Document instances.
        """
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())