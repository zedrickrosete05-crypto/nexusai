"""Research agent: answers factual, informational, and comparison queries."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

RESEARCH_SYSTEM_PROMPT = """You are a meticulous research assistant. Answer the user's \
question accurately and concisely. If you are uncertain about a fact, say so explicitly \
rather than guessing. Structure longer answers with clear headings or bullet points."""


async def research_node(state: AgentState) -> AgentState:
    """Generate a research-focused draft response.

    Args:
        state: The current agent state, containing the user's query.

    Returns:
        The updated state with "draft_response" populated.
    """
    ai_service = AIService()
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=RESEARCH_SYSTEM_PROMPT),
            ChatMessage(role="user", content=state["user_query"]),
        ]
    )
    response = await ai_service.generate(request)
    logger.info("research_draft_generated", query=state["user_query"][:80])
    return {**state, "draft_response": response.content}