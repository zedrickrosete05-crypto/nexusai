"""Pydantic schemas for authentication requests and responses.

Defines the request/response contracts for register, login, and
token refresh endpoints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration.

    Attributes:
        email: The new user's email address.
        password: The new user's plaintext password (will be hashed).
        full_name: The new user's display name.
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    """Request body for user login.

    Attributes:
        email: The user's registered email address.
        password: The user's plaintext password to verify.
    """

    email: EmailStr
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    """Request body for refreshing an access token.

    Attributes:
        refresh_token: A valid, unexpired refresh token.
    """

    refresh_token: str


class TokenResponse(BaseModel):
    """Response body containing issued JWT tokens.

    Attributes:
        access_token: Short-lived token for authenticating API requests.
        refresh_token: Long-lived token used to obtain new access tokens.
        token_type: Always "bearer", per OAuth2 convention.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"