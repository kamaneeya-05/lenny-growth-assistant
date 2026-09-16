"""
Artifacts API Endpoints.
Retrieval, inspection, and manual artifact generation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import GeneratedArtifact
from backend.app.schemas.chat import ArtifactSchema, ArtifactCreateRequest

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


@router.get("/{artifact_id}", response_model=ArtifactSchema)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Retrieve an artifact by its unique ID."""
    artifact = db.query(GeneratedArtifact).filter(GeneratedArtifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact '{artifact_id}' not found",
        )
    return artifact


@router.post("", response_model=ArtifactSchema, status_code=status.HTTP_201_CREATED)
def create_artifact(request: ArtifactCreateRequest, db: Session = Depends(get_db)):
    """Manually persist or create an artifact."""
    artifact = GeneratedArtifact(
        session_id=request.session_id,
        message_id=request.message_id,
        title=request.title,
        artifact_type=request.artifact_type,
        content=request.content,
        description=request.description,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact
