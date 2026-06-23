"""Summarization agent: condenses text into key points."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

SUMMARIZATION_SYSTEM_PROMPT = """You are a summarization specialist. Condense the given \
content into its most essential points, preserving key facts and figures. Default to \
bullet points unless the user requests a different format. Do not add information that \
isn't present in the original content."""


async def summarization_node(state: AgentState) -> AgentState:
    """Generate a summarization-focused draft response.

    Args:
        state: The current agent state, containing the user's query.

    Returns:
        The updated state with "draft_response" populated.
    """
    ai_service = AIService()
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=SUMMARIZATION_SYSTEM_PROMPT),
            ChatMessage(role="user", content=state["user_query"]),
        ]
    )
    response = await ai_service.generate(request)
    logger.info("summarization_draft_generated", query=state["user_query"][:80])
    return {**state, "draft_response": response.content}