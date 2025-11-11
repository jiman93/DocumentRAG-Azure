"""
Storage service - handles Azure Blob Storage and Cosmos DB operations
Falls back to local SQLite storage when Azure is not configured
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError

from app.core.config import settings
from app.core.azure_clients import azure_clients
from app.models.document import DocumentMetadata, DocumentStatus
from app.utils.file_utils import sanitize_filename
from app.services.local_metadata_store import LocalMetadataStore


class StorageService:
    """Handles document storage in Azure Blob and Cosmos DB with local fallback"""

    def __init__(self):
        self.blob_client = azure_clients.blob_client
        self.documents_container = azure_clients.documents_container
        self.conversations_container = azure_clients.conversations_container

        # Use local storage as fallback if Cosmos DB is not configured
        self.use_local_storage = self.documents_container is None
        if self.use_local_storage:
            self.local_store = LocalMetadataStore()
        else:
            self.local_store = None

    def upload_document_to_blob(
        self,
        file_path: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        preferred_filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Upload document to Azure Blob Storage

        Args:
            file_path: Local file path
            document_id: Unique document identifier
            metadata: Optional blob metadata

        Returns:
            Blob URL if successful, None otherwise
        """
        if not self.blob_client:
            return None

        try:
            # Get container client
            container_client = self.blob_client.get_container_client(
                settings.azure_storage_container_name
            )

            # Create container if it doesn't exist
            if not container_client.exists():
                container_client.create_container()

            base_name = preferred_filename or os.path.basename(file_path)
            filename = sanitize_filename(base_name)
            blob_name = f"{document_id}/{filename}"

            # Upload file
            blob_client = container_client.get_blob_client(blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    metadata=metadata or {},
                )

            return blob_client.url
        except AzureError as e:
            print(f"Error uploading to blob storage: {e}")
            return None

    def download_document_from_blob(
        self,
        document_id: str,
        local_path: str,
    ) -> bool:
        """
        Download document from Azure Blob Storage

        Args:
            document_id: Document identifier
            local_path: Local path to save file

        Returns:
            True if successful
        """
        if not self.blob_client:
            return False

        try:
            container_client = self.blob_client.get_container_client(
                settings.azure_storage_container_name
            )

            # List blobs with prefix
            blobs = container_client.list_blobs(name_starts_with=document_id)
            blob_list = list(blobs)

            if not blob_list:
                return False

            # Download first blob (assuming one file per document)
            blob_client = container_client.get_blob_client(blob_list[0].name)
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            return True
        except AzureError as e:
            print(f"Error downloading from blob storage: {e}")
            return False

    def delete_document_from_blob(self, document_id: str) -> bool:
        """
        Delete document from Azure Blob Storage

        Args:
            document_id: Document identifier

        Returns:
            True if successful
        """
        if not self.blob_client:
            return False

        try:
            container_client = self.blob_client.get_container_client(
                settings.azure_storage_container_name
            )

            # List and delete all blobs with prefix
            blobs = container_client.list_blobs(name_starts_with=document_id)
            for blob in blobs:
                blob_client = container_client.get_blob_client(blob.name)
                blob_client.delete_blob()

            return True
        except AzureError as e:
            print(f"Error deleting from blob storage: {e}")
            return False

    def save_document_metadata(
        self,
        document_metadata: DocumentMetadata,
    ) -> bool:
        """
        Save document metadata to Cosmos DB or local storage

        Args:
            document_metadata: Document metadata object

        Returns:
            True if successful
        """
        if self.use_local_storage:
            return self.local_store.save_document_metadata(document_metadata)

        if not self.documents_container:
            return False

        try:
            # Convert to dict
            doc_dict = document_metadata.model_dump(mode="json")
            doc_dict["id"] = document_metadata.document_id
            doc_dict["_partitionKey"] = document_metadata.document_id

            # Upsert document
            self.documents_container.upsert_item(doc_dict)
            return True
        except Exception as e:
            print(f"Error saving document metadata: {e}")
            return False

    def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        """
        Get document metadata from Cosmos DB or local storage

        Args:
            document_id: Document identifier

        Returns:
            DocumentMetadata if found, None otherwise
        """
        if self.use_local_storage:
            return self.local_store.get_document_metadata(document_id)

        if not self.documents_container:
            return None

        try:
            item = self.documents_container.read_item(
                item=document_id,
                partition_key=document_id,
            )

            # Remove Cosmos DB internal fields
            item.pop("_rid", None)
            item.pop("_self", None)
            item.pop("_etag", None)
            item.pop("_attachments", None)
            item.pop("_ts", None)
            item.pop("_partitionKey", None)

            return DocumentMetadata(**item)
        except Exception as e:
            print(f"Error getting document metadata: {e}")
            return None

    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DocumentMetadata]:
        """
        List all documents from Cosmos DB or local storage

        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of DocumentMetadata objects
        """
        if self.use_local_storage:
            return self.local_store.list_documents(limit=limit, offset=offset)

        if not self.documents_container:
            return []

        try:
            query = "SELECT * FROM c ORDER BY c.upload_time DESC OFFSET @offset LIMIT @limit"
            parameters = [
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit},
            ]

            items = self.documents_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )

            documents = []
            for item in items:
                # Remove Cosmos DB internal fields
                item.pop("_rid", None)
                item.pop("_self", None)
                item.pop("_etag", None)
                item.pop("_attachments", None)
                item.pop("_ts", None)
                item.pop("_partitionKey", None)

                documents.append(DocumentMetadata(**item))

            return documents
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def delete_document_metadata(self, document_id: str) -> bool:
        """
        Delete document metadata from Cosmos DB or local storage

        Args:
            document_id: Document identifier

        Returns:
            True if successful
        """
        if self.use_local_storage:
            return self.local_store.delete_document_metadata(document_id)

        if not self.documents_container:
            return False

        try:
            self.documents_container.delete_item(
                item=document_id,
                partition_key=document_id,
            )
            return True
        except Exception as e:
            print(f"Error deleting document metadata: {e}")
            return False

    def save_conversation(
        self,
        conversation_id: str,
        conversation_data: Dict[str, Any],
    ) -> bool:
        """
        Save conversation to Cosmos DB or local storage

        Args:
            conversation_id: Conversation identifier
            conversation_data: Conversation data

        Returns:
            True if successful
        """
        if self.use_local_storage:
            return self.local_store.save_conversation(
                conversation_id, conversation_data
            )

        if not self.conversations_container:
            return False

        try:
            conversation_data["id"] = conversation_id
            conversation_data["_partitionKey"] = conversation_id
            self.conversations_container.upsert_item(conversation_data)
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation from Cosmos DB or local storage

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation data if found, None otherwise
        """
        if self.use_local_storage:
            return self.local_store.get_conversation(conversation_id)

        if not self.conversations_container:
            return None

        try:
            item = self.conversations_container.read_item(
                item=conversation_id,
                partition_key=conversation_id,
            )

            # Remove Cosmos DB internal fields
            item.pop("_rid", None)
            item.pop("_self", None)
            item.pop("_etag", None)
            item.pop("_attachments", None)
            item.pop("_ts", None)
            item.pop("_partitionKey", None)

            return item
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return None

    def append_conversation_messages(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
    ) -> bool:
        """Append messages to an existing conversation"""
        if self.use_local_storage:
            return self.local_store.append_conversation_messages(
                conversation_id, messages
            )

        if not self.conversations_container:
            return False

        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return False

            existing_messages = conversation.get("messages", [])
            existing_messages.extend(messages)

            conversation["messages"] = existing_messages
            conversation["message_count"] = len(existing_messages)
            conversation["updated_at"] = datetime.utcnow().isoformat()

            conversation["id"] = conversation_id
            conversation["_partitionKey"] = conversation_id
            self.conversations_container.upsert_item(conversation)
            return True
        except Exception as e:
            print(f"Error appending conversation messages: {e}")
            return False
