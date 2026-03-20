# chatbot/retrieval/retriever.py

"""
FAISS-based retriever for resume chatbot.

Responsibilities:
1. Load FAISS index and metadata (lazily)
2. Embed user query
3. Retrieve top-k relevant resume/GitHub chunks
4. Apply light intent-aware filtering
"""

"""
FAISS-based retriever for resume chatbot.
"""

import faiss
import pickle
from pathlib import Path
from typing import List, Dict


# ==========================
# CONFIG
# ==========================

INDEX_DIR = Path("chatbot/embeddings/index")
FAISS_INDEX_PATH = INDEX_DIR / "resume_faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"

TOP_K_DEFAULT = 8
MIN_SCORE_THRESHOLD = 0.15


# ==========================
# RETRIEVER
# ==========================

class ResumeRetriever:
    def __init__(self):
        self.index = None
        self.texts: List[str] = []
        self.metadatas: List[Dict] = []

        # 🔥 lazy init
        self._embedder = None

    # ----------------------------
    # Lazy embedder
    # ----------------------------
    def _get_embedder(self):
        if self._embedder is None:
            from chatbot.embeddings.embedder import Embedder  # lazy import
            self._embedder = Embedder()
        return self._embedder

    # ----------------------------
    # Lazy load index
    # ----------------------------
    def _ensure_loaded(self) -> None:
        if self.index is not None:
            return

        if not FAISS_INDEX_PATH.exists():
            raise FileNotFoundError("FAISS index not found.")

        if not METADATA_PATH.exists():
            raise FileNotFoundError("Metadata not found.")

        self.index = faiss.read_index(str(FAISS_INDEX_PATH))

        with open(METADATA_PATH, "rb") as f:
            data = pickle.load(f)

        self.texts = data["texts"]
        self.metadatas = data["metadatas"]

    # ----------------------------
    # Intent inference (unchanged)
    # ----------------------------
    def _infer_intent(self, query: str) -> str:
        q = query.lower()

        if any(k in q for k in ["extracurricular", "activity", "activities", "volunteer", "interests", "charity", "sports"]):
            return "extracurricular_activities"

        if any(k in q for k in ["certification", "certifications", "certificate", "credential"]):
            return "certifications"

        if any(k in q for k in ["education", "degree", "university"]):
            return "education"

        if any(k in q for k in ["project", "projects", "github"]):
            return "projects"

        if any(k in q for k in ["skill", "skills", "technology", "tools"]):
            return "skills"

        if any(k in q for k in ["language", "languages", "spoken", "fluent"]):
            return "languages"

        if any(k in q for k in ["experience", "worked", "job", "role"]):
            return "experience"

        if any(s in q for s in ["who is", "tell me about", "profile", "summary"]):
            return "profile"

        return "general"

    # ----------------------------
    # Main retrieval (LOGIC UNCHANGED)
    # ----------------------------
    def retrieve(self, query: str, top_k: int = TOP_K_DEFAULT) -> List[Dict]:
        if not query.strip():
            return []

        self._ensure_loaded()

        # 🔥 lazy embedder usage
        embedder = self._get_embedder()

        embedded = embedder.embed([
            {"text": query, "metadata": {"source": "query"}}
        ])
        query_embedding = embedded["vectors"]

        raw_k = max(top_k * 3, 12)
        scores, indices = self.index.search(query_embedding, raw_k)

        intent = self._infer_intent(query)

        edu_filter = None
        q = query.lower()

        if "master" in q:
            edu_filter = "master"
        elif "engineering" in q or "bachelor" in q:
            edu_filter = "bachelor"

        # ============================
        # PROFILE
        # ============================
        if intent == "profile":
            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": meta.get("source", "profile"),
                    "section": "profile",
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "profile"
            ][:top_k]

        # ============================
        # EXPERIENCE
        # ============================
        exp_filter = None
        if "professional" in q:
            exp_filter = "professional"
        elif "experimental" in q:
            exp_filter = "experimental"

        if intent == "experience":
            matched_role_ids = set()

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or score < MIN_SCORE_THRESHOLD:
                    continue

                meta = self.metadatas[idx]
                if meta.get("section") != "experience":
                    continue

                if exp_filter and meta.get("experience_type") != exp_filter:
                    continue

                role_id = meta.get("role_id")
                if role_id:
                    matched_role_ids.add(role_id)

            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": meta.get("source", "experience"),
                    "section": "experience",
                    "role_id": meta.get("role_id"),
                    "field": meta.get("field"),
                    "experience_type": meta.get("experience_type"),
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "experience"
                and (not exp_filter or meta.get("experience_type") == exp_filter)
                and meta.get("role_id") in matched_role_ids
            ]

        # ============================
        # PROJECTS
        # ============================
        if intent == "projects":
            matched_ids = {
                self.metadatas[idx].get("project_id")
                for score, idx in zip(scores[0], indices[0])
                if idx >= 0 and score >= MIN_SCORE_THRESHOLD
                and self.metadatas[idx].get("section") == "projects"
            }

            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": "projects",
                    "section": "projects",
                    "project_id": meta.get("project_id"),
                    "field": meta.get("field"),
                    "url": meta.get("url"),
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "projects"
                and meta.get("project_id") in matched_ids
            ]

        # ============================
        # CERTIFICATIONS
        # ============================
        if intent == "certifications":
            matched_ids = {
                self.metadatas[idx].get("certification_id")
                for score, idx in zip(scores[0], indices[0])
                if idx >= 0 and score >= MIN_SCORE_THRESHOLD
                and self.metadatas[idx].get("section") == "certifications"
            }

            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": "certifications",
                    "section": "certifications",
                    "certification_id": meta.get("certification_id"),
                    "field": meta.get("field"),
                    "url": meta.get("url"),
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "certifications"
                and meta.get("certification_id") in matched_ids
            ]

        # ============================
        # EDUCATION
        # ============================
        if intent == "education":
            matched_ids = {
                self.metadatas[idx].get("education_id")
                for score, idx in zip(scores[0], indices[0])
                if idx >= 0 and score >= MIN_SCORE_THRESHOLD
                and self.metadatas[idx].get("section") == "education"
                and (not edu_filter or edu_filter in self.metadatas[idx].get("degree", ""))
            }

            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": "education",
                    "section": "education",
                    "education_id": meta.get("education_id"),
                    "field": meta.get("field"),
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "education"
                and meta.get("education_id") in matched_ids
            ]

        # ============================
        # SKILLS / LANG / ACTIVITIES
        # ============================
        if intent in ["skills", "languages", "extracurricular_activities"]:
            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": intent,
                    "section": intent,
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == intent
            ]

        return []
        

# ==========================
# SINGLETON
# ==========================

_RETRIEVER_SINGLETON = None


def retrieve_context(query: str, top_k: int = TOP_K_DEFAULT) -> str:
    global _RETRIEVER_SINGLETON

    if _RETRIEVER_SINGLETON is None:
        _RETRIEVER_SINGLETON = ResumeRetriever()

    results = _RETRIEVER_SINGLETON.retrieve(query, top_k=top_k)

    return "\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}"
        for r in results
    ) if results else ""