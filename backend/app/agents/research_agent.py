"""Research agent: answers factual, informational, and comparison queries."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.rag.retriever import build_rag_prompt
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

RESEARCH_SYSTEM_PROMPT = """You are a meticulous research assistant. Answer the user's \
question accurately and concisely. If you are uncertain about a fact, say so explicitly \
rather than guessing. Structure longer answers with clear headings or bullet points. If \
sources are provided, cite them using their [Source N] label."""


async def research_node(state: AgentState) -> AgentState:
    """Generate a research-focused draft response, using RAG context if available.

    Args:
        state: The current agent state, containing the user's query and
            optionally retrieved document context.

    Returns:
        The updated state with "draft_response" populated.
    """
    ai_service = AIService()
    user_content = build_rag_prompt(
        query=state["user_query"], context=state.get("rag_context") or ""
    )
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=RESEARCH_SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_content),
        ]
    )
    response = await ai_service.generate(request)
    logger.info("research_draft_generated", query=state["user_query"][:80])
    return {**state, "draft_response": response.content}