from functools import lru_cache

from app.adapters.base import BaseProvider
from app.adapters.gemini.adapter import GeminiProviderAdapter
from app.shared.exceptions import ValidationAppError


@lru_cache
def get_provider_adapter(provider_slug: str) -> BaseProvider:
    adapters: dict[str, BaseProvider] = {
        "gemini": GeminiProviderAdapter(),
    }
    adapter = adapters.get(provider_slug)
    if adapter is None:
        raise ValidationAppError(
            f"Adaptador automático não disponível para o provedor '{provider_slug}'.",
            code="unsupported_provider_adapter",
        )
    return adapter

