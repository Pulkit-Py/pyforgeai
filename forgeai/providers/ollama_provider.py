"""Ollama provider implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from forgeai.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama provider for local model execution."""

    def __init__(
        self,
        model: str = "llama3.1",
        host: str = "http://localhost:11434",
        timeout_s: float = 30.0,
        retries: int = 1,
    ) -> None:
        self.model = model
        self.host = host
        self.timeout_s = timeout_s
        self.retries = retries

    async def generate(self, prompt: str) -> str:
        try:
            from ollama import AsyncClient  # type: ignore
        except Exception:
            return self._fallback_response(prompt, reason="ollama package not installed")

        client = AsyncClient(host=self.host)
        attempts = self.retries + 1
        last_error = "unknown"
        for attempt in range(attempts):
            try:
                response: Any = await asyncio.wait_for(
                    client.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=self.timeout_s,
                )
                message: dict[str, Any] = response.get("message", {})
                return str(message.get("content", "")).strip()
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                if attempt < attempts - 1:
                    await asyncio.sleep(0.25 * (attempt + 1))

        return self._fallback_response(prompt, reason=f"provider_error: {last_error}")

    @staticmethod
    def _fallback_response(prompt: str, reason: str) -> str:
        _ = prompt
        payload = {
            "thought": f"Provider fallback active: {reason}",
            "final": "I cannot call Ollama right now, but the framework is operational.",
        }
        return json.dumps(payload)
