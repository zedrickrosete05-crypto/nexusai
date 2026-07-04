"""Dashboard API routes.

Provides aggregated statistics for the authenticated user's activity,
used to populate the frontend dashboard page.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return aggregated activity stats for the authenticated user.

    Args:
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        A dict containing conversation_count, message_count,
        document_count, and assistant_message_count.
    """
    conversation_count_result = await db.execute(
        select(func.count()).where(Conversation.user_id == current_user.id)
    )
    conversation_count = conversation_count_result.scalar() or 0

    conversation_ids_result = await db.execute(
        select(Conversation.id).where(Conversation.user_id == current_user.id)
    )
    conversation_ids = [row[0] for row in conversation_ids_result.fetchall()]

    message_count = 0
    assistant_message_count = 0

    if conversation_ids:
        message_count_result = await db.execute(
            select(func.count()).where(Message.conversation_id.in_(conversation_ids))
        )
        message_count = message_count_result.scalar() or 0

        assistant_count_result = await db.execute(
            select(func.count()).where(
                Message.conversation_id.in_(conversation_ids),
                Message.role == "assistant",
            )
        )
        assistant_message_count = assistant_count_result.scalar() or 0

    document_count_result = await db.execute(
        select(func.count()).where(Document.user_id == current_user.id)
    )
    document_count = document_count_result.scalar() or 0

    return {
        "conversation_count": conversation_count,
        "message_count": message_count,
        "assistant_message_count": assistant_message_count,
        "document_count": document_count,
    }
