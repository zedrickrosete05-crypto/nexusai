"""Shared state object for the LangGraph agent workflow.

Every agent node reads from and writes to this TypedDict as it flows
through the graph. LangGraph merges return values from each node back
into this shared state automatically.
"""

from typing import Literal, Optional, TypedDict

AgentRoute = Literal["research", "coding", "writing", "summarization"]


class AgentState(TypedDict):
    """The state object passed between all nodes in the agent graph.

    Attributes:
        user_query: The original user message that started this run.
        route: Which specialist agent the router selected.
        draft_response: The specialist agent's initial answer.
        critic_feedback: The critic's review of the draft, if any issues found.
        needs_revision: Whether the critic flagged the draft for rework.
        final_response: The polished, final answer returned to the user.
        revision_count: How many times the draft has been revised, to cap loops.
    """

    user_query: str
    route: Optional[AgentRoute]
    draft_response: Optional[str]
    critic_feedback: Optional[str]
    needs_revision: bool
    final_response: Optional[str]
    revision_count: int