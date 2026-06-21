"""Shared FastAPI dependencies for route handlers.

Provides reusable dependencies like extracting the current
authenticated user from a bearer token.
"""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the currently authenticated user from a bearer access token.

    Args:
        token: The bearer access token extracted from the Authorization header.
        db: Injected async database session.

    Returns:
        The authenticated User instance.

    Raises:
        TokenExpiredException: If the access token has expired.
        TokenInvalidException: If the access token is malformed.
        UserNotFoundException: If the user no longer exists.
    """
    user_id = decode_token(token, expected_type="access")

    repository = UserRepository(db)
    user = await repository.get_by_id(uuid.UUID(user_id))
    if user is None:
        raise UserNotFoundException(user_id=user_id)

    return user