"""WebSocket route for real-time streaming chat.

Provides a WebSocket endpoint that streams AI responses token-by-token,
authenticated via a JWT access token passed as a query parameter
(WebSocket clients cannot send custom Authorization headers easily).
"""

import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NexusAIException
from app.core.logging import get_logger
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.services.chat_service import ChatService

logger = get_logger(__name__)
router = APIRouter()


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    token: str = Query(...),
) -> None:
    """Stream AI chat responses over a WebSocket connection.

    Protocol:
        1. Client connects with ?token=<access_token> in the URL.
        2. Client sends a JSON message: {"content": "user's message"}.
        3. Server streams back JSON chunks: {"chunk": "..."}.
        4. Server sends {"done": true} when the response is complete.

    Args:
        websocket: The WebSocket connection.
        conversation_id: The conversation to stream messages in.
        token: A valid JWT access token, passed as a query parameter.
    """
    await websocket.accept()

    session: AsyncSession = AsyncSessionLocal()
    try:
        user_id_str = decode_token(token, expected_type="access")
        user_repository = UserRepository(session)
        user = await user_repository.get_by_id(uuid.UUID(user_id_str))
        if user is None:
            await websocket.send_json({"error": "User not found"})
            await websocket.close(code=4401)
            return

        chat_service = ChatService(session)

        while True:
            data = await websocket.receive_json()
            content = data.get("content", "")
            if not content:
                await websocket.send_json({"error": "Message content cannot be empty"})
                continue

            try:
                async for chunk in chat_service.stream_message(
                    conversation_id=conversation_id, user_id=user.id, content=content
                ):
                    await websocket.send_json({"chunk": chunk})
                await websocket.send_json({"done": True})
            except NexusAIException as exc:
                await websocket.send_json({"error": exc.message})

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", conversation_id=str(conversation_id))
    except Exception as exc:
        logger.error("websocket_error", error=str(exc))
        await websocket.send_json({"error": "Authentication failed or invalid token"})
        await websocket.close(code=4401)
    finally:
        await session.close()