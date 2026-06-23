"""Router agent: classifies user intent and selects a specialist agent.

Uses the configured AIService to classify the query into one of four
routes, then updates the shared AgentState accordingly.
"""

from app.agents.state import AgentRoute, AgentState
from app.core.logging import get_logger
from app.schemas.chat import ChatMessage, CompletionRequest
from app.services.ai_service import AIService

logger = get_logger(__name__)

ROUTER_SYSTEM_PROMPT = """You are a routing classifier. Read the user's message and \
respond with EXACTLY ONE WORD from this list, nothing else:

research - for questions seeking information, facts, comparisons, or explanations
coding - for requests to write, debug, explain, or review code
writing - for requests to draft, edit, or improve written content like emails or articles
summarization - for requests to summarize, condense, or extract key points from text

Respond with only the single word."""

VALID_ROUTES: set[str] = {"research", "coding", "writing", "summarization"}
DEFAULT_ROUTE: AgentRoute = "research"


async def router_node(state: AgentState) -> AgentState:
    """Classify the user's query and select a specialist route.

    Args:
        state: The current agent state, containing the user's query.

    Returns:
        The updated state with the "route" field set.
    """
    ai_service = AIService()
    request = CompletionRequest(
        messages=[
            ChatMessage(role="system", content=ROUTER_SYSTEM_PROMPT),
            ChatMessage(role="user", content=state["user_query"]),
        ],
        temperature=0.0,
        max_tokens=10,
    )
    response = await ai_service.generate(request)
    raw_route = response.content.strip().lower()

    route: AgentRoute = raw_route if raw_route in VALID_ROUTES else DEFAULT_ROUTE  # type: ignore[assignment]
    if raw_route not in VALID_ROUTES:
        logger.warning("router_invalid_response", raw_response=raw_route, fallback=DEFAULT_ROUTE)

    logger.info("query_routed", route=route, query=state["user_query"][:80])
    return {**state, "route": route}