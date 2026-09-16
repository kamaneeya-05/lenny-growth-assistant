"""
Ollama Local LLM Provider.
Connects to a locally running Ollama instance at http://localhost:11434.
"""

from typing import List, Optional
import httpx
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, ProviderStatus


class OllamaProvider(BaseLLMProvider):
    """Local LLM provider utilizing Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.2", timeout: int = 45):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout

    async def check_health(self) -> ProviderStatus:
        """Check if local Ollama daemon is reachable and list installed models."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return ProviderStatus(
                        is_available=True,
                        provider="ollama",
                        message=f"Ollama online with {len(models)} local models.",
                        models=models,
                    )
                return ProviderStatus(
                    is_available=False,
                    provider="ollama",
                    message=f"Ollama returned HTTP {resp.status_code}",
                )
        except Exception as e:
            return ProviderStatus(
                is_available=False,
                provider="ollama",
                message=f"Ollama offline at {self.base_url}. (Run 'ollama serve' or use mock provider for demo)",
            )

    async def complete(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2500,
        model_name: Optional[str] = None,
    ) -> LLMResponse:
        """Query Ollama chat API."""
        model = model_name or self.default_model

        # Build Ollama message payload
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                if resp.status_code != 200:
                    raise RuntimeError(f"Ollama API error ({resp.status_code}): {resp.text}")

                data = resp.json()
                msg = data.get("message", {})
                content = msg.get("content", "")
                tokens = data.get("eval_count", 0)

                return LLMResponse(
                    content=content,
                    model_name=model,
                    provider="ollama",
                    finish_reason=data.get("done_reason", "stop"),
                    total_tokens=tokens,
                )
        except httpx.ConnectError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running (`ollama serve`) or switch to the demo/mock provider."
            )
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Ollama timed out after {self.timeout}s on model '{model}'. Consider smaller prompts or faster local models."
            )
