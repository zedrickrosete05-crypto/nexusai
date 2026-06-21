"""Text embedding utilities for the RAG pipeline.

Wraps a local sentence-transformers model to convert text chunks
into vector embeddings for semantic similarity search.
"""

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.core.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """Load and cache the sentence-transformers embedding model.

    The model is loaded once per process and reused for all subsequent
    embedding calls, since loading it from disk is relatively slow.

    Returns:
        The loaded SentenceTransformer model instance.
    """
    logger.info("embedding_model_loading", model=EMBEDDING_MODEL_NAME)
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("embedding_model_loaded", model=EMBEDDING_MODEL_NAME)
    return model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate vector embeddings for a list of text chunks.

    Args:
        texts: A list of text chunks to embed.

    Returns:
        A list of embedding vectors, one per input text, in the same order.
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    logger.info("texts_embedded", count=len(texts))
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Generate a vector embedding for a single search query.

    Args:
        query: The search query text.

    Returns:
        The embedding vector for the query.
    """
    return embed_texts([query])[0]