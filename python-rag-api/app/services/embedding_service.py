"""
Embedding service - handles text embeddings using OpenAI/Azure OpenAI
"""
import os
import warnings
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings

from app.core.config import settings


# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
warnings.filterwarnings("ignore", message=".*telemetry.*")


class EmbeddingService:
    """Handles text embeddings"""
    
    def __init__(self, embedding_model: Optional[str] = None):
        """
        Initialize embedding service
        
        Args:
            embedding_model: Model name (overrides config)
        """
        self.embedding_model = embedding_model or settings.openai_embedding_model
        
        # Get configuration
        embedding_config = settings.get_embedding_config()
        
        # Initialize embeddings
        if embedding_config.get("azure_endpoint"):
            # Azure OpenAI
            self.embeddings = AzureOpenAIEmbeddings(
                api_key=embedding_config["azure_api_key"],
                azure_endpoint=embedding_config["azure_endpoint"],
                azure_deployment=embedding_config["azure_deployment"],
                api_version=embedding_config["azure_api_version"],
            )
        else:
            # Standard OpenAI
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=embedding_config["openai_api_key"],
                model=self.embedding_model,
            )
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
    
    def get_embedding_model(self) -> str:
        """Get the embedding model name"""
        return self.embedding_model

