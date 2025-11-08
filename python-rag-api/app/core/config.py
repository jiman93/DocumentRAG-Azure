"""
Application configuration using Pydantic settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_title: str = "Document RAG API"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready RAG API with Azure OpenAI and AI Search"
    debug: bool = False
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_embedding_deployment: str = "text-embedding-3-large"
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_chat_api_version: Optional[str] = None
    azure_openai_embedding_api_version: Optional[str] = None
    
    # OpenAI Configuration (fallback)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-large"
    
    # Azure AI Search Configuration
    azure_search_endpoint: Optional[str] = None
    azure_search_api_key: Optional[str] = None
    azure_search_index_name: str = "document-rag-index"
    
    # Azure Blob Storage Configuration
    azure_storage_account_name: Optional[str] = None
    azure_storage_account_key: Optional[str] = None
    azure_storage_connection_string: Optional[str] = None
    azure_storage_container_name: str = "documents"
    
    # Azure Cosmos DB Configuration
    azure_cosmos_endpoint: Optional[str] = None
    azure_cosmos_key: Optional[str] = None
    azure_cosmos_database_name: str = "rag-db"
    azure_cosmos_container_documents: str = "documents"
    azure_cosmos_container_conversations: str = "conversations"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_default: int = 5
    temperature_default: float = 0.3
    max_tokens: int = 2000
    
    # Vector Store Configuration
    vector_store_type: str = "chroma"  # Options: "chroma", "azure_search"
    chroma_persist_directory: str = "./chroma_db"
    
    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Security
    api_key: Optional[str] = None  # Optional API key for authentication
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_openai_config(self) -> dict:
        """Get OpenAI configuration (Azure or standard)"""
        if self.azure_openai_endpoint and self.azure_openai_api_key:
            chat_api_version = (
                self.azure_openai_chat_api_version or self.azure_openai_api_version
            )
            return {
                "api_type": "azure",
                "api_base": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "api_version": chat_api_version,
                "deployment_name": self.azure_openai_deployment_name,
            }
        elif self.openai_api_key:
            return {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            }
        else:
            raise ValueError(
                "Either Azure OpenAI or OpenAI API key must be configured. "
                "Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY environment variable."
            )
    
    def get_embedding_config(self) -> dict:
        """Get embedding configuration"""
        if self.azure_openai_endpoint and self.azure_openai_api_key:
            embedding_api_version = (
                self.azure_openai_embedding_api_version
                or self.azure_openai_api_version
            )
            return {
                "azure_endpoint": self.azure_openai_endpoint,
                "azure_api_key": self.azure_openai_api_key,
                "api_version": embedding_api_version,
                "azure_deployment": self.azure_openai_embedding_deployment,
            }
        elif self.openai_api_key:
            return {
                "openai_api_key": self.openai_api_key,
                "model": self.openai_embedding_model,
            }
        else:
            raise ValueError(
                "Either Azure OpenAI or OpenAI API key must be configured for embeddings."
            )


# Global settings instance
settings = Settings()

