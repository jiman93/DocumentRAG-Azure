"""
Document processing service - handles loading and chunking
"""
import os
import warnings
import logging
from typing import List
from datetime import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)

from app.core.config import settings
from app.utils.file_utils import validate_file_path, get_file_extension

# Suppress pypdf warnings about malformed PDF objects (usually harmless)
warnings.filterwarnings("ignore", message=".*wrong pointing object.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*Ignoring wrong pointing object.*", category=UserWarning)

# Suppress pypdf logger warnings
pypdf_logger = logging.getLogger("pypdf._reader")
pypdf_logger.setLevel(logging.ERROR)


class DocumentProcessor:
    """Handles document loading and chunking"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load document based on file extension
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects with metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is unsupported
        """
        # Validate file path
        is_valid, error_msg = validate_file_path(file_path)
        if not is_valid:
            raise FileNotFoundError(error_msg)
        
        ext = get_file_extension(file_path)
        
        loaders = {
            ".pdf": PyPDFLoader,
            ".docx": Docx2txtLoader,
            ".txt": TextLoader,
            ".md": UnstructuredMarkdownLoader,
        }
        
        if ext not in loaders:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported formats: PDF, DOCX, TXT, MD"
            )
        
        # Load document
        loader = loaders[ext](file_path)
        documents = loader.load()
        
        # Add metadata
        filename = os.path.basename(file_path)
        for doc in documents:
            doc.metadata["source_file"] = filename
            doc.metadata["file_path"] = file_path
            doc.metadata["upload_time"] = datetime.now().isoformat()
            if "page" in doc.metadata:
                doc.metadata["page_number"] = doc.metadata["page"]
        
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks with overlap
        
        Args:
            documents: List of Document objects to chunk
            
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)
            
            # Preserve source information
            if "source_file" in chunk.metadata:
                chunk.metadata["document_name"] = chunk.metadata["source_file"]
            if "page_number" in chunk.metadata:
                chunk.metadata["page"] = chunk.metadata["page_number"]
        
        return chunks
    
    def process_document(self, file_path: str) -> List[Document]:
        """
        Complete processing pipeline: Load → Chunk
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of chunked Document objects
        """
        documents = self.load_document(file_path)
        chunks = self.chunk_documents(documents)
        return chunks

