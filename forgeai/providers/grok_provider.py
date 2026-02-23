"""xAI Grok provider implementation."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from forgeai.providers.base import BaseProvider


class GrokProvider(BaseProvider):
    """Grok provider via xAI OpenAI-compatible API."""

    def __init__(
        self,
        model: str = "grok-2-latest",
        api_key: str | None = None,
        timeout_s: float = 30.0,
        retries: int = 1,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.timeout_s = timeout_s
        self.retries = retries

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            return self._fallback_response(prompt, reason="XAI_API_KEY not set")

        try:
            from openai import AsyncOpenAI  # type: ignore
        except Exception:
            return self._fallback_response(prompt, reason="openai package not installed")

        client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
        attempts = self.retries + 1
        last_error = "unknown"
        for attempt in range(attempts):
            try:
                response: Any = await asyncio.wait_for(
                    client.responses.create(model=self.model, input=prompt),
                    timeout=self.timeout_s,
                )
                return str(getattr(response, "output_text", "")).strip()
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
            "final": "I cannot call Grok right now, but the framework is operational.",
        }
        return json.dumps(payload)
