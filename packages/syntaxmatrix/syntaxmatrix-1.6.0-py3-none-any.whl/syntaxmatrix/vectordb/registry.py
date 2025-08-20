from __future__ import annotations

"""syntaxmatrix.vectordb.adapters.sqlite_adapter

SQLite‑backed implementation of the VectorDatabase interface.
Stores embeddings locally in a tiny SQLite file, using NumPy for brute‑force
cosine similarity.  Suitable for prototypes and small (<50 k vectors) corpora.
"""

import json
import sqlite3
import threading
from pathlib import Path
from typing import List, Sequence, Optional

import numpy as np

from syntaxmatrix.vectordb.base import Document, SearchResult, VectorDatabase

# ---------------------------------------------------------------------------
# SQL helpers
# ---------------------------------------------------------------------------
_SQL_CREATE = """
CREATE TABLE IF NOT EXISTS documents (
    id        TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    metadata  TEXT
);
"""

_SQL_INSERT = "INSERT OR REPLACE INTO documents (id, embedding, metadata) VALUES (?, ?, ?)"
_SQL_DELETE = "DELETE FROM documents WHERE id IN ({ph})"
_SQL_SELECT = "SELECT id, embedding, metadata FROM documents WHERE id = ?"
_SQL_SELECT_ALL = "SELECT id, embedding, metadata FROM documents"
_SQL_COUNT  = "SELECT COUNT(*) FROM documents"
_SQL_RESET  = "DELETE FROM documents"


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _vec_to_blob(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def _blob_to_vec(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
    return float(np.dot(a, b) / denom)


# ---------------------------------------------------------------------------
# Adapter implementation
# ---------------------------------------------------------------------------

class SQLiteVectorDB(VectorDatabase):
    """Minimal VectorDatabase backed by SQLite."""

    _thread_lock = threading.Lock()

    def __init__(self, db_path: str | Path = "system_vectors.sqlite") -> None:
        self.path = Path(db_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.execute(_SQL_CREATE)
        self._conn.commit()

    # -------------------------------------------------------------------
    # Required interface methods
    # -------------------------------------------------------------------

    def add_documents(self, docs: Sequence[Document]) -> List[str]:
        rows = [
            (d.id, _vec_to_blob(d.embedding), json.dumps(d.metadata or {}))
            for d in docs
        ]
        with self._thread_lock, self._conn:
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

        with self._conn:
            rows = self._conn.execute(_SQL_SELECT_ALL).fetchall()

        scored: List[SearchResult] = []
        for _id, blob, meta_json in rows:
            vec = _blob_to_vec(blob)
            score = _cosine(query_embedding, vec)
            meta = json.loads(meta_json or "{}")
            scored.append(
                SearchResult(
                    document=Document(id=_id, embedding=vec, metadata=meta),
                    score=score,
                )
            )

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[: top_k]

    # alias
    search = similarity_search

    def delete_documents(self, ids: Sequence[str]) -> int:
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        stmt = _SQL_DELETE.format(ph=placeholders)
        with self._thread_lock, self._conn:
            cur = self._conn.execute(stmt, list(ids))
        return cur.rowcount

    # Provide the single‑id convenience alias expected by some client code
    def delete(self, id: str) -> None:  # type: ignore[override]
        self.delete_documents([id])

    def update_document(
        self,
        id: str,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        doc = self.get_document(id)
        if doc is None:
            raise KeyError(f"Document {id!r} not found")
        new_emb = embedding if embedding is not None else doc.embedding
        new_meta = {**(doc.metadata or {}), **(metadata or {})}
        with self._thread_lock, self._conn:
            self._conn.execute(
                _SQL_INSERT,
                (id, _vec_to_blob(new_emb), json.dumps(new_meta)),
            )

    def get_document(self, id: str) -> Optional[Document]:
        with self._conn:
            row = self._conn.execute(_SQL_SELECT, (id,)).fetchone()
        if not row:
            return None
        _id, blob, meta_json = row
        return Document(id=_id, embedding=_blob_to_vec(blob), metadata=json.loads(meta_json or "{}"))

    def count(self) -> int:
        with self._conn:
            (n,) = self._conn.execute(_SQL_COUNT).fetchone()
        return int(n)

    def reset(self) -> None:
        with self._thread_lock, self._conn:
            self._conn.execute(_SQL_RESET)
            self._conn.commit()
