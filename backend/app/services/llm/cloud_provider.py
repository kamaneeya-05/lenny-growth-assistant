import asyncio
from typing import List, Optional
import httpx
from backend.app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse, ProviderStatus


class CloudLLMProvider(BaseLLMProvider):
    """Unified cloud provider for Anthropic Claude and OpenAI."""

    def __init__(
        self,
        provider_type: str = "anthropic",  # "anthropic" or "openai"
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: int = 45,
        base_url: Optional[str] = None,
    ):
        self.provider_type = provider_type.lower()
        self.api_key = api_key
        self.timeout = timeout

        if self.provider_type == "anthropic":
            self.default_model = default_model or "claude-3-5-sonnet-20241022"
            self.base_url = (base_url or "https://api.anthropic.com/v1").rstrip("/")
        else:
            self.default_model = default_model or "gpt-4o-mini"
            self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")

    async def check_health(self) -> ProviderStatus:
        """Check if API key is configured."""
        if not self.api_key:
            return ProviderStatus(
                is_available=False,
                provider=self.provider_type,
                message=f"Missing {self.provider_type.upper()}_API_KEY. Configure in .env to enable.",
                models=[],
            )
        return ProviderStatus(
            is_available=True,
            provider=self.provider_type,
            message=f"{self.provider_type.title()} API key configured and ready.",
            models=[self.default_model],
        )

    async def complete(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2500,
        model_name: Optional[str] = None,
    ) -> LLMResponse:
        """Call cloud LLM endpoint."""
        if not self.api_key:
            raise ValueError(
                f"Cannot use {self.provider_type} without an API key. Please set {self.provider_type.upper()}_API_KEY in .env."
            )

        model = model_name or self.default_model

        if self.provider_type == "anthropic":
            return await self._call_anthropic(messages, system_prompt, temperature, max_tokens, model)
        else:
            # If a Claude model is requested through the Groq/OpenAI provider, map to the active cloud model
            if model and ("claude" in model.lower() or "anthropic" in model.lower()):
                model = self.default_model
            return await self._call_openai(messages, system_prompt, temperature, max_tokens, model)

    async def _call_anthropic(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> LLMResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Format messages for Anthropic
        anthropic_messages = []
        for msg in messages:
            role = "user" if msg.role == "user" else "assistant"
            anthropic_messages.append({"role": role, "content": msg.content})

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Anthropic API error ({resp.status_code}): {resp.text}")

            data = resp.json()
            content = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    content += block.get("text", "")

            tokens = data.get("usage", {}).get("output_tokens", 0)
            return LLMResponse(
                content=content,
                model_name=model,
                provider="anthropic",
                finish_reason=data.get("stop_reason", "end_turn"),
                total_tokens=tokens,
            )

    async def _call_openai(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        model: str,
    ) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LennyGrowthAssistant/1.0",
        }

        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        for msg in messages:
            openai_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code == 429:
                await asyncio.sleep(2.5)
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)

            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI/Groq API error ({resp.status_code}): {resp.text}")

            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"].get("content") or ""
            tokens = data.get("usage", {}).get("total_tokens", 0)

            return LLMResponse(
                content=content,
                model_name=model,
                provider="openai",
                finish_reason=choice.get("finish_reason", "stop"),
                total_tokens=tokens,
            )
