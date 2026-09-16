"""
Session Management Routes.
CRUD operations for chat sessions with message isolation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.database import get_db
from backend.app.db.models import ChatSession, ChatMessage
from backend.app.schemas.chat import (
    SessionSchema,
    SessionCreateRequest,
    SessionUpdateRequest,
    MessageSchema,
)
from backend.app.core.config import settings

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
def create_session(request: SessionCreateRequest, db: Session = Depends(get_db)):
    """Create a new isolated chat session."""
    session = ChatSession(
        title=request.title or "New Conversation",
        model_provider=request.model_provider or settings.DEFAULT_MODEL_PROVIDER,
        model_name=request.model_name or settings.DEFAULT_MODEL_NAME,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=List[SessionSchema])
def list_sessions(limit: int = 50, db: Session = Depends(get_db)):
    """List all chat sessions ordered by most recently updated."""
    sessions = (
        db.query(ChatSession)
        .order_by(desc(ChatSession.updated_at))
        .limit(limit)
        .all()
    )
    results = []
    for s in sessions:
        count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        schema = SessionSchema(
            id=s.id,
            title=s.title,
            model_provider=s.model_provider,
            model_name=s.model_name,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=count,
            messages=None,
        )
        results.append(schema)
    return results


@router.get("/{session_id}", response_model=SessionSchema)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a single chat session with its full message history."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found",
        )
    return session


@router.patch("/{session_id}", response_model=SessionSchema)
def update_session(session_id: str, request: SessionUpdateRequest, db: Session = Depends(get_db)):
    """Update title or active model for a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found",
        )
    if request.title is not None:
        session.title = request.title
    if request.model_provider is not None:
        session.model_provider = request.model_provider
    if request.model_name is not None:
        session.model_name = request.model_name

    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all cascading messages and artifacts."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session '{session_id}' not found",
        )
    db.delete(session)
    db.commit()
    return None
