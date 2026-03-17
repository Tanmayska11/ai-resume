# chatbot/retrieval/retriever.py

"""
FAISS-based retriever for resume chatbot.

Responsibilities:
1. Load FAISS index and metadata (lazily)
2. Embed user query
3. Retrieve top-k relevant resume/GitHub chunks
4. Apply light intent-aware filtering
"""

import faiss
import pickle
from pathlib import Path
from typing import List, Dict

from chatbot.embeddings.embedder import Embedder


# ==========================
# CONFIG
# ==========================

INDEX_DIR = Path("chatbot/embeddings/index")
FAISS_INDEX_PATH = INDEX_DIR / "resume_faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"

TOP_K_DEFAULT = 8
MIN_SCORE_THRESHOLD = 0.15  # cosine similarity safeguard


# ==========================
# RETRIEVER
# ==========================

class ResumeRetriever:
    def __init__(self):
        self.index = None
        self.texts: List[str] = []
        self.metadatas: List[Dict] = []
        self.embedder = None
        if self.embedder is None:
            print("🔥 Loading embedder...")
            self.embedder = Embedder()




    # ----------------------------
    # Lazy load index
    # ----------------------------
    def _ensure_loaded(self) -> None:
        if self.index is not None:
            return

        if not FAISS_INDEX_PATH.exists():
            raise FileNotFoundError(
                "FAISS index not found. Run build_index.py first."
            )

        if not METADATA_PATH.exists():
            raise FileNotFoundError(
                "Metadata not found. Run build_index.py first."
            )

        self.index = faiss.read_index(str(FAISS_INDEX_PATH))

        with open(METADATA_PATH, "rb") as f:
            data = pickle.load(f)

        self.texts = data["texts"]
        self.metadatas = data["metadatas"]

    # ----------------------------
    # Intent inference (lightweight)
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
    # Main retrieval
    # ----------------------------
    def retrieve(self, query: str, top_k: int = TOP_K_DEFAULT) -> List[Dict]:
        if not query.strip():
            return []

        self._ensure_loaded()

        # 1️⃣ Embed query
        embedded = self.embedder.embed([
            {"text": query, "metadata": {"source": "query"}}
        ])
        query_embedding = embedded["vectors"]

        # 2️⃣ Broad FAISS retrieval
        raw_k = max(top_k * 3, 12)
        scores, indices = self.index.search(query_embedding, raw_k)

        # 3️⃣ Infer intent
        intent = self._infer_intent(query)

        #education filter
        edu_filter = None
        q = query.lower()

        if "master" in q:
            edu_filter = "master"
        elif "engineering" in q or "bachelor" in q:
            edu_filter = "bachelor"


        # ============================
        # PROFILE → bypass FAISS
        # ============================
        if intent == "profile":
            results = []
            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") == "profile":
                    results.append({
                        "text": text,
                        "score": 1.0,
                        "source": meta.get("source", "profile"),
                        "section": "profile",
                    })
            return results[:top_k]

        # ============================
        # EXPERIENCE TYPE FILTER
        # ============================
        exp_filter = None
        q = query.lower()
        if "professional" in q:
            exp_filter = "professional"
        elif "experimental" in q:
            exp_filter = "experimental"

        # ============================
        # EXPERIENCE → role-level retrieval (CORRECT PLACE)
        # ============================
        if intent == "experience":
            matched_role_ids = set()

            # Step 1: identify relevant role_ids via FAISS
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

            # Step 2: expand to ALL chunks of those roles
            results = []
            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") != "experience":
                    continue

                if exp_filter and meta.get("experience_type") != exp_filter:
                    continue

                if meta.get("role_id") in matched_role_ids:
                    results.append({
                        "text": text,
                        "score": 1.0,
                        "source": meta.get("source", "experience"),
                        "section": "experience",
                        "role_id": meta.get("role_id"),
                        "field": meta.get("field"),
                        "experience_type": meta.get("experience_type"),
                    })

            return results
        
        # ============================
        # PROJECTS → project-level retrieval
        # ============================
        if intent == "projects":
            matched_project_ids = set()

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or score < MIN_SCORE_THRESHOLD:
                    continue

                meta = self.metadatas[idx]
                if meta.get("section") != "projects":
                    continue

                pid = meta.get("project_id")
                if pid:
                    matched_project_ids.add(pid)

            results = []
            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") != "projects":
                    continue

                if meta.get("project_id") in matched_project_ids:
                    results.append({
                        "text": text,
                        "score": 1.0,
                        "source": "projects",
                        "section": "projects",
                        "project_id": meta.get("project_id"),
                        "field": meta.get("field"),
                        "url": meta.get("url"),
                    })

            return results
        

        # ============================
        # CERTIFICATIONS → cert-level retrieval
        # ============================
        if intent == "certifications":
            matched_cert_ids = set()

            # Step 1: find relevant certification_ids
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or score < MIN_SCORE_THRESHOLD:
                    continue

                meta = self.metadatas[idx]
                if meta.get("section") != "certifications":
                    continue

                cid = meta.get("certification_id")
                if cid:
                    matched_cert_ids.add(cid)

            # Step 2: expand full certification blocks
            results = []
            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") != "certifications":
                    continue

                if meta.get("certification_id") in matched_cert_ids:
                    results.append({
                        "text": text,
                        "score": 1.0,
                        "source": "certifications",
                        "section": "certifications",
                        "certification_id": meta.get("certification_id"),
                        "field": meta.get("field"),
                        "url": meta.get("url"),
                    })

            return results

        


        
        # ============================
        # EDUCATION → degree-level retrieval
        # ============================
        if intent == "education":
            matched_edu_ids = set()

            # Step 1: find matching education_ids
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or score < MIN_SCORE_THRESHOLD:
                    continue

                meta = self.metadatas[idx]
                if meta.get("section") != "education":
                    continue

                degree = meta.get("degree", "")
                if edu_filter and edu_filter not in degree:
                    continue

                eid = meta.get("education_id")
                if eid:
                    matched_edu_ids.add(eid)

            # Step 2: expand full education blocks
            results = []
            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") != "education":
                    continue

                degree = meta.get("degree", "")
                if edu_filter and edu_filter not in degree:
                    continue

                if meta.get("education_id") in matched_edu_ids:
                    results.append({
                        "text": text,
                        "score": 1.0,
                        "source": "education",
                        "section": "education",
                        "education_id": meta.get("education_id"),
                        "field": meta.get("field"),
                    })

            return results
        

        # ============================
        # SKILLS → category-level retrieval
        # ============================
        if intent == "skills":
            results = []

            for text, meta in zip(self.texts, self.metadatas):
                if meta.get("section") != "skills":
                    continue

                results.append({
                    "text": text,
                    "score": 1.0,
                    "source": "skills",
                    "section": "skills",
                    "category": meta.get("category"),
                    "field": meta.get("field"),
                })

            return results
        

        # ============================
        # Languages
        # ============================
        
        if intent == "languages":
            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": "languages",
                    "section": "languages",
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "languages"
            ]


        # ============================
        # EXTRACURRICULAR ACTIVITIES
        # ============================
        if intent == "extracurricular_activities":
            return [
                {
                    "text": text,
                    "score": 1.0,
                    "source": "extracurricular_activities",
                    "section": "extracurricular_activities",
                }
                for text, meta in zip(self.texts, self.metadatas)
                if meta.get("section") == "extracurricular_activities"
            ]

        return results


        




# ==========================
# SIMPLE HELPER (cached)
# ==========================

_RETRIEVER_SINGLETON: ResumeRetriever | None = None


def retrieve_context(query: str, top_k: int = TOP_K_DEFAULT) -> str:
    """
    Lightweight helper for quick context retrieval.
    """

    global _RETRIEVER_SINGLETON
    if _RETRIEVER_SINGLETON is None:
        _RETRIEVER_SINGLETON = ResumeRetriever()

    results = _RETRIEVER_SINGLETON.retrieve(query, top_k=top_k)

    if not results:
        return ""

    return "\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}"
        for r in results
    )
