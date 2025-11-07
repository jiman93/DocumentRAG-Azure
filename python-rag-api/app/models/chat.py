"""
Chat and RAG query models and schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Source citation with metadata"""

    number: int = Field(..., description="Citation number")
    document_id: str = Field(..., description="Source document ID")
    document_name: str = Field(..., description="Source document filename")
    chunk_id: str = Field(..., description="Source chunk ID")
    page: Optional[int] = Field(None, description="Page number if available")
    content: str = Field(..., description="Cited text excerpt")
    score: float = Field(..., description="Relevance score (0-1)")


class ChatMessage(BaseModel):
    """Chat message in conversation"""

    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""

    question: str = Field(..., description="User question", min_length=1)
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID to append messages to",
    )
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, description="Previous conversation messages"
    )
    top_k: int = Field(
        default=5, ge=1, le=20, description="Number of chunks to retrieve"
    )
    temperature: float = Field(
        default=0.3, ge=0.0, le=2.0, description="LLM temperature"
    )
    stream: bool = Field(default=False, description="Enable streaming response")
    include_sources: bool = Field(default=True, description="Include source citations")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional filters for document search"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main topics covered?",
                "conversation_id": "613f0134-52ea-48b3-a0eb-08337eee7c19",
            }
        }


class RAGQueryResponse(BaseModel):
    """Response from RAG query"""

    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(
        default_factory=list, description="Source citations"
    )
    related_questions: List[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    chunks_retrieved: int = Field(..., description="Number of chunks retrieved")
    chunks_used: int = Field(..., description="Number of chunks used in answer")
    total_time_ms: float = Field(
        ..., description="Total processing time in milliseconds"
    )
    estimated_cost: float = Field(default=0.0, description="Estimated API cost in USD")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class StreamingChunk(BaseModel):
    """Streaming response chunk"""

    chunk: str = Field(..., description="Text chunk")
    done: bool = Field(default=False, description="Whether this is the final chunk")
    citations: Optional[List[Citation]] = Field(
        None, description="Citations (only in final chunk)"
    )


class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation"""

    title: Optional[str] = Field(None, description="Conversation title")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ConversationResponse(BaseModel):
    """Conversation response"""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(default=0, description="Number of messages")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
