"""
Base LLM Provider Interface and Data Transfer Objects.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model_name: str
    provider: str
    finish_reason: str = "stop"
    total_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderStatus:
    is_available: bool
    provider: str
    message: str
    models: List[str] = field(default_factory=list)


class BaseLLMProvider(ABC):
    """Abstract interface for all model providers."""

    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2500,
        model_name: Optional[str] = None,
    ) -> LLMResponse:
        """Generate model completion for input messages."""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderStatus:
        """Verify model server reachability and model availability."""
        pass
