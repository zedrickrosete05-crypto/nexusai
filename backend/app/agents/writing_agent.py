"""Writing agent: drafts, edits, and improves written content."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

WRITING_SYSTEM_PROMPT = """You are a skilled writing assistant. Match the tone and \
formality the user's request implies (e.g., professional for business emails, casual \
for social posts). Keep writing clear and concise, and avoid unnecessary jargon."""


async def writing_node(state: AgentState) -> AgentState:
    """Generate a writing-focused draft response.

    Args:
        state: The current agent state, containing the user's query.

    Returns:
        The updated state with "draft_response" populated.
    """
    ai_service = AIService()
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=WRITING_SYSTEM_PROMPT),
            ChatMessage(role="user", content=state["user_query"]),
        ]
    )
    response = await ai_service.generate(request)
    logger.info("writing_draft_generated", query=state["user_query"][:80])
    return {**state, "draft_response": response.content}