"""RAG retrieval node: fetches relevant document context before routing.

Runs once at the start of the graph, attaching any relevant retrieved
chunks to the shared state so specialist agents can use them.
"""

import uuid

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.rag.retriever import retrieve_context
from app.services.vector_service import VectorService

logger = get_logger(__name__)


async def make_rag_retrieval_node(user_id: uuid.UUID):
    """Create a RAG retrieval node bound to a specific user.

    Args:
        user_id: The user whose documents should be searched.

    Returns:
        An async node function compatible with LangGraph's node signature.
    """
    vector_service = VectorService()

    async def rag_retrieval_node(state: AgentState) -> AgentState:
        """Retrieve relevant document context for the user's query.

        Args:
            state: The current agent state, containing the user's query.

        Returns:
            The updated state with "rag_context" populated, if relevant
            chunks were found.
        """
        context = retrieve_context(
            query=state["user_query"], user_id=user_id, vector_service=vector_service
        )
        logger.info("agent_rag_retrieval_complete", found_context=bool(context))
        return {**state, "rag_context": context}

    return rag_retrieval_node