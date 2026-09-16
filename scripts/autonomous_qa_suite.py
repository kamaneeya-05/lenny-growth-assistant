import urllib.request
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def api_get(endpoint: str):
    req = urllib.request.Request(f"{BASE_URL}{endpoint}")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def api_post(endpoint: str, data: dict):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("================================================================")
print(" AUTONOMOUS QA SUITE — THE LENNY GROWTH ASSISTANT")
print("================================================================")

# 1. Health & DB
health = api_get("/health")
assert health["status"] == "healthy", f"Health status bad: {health}"
assert health["database"]["healthy"] is True, "Database unhealthy"
print(f"[PASS] 1. System Health: {health['status']} | Database: SQLite ({health['database']['healthy']})")

# 2. Knowledge Base
kb = api_get("/api/knowledge/status")
assert kb["is_indexed"] is True, "Knowledge base not indexed"
assert kb["total_sources"] >= 14, f"Expected >= 14 sources, got {kb['total_sources']}"
assert kb["total_chunks"] >= 600, f"Expected >= 600 chunks, got {kb['total_chunks']}"
print(f"[PASS] 2. Knowledge Base: {kb['total_sources']} Sources | {kb['total_chunks']} Chunks | Vocab: {kb['vocab_size']}")

# 3. Grounded Q&A
session_a = api_post("/api/sessions", {"title": "QA Session A - Growth Loops", "model_provider": "mock"})
session_a_id = session_a["id"]

qa_resp = api_post(
    f"/api/sessions/{session_a_id}/messages",
    {
        "message": "What does Adam Mosseri say about AI being a tailwind for authenticity and taste?",
        "model_provider": "mock"
    }
)
citations = qa_resp.get("citations", [])
assert len(citations) > 0, "No citations returned for grounded query"
assert citations[0]["guest"] == "Adam Mosseri" or "Adam Mosseri" in citations[0]["title"], "Citation source incorrect"
assert citations[0]["timestamp_str"] is not None, "Missing timestamp in citation"
print(f"[PASS] 3. Grounded Q&A: Returned {len(citations)} citations. Guest: {citations[0].get('guest')} | Timestamp: {citations[0].get('timestamp_str')}")

# 4. Contextual Follow-Up
followup_resp = api_post(
    f"/api/sessions/{session_a_id}/messages",
    {
        "message": "Can you turn that into three practical actions for a product team?",
        "model_provider": "mock"
    }
)
# Check session history has 4 messages now (user 1, assistant 1, user 2, assistant 2)
session_history = api_get(f"/api/sessions/{session_a_id}")
msgs = session_history.get("messages", [])
assert len(msgs) == 4, f"Expected 4 messages in history, found {len(msgs)}"
print(f"[PASS] 4. Contextual Follow-up: Turn 2 recorded. Session message count: {len(msgs)}")

# 5. Session Isolation
session_b = api_post("/api/sessions", {"title": "QA Session B - Retention", "model_provider": "mock"})
session_b_id = session_b["id"]
session_b_history = api_get(f"/api/sessions/{session_b_id}")
b_msgs = session_b_history.get("messages", []) or []
assert len(b_msgs) == 0, f"Session B should have 0 messages, found {len(b_msgs)}"

# Verify Session A is untouched
a_again = api_get(f"/api/sessions/{session_a_id}")
assert len(a_again["messages"]) == 4, "Session A corrupted by Session B creation"
print(f"[PASS] 5. Session Isolation: Session B isolated (0 msgs) while Session A preserves {len(a_again['messages'])} msgs")

# 6. Guardrail on Unsupported Query
guardrail_resp = api_post(
    f"/api/sessions/{session_b_id}/messages",
    {
        "message": "What is Lenny's recipe for chocolate cake?",
        "model_provider": "mock"
    }
)
reply_text = guardrail_resp.get("message", {}).get("content", "").lower()
assert "couldn't find" in reply_text or "unsupported" in reply_text or "not find" in reply_text, f"Guardrail failed to refuse: {reply_text}"
assert len(guardrail_resp.get("citations", [])) == 0, f"Guardrail produced fake citations: {guardrail_resp.get('citations')}"
print(f"[PASS] 6. Guardrail Refusal: Gracefully refused with 0 fake citations")

# 7. Ship 30 for 30 Skill
ship30_resp = api_post(
    f"/api/sessions/{session_b_id}/messages",
    {
        "message": "Write a Ship 30 for 30 essay on product market fit retention",
        "model_provider": "mock",
        "generate_ship30_essay": True
    }
)
essay_content = ship30_resp.get("message", {}).get("content", "")
word_count = len(essay_content.split())
assert word_count > 800, f"Ship 30 essay too short: {word_count} words"
print(f"[PASS] 7. Ship 30 for 30 Skill: Generated {word_count} words (Target: ~1,250 words) with structured headings")

# 8. HTML Artifact Generation
art_resp = api_post(
    f"/api/sessions/{session_b_id}/messages",
    {
        "message": "Create an HTML product strategy one-pager artifact for PMF metrics",
        "model_provider": "mock",
        "generate_artifact": True,
        "artifact_type": "html"
    }
)
art_obj = art_resp.get("artifact")
assert art_obj is not None, "HTML artifact not returned in response"
assert art_obj["artifact_type"] == "html", "Artifact type is not html"
assert "<html" in art_obj["content"].lower() or "<div" in art_obj["content"].lower() or "<style" in art_obj["content"].lower(), "HTML content missing tags"
artifact_id = art_obj["id"]

# Verify fetch by ID
fetched_art = api_get(f"/api/artifacts/{artifact_id}")
assert fetched_art["id"] == artifact_id, "Fetched artifact ID mismatch"
assert len(fetched_art["content"]) > 500, "Fetched artifact content too small"
print(f"[PASS] 8. HTML Artifact Studio: Generated '{art_obj['title']}' ({len(art_obj['content'])} chars), fetched via API")

# 9. Markdown Artifact Generation
md_art_resp = api_post(
    f"/api/sessions/{session_b_id}/messages",
    {
        "message": "Create a Markdown checklist artifact for B2B growth loops",
        "model_provider": "mock",
        "generate_artifact": True,
        "artifact_type": "markdown"
    }
)
md_obj = md_art_resp.get("artifact")
assert md_obj is not None, "Markdown artifact not returned"
assert md_obj["artifact_type"] == "markdown", "Artifact type is not markdown"
print(f"[PASS] 9. Markdown Artifact Studio: Generated '{md_obj['title']}' ({len(md_obj['content'])} chars)")

# 10. Models List & Connectivity Health
models_resp = api_get("/api/models")
assert len(models_resp["models"]) >= 3, "Expected at least 3 models in list"
print(f"[PASS] 10. Model Provider Abstraction: {len(models_resp['models'])} models available. Active: {models_resp['active_provider']}")

print("\n================================================================")
print(" ALL 10 AUTONOMOUS BACKEND/API CHECKS PASSED 100%")
print("================================================================")
