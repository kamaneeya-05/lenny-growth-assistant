"""
SQLAlchemy Database Models for The Lenny Growth Assistant.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    model_provider = Column(String(50), nullable=False, default="ollama")
    model_name = Column(String(100), nullable=False, default="llama3.2")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )
    artifacts = relationship(
        "GeneratedArtifact",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # List of citation dicts
    artifact_id = Column(String(36), ForeignKey("generated_artifacts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    artifact = relationship("GeneratedArtifact", foreign_keys=[artifact_id])


class GeneratedArtifact(Base):
    __tablename__ = "generated_artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # "html", "markdown"
    content = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="artifacts")


class TranscriptSource(Base):
    __tablename__ = "transcript_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    title = Column(String(255), nullable=False)
    guest = Column(String(255), nullable=True)
    source_type = Column(String(50), nullable=False, default="podcast")  # "podcast", "newsletter"
    url = Column(String(512), nullable=True)
    word_count = Column(Integer, default=0)
    date = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chunks = relationship("TranscriptChunk", back_populates="source", cascade="all, delete-orphan")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    source_id = Column(String(36), ForeignKey("transcript_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String(100), nullable=True)
    timestamp_str = Column(String(50), nullable=True)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)

    source = relationship("TranscriptSource", back_populates="chunks")


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    status = Column(String(50), nullable=False, default="pending")  # "pending", "running", "completed", "failed"
    total_sources = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
