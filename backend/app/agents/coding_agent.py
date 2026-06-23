"""Coding agent: writes, explains, debugs, and reviews code."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

CODING_SYSTEM_PROMPT = """You are an expert software engineer. When writing code, use \
clear variable names, include brief comments only where logic is non-obvious, and follow \
language-standard conventions. When explaining or debugging code, be precise and specific \
about line numbers or function names where relevant."""


async def coding_node(state: AgentState) -> AgentState:
    """Generate a coding-focused draft response.

    Args:
        state: The current agent state, containing the user's query.

    Returns:
        The updated state with "draft_response" populated.
    """
    ai_service = AIService()
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=CODING_SYSTEM_PROMPT),
            ChatMessage(role="user", content=state["user_query"]),
        ]
    )
    response = await ai_service.generate(request)
    logger.info("coding_draft_generated", query=state["user_query"][:80])
    return {**state, "draft_response": response.content}