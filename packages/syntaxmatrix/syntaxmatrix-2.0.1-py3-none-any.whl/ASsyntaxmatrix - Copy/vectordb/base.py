from __future__ import annotations

"""syntaxmatrix.vectordb.base

Abstract interface for pluggable vector‑database adapters.
Each concrete adapter (e.g. SQLite, Postgres/pgvector, Milvus) must implement
this contract so that SyntaxMatrix can treat them interchangeably.
"""

import abc
import typing
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Type aliases & simple value objects
# ---------------------------------------------------------------------------

Embedding = list[float]
"""Raw embedding vector (already normalised if the backend expects it)."""


@dataclass
class Document:
    """Minimal representation of a chunk/text record stored alongside a vector."""

    id: str
    text: str
    embedding: Embedding | None = None  # May be None if backend computes/stores separately
    metadata: dict[str, typing.Any] | None = None

    def __post_init__(self) -> None:
        # Normalise metadata to empty dict for ease of use
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """Return object for similarity searches."""

    document: Document
    score: float  # Higher == more similar (cosine/IP) unless backend documents otherwise


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class VectorDatabase(abc.ABC):
    """Abstract interface every vector‑database adapter must satisfy.

    All concrete subclasses must implement each abstractmethod; mixins or
    defaults can be placed in *utils.py* if helpful, but *do not* rely on them
    here—keep this contract minimal and framework‑agnostic.
    """

    #: Name of the distance metric employed by the backend ("cosine", "l2", "ip", ...).
    distance_metric: str = "cosine"

    # ---------------------------------------------------------------------
    # CRUD API
    # ---------------------------------------------------------------------

    @abc.abstractmethod
    def add_documents(self, documents: list[Document]) -> None:
        """Insert or upsert a batch of documents.
        
        Implementations should either raise on duplicate *id* (and document that
        behaviour) or silently overwrite; whichever route you take, stay
        consistent across adapters.
        """

    @abc.abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Remove the vectors + metadata associated with *ids*."""

    @abc.abstractmethod
    def update_document(self, document: Document) -> None:
        """Replace an existing document (matched on *id*) with *document*."""

    @abc.abstractmethod
    def get_document(self, id: str) -> Document | None:
        """Fetch a single document by primary key; returns *None* if absent."""

    # ---------------------------------------------------------------------
    # Vector similarity search
    # ---------------------------------------------------------------------

    @abc.abstractmethod
    def similarity_search(
        self,
        query_embedding: Embedding,
        top_k: int = 5,
        metadata_filter: dict[str, typing.Any] | None = None,
    ) -> list[SearchResult]:
        """Return top‑*k* ``SearchResult``s ordered by descending similarity."""

    # ---------------------------------------------------------------------
    # Introspection / maintenance
    # ---------------------------------------------------------------------

    @abc.abstractmethod
    def count(self) -> int:
        """Total number of stored documents."""

    @abc.abstractmethod
    def reset(self) -> None:
        """Drop all data and re‑initialise any indexes/tables."""


__all__ = [
    "Embedding",
    "Document",
    "SearchResult",
    "VectorDatabase",
]
