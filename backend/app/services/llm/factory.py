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
            default_model=settings.DEFAULT_MODEL_NAME if settings.DEFAULT_MODEL_PROVIDER == "ollama" else "llama3.2",
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
        """Resolve requested provider with graceful fallback and cross-provider bridging."""
        target = (provider_name or settings.DEFAULT_MODEL_PROVIDER).lower()

        if target == "ollama":
            status = await self.ollama.check_health()
            if status.is_available:
                return self.ollama
            print(f"[!] Ollama is not responding at {settings.OLLAMA_BASE_URL}. Falling back to deterministic demo/mock provider.")
            return self.mock

        elif target in ("anthropic", "claude"):
            status = await self.anthropic.check_health()
            if status.is_available:
                return self.anthropic
            # Intelligent Claude -> Groq / Grok Cloud Bridge
            openai_status = await self.openai.check_health()
            if openai_status.is_available:
                print(f"[*] Anthropic key not configured. Gracefully bridging Claude request to Groq Cloud ({self.openai.default_model}).")
                return self.openai
            print("[!] Anthropic and cloud providers unavailable. Falling back to mock evaluator.")
            return self.mock

        elif target in ("openai", "groq", "grok"):
            status = await self.openai.check_health()
            if status.is_available:
                return self.openai
            print("[!] Groq/OpenAI provider unavailable. Falling back to mock evaluator.")
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
