"""Custom exception classes for NexusAI application errors.

All custom exceptions inherit from NexusAIException, allowing FastAPI
exception handlers to catch them broadly or specifically, and map
each to an appropriate HTTP status code and error response.
"""

from typing import Any, Dict, Optional


class NexusAIException(Exception):
    """Base exception for all NexusAI application-specific errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code to return to the client.
        details: Optional additional context about the error.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the base application exception.

        Args:
            message: Human-readable description of what went wrong.
            status_code: HTTP status code to associate with this error.
            details: Optional dictionary of extra error context.
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# === AUTH EXCEPTIONS ===


class InvalidCredentialsException(NexusAIException):
    """Raised when login credentials are incorrect."""

    def __init__(self) -> None:
        super().__init__(message="Invalid email or password", status_code=401)


class TokenExpiredException(NexusAIException):
    """Raised when a JWT access or refresh token has expired."""

    def __init__(self) -> None:
        super().__init__(message="Token has expired", status_code=401)


class TokenInvalidException(NexusAIException):
    """Raised when a JWT token is malformed or fails signature verification."""

    def __init__(self) -> None:
        super().__init__(message="Invalid authentication token", status_code=401)


class UnauthorizedException(NexusAIException):
    """Raised when a user attempts an action they don't have permission for."""

    def __init__(self, message: str = "You are not authorized to perform this action") -> None:
        super().__init__(message=message, status_code=403)


# === RESOURCE EXCEPTIONS ===


class UserNotFoundException(NexusAIException):
    """Raised when a requested user does not exist."""

    def __init__(self, user_id: Optional[str] = None) -> None:
        details = {"user_id": user_id} if user_id else {}
        super().__init__(message="User not found", status_code=404, details=details)


class UserAlreadyExistsException(NexusAIException):
    """Raised when attempting to register a user with an existing email."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"A user with email '{email}' already exists",
            status_code=409,
            details={"email": email},
        )


class ConversationNotFoundException(NexusAIException):
    """Raised when a requested conversation does not exist."""

    def __init__(self, conversation_id: Optional[str] = None) -> None:
        details = {"conversation_id": conversation_id} if conversation_id else {}
        super().__init__(message="Conversation not found", status_code=404, details=details)


class DocumentNotFoundException(NexusAIException):
    """Raised when a requested document does not exist."""

    def __init__(self, document_id: Optional[str] = None) -> None:
        details = {"document_id": document_id} if document_id else {}
        super().__init__(message="Document not found", status_code=404, details=details)


# === VALIDATION / INPUT EXCEPTIONS ===


class InvalidFileTypeException(NexusAIException):
    """Raised when an uploaded file's type is not supported."""

    def __init__(self, file_type: str, allowed_types: list) -> None:
        super().__init__(
            message=f"File type '{file_type}' is not supported",
            status_code=400,
            details={"file_type": file_type, "allowed_types": allowed_types},
        )


class FileTooLargeException(NexusAIException):
    """Raised when an uploaded file exceeds the maximum allowed size."""

    def __init__(self, max_size_mb: int) -> None:
        super().__init__(
            message=f"File exceeds maximum size of {max_size_mb}MB",
            status_code=413,
            details={"max_size_mb": max_size_mb},
        )


# === RATE LIMITING / EXTERNAL SERVICE EXCEPTIONS ===


class RateLimitExceededException(NexusAIException):
    """Raised when a client exceeds the allowed request rate."""

    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            details={"retry_after_seconds": retry_after},
        )


class AIServiceException(NexusAIException):
    """Raised when an underlying AI provider (OpenAI, Ollama) call fails."""

    def __init__(self, provider: str, original_error: str) -> None:
        super().__init__(
            message=f"AI service '{provider}' failed to respond",
            status_code=502,
            details={"provider": provider, "original_error": original_error},
        )


class VectorDBException(NexusAIException):
    """Raised when a ChromaDB operation fails."""

    def __init__(self, operation: str, original_error: str) -> None:
        super().__init__(
            message=f"Vector database operation '{operation}' failed",
            status_code=502,
            details={"operation": operation, "original_error": original_error},
        )