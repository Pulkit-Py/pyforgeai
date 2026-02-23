from __future__ import annotations

from forgeai.providers.factory import create_provider
from forgeai.providers.ollama_provider import OllamaProvider
from forgeai.providers.openai_provider import OpenAIProvider


def test_provider_factory_builds_expected_provider() -> None:
    provider = create_provider("ollama", model="llama3.1")
    assert isinstance(provider, OllamaProvider)


async def test_openai_provider_fallback_without_key() -> None:
    provider = OpenAIProvider(api_key=None)
    result = await provider.generate("hello")
    assert "final" in result
