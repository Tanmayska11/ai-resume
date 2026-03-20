# chatbot/embeddings/embedder.py





"""
Embedding layer using OpenAI API (lightweight, no torch).
"""

from typing import List, Dict, Any
import numpy as np
from openai import OpenAI

# 🔥 global client (cached)
_client = None

# 🔥 embedding model (fast + cheap)
EMBEDDING_MODEL = "text-embedding-3-small"


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


class Embedder:
    """
    OpenAI-based embedder (no local ML model).
    """

    def __init__(self):
        self.client = _get_client()

    def embed(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not documents:
            return {
                "vectors": np.empty((0, 1536), dtype="float32"),
                "texts": [],
                "metadatas": [],
            }

        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # 🔥 Call OpenAI embedding API
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )

        vectors = [item.embedding for item in response.data]

        return {
            "vectors": np.asarray(vectors, dtype="float32"),
            "texts": texts,
            "metadatas": metadatas,
        }












# """
# Embedding layer for Resume + GitHub knowledge.

# Responsibilities:
# - Convert text chunks into dense vectors
# - Preserve metadata for later retrieval
# - Stay completely independent of FAISS, DB, and LLMs
# """

# from typing import List, Dict, Any
# import numpy as np

# DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


# # 🔥 Global cache (IMPORTANT)
# _model = None


# def _get_model(model_name: str):
#     """
#     Lazy load SentenceTransformer model.
#     """
#     global _model

#     if _model is None:
#         print("⚡ Loading embedding model...")

#         # 🔥 lazy import
#         from sentence_transformers import SentenceTransformer

#         _model = SentenceTransformer(model_name)

#     return _model


# class Embedder:
#     """
#     Thin wrapper around SentenceTransformer.
#     """

#     def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
#         self.model_name = model_name

#     def embed(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         Embed text documents into vectors.
#         """

#         if not documents:
#             return {
#                 "vectors": np.empty((0, 384), dtype="float32"),
#                 "texts": [],
#                 "metadatas": [],
#             }

#         texts = [doc["text"] for doc in documents]
#         metadatas = [doc.get("metadata", {}) for doc in documents]

#         # 🔥 model loads only here
#         model = _get_model(self.model_name)

#         vectors = model.encode(
#             texts,
#             normalize_embeddings=True,
#             show_progress_bar=False,
#         )

#         return {
#             "vectors": np.asarray(vectors, dtype="float32"),
#             "texts": texts,
#             "metadatas": metadatas,
#         }