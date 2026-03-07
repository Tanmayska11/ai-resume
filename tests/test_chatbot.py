# # tests/test_chatbot.py

# from chatbot.knowledge.resume_builder import build_resume_knowledge_base

USER_ID = "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"


# def test_resume_builder_generates_chunks():
#     chunks = build_resume_knowledge_base(USER_ID)

#     # Basic sanity
#     assert isinstance(chunks, list)
#     assert len(chunks) >= 6

#     # Core sections must exist
#     assert any("PROFILE SUMMARY" in c for c in chunks)
#     assert any("EXPERIENCE" in c for c in chunks)
#     assert any("PROJECT" in c for c in chunks)
#     assert any("SKILLS" in c for c in chunks)
#     assert any("EDUCATION" in c for c in chunks)
#     assert any("CERTIFICATIONS" in c for c in chunks)
#     assert any("LANGUAGES" in c for c in chunks)


# def test_no_empty_chunks():
#     chunks = build_resume_knowledge_base(USER_ID)

#     for c in chunks:
#         assert c.strip() != ""
#         assert len(c) > 50  # prevents useless micro-chunks


# from chatbot.knowledge.github_ingestor import fetch_github_knowledge

# def test_github_ingestor_returns_list():
#     chunks = fetch_github_knowledge(USER_ID)
#     assert isinstance(chunks, list)

# def test_github_ingestor_handles_empty_gracefully():
#     chunks = fetch_github_knowledge(USER_ID)
#     if chunks:
#         assert all(len(c.strip()) > 0 for c in chunks)


# from chatbot.embeddings.embedder import Embedder

# def test_embedder_basic():
#     docs = [
#         {"text": "Built ETL pipelines using Python and PostgreSQL", "metadata": {"source": "resume"}},
#         {"text": "Implemented NLP classifier using scikit-learn", "metadata": {"source": "github"}},
#     ]

#     embedder = Embedder()
#     result = embedder.embed(docs)

#     assert result["vectors"].shape[0] == 2
#     assert result["vectors"].dtype == "float32"
#     assert len(result["metadatas"]) == 2


# tests/test_chatbot_retriever.py

import pytest
from chatbot.retrieval.retriever import (
    ResumeRetriever,
    retrieve_context
)


# -------------------------
# FIXTURES
# -------------------------

@pytest.fixture(scope="module")
def retriever():
    """
    Load retriever once (FAISS index is expensive).
    """
    return ResumeRetriever()


# -------------------------
# TESTS
# -------------------------

def test_retrieve_returns_results(retriever):
    query = "What experience do you have in machine learning?"

    results = retriever.retrieve(query, top_k=3)

    assert isinstance(results, list)
    assert len(results) > 0, "Retriever returned no results"

    for r in results:
        assert "text" in r
        assert "score" in r
        assert isinstance(r["text"], str)
        assert isinstance(r["score"], float)


def test_retrieve_empty_query_returns_empty_list(retriever):
    results = retriever.retrieve("", top_k=3)
    assert results == []


def test_retrieve_context_returns_string():
    query = "Tell me about your data engineering experience"

    context = retrieve_context(query, top_k=3)

    assert isinstance(context, str)
    assert len(context.strip()) > 0
    assert "Source:" in context


def test_retrieve_context_empty_query():
    context = retrieve_context("")
    assert context == ""
