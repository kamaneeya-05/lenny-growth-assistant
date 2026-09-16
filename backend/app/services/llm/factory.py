"""
Provider Factory & Manager.
Instantiates and routes to the requested model provider with automatic health fallback.
"""

from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.services.llm.base import BaseLLMProvider, ProviderStatus
from backend.app.services.llm.ollama_provider import OllamaProvider
from backend.app.services.llm.cloud_provider import CloudLLMProvider
from backend.app.services.llm.mock_provider import MockEvaluationProvider


class ProviderFactory:
    """Manages LLM providers with health checks and fallbacks."""

    def __init__(self):
        self.ollama = OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            default_model=settings.DEFAULT_MODEL_NAME,
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        self.anthropic = CloudLLMProvider(
            provider_type="anthropic",
            api_key=settings.ANTHROPIC_API_KEY,
        )
        self.openai = CloudLLMProvider(
            provider_type="openai",
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            default_model=settings.DEFAULT_MODEL_NAME if settings.DEFAULT_MODEL_PROVIDER == "openai" else "gpt-4o-mini",
        )
        self.mock = MockEvaluationProvider()

    async def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """Resolve requested provider with graceful fallback."""
        target = (provider_name or settings.DEFAULT_MODEL_PROVIDER).lower()

        if target == "ollama":
            status = await self.ollama.check_health()
            if status.is_available:
                return self.ollama
            # Graceful fallback: If Ollama requested but unavailable, fallback to mock provider
            print(f"[!] Ollama is not responding at {settings.OLLAMA_BASE_URL}. Falling back to deterministic demo/mock provider.")
            return self.mock

        elif target == "anthropic":
            status = await self.anthropic.check_health()
            if status.is_available:
                return self.anthropic
            return self.mock

        elif target == "openai":
            status = await self.openai.check_health()
            if status.is_available:
                return self.openai
            return self.mock

        elif target == "mock":
            return self.mock

        return self.mock

    async def get_all_provider_statuses(self) -> Dict[str, Any]:
        """Check availability across all providers."""
        ollama_status = await self.ollama.check_health()
        anthropic_status = await self.anthropic.check_health()
        openai_status = await self.openai.check_health()

        return {
            "ollama": {
                "available": ollama_status.is_available,
                "message": ollama_status.message,
                "models": ollama_status.models,
            },
            "anthropic": {
                "available": anthropic_status.is_available,
                "message": anthropic_status.message,
            },
            "openai": {
                "available": openai_status.is_available,
                "message": openai_status.message,
            },
            "mock": {
                "available": True,
                "message": "Deterministic offline mock ready",
            },
        }


provider_factory = ProviderFactory()
