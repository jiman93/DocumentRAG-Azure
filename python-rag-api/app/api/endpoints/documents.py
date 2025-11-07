"""
Document management endpoints
"""
import logging
import os
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse

from app.models.document import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    DocumentMetadata,
    DocumentStatus,
)
from app.services.rag_service import RAGService
from app.services.storage_service import StorageService
from app.utils.file_utils import (
    is_supported_file_type,
    generate_document_id,
    get_file_size,
    sanitize_filename,
)

logger = logging.getLogger("document_rag_api")

router = APIRouter(prefix="/documents", tags=["documents"])


# Dependency to get RAG service instance
def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    return RAGService()


def get_storage_service() -> StorageService:
    """Get storage service instance"""
    return StorageService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    rag_service: RAGService = Depends(get_rag_service),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    Upload and index a document
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    logger.info(f"Upload request received: filename='{file.filename}' | content_type='{file.content_type}'")
    
    # Validate file type
    if not is_supported_file_type(file.filename):
        error_msg = f"Unsupported file type: {file.filename}. Supported: PDF, DOCX, TXT, MD"
        logger.warning(error_msg)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported File Type",
                "message": error_msg,
                "filename": file.filename,
            }
        )
    
    # Save uploaded file temporarily
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            file_size = len(content)
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"File saved temporarily: {tmp_file_path} | size={file_size} bytes")
        
        # Generate document ID
        document_id = generate_document_id(tmp_file_path, content)
        logger.info(f"Generated document ID: {document_id}")
        
        # Index document
        document_metadata = rag_service.index_document(
            file_path=tmp_file_path,
            document_id=document_id,
        )
        
        logger.info(
            f"Document indexed successfully: document_id={document_id} | "
            f"chunks={document_metadata.chunk_count} | "
            f"status={document_metadata.status}"
        )
        
        return DocumentUploadResponse(
            document_id=document_metadata.document_id,
            filename=document_metadata.filename,
            status=document_metadata.status,
            message="Document uploaded and indexed successfully",
            chunk_count=document_metadata.chunk_count,
        )
    except Exception as e:
        error_msg = f"Error processing document: {str(e)}"
        logger.error(f"Failed to process document: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Document Processing Error",
                "message": error_msg,
                "type": type(e).__name__,
            }
        )
    finally:
        # Clean up temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
                logger.debug(f"Temporary file deleted: {tmp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_file_path}: {e}")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 100,
    offset: int = 0,
    storage_service: StorageService = Depends(get_storage_service),
):
    """List all indexed documents"""
    documents = storage_service.list_documents(limit=limit, offset=offset)
    return DocumentListResponse(
        documents=documents,
        total=len(documents),
    )


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(
    document_id: str,
    storage_service: StorageService = Depends(get_storage_service),
):
    """Get document metadata by ID"""
    document = storage_service.get_document_metadata(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    rag_service: RAGService = Depends(get_rag_service),
    storage_service: StorageService = Depends(get_storage_service),
):
    """Delete a document and its chunks"""
    success = rag_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    return DocumentDeleteResponse(
        document_id=document_id,
        deleted=True,
        message="Document deleted successfully",
    )

