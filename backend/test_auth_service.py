"""Quick manual test for AuthService against the real database."""

import asyncio
import uuid

from app.db.session import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException


async def main() -> None:
    """Exercise register, login, and refresh, then clean up."""
    async with AsyncSessionLocal() as session:
        service = AuthService(session)
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SuperSecret123!"

        user = await service.register(
            email=test_email, password=test_password, full_name="Service Test User"
        )
        print(f"Registered: {user.email}")
        await session.commit()

        try:
            await service.register(
                email=test_email, password=test_password, full_name="Duplicate"
            )
            print("ERROR: duplicate registration should have failed!")
        except UserAlreadyExistsException:
            print("Correctly rejected duplicate email")

        logged_in_user, tokens = await service.login(email=test_email, password=test_password)
        print(f"Login success: {logged_in_user.email}")
        print(f"Access token (first 30 chars): {tokens.access_token[:30]}...")

        try:
            await service.login(email=test_email, password="wrong_password")
            print("ERROR: wrong password login should have failed!")
        except InvalidCredentialsException:
            print("Correctly rejected wrong password")

        new_tokens = await service.refresh(refresh_token=tokens.refresh_token)
        print(f"Refresh success, new access token: {new_tokens.access_token[:30]}...")

        await service.user_repository.delete(user)
        await session.commit()
        print("Test user cleaned up.")

        print("\n=== Auth service tests passed! ===")


if __name__ == "__main__":
    asyncio.run(main())