"""Authentication API routes.

Thin HTTP layer for register, login, and token refresh. All business
logic is delegated to AuthService.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Register a new user account.

    Args:
        payload: The registration request body (email, password, full_name).
        db: Injected async database session.

    Returns:
        The newly created user's public data (excludes password).
    """
    service = AuthService(db)
    user = await service.register(
        email=payload.email, password=payload.password, full_name=payload.full_name
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and issue access/refresh tokens.

    Args:
        payload: The login request body (email, password).
        db: Injected async database session.

    Returns:
        A token pair (access_token, refresh_token).
    """
    service = AuthService(db)
    _, tokens = await service.login(email=payload.email, password=payload.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Issue a new token pair from a valid refresh token.

    Args:
        payload: The refresh request body containing the refresh token.
        db: Injected async database session.

    Returns:
        A new token pair (access_token, refresh_token).
    """
    service = AuthService(db)
    tokens = await service.refresh(refresh_token=payload.refresh_token)
    return tokens