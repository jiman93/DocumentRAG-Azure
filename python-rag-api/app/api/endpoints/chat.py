"""
Chat and RAG query endpoints
"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, List

from app.models.chat import (
    RAGQueryRequest,
    RAGQueryResponse,
    StreamingChunk,
    ConversationCreateRequest,
    ConversationResponse,
    ConversationHistoryResponse,
    ConversationSummary,
    ChatMessage,
)
from app.services.rag_service import RAGService
from app.services.storage_service import StorageService

logger = logging.getLogger("document_rag_api")

router = APIRouter(prefix="/chat", tags=["chat"])


# Dependency to get RAG service instance
def get_rag_service() -> RAGService:
    """Get RAG service instance"""
    return RAGService()


def get_storage_service() -> StorageService:
    """Get storage service instance"""
    return StorageService()


@router.post("/query", response_model=RAGQueryResponse)
async def query(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Execute a RAG query
    
    Returns answer with citations and metadata
    """
    logger.info(f"Processing RAG query: question='{request.question[:50]}...' | top_k={request.top_k}")
    
    try:
        response = rag_service.query(request)
        logger.info(
            f"Query successful: answer_length={len(response.answer)} | "
            f"citations={len(response.citations)} | "
            f"confidence={response.confidence_score:.2%} | "
            f"time_ms={response.total_time_ms:.1f}"
        )
        return response
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Validation error in query: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation Error",
                "message": error_msg,
                "type": type(e).__name__,
            }
        )
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(f"Unexpected error in query: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": error_msg,
                "type": type(e).__name__,
            }
        )


@router.post("/query/stream")
async def query_stream(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Execute a RAG query with streaming response
    
    Returns Server-Sent Events (SSE) stream
    """
    if not request.stream:
        request.stream = True
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # For now, return non-streaming response as single chunk
            # In production, implement proper streaming
            response = rag_service.query(request)
            
            # Send answer in chunks
            chunk_size = 50
            answer = response.answer
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i:i + chunk_size]
                chunk_data = StreamingChunk(
                    chunk=chunk,
                    done=False,
                )
                yield f"data: {chunk_data.model_dump_json()}\n\n"
            
            # Send final chunk with citations
            final_chunk = StreamingChunk(
                chunk="",
                done=True,
                citations=response.citations,
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
            
        except Exception as e:
            error_chunk = StreamingChunk(
                chunk=f"Error: {str(e)}",
                done=True,
            )
            yield f"data: {error_chunk.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    storage_service: StorageService = Depends(get_storage_service),
):
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    conversation_data = {
        "conversation_id": conversation_id,
        "title": request.title or "New Conversation",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "messages": [],
        "metadata": request.metadata,
    }
    
    success = storage_service.save_conversation(conversation_id, conversation_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    
    return ConversationResponse(
        conversation_id=conversation_id,
        title=conversation_data["title"],
        created_at=datetime.fromisoformat(conversation_data["created_at"]),
        updated_at=datetime.fromisoformat(conversation_data["updated_at"]),
        message_count=0,
        metadata=request.metadata,
        messages=[],
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    storage_service: StorageService = Depends(get_storage_service),
):
    """Get conversation by ID"""
    conversation = storage_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = [
        ChatMessage(
            role=msg.get("role", "assistant"),
            content=msg.get("content", ""),
            timestamp=datetime.fromisoformat(msg.get("timestamp"))
            if msg.get("timestamp")
            else datetime.utcnow(),
            metadata=msg.get("metadata"),
        )
        for msg in conversation.get("messages", [])
    ]

    return ConversationResponse(
        conversation_id=conversation["conversation_id"],
        title=conversation.get("title"),
        created_at=datetime.fromisoformat(conversation["created_at"]),
        updated_at=datetime.fromisoformat(conversation["updated_at"]),
        message_count=len(messages),
        metadata=conversation.get("metadata", {}),
        messages=messages,
    )


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    storage_service: StorageService = Depends(get_storage_service),
):
    """Get conversation history (messages only)"""
    conversation = storage_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = [
        ChatMessage(
            role=msg.get("role", "assistant"),
            content=msg.get("content", ""),
            timestamp=datetime.fromisoformat(msg.get("timestamp"))
            if msg.get("timestamp")
            else datetime.utcnow(),
            metadata=msg.get("metadata"),
        )
        for msg in conversation.get("messages", [])
    ]

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=messages,
    )


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    storage_service: StorageService = Depends(get_storage_service),
):
    """List conversations with metadata"""
    conversations = storage_service.list_conversations(limit=limit, offset=offset)
    summaries: List[ConversationSummary] = []

    for conversation in conversations:
        try:
            created_at = datetime.fromisoformat(conversation["created_at"])
        except (KeyError, ValueError):
            created_at = datetime.utcnow()

        try:
            updated_at = datetime.fromisoformat(conversation["updated_at"])
        except (KeyError, ValueError):
            updated_at = created_at

        metadata = conversation.get("metadata") or {}
        summary = ConversationSummary(
            conversation_id=conversation["conversation_id"],
            title=conversation.get("title"),
            created_at=created_at,
            updated_at=updated_at,
            message_count=conversation.get("message_count", 0),
            metadata=metadata,
            last_message_preview=conversation.get("last_message_preview"),
        )
        summaries.append(summary)

    return summaries

