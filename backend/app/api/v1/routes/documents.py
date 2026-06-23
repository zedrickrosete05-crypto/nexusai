"""Document upload and management API routes.

Thin HTTP layer for uploading, listing, and deleting documents.
File text extraction and RAG processing are delegated to
DocumentService and the extractor utility.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import FileTooLargeException, InvalidFileTypeException
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.rag.extractor import SUPPORTED_FILE_TYPES, extract_text
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post(
    "/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Upload a document for RAG processing.

    Extracts text from the uploaded file, chunks it, generates
    embeddings, and stores them in the vector database.

    Args:
        file: The uploaded file (PDF, DOCX, or TXT).
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        The processed document's metadata, including chunk count.

    Raises:
        InvalidFileTypeException: If the file extension is unsupported.
        FileTooLargeException: If the file exceeds the size limit.
    """
    filename = file.filename or "untitled"
    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if file_type not in SUPPORTED_FILE_TYPES:
        raise InvalidFileTypeException(
            file_type=file_type, allowed_types=sorted(SUPPORTED_FILE_TYPES)
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeException(max_size_mb=MAX_FILE_SIZE_MB)

    text = extract_text(file_bytes=file_bytes, file_type=file_type)

    service = DocumentService(db)
    document = await service.process_document(
        user_id=current_user.id, filename=filename, file_type=file_type, text=text
    )

    return DocumentResponse.model_validate(document)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[DocumentResponse]:
    """List all documents belonging to the authenticated user.

    Args:
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Returns:
        A list of the user's document metadata, most recent first.
    """
    service = DocumentService(db)
    documents = await service.list_documents(user_id=current_user.id)
    return [DocumentResponse.model_validate(d) for d in documents]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document and its associated vector chunks.

    Args:
        document_id: The document to delete.
        current_user: The authenticated user, injected via dependency.
        db: Injected async database session.

    Raises:
        DocumentNotFoundException: If not found or not owned by this user.
    """
    service = DocumentService(db)
    await service.delete_document(document_id=document_id, user_id=current_user.id)