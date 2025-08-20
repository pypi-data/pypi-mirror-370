from __future__ import annotations

"""
syntaxmatrix.vectordb.adapters.sqlite_adapter

Light-weight, zero-dependency VectorDatabase backed by a local SQLite file.
* Embeddings are stored as raw float32 blobs (`BLOB` column).
* Metadata is JSON-encoded.
* Brute-force cosine similarity is done with NumPy – good enough for a few
  thousand vectors and keeps the package footprint tiny.
"""

import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import List, Sequence, Optional

import numpy as np

from syntaxmatrix.vectordb.base import (
    Document,
    SearchResult,
    VectorDatabase,
)

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_SQL_CREATE = """
CREATE TABLE IF NOT EXISTS documents (
    id        TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    metadata  TEXT
);
"""

_SQL_INSERT = "INSERT OR REPLACE INTO documents (id, embedding, metadata) VALUES (?, ?, ?)"
_SQL_DELETE = "DELETE FROM documents WHERE id IN ({placeholders})"
_SQL_SELECT = "SELECT id, embedding, metadata FROM documents WHERE id = ?"
_SQL_COUNT  = "SELECT COUNT(*) FROM documents"
_SQL_RESET  = "DELETE FROM documents"
_SQL_SELECT_ALL = "SELECT id, embedding, metadata FROM documents"

def _to_blob(vec: np.ndarray) -> bytes:
    """float32 ndarray -> bytes for SQLite."""
    return vec.astype(np.float32).tobytes()

def _from_blob(blob: bytes) -> np.ndarray:
    """bytes -> float32 ndarray."""
    return np.frombuffer(blob, dtype=np.float32)

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
    return float(np.dot(a, b) / denom)

# --------------------------------------------------------------------------- #
# Main adapter
# --------------------------------------------------------------------------- #

class SQLiteVectorDB(VectorDatabase):
    """Local file-based vector store."""

    _lock = threading.Lock()

    def __init__(self, db_path: str | Path = "system_vectors.sqlite") -> None:
        self.path = Path(db_path).expanduser().resolve()
        # Ensure directory
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # One connection per thread is safest with sqlite3
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.execute(_SQL_CREATE)
        self._conn.commit()

    # --------------------------------------------------- #
    # Required interface methods
    # --------------------------------------------------- #

    def add_documents(self, docs: Sequence[Document]) -> List[str]:
        rows = [(d.id, _to_blob(d.embedding), json.dumps(d.metadata or {})) for d in docs]
        with self._lock, self._conn:
            self._conn.executemany(_SQL_INSERT, rows)
        return [d.id for d in docs]

    def similarity_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
        metric: str = "cosine",
    ) -> List[SearchResult]:
        if metric.lower() != "cosine":
            raise ValueError("SQLiteVectorDB currently supports only cosine similarity.")

        # Brute-force: pull every vector into RAM (fine for <50k)
        with self._conn:
            rows = self._conn.execute(_SQL_SELECT_ALL).fetchall()

        scores: List[SearchResult] = []
        for _id, blob, meta_json in rows:
            vec = _from_blob(blob)
            score = _cosine(query_embedding, vec)
            meta  = json.loads(meta_json) if meta_json else {}
            scores.append(
                SearchResult(
                    document=Document(id=_id, embedding=vec, metadata=meta),
                    score=score,
                )
            )

        return sorted(scores, key=lambda r: r.score, reverse=True)[: top_k]

    # Simple alias so callers can use either name
    search = similarity_search

    def delete_documents(self, ids: Sequence[str]) -> int:
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        with self._lock, self._conn:
            cur = self._conn.execute(_SQL_DELETE.format(placeholders=placeholders), list(ids))
        return cur.rowcount

    def update_document(
        self,
        id: str,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        # Fetch existing
        doc = self.get_document(id)
        if doc is None:
            raise KeyError(f"Document {id!r} not found")

        new_emb = embedding if embedding is not None else doc.embedding
        new_meta = {**(doc.metadata or {}), **(metadata or {})}

        with self._lock, self._conn:
            self._conn.execute(
                _SQL_INSERT,
                (id, _to_blob(new_emb), json.dumps(new_meta)),
            )

    def get_document(self, id: str) -> Optional[Document]:
        with self._conn:
            row = self._conn.execute(_SQL_SELECT, (id,)).fetchone()
        if not row:
            return None
        _id, blob, meta_json = row
        return Document(id=_id, embedding=_from_blob(blob), metadata=json.loads(meta_json or "{}"))

    def count(self) -> int:
        with self._conn:
            (n,) = self._conn.execute(_SQL_COUNT).fetchone()
        return int(n)

    def reset(self) -> None:
        with self._lock, self._conn:
            self._conn.execute(_SQL_RESET)
            self._conn.commit()

# --- NEW: satisfy VectorDatabase.delete(ids: list[str]) -----------------
    def delete(self, ids: List[str]) -> None:            # ✅ now matches the ABC
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        stmt = _SQL_DELETE.format(placeholders=placeholders)
        with self._lock, self._conn:
            self._conn.execute(stmt, ids)