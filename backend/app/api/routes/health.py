"""
Health and Status Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.services.vector_store import HybridVectorStore
from backend.app.services.llm.factory import provider_factory

router = APIRouter(tags=["Health"])

vector_store = HybridVectorStore(index_dir=settings.VECTOR_STORE_DIR)


@router.get("/health")
@router.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for API, database, vector store, and model providers."""
    # Check Database connectivity
    db_healthy = False
    db_error = None
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        db_error = str(e)

    # Check Vector Store
    kb_status = vector_store.get_status()

    # Check Model Providers
    providers_status = await provider_factory.get_all_provider_statuses()

    all_healthy = db_healthy

    return {
        "status": "healthy" if all_healthy else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": {
            "healthy": db_healthy,
            "url_type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql",
            "error": db_error,
        },
        "knowledge_base": {
            "is_indexed": kb_status["is_indexed"],
            "total_sources": kb_status["total_sources"],
            "total_chunks": kb_status["total_chunks"],
        },
        "providers": providers_status,
    }
