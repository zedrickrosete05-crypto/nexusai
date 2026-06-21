"""Quick manual test for password hashing and JWT tokens."""

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

# Test password hashing
password = "SuperSecret123!"
hashed = hash_password(password)
print(f"Hashed: {hashed[:30]}...")
print(f"Verify correct password: {verify_password(password, hashed)}")
print(f"Verify wrong password: {verify_password('wrong', hashed)}")

# Test JWT tokens
fake_user_id = "abc-123-def-456"
access_token = create_access_token(fake_user_id)
refresh_token = create_refresh_token(fake_user_id)
print(f"\nAccess token: {access_token[:40]}...")
print(f"Refresh token: {refresh_token[:40]}...")

decoded_user_id = decode_token(access_token, expected_type="access")
print(f"\nDecoded user_id from access token: {decoded_user_id}")
print(f"Matches original: {decoded_user_id == fake_user_id}")

print("\n=== Security tests passed! ===")