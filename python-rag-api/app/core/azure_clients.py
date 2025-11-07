"""
Azure SDK client initialization and management
"""
from typing import Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.container import ContainerProxy

from app.core.config import settings


class AzureClients:
    """Manages Azure service clients"""
    
    def __init__(self):
        self._search_client: Optional[SearchClient] = None
        self._blob_client: Optional[BlobServiceClient] = None
        self._cosmos_client: Optional[CosmosClient] = None
        self._cosmos_database: Optional[DatabaseProxy] = None
        self._documents_container: Optional[ContainerProxy] = None
        self._conversations_container: Optional[ContainerProxy] = None
    
    @property
    def search_client(self) -> Optional[SearchClient]:
        """Get Azure AI Search client"""
        if self._search_client is None and settings.azure_search_endpoint and settings.azure_search_api_key:
            self._search_client = SearchClient(
                endpoint=settings.azure_search_endpoint,
                index_name=settings.azure_search_index_name,
                credential=AzureKeyCredential(settings.azure_search_api_key)
            )
        return self._search_client
    
    @property
    def blob_client(self) -> Optional[BlobServiceClient]:
        """Get Azure Blob Storage client"""
        if self._blob_client is None:
            if settings.azure_storage_connection_string:
                self._blob_client = BlobServiceClient.from_connection_string(
                    settings.azure_storage_connection_string
                )
            elif settings.azure_storage_account_name and settings.azure_storage_account_key:
                account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
                self._blob_client = BlobServiceClient(
                    account_url=account_url,
                    credential=AzureKeyCredential(settings.azure_storage_account_key)
                )
        return self._blob_client
    
    @property
    def cosmos_client(self) -> Optional[CosmosClient]:
        """Get Azure Cosmos DB client"""
        if self._cosmos_client is None and settings.azure_cosmos_endpoint and settings.azure_cosmos_key:
            self._cosmos_client = CosmosClient(
                url=settings.azure_cosmos_endpoint,
                credential=settings.azure_cosmos_key
            )
        return self._cosmos_client
    
    @property
    def cosmos_database(self) -> Optional[DatabaseProxy]:
        """Get Cosmos DB database"""
        if self._cosmos_database is None and self.cosmos_client:
            self._cosmos_database = self.cosmos_client.get_database_client(
                settings.azure_cosmos_database_name
            )
        return self._cosmos_database
    
    @property
    def documents_container(self) -> Optional[ContainerProxy]:
        """Get Cosmos DB documents container"""
        if self._documents_container is None and self.cosmos_database:
            self._documents_container = self.cosmos_database.get_container_client(
                settings.azure_cosmos_container_documents
            )
        return self._documents_container
    
    @property
    def conversations_container(self) -> Optional[ContainerProxy]:
        """Get Cosmos DB conversations container"""
        if self._conversations_container is None and self.cosmos_database:
            self._conversations_container = self.cosmos_database.get_container_client(
                settings.azure_cosmos_container_conversations
            )
        return self._conversations_container
    
    def is_azure_configured(self) -> bool:
        """Check if Azure services are configured"""
        return (
            (settings.azure_search_endpoint is not None) or
            (settings.azure_storage_connection_string is not None) or
            (settings.azure_cosmos_endpoint is not None)
        )


# Global Azure clients instance
azure_clients = AzureClients()

