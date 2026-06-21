"""Retrieval and citation formatting for the RAG pipeline.

Converts raw vector search results into LLM-ready context blocks
with source citations, and filters out weak/irrelevant matches.
"""

import uuid
from typing import List

from app.core.logging import get_logger
from app.rag.embedder import embed_query
from app.services.vector_service import VectorService

logger = get_logger(__name__)

MAX_RELEVANT_DISTANCE = 1.5


def retrieve_context(
    *, query: str, user_id: uuid.UUID, vector_service: VectorService, top_k: int = 5
) -> str:
    """Retrieve relevant document chunks and format them as cited context.

    Args:
        query: The user's question or search query.
        user_id: Restricts retrieval to documents owned by this user.
        vector_service: The VectorService instance to query.
        top_k: Maximum number of chunks to retrieve before filtering.

    Returns:
        A formatted string of relevant chunks with source citations,
        ready to inject into an LLM prompt. Empty string if no
        sufficiently relevant chunks are found.
    """
    query_embedding = embed_query(query)
    matches = vector_service.query(
        query_embedding=query_embedding, user_id=user_id, top_k=top_k
    )

    relevant = [m for m in matches if m["distance"] <= MAX_RELEVANT_DISTANCE]

    if not relevant:
        logger.info("retrieval_no_relevant_chunks", query=query)
        return ""

    blocks: List[str] = []
    for i, match in enumerate(relevant, start=1):
        blocks.append(f"[Source {i}]\n{match['content']}")

    logger.info("retrieval_succeeded", chunk_count=len(relevant))
    return "\n\n".join(blocks)


def build_rag_prompt(*, query: str, context: str) -> str:
    """Combine retrieved context and the user's query into a grounded prompt.

    Args:
        query: The user's original question.
        context: The formatted, cited context from retrieve_context().

    Returns:
        A prompt instructing the LLM to answer using the provided
        sources and cite them, or the original query unchanged if
        no context was retrieved.
    """
    if not context:
        return query

    return (
        "Answer the question using the sources below. Cite sources using "
        "their [Source N] label when you use information from them. If the "
        "sources don't contain the answer, say so.\n\n"
        f"{context}\n\n"
        f"Question: {query}"
    )