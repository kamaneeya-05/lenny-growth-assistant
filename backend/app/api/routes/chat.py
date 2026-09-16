"""
Conversational Chat and Execution Endpoints.
Processes user prompts with retrieval grounding, model orchestration, and session persistence.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import ChatSession, ChatMessage, GeneratedArtifact
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageSchema,
    ArtifactSchema,
    CitationItem,
)
from backend.app.core.config import settings
from backend.app.services.vector_store import HybridVectorStore
from backend.app.services.llm.factory import provider_factory
from backend.app.services.llm.base import LLMMessage
from backend.app.services.agent.orchestrator import AgentOrchestrator

router = APIRouter(tags=["Chat"])

vector_store = HybridVectorStore(index_dir=settings.VECTOR_STORE_DIR)


@router.post("/api/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Post a message to an existing session, execute grounded agent, and return response."""
    # 1. Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found",
        )

    # 2. Persist User Message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # 3. Auto-generate title if this is the first message
    msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
    if msg_count <= 1 or session.title == "New Conversation":
        snippet = " ".join(request.message.split()[:6])
        session.title = snippet.capitalize() or "Conversation"
        db.commit()

    # 4. Resolve Model Provider
    provider_name = request.model_provider or session.model_provider or settings.DEFAULT_MODEL_PROVIDER
    model_name = request.model_name or session.model_name or settings.DEFAULT_MODEL_NAME

    provider = await provider_factory.get_provider(provider_name)

    # 5. Fetch recent session history for context
    past_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.id != user_msg.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    history = [LLMMessage(role=m.role, content=m.content) for m in past_messages]

    # 6. Execute Agent Orchestrator
    orchestrator = AgentOrchestrator(vector_store=vector_store, provider=provider)
    result = await orchestrator.run(
        user_message=request.message,
        history=history,
        force_ship30=request.generate_ship30_essay or False,
        force_artifact=request.generate_artifact or False,
        artifact_type=request.artifact_type or "html",
        model_name=model_name,
    )

    # 7. Persist Artifact if one was generated
    saved_artifact = None
    artifact_schema = None
    if result.artifact:
        saved_artifact = GeneratedArtifact(
            session_id=session_id,
            title=result.artifact["title"],
            artifact_type=result.artifact["artifact_type"],
            content=result.artifact["content"],
            description=result.artifact.get("description"),
        )
        db.add(saved_artifact)
        db.commit()
        db.refresh(saved_artifact)
        artifact_schema = ArtifactSchema.model_validate(saved_artifact)

    # 8. Persist Assistant Message
    citations_data = [c.model_dump() for c in result.citations] if result.citations else None
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=result.content,
        citations=citations_data,
        artifact_id=saved_artifact.id if saved_artifact else None,
    )
    db.add(assistant_msg)
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assistant_msg)

    # Link artifact to message
    if saved_artifact:
        saved_artifact.message_id = assistant_msg.id
        db.commit()

    message_schema = MessageSchema(
        id=assistant_msg.id,
        session_id=assistant_msg.session_id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        citations=result.citations,
        artifact_id=assistant_msg.artifact_id,
        artifact=artifact_schema,
        created_at=assistant_msg.created_at,
    )

    return ChatResponse(
        message=message_schema,
        citations=result.citations,
        artifact=artifact_schema,
        session_id=session_id,
        model_used=result.model_used,
        duration_seconds=result.duration_seconds,
    )


@router.post("/api/chat", response_model=ChatResponse)
async def stateless_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Stateless chat endpoint that automatically creates or uses a transient session."""
    session = ChatSession(
        title="Quick Chat",
        model_provider=request.model_provider or settings.DEFAULT_MODEL_PROVIDER,
        model_name=request.model_name or settings.DEFAULT_MODEL_NAME,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return await send_message(session_id=session.id, request=request, db=db)
