"""
Build and persist FAISS index for chatbot retrieval.

Pipeline:
1. Build resume knowledge (PostgreSQL)
2. Fetch GitHub README knowledge
3. Normalize into documents
4. Embed using SentenceTransformers
5. Store FAISS index + metadata locally
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict
import numpy as np
import logging

from chatbot.knowledge.resume_builder import build_resume_knowledge_base
from chatbot.knowledge.github_ingestor import fetch_github_knowledge
from chatbot.embeddings.embedder import Embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# CONFIG
# ==========================

INDEX_DIR = Path("chatbot/embeddings/index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

FAISS_INDEX_PATH = INDEX_DIR / "resume_faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


# ==========================
# INTERNAL HELPERS
# ==========================

def _build_documents(user_id: str) -> List[Dict]:
    documents: List[Dict] = []

    resume_chunks = build_resume_knowledge_base(user_id)
    for i, chunk in enumerate(resume_chunks):
        chunk["metadata"]["doc_id"] = f"resume_{i}"
        documents.append(chunk)

    github_chunks = fetch_github_knowledge(user_id)
    for i, text in enumerate(github_chunks):
        documents.append({
            "text": text,
            "metadata": {
                "source": "github",
                "section": "github",
                "doc_id": f"github_{i}",
            }
        })

    return documents


# ==========================
# PUBLIC ENTRY POINT
# ==========================

def build_faiss_index(user_id: str) -> None:
    """
    Build and persist FAISS index for the given user.
    """

    logger.info("🔹 Building documents...")
    documents = _build_documents(user_id)

    if not documents:
        raise RuntimeError("No documents found to index.")

    logger.info(f"🔹 Total documents: {len(documents)}")

    logger.info("🔹 Embedding documents...")
    embedder = Embedder()
    embedded = embedder.embed(documents)

    vectors = embedded["vectors"]
    metadatas = embedded["metadatas"]
    texts = embedded["texts"]

    logger.info("🔹 Creating FAISS index...")

    # 🔥 LAZY IMPORT (CRITICAL FIX)
    import faiss

    if vectors.shape[0] == 0:
        raise RuntimeError("No vectors generated for FAISS index.")

    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(vectors)

    logger.info(f"🔹 FAISS index size: {index.ntotal}")

    logger.info("🔹 Persisting index and metadata...")
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(
            {
                "texts": texts,
                "metadatas": metadatas,
                "embedding_model": "all-MiniLM-L6-v2",
                "dimension": EMBEDDING_DIM,
                "similarity": "cosine",
            },
            f
        )

    logger.info("✅ FAISS index built successfully.")
    logger.info(f"📁 Index: {FAISS_INDEX_PATH}")
    logger.info(f"📁 Metadata: {METADATA_PATH}")


# ==========================
# CLI ENTRY
# ==========================

if __name__ == "__main__":
    USER_ID = os.getenv(
        "RESUME_USER_ID",
        "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"
    )

    build_faiss_index(USER_ID)