"""User-specific repository for database access.

Extends the generic BaseRepository with queries unique to the User
model, such as lookups by email.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for all User model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the user repository with an active session.

        Args:
            session: The async database session to use for queries.
        """
        super().__init__(model=User, session=session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The matching User instance, or None if not found.
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, full_name: str) -> User:
        """Create and persist a new user record.

        Args:
            email: The new user's email address.
            hashed_password: The bcrypt-hashed password.
            full_name: The new user's display name.

        Returns:
            The newly created User instance, with its generated id.
        """
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        """Check whether a user with the given email already exists.

        Args:
            email: The email address to check.

        Returns:
            True if a user with this email exists, False otherwise.
        """
        user = await self.get_by_email(email)
        return user is not None