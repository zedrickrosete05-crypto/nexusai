"""Pydantic schemas for user data input and output.

These schemas define the exact shape of user-related data crossing
the API boundary, intentionally excluding sensitive fields like
hashed_password from any response.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared base fields common to user creation and responses."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user (used internally by the auth service).

    Attributes:
        password: The plaintext password, hashed before storage.
    """

    password: str = Field(min_length=8, max_length=72)


class UserResponse(UserBase):
    """Schema for returning user data in API responses.

    Deliberately excludes hashed_password and any other sensitive field.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime