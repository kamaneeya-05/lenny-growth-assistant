"""
Agent Skills and Grounding Guardrail Tests.
"""

import pytest
from backend.app.services.vector_store import HybridVectorStore
from backend.app.services.llm.mock_provider import MockEvaluationProvider
from backend.app.services.agent.orchestrator import AgentOrchestrator
from backend.app.core.config import settings


@pytest.mark.asyncio
async def test_grounded_qa_with_citations():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    provider = MockEvaluationProvider()
    orchestrator = AgentOrchestrator(vs, provider)

    result = await orchestrator.run(
        user_message="What did Adam Mosseri say about AI being a tailwind for authenticity?",
        history=[],
    )

    assert len(result.citations) >= 1
    assert "Adam Mosseri" in result.citations[0].title or result.citations[0].guest == "Adam Mosseri"
    assert result.citations[0].timestamp_str is not None
    assert len(result.content) > 100
    assert "taste" in result.content.lower() or "authenticity" in result.content.lower()


@pytest.mark.asyncio
async def test_unsupported_question_guardrail():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    provider = MockEvaluationProvider()
    orchestrator = AgentOrchestrator(vs, provider)

    result = await orchestrator.run(
        user_message="What is Lenny's favorite recipe for chocolate cake?",
        history=[],
    )

    # Must refuse gracefully
    assert "couldn't find enough support" in result.content.lower()
    # Must NOT fabricate fake citations
    assert len(result.citations) == 0


@pytest.mark.asyncio
async def test_ship30_essay_skill():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    provider = MockEvaluationProvider()
    orchestrator = AgentOrchestrator(vs, provider)

    result = await orchestrator.run(
        user_message="Turn Adam Mosseri's advice on AI and taste into a Ship 30 for 30 essay",
        history=[],
        force_ship30=True,
    )

    words = result.content.split()
    # Ensure word count is approximately 1,250 words
    assert 1000 <= len(words) <= 1500, f"Expected ~1,250 words, got {len(words)}"
    # Verify hook and rhythm elements
    assert "Hook" in result.content or "1." in result.content
    assert "##" in result.content
    assert "*" in result.content or "-" in result.content


@pytest.mark.asyncio
async def test_artifact_generation_skill():
    vs = HybridVectorStore(settings.VECTOR_STORE_DIR)
    provider = MockEvaluationProvider()
    orchestrator = AgentOrchestrator(vs, provider)

    result = await orchestrator.run(
        user_message="Create an HTML landing page framework for AI product growth",
        history=[],
        force_artifact=True,
        artifact_type="html",
    )

    assert result.artifact is not None
    assert result.artifact["artifact_type"] == "html"
    assert "<!DOCTYPE html>" in result.artifact["content"]
    assert "<style>" in result.artifact["content"]
    assert len(result.artifact["title"]) > 3
