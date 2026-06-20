"""User database model.

Defines the `users` table schema, including authentication fields
and timestamps. This is the single source of truth for user data structure.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Represents a registered user of the NexusAI platform.

    Attributes:
        id: Unique UUID primary key.
        email: User's unique email address, used for login.
        hashed_password: Bcrypt-hashed password, never stored in plaintext.
        full_name: User's display name.
        is_active: Whether the account is active (False = soft-disabled).
        is_verified: Whether the user has verified their email.
        created_at: Timestamp of account creation.
        updated_at: Timestamp of the last update to this record.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation of the user.

        Returns:
            A string showing the user's id and email for debugging.
        """
        return f"<User id={self.id} email={self.email}>"