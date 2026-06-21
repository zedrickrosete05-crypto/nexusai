"""Vector database service wrapping ChromaDB operations.

Provides a clean interface for storing and querying document chunk
embeddings, isolating the rest of the app from ChromaDB's client API.
"""

import uuid
from typing import Any, Dict, List

import chromadb

from app.core.config import settings
from app.core.exceptions import VectorDBException
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorService:
    """Service for storing and querying vector embeddings in ChromaDB."""

    def __init__(self) -> None:
        """Initialize the ChromaDB client and target collection."""
        self._client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, port=settings.CHROMA_PORT
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )

    def add_chunks(
        self,
        *,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> None:
        """Store document chunks and their embeddings in ChromaDB.

        Args:
            document_id: The owning document's id, stored as metadata
                so chunks can be filtered or deleted per-document.
            user_id: The owning user's id, stored as metadata for
                access-scoped retrieval.
            chunks: The text chunks to store.
            embeddings: The corresponding embedding vectors.

        Raises:
            VectorDBException: If the ChromaDB write operation fails.
        """
        if not chunks:
            return

        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"document_id": str(document_id), "user_id": str(user_id), "chunk_index": i}
            for i in range(len(chunks))
        ]

        try:
            self._collection.add(
                ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas
            )
        except Exception as exc:
            logger.error("vector_add_failed", document_id=str(document_id), error=str(exc))
            raise VectorDBException(operation="add_chunks", original_error=str(exc)) from exc

        logger.info("chunks_stored", document_id=str(document_id), chunk_count=len(chunks))

    def query(
        self, *, query_embedding: List[float], user_id: uuid.UUID, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find the most semantically similar chunks for a query embedding.

        Args:
            query_embedding: The embedding vector of the search query.
            user_id: Restricts results to chunks owned by this user.
            top_k: Maximum number of results to return.

        Returns:
            A list of dicts, each containing "content", "document_id",
            and "distance" (lower distance means more similar).

        Raises:
            VectorDBException: If the ChromaDB query operation fails.
        """
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"user_id": str(user_id)},
            )
        except Exception as exc:
            logger.error("vector_query_failed", error=str(exc))
            raise VectorDBException(operation="query", original_error=str(exc)) from exc

        matches: List[Dict[str, Any]] = []
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]

        for content, metadata, distance in zip(documents[0], metadatas[0], distances[0]):
            matches.append(
                {
                    "content": content,
                    "document_id": metadata.get("document_id"),
                    "distance": distance,
                }
            )

        logger.info("vector_query_succeeded", user_id=str(user_id), result_count=len(matches))
        return matches

    def delete_document_chunks(self, *, document_id: uuid.UUID) -> None:
        """Delete all chunks belonging to a specific document.

        Args:
            document_id: The document whose chunks should be removed.

        Raises:
            VectorDBException: If the ChromaDB delete operation fails.
        """
        try:
            self._collection.delete(where={"document_id": str(document_id)})
        except Exception as exc:
            logger.error("vector_delete_failed", document_id=str(document_id), error=str(exc))
            raise VectorDBException(operation="delete_chunks", original_error=str(exc)) from exc

        logger.info("document_chunks_deleted", document_id=str(document_id))