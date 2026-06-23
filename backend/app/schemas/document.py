"""Pydantic schemas for document API requests/responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Schema for returning document metadata in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    file_type: str
    status: str
    chunk_count: int
    created_at: datetime