"""
Hybrid Vector Store and Grounding Tests.
"""

from pathlib import Path
import pytest
from backend.app.services.vector_store import HybridVectorStore
from backend.app.core.config import settings


def test_vector_store_is_indexed():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    assert vs.is_indexed() is True
    status = vs.get_status()
    assert status["total_sources"] >= 1
    assert status["total_chunks"] >= 50
    assert status["vocab_size"] > 500


def test_grounded_retrieval():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    results = vs.query("Adam Mosseri AI and authenticity", top_k=4)

    assert len(results) > 0
    top_hit = results[0]
    assert top_hit["score"] > 0.25
    assert top_hit["is_grounded"] is True
    assert "Adam Mosseri" in top_hit["chunk"]["source_title"] or top_hit["chunk"]["source_guest"] == "Adam Mosseri"


def test_unsupported_query_retrieval():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    # Query completely unrepresented in product podcast transcripts
    results = vs.query("What is the exact culinary recipe for baking chocolate cake?", top_k=4)

    assert len(results) > 0
    # Must NOT be marked as grounded
    assert results[0]["is_grounded"] is False
