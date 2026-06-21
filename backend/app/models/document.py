"""Document database model.

Tracks metadata for uploaded files used in the RAG pipeline. The
actual file content's chunks/embeddings live in ChromaDB, not here —
this table is the relational source of truth for ownership and status.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    """Represents an uploaded document tracked for RAG processing.

    Attributes:
        id: Unique UUID primary key.
        user_id: The owning user's id.
        filename: The original uploaded filename.
        file_type: The file extension/type (pdf, docx, txt).
        status: Processing status — pending, processing, completed, failed.
        chunk_count: Number of chunks generated from this document.
        created_at: Timestamp of upload.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            A string showing the document's id and filename.
        """
        return f"<Document id={self.id} filename={self.filename}>"