"""
Knowledge Base Management and Ingestion Routes.
"""

from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.app.core.config import settings
from backend.app.schemas.chat import KnowledgeStatusResponse, IngestRequest
from backend.app.services.vector_store import HybridVectorStore
from scripts.ingest_transcripts import run_ingestion, fetch_remote_transcripts

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])

vector_store = HybridVectorStore(index_dir=settings.VECTOR_STORE_DIR)


@router.get("/status", response_model=KnowledgeStatusResponse)
def get_knowledge_status():
    """Check knowledge base indexing status, chunk counts, and ingested sources."""
    status = vector_store.get_status()
    return KnowledgeStatusResponse(
        is_indexed=status["is_indexed"],
        total_sources=status["total_sources"],
        total_chunks=status["total_chunks"],
        vocab_size=status["vocab_size"],
        sources=status["sources"],
    )


@router.get("/search")
def search_transcripts(q: str, top_k: int = 10):
    """Search transcript chunks directly by query or keywords."""
    if not q or not q.strip():
        return {"query": q, "results": []}

    results = vector_store.query(query_text=q, top_k=top_k, threshold=0.10)
    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "title": r["chunk"]["source_title"],
                "guest": r["chunk"]["source_guest"],
                "speaker": r["chunk"]["speaker"],
                "timestamp_str": r["chunk"]["timestamp_str"],
                "url": r["chunk"]["source_url"],
                "excerpt": r["chunk"]["text"],
                "score": r["score"],
                "is_grounded": r["is_grounded"],
            }
            for r in results
        ],
    }


@router.post("/ingest")
def trigger_ingestion(request: IngestRequest, background_tasks: BackgroundTasks):
    """Trigger ingestion of transcripts into the vector store."""
    data_path = Path(settings.TRANSCRIPTS_DATA_DIR)
    fixtures_path = Path(settings.FIXTURES_DATA_DIR)
    vector_path = Path(settings.VECTOR_STORE_DIR)

    if request.download_remote:
        fetch_remote_transcripts(data_path, max_episodes=request.max_episodes)

    result = run_ingestion(
        data_dir=data_path,
        vector_store_dir=vector_path,
        fixtures_dir=fixtures_path,
        force_reindex=request.force_reindex,
    )

    # Reload in-memory store
    vector_store.load_index()

    return {
        "status": "success",
        "result": result,
    }
