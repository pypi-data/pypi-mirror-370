import os, sqlite3, uuid, json
import numpy as np
from typing import List, Optional, Union
from syntaxmatrix.project_root import detect_project_root


# Persist the SMX database under developers app’s data/ directory
_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "smpv.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# from .db import DB_PATH

def _init_smpv():
    """
    Create the embeddings table with an extra column for chunk_text.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            metadata TEXT,
            vector BLOB NOT NULL
        )
    """)

    # Create table for pdf_chunks for the admin files
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pdf_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            chunk_index INTEGER,
            chunk_text TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize on import
_init_smpv()


def insert_embedding(
    vector: Union[List[float], np.ndarray],
    id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> str:
    """
    Serialize and insert an embedding vector with optional metadata.
    Returns the assigned record id.
    """
    # Ensure numpy array
    arr = np.array(vector, dtype=np.float32)
    blob = arr.tobytes()

    rec_id = id or str(uuid.uuid4())
    meta_json = json.dumps(metadata) if metadata is not None else None

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO embeddings (id, metadata, vector) VALUES (?, ?, ?)",
        (rec_id, meta_json, blob)
    )
    conn.commit()
    conn.close()

    return rec_id


def query_embeddings(
    query_vector: Union[List[float], np.ndarray],
    top_k: int = 5
) -> List[dict]:
    """
    Retrieve the top_k most similar embeddings (cosine similarity) to the query_vector.
    Returns a list of dicts:
      {
        'id':         <str>,
        'score':      <float>,
        'metadata':   <dict>,    # should include 'file_name' and 'chunk_index'
        'chunk_text': <str>
      }
    """
    # Normalize query
    q_arr = np.array(query_vector, dtype=np.float32)
    norm = np.linalg.norm(q_arr)
    if norm == 0:
        raise ValueError("Query was not detected!")
    q_arr /= norm

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1) Load all stored embeddings
    cursor.execute("SELECT id, metadata, vector FROM embeddings")
    rows = cursor.fetchall()

    hits = []
    for rec_id, meta_json, blob in rows:
        # 2) Compute cosine similarity
        stored = np.frombuffer(blob, dtype=np.float32)
        stored_norm = np.linalg.norm(stored)
        if stored_norm == 0:
            continue
        score = float(np.dot(q_arr, stored / stored_norm))

        # 3) Decode metadata to find which chunk this is
        metadata = json.loads(meta_json) if meta_json else {}
        file_name  = metadata.get("file_name")
        chunk_index = metadata.get("chunk_index")

        # 4) Fetch the corresponding chunk_text
        chunk_text = ""
        if file_name is not None and chunk_index is not None:
            cursor.execute(
                "SELECT chunk_text FROM pdf_chunks WHERE file_name = ? AND chunk_index = ?",
                (file_name, chunk_index)
            )
            row = cursor.fetchone()
            if row:
                chunk_text = row[0]

        hits.append({
            "id":         rec_id,
            "score":      score,
            "metadata":   metadata,
            "chunk_text": chunk_text
        })

    conn.close()

    # 5) Return the top_k by descending score
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:top_k]


def delete_embeddings_for_file(file_name: str) -> None:
    """
    Remove all stored embeddings whose metadata.file_name == file_name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM embeddings WHERE json_extract(metadata, '$.file_name') = ?",
        (file_name,)
    )
    conn.commit()
    conn.close()


def add_pdf_chunk(file_name:str, chunk_index:int, chunk_text:str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO pdf_chunks (file_name, chunk_index, chunk_text) VALUES (?, ?, ?)",
        (file_name, chunk_index, chunk_text)
    )
    conn.commit()
    conn.close()


def get_pdf_chunks(file_name: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if file_name:
        cursor.execute(
            "SELECT chunk_index, chunk_text FROM pdf_chunks WHERE file_name = ? ORDER BY chunk_index",
            (file_name,)
        )
    else:
        cursor.execute(
            "SELECT file_name, chunk_index, chunk_text FROM pdf_chunks ORDER BY file_name, chunk_index"
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_pdf_chunk(chunk_id: int, new_chunk_text: str):
    """
    Updates the chunk_text of a PDF chunk record identified by chunk_id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pdf_chunks
        SET chunk_text = ?
        WHERE id = ?
    """, (new_chunk_text, chunk_id))
    conn.commit()
    conn.close()


def delete_pdf_chunks(file_name):
    """
    Delete all chunks associated with the given PDF file name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "DELETE FROM pdf_chunks WHERE file_name = ?",
        (file_name,)
    )
    conn.commit()
    conn.close()
