"""Revision node: regenerates a draft response incorporating critic feedback."""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

REVISION_SYSTEM_PROMPT = """You previously gave a draft answer that was flagged for \
revision. Rewrite the answer to address the specific feedback given, while still fully \
answering the original question."""


async def revision_node(state: AgentState) -> AgentState:
    """Regenerate the draft response using the critic's feedback.

    Args:
        state: The current agent state, containing the draft and feedback.

    Returns:
        The updated state with a revised "draft_response" and an
        incremented "revision_count".
    """
    ai_service = AIService()
    revision_input = (
        f"Original question: {state['user_query']}\n\n"
        f"Previous draft: {state['draft_response']}\n\n"
        f"Feedback to address: {state['critic_feedback']}"
    )
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=REVISION_SYSTEM_PROMPT),
            ChatMessage(role="user", content=revision_input),
        ]
    )
    response = await ai_service.generate(request)

    new_count = state["revision_count"] + 1
    logger.info("draft_revised", revision_count=new_count)
    return {**state, "draft_response": response.content, "revision_count": new_count}