"""Password hashing and JWT token utilities.

Provides secure password hashing with bcrypt and JWT access/refresh
token creation and verification for stateless authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import TokenExpiredException, TokenInvalidException


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        plain_password: The user's raw password.

    Returns:
        The bcrypt-hashed password, safe to store in the database.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash.

    Args:
        plain_password: The raw password provided at login.
        hashed_password: The stored hash to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash.

    Args:
        plain_password: The raw password provided at login.
        hashed_password: The stored hash to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def _create_token(
    subject: str,
    expires_delta: timedelta,
    token_type: Literal["access", "refresh"],
) -> str:
    """Create a signed JWT token with an expiration and type claim.

    Args:
        subject: The token subject, typically the user's id.
        expires_delta: How long until the token expires.
        token_type: Whether this is an "access" or "refresh" token.

    Returns:
        The encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    """Create a short-lived JWT access token for a user.

    Args:
        user_id: The id of the authenticated user.

    Returns:
        A signed JWT access token string.
    """
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject=user_id, expires_delta=expires_delta, token_type="access")


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token for a user.

    Args:
        user_id: The id of the authenticated user.

    Returns:
        A signed JWT refresh token string.
    """
    expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject=user_id, expires_delta=expires_delta, token_type="refresh")


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> str:
    """Decode and validate a JWT token, returning the user id.

    Args:
        token: The JWT string to decode.
        expected_type: The token type this caller expects ("access" or "refresh").

    Returns:
        The user id stored in the token's subject claim.

    Raises:
        TokenExpiredException: If the token has expired.
        TokenInvalidException: If the token is malformed, has the wrong
            signature, or does not match the expected type.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise TokenInvalidException()

    if payload.get("type") != expected_type:
        raise TokenInvalidException()

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise TokenInvalidException()

    return user_id