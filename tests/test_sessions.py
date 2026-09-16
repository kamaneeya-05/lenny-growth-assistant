"""
Session Management and Isolation Tests.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_session_lifecycle():
    # 1. Create session A
    res_a = client.post("/api/sessions", json={"title": "Session A - Product Market Fit"})
    assert res_a.status_code == 201
    session_a = res_a.json()
    id_a = session_a["id"]
    assert session_a["title"] == "Session A - Product Market Fit"

    # 2. Create session B
    res_b = client.post("/api/sessions", json={"title": "Session B - Retention Loops"})
    assert res_b.status_code == 201
    session_b = res_b.json()
    id_b = session_b["id"]

    # 3. Post message to session A
    res_msg_a = client.post(
        f"/api/sessions/{id_a}/messages",
        json={"message": "How do you find product market fit according to Lenny?", "model_provider": "mock"}
    )
    assert res_msg_a.status_code == 200

    # 4. Verify Session B does NOT contain messages from Session A (Session Isolation)
    res_get_b = client.get(f"/api/sessions/{id_b}")
    assert res_get_b.status_code == 200
    data_b = res_get_b.json()
    messages_b = data_b.get("messages", [])
    assert len(messages_b) == 0, "Session B must have 0 messages (isolated from Session A)"

    # 5. Verify Session A contains its messages
    res_get_a = client.get(f"/api/sessions/{id_a}")
    assert res_get_a.status_code == 200
    data_a = res_get_a.json()
    assert len(data_a.get("messages", [])) >= 2

    # 6. Update session title
    res_update = client.patch(f"/api/sessions/{id_a}", json={"title": "Updated Session A Title"})
    assert res_update.status_code == 200
    assert res_update.json()["title"] == "Updated Session A Title"

    # 7. Delete session A
    res_del = client.delete(f"/api/sessions/{id_a}")
    assert res_del.status_code == 204

    # 8. Verify 404 on deleted session
    res_check = client.get(f"/api/sessions/{id_a}")
    assert res_check.status_code == 404
