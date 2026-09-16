"""
Main FastAPI Application Entrypoint.
Initializes database tables, configures CORS and security headers,
mounts API routers, and bootstraps knowledge base index if needed.
"""

import time
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.api.routes import health, sessions, chat, artifacts, models, knowledge
from backend.app.services.vector_store import HybridVectorStore
from scripts.ingest_transcripts import run_ingestion


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    # 1. Initialize DB tables
    try:
        init_db()
        print("[+] Database initialized successfully.")
    except Exception as e:
        print(f"[!] Warning: Database init error: {e}")

    # 2. Check and auto-bootstrap knowledge base if empty
    vector_store = HybridVectorStore(index_dir=settings.VECTOR_STORE_DIR)
    if not vector_store.is_indexed():
        print("[*] Knowledge base not indexed. Checking for transcripts/fixtures...")
        data_path = Path(settings.TRANSCRIPTS_DATA_DIR)
        fixtures_path = Path(settings.FIXTURES_DATA_DIR)
        vector_path = Path(settings.VECTOR_STORE_DIR)

        try:
            run_ingestion(
                data_dir=data_path,
                vector_store_dir=vector_path,
                fixtures_dir=fixtures_path,
                force_reindex=False,
            )
            print("[+] Auto-indexed knowledge base on startup.")
        except Exception as e:
            print(f"[!] Warning during auto-ingestion: {e}")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Internal product and growth knowledge assistant grounded in transcripts from Lenny's Podcast and Newsletter.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Correlation ID and Request Timing Middleware
@app.middleware("http")
async def add_correlation_and_timing(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[ERR] Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request.",
            "path": request.url.path,
        },
    )


# Mount API Routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(artifacts.router)
app.include_router(models.router)
app.include_router(knowledge.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
