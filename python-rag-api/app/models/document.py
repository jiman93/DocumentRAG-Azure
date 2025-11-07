"""
Document models and schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Document metadata"""

    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File extension (pdf, docx, txt, md)")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: datetime = Field(
        default_factory=datetime.now, description="Upload timestamp"
    )
    indexed_at: Optional[datetime] = Field(None, description="Indexing completion time")
    status: DocumentStatus = Field(
        default=DocumentStatus.UPLOADED, description="Processing status"
    )
    chunk_count: int = Field(default=0, description="Number of chunks created")
    blob_url: Optional[str] = Field(None, description="Azure Blob Storage URL")
    error_message: Optional[str] = Field(
        None, description="Error message if processing failed"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DocumentChunk(BaseModel):
    """Document chunk with metadata"""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    page_number: Optional[int] = Field(None, description="Page number if available")
    chunk_index: int = Field(..., description="Chunk index within document")
    chunk_size: int = Field(..., description="Character count")
    embedding: Optional[List[float]] = Field(None, description="Embedding vector")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional chunk metadata"
    )


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""

    document_id: str
    filename: str
    status: DocumentStatus
    message: str
    chunk_count: Optional[int] = None


class DocumentListResponse(BaseModel):
    """Response for listing documents"""

    documents: List[DocumentMetadata]
    total: int


class DocumentDeleteResponse(BaseModel):
    """Response for document deletion"""

    document_id: str
    deleted: bool
    message: str
