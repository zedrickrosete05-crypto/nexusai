"""Text extraction utilities for uploaded documents.

Extracts plain text from PDF, DOCX, and TXT files so it can be
passed into the chunking and embedding pipeline.
"""

import io

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.exceptions import InvalidFileTypeException
from app.core.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_FILE_TYPES = {"pdf", "docx", "txt"}


def extract_text(*, file_bytes: bytes, file_type: str) -> str:
    """Extract plain text from raw file bytes based on file type.

    Args:
        file_bytes: The raw uploaded file content.
        file_type: The file extension, lowercase, without a leading dot
            (e.g. "pdf", "docx", "txt").

    Returns:
        The extracted plain text content.

    Raises:
        InvalidFileTypeException: If file_type is not supported.
    """
    file_type = file_type.lower()

    if file_type == "pdf":
        return _extract_pdf(file_bytes)
    if file_type == "docx":
        return _extract_docx(file_bytes)
    if file_type == "txt":
        return _extract_txt(file_bytes)

    raise InvalidFileTypeException(
        file_type=file_type, allowed_types=sorted(SUPPORTED_FILE_TYPES)
    )


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file's raw bytes.

    Args:
        file_bytes: The raw PDF file content.

    Returns:
        The concatenated text of all pages.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages_text)
    logger.info("pdf_text_extracted", page_count=len(reader.pages))
    return text


def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file's raw bytes.

    Args:
        file_bytes: The raw DOCX file content.

    Returns:
        The concatenated text of all paragraphs.
    """
    document = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)
    logger.info("docx_text_extracted", paragraph_count=len(paragraphs))
    return text


def _extract_txt(file_bytes: bytes) -> str:
    """Decode raw bytes of a plain text file.

    Args:
        file_bytes: The raw TXT file content.

    Returns:
        The decoded UTF-8 text content.
    """
    return file_bytes.decode("utf-8", errors="ignore")