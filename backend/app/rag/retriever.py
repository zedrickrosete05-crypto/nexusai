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

MAX_RELEVANT_DISTANCE = 2.0


def retrieve_context(
    *, query: str, user_id: uuid.UUID, vector_service: VectorService, top_k: int = 5
) -> str:
    """Retrieve relevant document chunks and format them as cited context."""
    query_embedding = embed_query(query)
    matches = vector_service.query(
        query_embedding=query_embedding, user_id=user_id, top_k=top_k
    )

    logger.info("retrieval_distances", distances=[round(m["distance"], 3) for m in matches])

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
    """Combine retrieved context and the user's query into a grounded prompt."""
    if not context:
        return query

    return (
        "The following numbered sources are excerpts from a document the user "
        "has uploaded and that you can directly read below. This is NOT public "
        "information — it is private content provided to you for this question. "
        "Answer using these sources, citing [Source N]. Do not say you lack "
        "access, cannot view files, or that information is 'publicly available' "
        "— the text below IS the file's content, already given to you.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n\n"
        "Answer directly using the sources above:"
    )