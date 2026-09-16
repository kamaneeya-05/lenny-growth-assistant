"""
Model Provider Abstraction Tests.
"""

import pytest
from backend.app.services.llm.base import LLMMessage
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.services.llm.cloud_provider import CloudLLMProvider
from backend.app.services.llm.mock_provider import MockEvaluationProvider
from backend.app.services.llm.factory import ProviderFactory


@pytest.mark.asyncio
async def test_mock_provider_health_and_completion():
    prov = MockEvaluationProvider()
    status = await prov.check_health()
    assert status.is_available is True
    assert status.provider == "mock"

    resp = await prov.complete(
        messages=[LLMMessage(role="user", content="Hello, tell me about product management")]
    )
    assert len(resp.content) > 20
    assert resp.provider == "mock"


@pytest.mark.asyncio
async def test_ollama_offline_handling():
    # Test with non-existent port to verify graceful failure handling
    prov = OllamaProvider(base_url="http://localhost:59999", timeout=2)
    status = await prov.check_health()
    assert status.is_available is False
    assert "offline" in status.message.lower()

    # Attempting to query offline Ollama should raise ConnectionError or TimeoutError
    with pytest.raises((ConnectionError, TimeoutError)):
        await prov.complete(messages=[LLMMessage(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_cloud_provider_missing_key():
    # Cloud provider without key must report unavailable and raise clean ValueError
    prov = CloudLLMProvider(provider_type="anthropic", api_key=None)
    status = await prov.check_health()
    assert status.is_available is False
    assert "missing" in status.message.lower()

    with pytest.raises(ValueError):
        await prov.complete(messages=[LLMMessage(role="user", content="Hi")])


@pytest.mark.asyncio
async def test_provider_factory_fallback():
    factory = ProviderFactory()
    # If Ollama is offline, factory should safely fall back to mock
    resolved = await factory.get_provider("ollama")
    assert resolved is not None
    # Can complete regardless
    resp = await resolved.complete(messages=[LLMMessage(role="user", content="What is PMF?")])
    assert len(resp.content) > 10
