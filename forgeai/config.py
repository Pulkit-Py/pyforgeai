"""Configuration helpers for forgeai."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class ForgeAIConfig:
    """Runtime configuration for provider and engine defaults."""

    default_provider: str = "ollama"
    default_model: str = "qwen3:4b"
    provider_timeout_s: float = 30.0
    provider_retries: int = 1
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    max_iterations: int = 5
    max_retries: int = 2

    @classmethod
    def from_env(cls) -> "ForgeAIConfig":
        """Load configuration values from environment variables."""
        return cls(
            default_provider=os.getenv("FORGEAI_DEFAULT_PROVIDER", "ollama"),
            default_model=os.getenv("FORGEAI_DEFAULT_MODEL", "qwen3:4b"),
            provider_timeout_s=float(os.getenv("FORGEAI_PROVIDER_TIMEOUT_S", "30.0")),
            provider_retries=int(os.getenv("FORGEAI_PROVIDER_RETRIES", "1")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_iterations=int(os.getenv("FORGEAI_MAX_ITERATIONS", "5")),
            max_retries=int(os.getenv("FORGEAI_MAX_RETRIES", "2")),
        )
