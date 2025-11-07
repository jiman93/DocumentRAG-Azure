"""
File handling utilities
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
import mimetypes


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    return os.path.splitext(filename)[1].lower()


def is_supported_file_type(filename: str) -> bool:
    """Check if file type is supported"""
    ext = get_file_extension(filename)
    supported = {".pdf", ".docx", ".txt", ".md"}
    return ext in supported


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)


def generate_document_id(file_path: str, content: Optional[bytes] = None) -> str:
    """Generate unique document ID from file path or content"""
    if content:
        return hashlib.md5(content).hexdigest()
    return hashlib.md5(file_path.encode()).hexdigest()[:16]


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """Generate unique chunk ID"""
    return f"{document_id}_chunk_{chunk_index}"


def get_mime_type(filename: str) -> str:
    """Get MIME type for file"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file path exists and is readable
    Returns: (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"File is not readable: {file_path}"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for storage"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def ensure_directory_exists(directory: str) -> None:
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

