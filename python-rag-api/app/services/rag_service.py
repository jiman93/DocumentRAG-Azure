"""
RAG service - orchestrates document processing, retrieval, and generation
"""

import logging
import os
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.storage_service import StorageService
from app.utils.confidence_calculator import ImprovedConfidenceCalculator
from app.models.chat import RAGQueryRequest, RAGQueryResponse, Citation, ChatMessage
from app.models.document import DocumentMetadata, DocumentStatus
from app.utils.file_utils import generate_document_id, generate_chunk_id


logger = logging.getLogger("document_rag_api")


class RAGService:
    """Main RAG orchestration service"""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize RAG service

        Args:
            chunk_size: Chunk size for text splitting
            chunk_overlap: Chunk overlap size
            embedding_model: Embedding model name
        """
        # Initialize services
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.embedding_service = EmbeddingService(embedding_model=embedding_model)
        self.vector_store = VectorStore(embedding_service=self.embedding_service)
        self.storage_service = StorageService()
        self.confidence_calculator = ImprovedConfidenceCalculator(
            self.embedding_service.embeddings
        )

        # Initialize LLM
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client"""
        openai_config = settings.get_openai_config()

        if "api_type" in openai_config and openai_config["api_type"] == "azure":
            # Azure OpenAI
            self.llm = AzureChatOpenAI(
                api_key=openai_config["api_key"],
                azure_endpoint=openai_config["api_base"],
                azure_deployment=openai_config["deployment_name"],
                api_version=openai_config["api_version"],
                temperature=settings.temperature_default,
                max_tokens=settings.max_tokens,
            )
        else:
            # Standard OpenAI
            self.llm = ChatOpenAI(
                openai_api_key=openai_config["api_key"],
                model=openai_config.get("model", settings.openai_model),
                temperature=settings.temperature_default,
                max_tokens=settings.max_tokens,
            )

    def index_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
    ) -> DocumentMetadata:
        """
        Index a document: Load → Chunk → Embed → Store

        Args:
            file_path: Path to document file
            document_id: Optional document ID (generated if not provided)

        Returns:
            DocumentMetadata object
        """
        start_time = time.time()

        # Generate document ID if not provided
        if not document_id:
            document_id = generate_document_id(file_path)

        # Create metadata
        filename = os.path.basename(file_path)
        file_type = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(file_path)

        document_metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            status=DocumentStatus.PROCESSING,
        )

        try:
            # Step 1: Process document (load and chunk)
            chunks = self.document_processor.process_document(file_path)

            # Step 2: Generate chunk IDs
            chunk_ids = [generate_chunk_id(document_id, i) for i in range(len(chunks))]

            # Step 3: Add to vector store
            self.vector_store.add_documents(chunks, document_ids=chunk_ids)

            # Step 4: Upload to blob storage (if configured)
            blob_url = self.storage_service.upload_document_to_blob(
                file_path=file_path,
                document_id=document_id,
                metadata={"filename": filename, "file_type": file_type},
            )

            # Step 5: Update metadata
            document_metadata.status = DocumentStatus.INDEXED
            document_metadata.chunk_count = len(chunks)
            document_metadata.indexed_at = datetime.now()
            document_metadata.blob_url = blob_url

            # Step 6: Save metadata to Cosmos DB (if configured)
            self.storage_service.save_document_metadata(document_metadata)

            return document_metadata

        except Exception as e:
            document_metadata.status = DocumentStatus.FAILED
            document_metadata.error_message = str(e)
            self.storage_service.save_document_metadata(document_metadata)
            raise

    def query(
        self,
        request: RAGQueryRequest,
    ) -> RAGQueryResponse:
        """
        Execute RAG query: Retrieve → Generate → Return

        Args:
            request: RAG query request

        Returns:
            RAG query response
        """
        start_time = time.time()

        if not self.vector_store.is_initialized():
            raise ValueError("No documents indexed yet. Index documents first.")

        # Step 1: Enhance query with conversation context
        enhanced_query = self._enhance_query(
            request.question, request.conversation_history
        )

        # Step 2: Retrieve relevant chunks
        retriever = self.vector_store.get_retriever(
            search_type="mmr",
            search_kwargs={
                "k": request.top_k * 2,
                "fetch_k": 20,
            },
        )

        relevant_docs = retriever.invoke(enhanced_query)

        # Step 3: Rerank and select top chunks
        scored_docs = self._rerank_documents(relevant_docs, enhanced_query)[
            : request.top_k
        ]

        # Step 4: Generate response
        answer, prompt_inputs = self._generate_answer(
            question=request.question,
            context_docs=scored_docs,
            temperature=request.temperature,
            stream=request.stream,
        )

        # Step 5: Calculate confidence
        confidence_score = self.confidence_calculator.calculate_confidence(
            query=request.question,
            answer=answer,
            retrieved_docs=relevant_docs,
            used_docs=scored_docs,
        )

        # Step 6: Generate citations
        citations = (
            self._generate_citations(scored_docs) if request.include_sources else []
        )

        # Step 7: Generate related questions
        related_questions = self._generate_related_questions(
            request.question, scored_docs
        )

        # Calculate metrics
        total_time_ms = (time.time() - start_time) * 1000
        estimated_cost = self._estimate_cost(len(scored_docs), len(answer))

        # Summaries for logging / metadata
        retrieved_summary = [
            {
                "document_id": doc.metadata.get("document_id"),
                "source": doc.metadata.get(
                    "document_name", doc.metadata.get("source_file")
                ),
                "score": doc.metadata.get("score"),
                "preview": doc.page_content[:200],
            }
            for doc in scored_docs
        ]

        logger.info(
            "Query processed | top_k=%s | retrieved=%s",
            request.top_k,
            len(scored_docs),
        )
        for idx, doc_meta in enumerate(retrieved_summary, start=1):
            logger.debug("Retrieved[%s]: %s", idx, doc_meta)

        response_metadata = {
            "retrieved_documents": retrieved_summary,
            "prompt": {
                "question": prompt_inputs["question"],
                "context_preview": prompt_inputs["context"][:500],
            },
        }

        if request.conversation_id:
            message_timestamp = datetime.utcnow().isoformat()
            conversation_messages = [
                {
                    "role": "user",
                    "content": request.question,
                    "timestamp": message_timestamp,
                },
                {
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": response_metadata,
                },
            ]
            self.storage_service.append_conversation_messages(
                request.conversation_id, conversation_messages
            )

        return RAGQueryResponse(
            answer=answer,
            citations=citations,
            related_questions=related_questions,
            confidence_score=confidence_score,
            chunks_retrieved=len(relevant_docs),
            chunks_used=len(scored_docs),
            total_time_ms=total_time_ms,
            estimated_cost=estimated_cost,
            metadata=response_metadata,
        )

    def _enhance_query(
        self,
        question: str,
        conversation_history: Optional[List[ChatMessage]] = None,
    ) -> str:
        """Enhance query with conversation context"""
        if not conversation_history:
            return question

        # Build context from recent messages
        context = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in conversation_history[-5:]]
        )

        return f"Context from conversation:\n{context}\n\nQuestion: {question}"

    def _rerank_documents(
        self,
        documents: List,
        query: str,
    ) -> List:
        """Rerank documents by relevance"""
        # Simple reranking: sort by similarity score if available
        # In production, use a dedicated reranking model
        if hasattr(documents[0], "metadata") and "score" in documents[0].metadata:
            return sorted(
                documents, key=lambda d: d.metadata.get("score", 0), reverse=True
            )
        return documents

    def _generate_answer(
        self,
        question: str,
        context_docs: List,
        temperature: float = 0.3,
        stream: bool = False,
    ) -> tuple[str, Dict[str, str]]:
        """Generate answer using LLM and return prompt inputs for tracking"""
        # Build context
        context = "\n\n".join(
            [
                f"[Document {i+1}]: {doc.page_content}"
                for i, doc in enumerate(context_docs)
            ]
        )

        prompt_inputs = {
            "context": context,
            "question": question,
        }

        # Create prompt
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful AI assistant. Answer the question based ONLY on the following context. Always cite your sources using [1], [2], etc.

Context:
{context}

Question: {question}

Answer:""",
        )

        # Generate response
        chain = prompt_template | self.llm

        if stream:
            # Streaming response
            response = chain.stream(prompt_inputs)
            # For streaming, we'd need to handle this differently
            # For now, collect all chunks
            answer_parts = []
            for chunk in response:
                if hasattr(chunk, "content"):
                    answer_parts.append(chunk.content)
            return "".join(answer_parts), prompt_inputs
        else:
            # Non-streaming response
            response = chain.invoke(prompt_inputs)
            answer_text = (
                response.content if hasattr(response, "content") else str(response)
            )
            return answer_text, prompt_inputs

    def _generate_citations(self, documents: List) -> List[Citation]:
        """Generate citations from retrieved documents"""
        citations = []
        for i, doc in enumerate(documents):
            metadata = doc.metadata
            citations.append(
                Citation(
                    number=i + 1,
                    document_id=metadata.get("document_id", "unknown"),
                    document_name=metadata.get(
                        "document_name", metadata.get("source_file", "unknown")
                    ),
                    chunk_id=metadata.get("chunk_id", str(i)),
                    page=metadata.get("page", metadata.get("page_number")),
                    content=(
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    score=metadata.get("score", 0.0),
                )
            )
        return citations

    def _generate_related_questions(
        self,
        question: str,
        documents: List,
    ) -> List[str]:
        """Generate related questions (simplified implementation)"""
        # In production, use LLM to generate related questions
        # For now, return empty list
        return []

    def _estimate_cost(self, num_chunks: int, answer_length: int) -> float:
        """Estimate API cost"""
        # Rough estimation
        # Embedding cost: ~$0.00013 per 1K tokens
        # GPT-4 cost: ~$0.03 per 1K input tokens, $0.06 per 1K output tokens
        embedding_cost = (num_chunks * 512 / 1000) * 0.00013
        input_cost = (num_chunks * 512 / 1000) * 0.03
        output_cost = (answer_length / 1000) * 0.06
        return embedding_cost + input_cost + output_cost

    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector store and storage

        Args:
            document_id: Document identifier

        Returns:
            True if successful
        """
        try:
            # Delete from vector store (would need chunk IDs)
            # For now, just delete metadata
            self.storage_service.delete_document_metadata(document_id)
            self.storage_service.delete_document_from_blob(document_id)
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
