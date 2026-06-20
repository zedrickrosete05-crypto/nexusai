"""Generic base repository providing common CRUD operations.

Specific repositories (UserRepository, etc.) inherit from this class
to avoid duplicating standard create/read/update/delete logic.
"""

import uuid
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing shared database operations.

    Attributes:
        model: The SQLAlchemy model class this repository manages.
        session: The active async database session.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        """Initialize the repository with a model class and session.

        Args:
            model: The SQLAlchemy model class to operate on.
            session: The async database session to use for queries.
        """
        self.model = model
        self.session = session

    async def get_by_id(self, record_id: uuid.UUID) -> Optional[ModelType]:
        """Fetch a single record by its primary key.

        Args:
            record_id: The UUID primary key of the record.

        Returns:
            The matching model instance, or None if not found.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, instance: ModelType) -> None:
        """Delete a record from the database.

        Args:
            instance: The model instance to delete.
        """
        await self.session.delete(instance)
        await self.session.flush()