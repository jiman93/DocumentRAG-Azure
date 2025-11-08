"""
Vector store service - handles vector storage and retrieval
Supports ChromaDB (local) and Azure AI Search
"""
import json
import logging
import os
import sys
import uuid
import warnings
from typing import List, Optional, Dict, Any
from contextlib import redirect_stderr
from io import StringIO

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


# Module logger
logger = logging.getLogger("document_rag_api")

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
        self.search_client: Optional[SearchClient] = None
        self._azure_dimensions: Optional[int] = None
        
        if self.vector_store_type == "chroma":
            self._init_chroma()
        elif self.vector_store_type == "azure_search":
            self._init_azure_search()
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
                        embedding_function=self.embedding_service.embeddings,
                        persist_directory=persist_dir,
                    )
        except Exception as exc:
            warnings.warn(
                f"Failed to load existing ChromaDB at {persist_dir}: {exc}. "
                "A new vector store will be created when documents are added.",
                RuntimeWarning,
            )
    
    def _init_azure_search(self):
        """Initialise Azure AI Search index and client"""
        if not settings.azure_search_endpoint or not settings.azure_search_api_key:
            raise ValueError("Azure Search endpoint and api key must be configured.")
        
        credential = AzureKeyCredential(settings.azure_search_api_key)
        index_name = settings.azure_search_index_name
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=index_name,
            credential=credential,
        )
        index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential,
        )
        
        try:
            index_client.get_index(index_name)
        except ResourceNotFoundError:
            # Determine embedding dimension
            sample_embedding = self.embedding_service.embed_text("dimension probe")
            self._azure_dimensions = len(sample_embedding)
            
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="default",
                        parameters=HnswParameters(metric="cosine"),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="default",
                        algorithm_configuration_name="default",
                    )
                ],
            )
            
            index = SearchIndex(
                name=index_name,
                fields=[
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                    SimpleField(
                        name="document_id",
                        type=SearchFieldDataType.String,
                        filterable=True,
                        facetable=False,
                    ),
                    SearchableField(
                        name="content",
                    ),
                    SimpleField(
                        name="chunk_index",
                        type=SearchFieldDataType.Int32,
                        filterable=True,
                        sortable=True,
                    ),
                    SearchField(
                        name="contentVector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        vector_search_profile_name="default",
                        vector_search_dimensions=self._azure_dimensions,
                    ),
                    SimpleField(
                        name="source",
                        type=SearchFieldDataType.String,
                        filterable=True,
                    ),
                    SimpleField(
                        name="metadata_json",
                        type=SearchFieldDataType.String,
                        filterable=False,
                        sortable=False,
                        facetable=False,
                    ),
                ],
                vector_search=vector_search,
            )
            index_client.create_index(index)
        else:
            # Retrieve dimension from existing index
            index = index_client.get_index(index_name)
            vector_field = next(
                (
                    field
                    for field in index.fields
                    if isinstance(field, SearchField) and field.name == "contentVector"
                ),
                None,
            )
            if vector_field:
                self._azure_dimensions = vector_field.vector_search_dimensions
            # Ensure schema contains required fields; if not, recreate index
            required_field_names = {
                "id",
                "document_id",
                "content",
                "chunk_index",
                "contentVector",
                "source",
                "metadata_json",
            }
            existing_field_names = {field.name for field in index.fields}
            if not required_field_names.issubset(existing_field_names):
                logger.warning(
                    "Azure Search index '%s' missing required fields (%s). Recreating index.",
                    index_name,
                    required_field_names - existing_field_names,
                )
                index_client.delete_index(index_name)
                self._azure_dimensions = len(self.embedding_service.embed_text("dimension probe"))
                vector_search = VectorSearch(
                    algorithms=[
                HnswAlgorithmConfiguration(
                            name="default",
                            parameters=HnswParameters(metric="cosine"),
                        )
                    ],
                    profiles=[
                        VectorSearchProfile(
                            name="default",
                            algorithm_configuration_name="default",
                        )
                    ],
                )
                index = SearchIndex(
                    name=index_name,
                    fields=[
                        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                        SimpleField(
                            name="document_id",
                            type=SearchFieldDataType.String,
                            filterable=True,
                            sortable=False,
                            facetable=False,
                        ),
                        SearchableField(
                            name="content",
                        ),
                        SimpleField(
                            name="chunk_index",
                            type=SearchFieldDataType.Int32,
                            filterable=True,
                            sortable=True,
                        ),
                        SearchField(
                            name="contentVector",
                            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                            vector_search_profile_name="default",
                            vector_search_dimensions=self._azure_dimensions,
                        ),
                        SimpleField(
                            name="source",
                            type=SearchFieldDataType.String,
                            filterable=True,
                            sortable=False,
                            facetable=False,
                        ),
                        SimpleField(
                            name="metadata_json",
                            type=SearchFieldDataType.String,
                            filterable=False,
                            sortable=False,
                            facetable=False,
                        ),
                    ],
                    vector_search=vector_search,
                )
                index_client.create_index(index)
    
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
        elif self.vector_store_type == "azure_search":
            return self._add_to_azure_search(documents, document_ids)
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
    
    def _add_to_azure_search(
        self,
        documents: List[Document],
        document_ids: Optional[List[str]] = None,
    ) -> List[str]:
        if self.search_client is None:
            raise ValueError("Azure Search client not initialised.")
        
        ids: List[str] = []
        embeddings = self.embedding_service.embed_documents(
            [doc.page_content for doc in documents]
        )
        
        search_docs = []
        for idx, doc in enumerate(documents):
            doc_id = None
            if document_ids and idx < len(document_ids):
                doc_id = document_ids[idx]
            else:
                doc_id = doc.metadata.get("chunk_id") or str(uuid.uuid4())
            ids.append(doc_id)
            
            metadata_json = json.dumps(doc.metadata, default=str)
            search_docs.append(
                {
                    "id": doc_id,
                    "document_id": doc.metadata.get("document_id"),
                    "content": doc.page_content,
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "source": doc.metadata.get("source_file") or doc.metadata.get("document_name"),
                    "metadata_json": metadata_json,
                    "contentVector": embeddings[idx],
                }
            )
        
        self.search_client.upload_documents(search_docs)
        return ids
    
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
        if self.vector_store_type == "chroma":
            if self.vectorstore is None:
                raise ValueError("Vector store not initialized. Add documents first.")
            with TelemetrySuppressor():
                return self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter,
                )
        elif self.vector_store_type == "azure_search":
            return self._search_azure(query, k, filter)
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
        if self.vector_store_type == "chroma":
            if self.vectorstore is None:
                raise ValueError("Vector store not initialized. Add documents first.")
            with TelemetrySuppressor():
                return self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter,
                )
        elif self.vector_store_type == "azure_search":
            docs = self._search_azure(query, k, filter)
            return [(doc, doc.metadata.get("score", 0.0)) for doc in docs]
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
        if self.vector_store_type == "chroma":
            if self.vectorstore is None:
                raise ValueError("Vector store not initialized. Add documents first.")
            with TelemetrySuppressor():
                return self.vectorstore.as_retriever(
                    search_type=search_type,
                    search_kwargs=search_kwargs or {},
                )
        elif self.vector_store_type == "azure_search":
            kwargs = search_kwargs or {}
            return _AzureSearchRetriever(self, kwargs)
        else:
            raise NotImplementedError(f"Retriever not implemented for {self.vector_store_type}")
    
    def is_initialized(self) -> bool:
        """
        Check whether the underlying vector backend is ready to serve queries.
        """
        if self.vector_store_type == "chroma":
            return self.vectorstore is not None
        if self.vector_store_type == "azure_search":
            return self.search_client is not None
        return False
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents from vector store
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        if self.vector_store_type == "chroma":
            if self.vectorstore is None:
                return False
            with TelemetrySuppressor():
                self.vectorstore.delete(ids=document_ids)
                return True
        elif self.vector_store_type == "azure_search":
            if self.search_client is None:
                return False
            docs = [{"id": doc_id} for doc_id in document_ids]
            self.search_client.delete_documents(docs)
            return True
        else:
            raise NotImplementedError(f"Delete documents not implemented for {self.vector_store_type}")
    
    def _search_azure(
        self,
        query: str,
        k: int,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        if self.search_client is None:
            raise ValueError("Azure Search client not initialised.")
        if self._azure_dimensions is None:
            self._azure_dimensions = len(self.embedding_service.embed_text("dimension probe"))
        
        query_embedding = self.embedding_service.embed_text(query)
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=k,
            fields="contentVector",
        )
        
        azure_filter = None
        if filter:
            parts = []
            for key, value in filter.items():
                if isinstance(value, str):
                    parts.append(f"{key} eq '{value}'")
                else:
                    parts.append(f"{key} eq {value}")
            if parts:
                azure_filter = " and ".join(parts)
        
        results = self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            filter=azure_filter,
            select=["id", "document_id", "content", "chunk_index", "source", "metadata_json"],
        )
        
        documents: List[Document] = []
        for result in results:
            metadata = {
                "document_id": result.get("document_id"),
                "chunk_index": result.get("chunk_index"),
                "chunk_id": result.get("id"),
                "source_file": result.get("source"),
                "score": result.get("@search.score"),
            }
            metadata_json = result.get("metadata_json")
            if metadata_json:
                try:
                    parsed_metadata = json.loads(metadata_json)
                    if isinstance(parsed_metadata, dict):
                        metadata.update(parsed_metadata)
                except json.JSONDecodeError:
                    pass

            # Ensure document_id exists and is string-typed for downstream validation
            document_id = metadata.get("document_id") or result.get("document_id")
            if not document_id:
                document_id = metadata.get("source_document_id") or metadata.get("chunk_id")
            if document_id is not None:
                metadata["document_id"] = str(document_id)

            documents.append(
                Document(
                    page_content=result.get("content", ""),
                    metadata=metadata,
                )
            )
        return documents


class _AzureSearchRetriever:
    """Simple retriever wrapper to mimic LangChain retriever interface"""

    def __init__(self, store: VectorStore, search_kwargs: Dict[str, Any]):
        self.store = store
        self.search_kwargs = search_kwargs

    def invoke(self, query: str) -> List[Document]:
        k = self.search_kwargs.get("k", 5)
        filter = self.search_kwargs.get("filter")
        return self.store.similarity_search(query=query, k=k, filter=filter)
    
    def is_initialized(self) -> bool:
        """Check if vector store is initialized"""
        if self.store.vector_store_type == "chroma":
            return self.store.vectorstore is not None
        return self.store.search_client is not None

