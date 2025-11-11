"""
Local metadata storage using SQLite as fallback when Cosmos DB is not configured
"""

import os
import sqlite3
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.models.document import DocumentMetadata, DocumentStatus


class LocalMetadataStore:
    """Local SQLite-based metadata storage"""

    def __init__(self, db_path: str = "./metadata.db"):
        """Initialize local metadata store"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database and create tables"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create documents table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    upload_time TEXT NOT NULL,
                    indexed_at TEXT,
                    status TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0,
                    blob_url TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Create conversations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    messages TEXT
                )
            """
            )

            # Create indexes
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_upload_time 
                ON documents(upload_time DESC)
            """
            )

            conn.commit()

    def save_document_metadata(self, document_metadata: DocumentMetadata) -> bool:
        """Save document metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO documents 
                    (document_id, filename, file_type, file_size, upload_time, 
                     indexed_at, status, chunk_count, blob_url, error_message, 
                     metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        document_metadata.document_id,
                        document_metadata.filename,
                        document_metadata.file_type,
                        document_metadata.file_size,
                        (
                            document_metadata.upload_time.isoformat()
                            if isinstance(document_metadata.upload_time, datetime)
                            else str(document_metadata.upload_time)
                        ),
                        (
                            document_metadata.indexed_at.isoformat()
                            if document_metadata.indexed_at
                            and isinstance(document_metadata.indexed_at, datetime)
                            else (
                                str(document_metadata.indexed_at)
                                if document_metadata.indexed_at
                                else None
                            )
                        ),
                        document_metadata.status.value,
                        document_metadata.chunk_count,
                        document_metadata.blob_url,
                        document_metadata.error_message,
                        json.dumps(document_metadata.metadata),
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving document metadata to local store: {e}")
            return False

    def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM documents WHERE document_id = ?
                """,
                    (document_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                return self._row_to_document_metadata(row)
        except Exception as e:
            print(f"Error getting document metadata from local store: {e}")
            return None

    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DocumentMetadata]:
        """List all documents"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM documents 
                    ORDER BY upload_time DESC 
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

                rows = cursor.fetchall()
                return [self._row_to_document_metadata(row) for row in rows]
        except Exception as e:
            print(f"Error listing documents from local store: {e}")
            return []

    def delete_document_metadata(self, document_id: str) -> bool:
        """Delete document metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM documents WHERE document_id = ?", (document_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting document metadata from local store: {e}")
            return False

    def save_conversation(
        self,
        conversation_id: str,
        conversation_data: dict,
    ) -> bool:
        """Save conversation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, title, created_at, updated_at, 
                     message_count, metadata, messages)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        conversation_id,
                        conversation_data.get("title"),
                        conversation_data.get("created_at"),
                        conversation_data.get("updated_at"),
                        conversation_data.get("message_count", 0),
                        json.dumps(conversation_data.get("metadata", {})),
                        json.dumps(conversation_data.get("messages", [])),
                    ),
                )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving conversation to local store: {e}")
            return False

    def append_conversation_messages(
        self, conversation_id: str, messages: List[dict], metadata: Optional[dict] = None
    ) -> bool:
        """Append messages to an existing conversation"""
        if not messages:
            return True

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT messages FROM conversations WHERE conversation_id = ?",
                    (conversation_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return False

                existing_messages = json.loads(row["messages"] or "[]")
                existing_messages.extend(messages)

                updated_at = datetime.utcnow().isoformat()
                merged_metadata = json.loads(row["metadata"] or "{}")
                if metadata:
                    merged_metadata.update(metadata)
                cursor.execute(
                    """
                    UPDATE conversations
                    SET messages = ?, message_count = ?, updated_at = ?, metadata = ?
                    WHERE conversation_id = ?
                    """,
                    (
                        json.dumps(existing_messages),
                        len(existing_messages),
                        updated_at,
                        json.dumps(merged_metadata),
                        conversation_id,
                    ),
                )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error appending messages to conversation: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get conversation by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM conversations WHERE conversation_id = ?
                """,
                    (conversation_id,),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                return {
                    "conversation_id": row["conversation_id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["message_count"],
                    "metadata": json.loads(row["metadata"] or "{}"),
                    "messages": json.loads(row["messages"] or "[]"),
                }
        except Exception as e:
            print(f"Error getting conversation from local store: {e}")
            return None

    def list_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> List[dict]:
        """List conversations with metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM conversations
                    ORDER BY datetime(updated_at) DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

                rows = cursor.fetchall()
                conversations: List[dict] = []
                for row in rows:
                    conversations.append(
                        {
                            "conversation_id": row["conversation_id"],
                            "title": row["title"],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                            "message_count": row["message_count"],
                            "metadata": json.loads(row["metadata"] or "{}"),
                            "messages": json.loads(row["messages"] or "[]"),
                        }
                    )
                return conversations
        except Exception as e:
            print(f"Error listing conversations from local store: {e}")
            return []

    def _row_to_document_metadata(self, row: sqlite3.Row) -> DocumentMetadata:
        """Convert database row to DocumentMetadata object"""
        return DocumentMetadata(
            document_id=row["document_id"],
            filename=row["filename"],
            file_type=row["file_type"],
            file_size=row["file_size"],
            upload_time=datetime.fromisoformat(row["upload_time"]),
            indexed_at=(
                datetime.fromisoformat(row["indexed_at"]) if row["indexed_at"] else None
            ),
            status=DocumentStatus(row["status"]),
            chunk_count=row["chunk_count"],
            blob_url=row["blob_url"],
            error_message=row["error_message"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
