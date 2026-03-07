# chatbot/embeddings/embedder.py

"""
Embedding layer for Resume + GitHub knowledge.

Responsibilities:
- Convert text chunks into dense vectors
- Preserve metadata for later retrieval
- Stay completely independent of FAISS, DB, and LLMs
"""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


class Embedder:
    """
    Thin wrapper around SentenceTransformer.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Embed text documents into vectors.

        Parameters
        ----------
        documents : List[Dict]
            Each document must contain:
              - "text": str
              - "metadata": dict (optional)

        Returns
        -------
        Dict containing:
          - vectors   : np.ndarray (float32)
          - texts     : List[str]
          - metadatas : List[dict]
        """

        if not documents:
            return {
                "vectors": np.empty((0, 384), dtype="float32"),
                "texts": [],
                "metadatas": [],
            }

        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return {
            "vectors": np.asarray(vectors, dtype="float32"),
            "texts": texts,
            "metadatas": metadatas,
        }
