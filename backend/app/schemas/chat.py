"""
Pydantic Schemas for API Requests and Responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class CitationItem(BaseModel):
    title: str = Field(..., description="Episode or Newsletter Title")
    guest: Optional[str] = Field(None, description="Guest Name, if podcast")
    source_type: str = Field("podcast", description="'podcast' or 'newsletter'")
    url: Optional[str] = Field(None, description="Direct URL to newsletter/podcast")
    timestamp_str: Optional[str] = Field(None, description="Timestamp marker (e.g. 00:12:45)")
    speaker: Optional[str] = Field(None, description="Speaker name")
    excerpt: str = Field(..., description="Relevant verbatim or supporting passage")
    relevance_score: float = Field(0.0, description="Normalized retrieval relevance score")


class ArtifactSchema(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    title: str
    artifact_type: str  # "html" or "markdown"
    content: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArtifactCreateRequest(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    title: str
    artifact_type: str = Field(..., description="'html' or 'markdown'")
    content: str
    description: Optional[str] = None


class MessageSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: Optional[List[CitationItem]] = None
    artifact_id: Optional[str] = None
    artifact: Optional[ArtifactSchema] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionSchema(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: str
    title: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    messages: Optional[List[MessageSchema]] = None


class SessionCreateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    title: Optional[str] = "New Conversation"
    model_provider: Optional[str] = None
    model_name: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    title: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None


class ChatRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    message: str = Field(..., min_length=1, max_length=10000, description="User prompt")
    model_provider: Optional[str] = Field(None, description="Override model provider")
    model_name: Optional[str] = Field(None, description="Override model name")
    generate_ship30_essay: Optional[bool] = Field(False, description="Directly trigger Ship 30 for 30 skill")
    generate_artifact: Optional[bool] = Field(False, description="Directly trigger Artifact generation skill")
    artifact_type: Optional[str] = Field("html", description="Target artifact type: 'html' or 'markdown'")


class ChatResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    message: MessageSchema
    citations: List[CitationItem] = []
    artifact: Optional[ArtifactSchema] = None
    session_id: str
    model_used: str
    duration_seconds: float


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str  # "ollama", "anthropic", "openai", "mock"
    is_local: bool
    is_available: bool
    context_length: int = 8192
    description: Optional[str] = None


class ModelsListResponse(BaseModel):
    active_provider: str
    active_model: str
    models: List[ModelInfo]
    ollama_status: Dict[str, Any]
    cloud_providers: Dict[str, bool]


class KnowledgeStatusResponse(BaseModel):
    is_indexed: bool
    total_sources: int
    total_chunks: int
    vocab_size: int
    sources: List[Dict[str, Any]]
    last_updated: Optional[str] = None


class IngestRequest(BaseModel):
    download_remote: bool = False
    force_reindex: bool = False
    max_episodes: int = 15
