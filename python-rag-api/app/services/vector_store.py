"""
Vector store service - handles vector storage and retrieval
Supports ChromaDB (local) and Azure AI Search
"""
import os
import sys
import warnings
from typing import List, Optional, Dict, Any
from contextlib import redirect_stderr
from io import StringIO
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
warnings.filterwarnings("ignore", message=".*telemetry.*")
warnings.filterwarnings("ignore", message=".*Failed to send telemetry.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*persist.*")


class TelemetrySuppressor:
    """Context manager to suppress ChromaDB telemetry errors"""
    
    def __enter__(self):
        self._stderr_buffer = StringIO()
        self._original_stderr = sys.stderr
        sys.stderr = self._stderr_buffer
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self._original_stderr
        return False


class VectorStore:
    """Vector store abstraction layer"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store_type: Optional[str] = None,
    ):
        """
        Initialize vector store
        
        Args:
            embedding_service: Embedding service instance
            vector_store_type: Type of vector store ("chroma" or "azure_search")
        """
        self.embedding_service = embedding_service
        self.vector_store_type = vector_store_type or settings.vector_store_type
        self.vectorstore: Optional[Chroma] = None
        
        if self.vector_store_type == "chroma":
            self._init_chroma()
        elif self.vector_store_type == "azure_search":
            # Azure AI Search initialization would go here
            # For now, fallback to Chroma
            self._init_chroma()
        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")
    
    def _init_chroma(self):
        """Initialize ChromaDB vector store"""
        persist_dir = settings.chroma_persist_directory
        os.makedirs(persist_dir, exist_ok=True)
        # Load existing vector store if it exists
        sqlite_path = os.path.join(persist_dir, "chroma.sqlite3")
        try:
            if os.path.exists(sqlite_path):
                with TelemetrySuppressor():
                    self.vectorstore = Chroma(
                        embedding=self.embedding_service.embeddings,
                        persist_directory=persist_dir,
                    )
        except Exception as exc:
            warnings.warn(
                f"Failed to load existing ChromaDB at {persist_dir}: {exc}. "
                "A new vector store will be created when documents are added.",
                RuntimeWarning,
            )
    
    def add_documents(
        self,
        documents: List[Document],
        document_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to vector store
        
        Args:
            documents: List of Document objects
            document_ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        if self.vector_store_type == "chroma":
            return self._add_to_chroma(documents, document_ids)
        else:
            raise NotImplementedError(f"Add documents not implemented for {self.vector_store_type}")
    
    def _add_to_chroma(
        self,
        documents: List[Document],
        document_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to ChromaDB"""
        with TelemetrySuppressor():
            if self.vectorstore is None:
                # Create new vector store
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_service.embeddings,
                    persist_directory=settings.chroma_persist_directory,
                    ids=document_ids,
                )
            else:
                # Add to existing vector store
                self.vectorstore.add_documents(
                    documents=documents,
                    ids=document_ids,
                )
        
        # Return IDs (ChromaDB generates them if not provided)
        if document_ids:
            return document_ids
        # ChromaDB auto-generates IDs, but we can't easily retrieve them
        # Return a placeholder list
        return [f"doc_{i}" for i in range(len(documents))]
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Add documents first.")
        
        if self.vector_store_type == "chroma":
            with TelemetrySuppressor():
                return self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter,
                )
        else:
            raise NotImplementedError(f"Similarity search not implemented for {self.vector_store_type}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with scores
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Add documents first.")
        
        if self.vector_store_type == "chroma":
            with TelemetrySuppressor():
                return self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter,
                )
        else:
            raise NotImplementedError(f"Similarity search with score not implemented for {self.vector_store_type}")
    
    def get_retriever(
        self,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Get a retriever for the vector store
        
        Args:
            search_type: Type of search ("similarity", "mmr", etc.)
            search_kwargs: Additional search parameters
            
        Returns:
            Retriever instance
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Add documents first.")
        
        if self.vector_store_type == "chroma":
            with TelemetrySuppressor():
                return self.vectorstore.as_retriever(
                    search_type=search_type,
                    search_kwargs=search_kwargs or {},
                )
        else:
            raise NotImplementedError(f"Retriever not implemented for {self.vector_store_type}")
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents from vector store
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        if self.vectorstore is None:
            return False
        
        if self.vector_store_type == "chroma":
            with TelemetrySuppressor():
                self.vectorstore.delete(ids=document_ids)
                return True
        else:
            raise NotImplementedError(f"Delete documents not implemented for {self.vector_store_type}")
    
    def is_initialized(self) -> bool:
        """Check if vector store is initialized"""
        return self.vectorstore is not None

