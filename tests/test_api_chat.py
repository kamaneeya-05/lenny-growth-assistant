"""
End-to-End Chat and Artifacts Endpoint Tests.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_chat_and_artifact_flow():
    # 1. Create a session
    sess_res = client.post("/api/sessions", json={"title": "E2E Test Session", "model_provider": "mock"})
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    # 2. Grounded message
    chat_res = client.post(
        f"/api/sessions/{session_id}/messages",
        json={
            "message": "What does Adam Mosseri say about AI?",
            "model_provider": "mock",
        },
    )
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["citations"]) >= 1
    assert data["duration_seconds"] >= 0

    # 3. Artifact generation message
    art_res = client.post(
        f"/api/sessions/{session_id}/messages",
        json={
            "message": "Generate an HTML strategy one-pager artifact for this",
            "model_provider": "mock",
            "generate_artifact": True,
            "artifact_type": "html",
        },
    )
    assert art_res.status_code == 200
    art_data = art_res.json()
    assert art_data["artifact"] is not None
    artifact_id = art_data["artifact"]["id"]
    assert art_data["artifact"]["artifact_type"] == "html"

    # 4. Fetch artifact via /api/artifacts/{id}
    fetch_art = client.get(f"/api/artifacts/{artifact_id}")
    assert fetch_art.status_code == 200
    assert fetch_art.json()["id"] == artifact_id
    assert "<!DOCTYPE html>" in fetch_art.json()["content"]

    # 5. Clean up session
    client.delete(f"/api/sessions/{session_id}")
