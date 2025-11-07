"""
Text processing utilities
"""
import re
from typing import List, Optional


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text"""
    # Simple sentence splitting (can be improved with NLP libraries)
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def count_tokens_approx(text: str) -> int:
    """
    Approximate token count (rough estimate: 1 token ≈ 4 characters)
    For accurate counts, use tiktoken library
    """
    return len(text) // 4


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    For production, consider using NLP libraries like spaCy or NLTK
    """
    # Remove common stop words (simplified list)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Extract words (alphanumeric, at least 3 characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and get unique words
    keywords = [w for w in words if w not in stop_words]
    
    # Count frequency and return top keywords
    from collections import Counter
    word_freq = Counter(keywords)
    return [word for word, _ in word_freq.most_common(max_keywords)]


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace characters"""
    # Replace various whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """Remove special characters, optionally keep punctuation"""
    if keep_punctuation:
        # Keep alphanumeric, spaces, and common punctuation
        return re.sub(r'[^a-zA-Z0-9\s.,!?;:\-()\[\]{}"\']', '', text)
    else:
        # Keep only alphanumeric and spaces
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs"""
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]

