"""LangGraph state machine wiring all agents into a complete workflow.

Defines the graph structure: Router dispatches to a specialist agent,
the Critic reviews the draft, optionally looping through Revision,
before Final Response finalizes the answer.
"""

from langgraph.graph import END, StateGraph

from app.agents.coding_agent import coding_node
from app.agents.critic_agent import critic_node
from app.agents.final_response_agent import final_response_node
from app.agents.research_agent import research_node
from app.agents.revision_node import revision_node
from app.agents.router_agent import router_node
from app.agents.state import AgentState
from app.agents.summarization_agent import summarization_node
from app.agents.writing_agent import writing_node
from app.core.logging import get_logger

logger = get_logger(__name__)


def _select_specialist(state: AgentState) -> str:
    """Choose which specialist node to run based on the router's decision.

    Args:
        state: The current agent state, with "route" already set.

    Returns:
        The name of the specialist node to route to next.
    """
    return state["route"] or "research"


def _after_critic(state: AgentState) -> str:
    """Decide whether to revise the draft or finalize it.

    Args:
        state: The current agent state, with critic results set.

    Returns:
        "revision" if the draft needs rework, otherwise "final_response".
    """
    return "revision" if state["needs_revision"] else "final_response"


def build_agent_graph():
    """Construct and compile the full LangGraph agent workflow.

    Returns:
        A compiled LangGraph graph, ready to be invoked with an
        initial AgentState.
    """
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("research", research_node)
    graph.add_node("coding", coding_node)
    graph.add_node("writing", writing_node)
    graph.add_node("summarization", summarization_node)
    graph.add_node("critic", critic_node)
    graph.add_node("revision", revision_node)
    graph.add_node("final_response", final_response_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        _select_specialist,
        {
            "research": "research",
            "coding": "coding",
            "writing": "writing",
            "summarization": "summarization",
        },
    )

    for specialist in ("research", "coding", "writing", "summarization"):
        graph.add_edge(specialist, "critic")

    graph.add_conditional_edges(
        "critic",
        _after_critic,
        {"revision": "revision", "final_response": "final_response"},
    )

    graph.add_edge("revision", "critic")
    graph.add_edge("final_response", END)

    compiled = graph.compile()
    logger.info("agent_graph_compiled")
    return compiled


agent_graph = build_agent_graph()