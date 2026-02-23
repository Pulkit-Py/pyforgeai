"""Provider factory for ergonomic provider selection."""

from __future__ import annotations

import inspect
from typing import Any

from forgeai.providers.anthropic_provider import AnthropicProvider
from forgeai.providers.base import BaseProvider
from forgeai.providers.deepseek_provider import DeepSeekProvider
from forgeai.providers.gemini_provider import GeminiProvider
from forgeai.providers.grok_provider import GrokProvider
from forgeai.providers.ollama_provider import OllamaProvider
from forgeai.providers.openai_provider import OpenAIProvider


def create_provider(name: str, **kwargs: Any) -> BaseProvider:
    """Create a provider instance by short provider name."""
    normalized = name.strip().lower()
    if normalized == "openai":
        return _construct(OpenAIProvider, **kwargs)
    if normalized == "ollama":
        return _construct(OllamaProvider, **kwargs)
    if normalized == "anthropic":
        return _construct(AnthropicProvider, **kwargs)
    if normalized == "gemini":
        return _construct(GeminiProvider, **kwargs)
    if normalized == "deepseek":
        return _construct(DeepSeekProvider, **kwargs)
    if normalized in {"grok", "xai"}:
        return _construct(GrokProvider, **kwargs)
    raise ValueError(f"Unsupported provider: {name}")


def _construct(provider_cls: type[BaseProvider], **kwargs: Any) -> BaseProvider:
    accepted = inspect.signature(provider_cls.__init__).parameters
    filtered = {key: value for key, value in kwargs.items() if key in accepted}
    return provider_cls(**filtered)
