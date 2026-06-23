"""Final response agent: finalizes the answer returned to the user.

If the draft was revised, this is the last revised version. Otherwise
it's the original specialist draft, passed through unchanged.
"""

from app.agents.state import AgentState
from app.core.logging import get_logger

logger = get_logger(__name__)


async def final_response_node(state: AgentState) -> AgentState:
    """Set the final response from the current draft.

    Args:
        state: The current agent state, containing the (possibly
            revised) draft response.

    Returns:
        The updated state with "final_response" populated.
    """
    final_text = state["draft_response"] or "I wasn't able to generate a response."
    logger.info("final_response_set", route=state["route"], revisions=state["revision_count"])
    return {**state, "final_response": final_text}