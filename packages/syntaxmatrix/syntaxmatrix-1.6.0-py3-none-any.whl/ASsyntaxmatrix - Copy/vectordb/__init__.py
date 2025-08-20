"""
syntaxmatrix.vectordb package export surface

Re-exports the public API so callers can simply:
    from syntaxmatrix.vectordb import get_vectordb, Document
"""

from .base import Document, SearchResult, VectorDatabase
from .registry import get_vectordb

__all__ = [
    "Document",
    "SearchResult",
    "VectorDatabase",
    "get_vectordb",
]
