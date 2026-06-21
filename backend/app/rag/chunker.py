"""Text chunking utilities for the RAG pipeline.

Splits long documents into overlapping chunks sized appropriately
for embedding models and semantic retrieval.
"""

from typing import List

from app.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """Split text into overlapping chunks by word count.

    Uses a simple sliding window over words rather than characters,
    which keeps chunk boundaries from splitting mid-word and gives
    a more predictable token-to-word ratio for embedding models.

    Args:
        text: The full document text to split.
        chunk_size: Target number of words per chunk.
        chunk_overlap: Number of words shared between consecutive chunks.

    Returns:
        A list of text chunks. Returns an empty list if input is blank.

    Raises:
        ValueError: If chunk_overlap is greater than or equal to chunk_size.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    cleaned = text.strip()
    if not cleaned:
        return []

    words = cleaned.split()
    if len(words) <= chunk_size:
        return [cleaned]

    chunks: List[str] = []
    step = chunk_size - chunk_overlap
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break
        start += step

    logger.info("text_chunked", total_words=len(words), chunk_count=len(chunks))
    return chunks