# syntaxmatrix/smiv.py

import uuid
import numpy as np
from typing import List, Dict, Optional

class SMIV:
    """SyntaxMatrix In-memory Vectorstore"""
    def __init__(self, dim: int):
        self.dim = dim
        self.vectors = np.zeros((0, dim), dtype=np.float32)
        self.metadatas: List[Dict] = []
        self.ids: List[str] = []

    def add(
        self,
        vector: List[float],
        metadata: Dict,
        id: Optional[str] = None
    ) -> str:
        v = np.array(vector, dtype=np.float32)
        # stack into our 2D array
        self.vectors = np.vstack([self.vectors, v])
        rec_id = id or str(uuid.uuid4())
        self.ids.append(rec_id)
        self.metadatas.append(metadata)
        return rec_id

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        q = np.array(query_vector, dtype=np.float32)
        q /= np.linalg.norm(q)
        # normalize stored
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        vecs_normed = self.vectors / norms
        # cosine scores
        scores = vecs_normed.dot(q)
        # top-k
        idxs = np.argsort(scores)[-top_k:][::-1]
        return [
            {
                "id": self.ids[i], 
                "score": float(scores[i]), 
                "metadata": self.metadatas[i]}
            for i in idxs
        ]
