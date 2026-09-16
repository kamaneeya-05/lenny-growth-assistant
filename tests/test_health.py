"""
Health check and configuration endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoints():
    for path in ["/health", "/api/health"]:
        resp = client.get(path)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "database" in data
        assert "knowledge_base" in data
        assert "providers" in data
        assert "version" in data


def test_configuration_endpoint():
    resp = client.get("/api/configuration")
    assert resp.status_code == 200
    data = resp.json()
    assert "app_name" in data
    assert "default_provider" in data
    assert "retrieval_top_k" in data


def test_models_list_endpoint():
    resp = client.get("/api/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert len(data["models"]) >= 3
    assert "active_provider" in data
    assert "ollama_status" in data
