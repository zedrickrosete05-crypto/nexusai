"""Critic agent: reviews specialist drafts and flags issues for revision.

Acts as a quality gate before a response reaches the user. Uses a
strict revision cap to prevent infinite feedback loops.
"""

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

MAX_REVISIONS = 1

CRITIC_SYSTEM_PROMPT = """You are a strict quality reviewer. Given a user's question and \
a draft answer, decide if the draft adequately and accurately addresses the question.

Respond in EXACTLY this format, nothing else:
VERDICT: PASS
or
VERDICT: REVISE
REASON: <one short sentence explaining what's missing or wrong>

Only respond REVISE if there is a real, significant problem (factually wrong, ignores \
part of the question, or dangerously incomplete). Minor style preferences are not grounds \
for REVISE."""


async def critic_node(state: AgentState) -> AgentState:
    """Review the draft response and decide whether it needs revision.

    Args:
        state: The current agent state, containing the user query and draft.

    Returns:
        The updated state with "needs_revision" and "critic_feedback" set.
        Revision is never requested if MAX_REVISIONS has been reached.
    """
    if state["revision_count"] >= MAX_REVISIONS:
        logger.info("critic_skipped_max_revisions", revision_count=state["revision_count"])
        return {**state, "needs_revision": False, "critic_feedback": None}

    ai_service = AIService()
    review_input = (
        f"User question: {state['user_query']}\n\n"
        f"Draft answer: {state['draft_response']}"
    )
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=CRITIC_SYSTEM_PROMPT),
            ChatMessage(role="user", content=review_input),
        ],
        temperature=0.0,
        max_tokens=100,
    )
    response = await ai_service.generate(request)
    verdict_text = response.content.strip()

    needs_revision = "VERDICT: REVISE" in verdict_text.upper()
    feedback = None
    if needs_revision and "REASON:" in verdict_text.upper():
        feedback = verdict_text.split("REASON:", 1)[-1].strip()

    logger.info(
        "critic_review_complete",
        needs_revision=needs_revision,
        revision_count=state["revision_count"],
    )
    return {**state, "needs_revision": needs_revision, "critic_feedback": feedback}