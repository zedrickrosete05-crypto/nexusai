"""Authentication business logic service.

Orchestrates user registration, login, and token refresh by
coordinating the UserRepository and security utilities. Contains
no direct database queries or HTTP-specific logic.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse

logger = get_logger(__name__)


class AuthService:
    """Service handling registration, login, and token refresh logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the auth service with a database session.

        Args:
            session: The active async database session.
        """
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(self, *, email: str, password: str, full_name: str) -> User:
        """Register a new user account.

        Args:
            email: The new user's email address.
            password: The new user's plaintext password.
            full_name: The new user's display name.

        Returns:
            The newly created User instance.

        Raises:
            UserAlreadyExistsException: If the email is already registered.
        """
        if await self.user_repository.email_exists(email):
            logger.warning("registration_failed_duplicate_email", email=email)
            raise UserAlreadyExistsException(email=email)

        hashed = hash_password(password)
        user = await self.user_repository.create(
            email=email, hashed_password=hashed, full_name=full_name
        )
        logger.info("user_registered", user_id=str(user.id), email=user.email)
        return user

    async def login(self, *, email: str, password: str) -> tuple[User, TokenResponse]:
        """Authenticate a user and issue access/refresh tokens.

        Args:
            email: The user's email address.
            password: The user's plaintext password.

        Returns:
            A tuple of the authenticated User and their TokenResponse.

        Raises:
            InvalidCredentialsException: If the email or password is incorrect.
        """
        user = await self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            logger.warning("login_failed", email=email)
            raise InvalidCredentialsException()

        tokens = self._issue_tokens(str(user.id))
        logger.info("user_logged_in", user_id=str(user.id))
        return user, tokens

    async def refresh(self, *, refresh_token: str) -> TokenResponse:
        """Issue a new token pair from a valid refresh token.

        Args:
            refresh_token: A previously issued, unexpired refresh token.

        Returns:
            A new TokenResponse with fresh access and refresh tokens.

        Raises:
            TokenExpiredException: If the refresh token has expired.
            TokenInvalidException: If the refresh token is malformed.
            UserNotFoundException: If the user no longer exists.
        """
        user_id = decode_token(refresh_token, expected_type="refresh")

        user = await self.user_repository.get_by_id(uuid.UUID(user_id))
        if user is None:
            logger.warning("refresh_failed_user_not_found", user_id=user_id)
            raise UserNotFoundException(user_id=user_id)

        tokens = self._issue_tokens(str(user.id))
        logger.info("tokens_refreshed", user_id=str(user.id))
        return tokens

    def _issue_tokens(self, user_id: str) -> TokenResponse:
        """Generate a new access/refresh token pair for a user.

        Args:
            user_id: The user's id to embed in the token subject.

        Returns:
            A TokenResponse containing both tokens.
        """
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )