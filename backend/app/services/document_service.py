"""Document processing service for the RAG pipeline.

Orchestrates document ingestion: persisting metadata, chunking text,
generating embeddings, and storing vectors, while tracking processing
status throughout.
"""

import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DocumentNotFoundException
from app.core.logging import get_logger
from app.models.document import Document
from app.rag.chunker import chunk_text
from app.rag.embedder import embed_texts
from app.repositories.document_repository import DocumentRepository
from app.services.vector_service import VectorService

logger = get_logger(__name__)


class DocumentService:
    """Service handling document upload, processing, and retrieval."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the document service with a database session.

        Args:
            session: The active async database session.
        """
        self.session = session
        self.document_repository = DocumentRepository(session)
        self.vector_service = VectorService()

    async def process_document(
        self, *, user_id: uuid.UUID, filename: str, file_type: str, text: str
    ) -> Document:
        """Ingest a document: persist metadata, chunk, embed, and store vectors.

        Args:
            user_id: The owning user's id.
            filename: The original uploaded filename.
            file_type: The file extension/type (pdf, docx, txt).
            text: The extracted plain text content of the document.

        Returns:
            The processed Document instance, with status "completed" or "failed".
        """
        document = await self.document_repository.create(
            user_id=user_id, filename=filename, file_type=file_type
        )
        await self.session.commit()

        try:
            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("Document contains no extractable text")

            embeddings = embed_texts(chunks)
            self.vector_service.add_chunks(
                document_id=document.id, user_id=user_id, chunks=chunks, embeddings=embeddings
            )

            document = await self.document_repository.update_status(
                document=document, status="completed", chunk_count=len(chunks)
            )
            await self.session.commit()

            logger.info(
                "document_processed", document_id=str(document.id), chunk_count=len(chunks)
            )
        except Exception as exc:
            await self.document_repository.update_status(document=document, status="failed")
            await self.session.commit()
            logger.error("document_processing_failed", document_id=str(document.id), error=str(exc))
            raise

        return document

    async def list_documents(self, *, user_id: uuid.UUID) -> List[Document]:
        """List all documents belonging to a user.

        Args:
            user_id: The owning user's id.

        Returns:
            A list of the user's documents, most recent first.
        """
        return await self.document_repository.list_for_user(user_id)

    async def delete_document(self, *, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a document and its associated vector chunks.

        Args:
            document_id: The document to delete.
            user_id: The requesting user's id, to enforce ownership.

        Raises:
            DocumentNotFoundException: If not found or not owned by this user.
        """
        document = await self.document_repository.get_by_id_for_user(document_id, user_id)
        if document is None:
            raise DocumentNotFoundException(document_id=str(document_id))

        self.vector_service.delete_document_chunks(document_id=document.id)
        await self.document_repository.delete(document)
        await self.session.commit()

        logger.info("document_deleted", document_id=str(document_id))