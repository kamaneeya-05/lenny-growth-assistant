"""
Models and Provider Configuration Routes.
"""

from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.chat import ModelsListResponse, ModelInfo
from backend.app.services.llm.factory import provider_factory

router = APIRouter(prefix="/api", tags=["Models"])


@router.get("/models", response_model=ModelsListResponse)
async def list_available_models():
    """List available LLM providers, active selection, and Ollama connectivity status."""
    statuses = await provider_factory.get_all_provider_statuses()

    models_list = [
        # Ollama models
        ModelInfo(
            id="ollama:llama3.2",
            name="Ollama (llama3.2)",
            provider="ollama",
            is_local=True,
            is_available=statuses["ollama"]["available"],
            context_length=8192,
            description="Local Ollama model (default local demo)",
        ),
        ModelInfo(
            id="ollama:mistral",
            name="Ollama (mistral)",
            provider="ollama",
            is_local=True,
            is_available=statuses["ollama"]["available"],
            context_length=8192,
            description="Local Mistral model",
        ),
        # Cloud providers
        ModelInfo(
            id="anthropic:claude-3-5-sonnet-20241022",
            name="Claude 3.5 Sonnet" if statuses["anthropic"]["available"] else "Claude 3.5 Sonnet (Groq Bridge)",
            provider="anthropic",
            is_local=False,
            is_available=statuses["anthropic"]["available"] or statuses["openai"]["available"],
            context_length=200000 if statuses["anthropic"]["available"] else 128000,
            description=(
                "Anthropic Claude 3.5 Sonnet" if statuses["anthropic"]["available"]
                else "Claude 3.5 Sonnet (Bridged to Groq Cloud inference)"
            ),
        ),
        ModelInfo(
            id=f"openai:{settings.DEFAULT_MODEL_NAME if settings.DEFAULT_MODEL_PROVIDER == 'openai' else 'groq/compound'}",
            name=(
                f"Groq Cloud ({settings.DEFAULT_MODEL_NAME})" if "groq.com" in settings.OPENAI_BASE_URL
                else f"xAI Grok ({settings.DEFAULT_MODEL_NAME})" if "x.ai" in settings.OPENAI_BASE_URL
                else f"OpenAI ({settings.DEFAULT_MODEL_NAME or 'GPT-4o Mini'})"
            ),
            provider="openai",
            is_local=False,
            is_available=statuses["openai"]["available"],
            context_length=128000,
            description=(
                f"Groq ultra-fast cloud inference ({settings.DEFAULT_MODEL_NAME})" if "groq.com" in settings.OPENAI_BASE_URL
                else f"xAI Grok cloud inference ({settings.DEFAULT_MODEL_NAME})" if "x.ai" in settings.OPENAI_BASE_URL
                else "OpenAI cloud inference model"
            ),
        ),
        # Offline Deterministic Mock
        ModelInfo(
            id="mock:mock-grounded-pm",
            name="Deterministic Grounded PM (Demo/Test)",
            provider="mock",
            is_local=True,
            is_available=True,
            context_length=16000,
            description="Zero-dependency offline grounded evaluator",
        ),
    ]

    return ModelsListResponse(
        active_provider=settings.DEFAULT_MODEL_PROVIDER,
        active_model=settings.DEFAULT_MODEL_NAME,
        models=models_list,
        ollama_status=statuses["ollama"],
        cloud_providers={
            "anthropic": statuses["anthropic"]["available"],
            "openai": statuses["openai"]["available"],
        },
    )


@router.get("/configuration")
def get_configuration():
    """Return non-sensitive runtime configuration parameters."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "default_provider": settings.DEFAULT_MODEL_PROVIDER,
        "default_model": settings.DEFAULT_MODEL_NAME,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "retrieval_top_k": settings.RETRIEVAL_TOP_K,
        "retrieval_threshold": settings.RETRIEVAL_CONFIDENCE_THRESHOLD,
    }
