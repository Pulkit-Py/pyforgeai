"""Anthropic provider implementation."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from forgeai.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic chat provider using the official SDK if available."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-latest",
        api_key: str | None = None,
        timeout_s: float = 30.0,
        retries: int = 1,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.timeout_s = timeout_s
        self.retries = retries

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            return self._fallback_response(prompt, reason="ANTHROPIC_API_KEY not set")

        try:
            from anthropic import AsyncAnthropic  # type: ignore
        except Exception:
            return self._fallback_response(prompt, reason="anthropic package not installed")

        client = AsyncAnthropic(api_key=self.api_key)
        attempts = self.retries + 1
        last_error = "unknown"
        for attempt in range(attempts):
            try:
                response: Any = await asyncio.wait_for(
                    client.messages.create(
                        model=self.model,
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                    timeout=self.timeout_s,
                )
                content = getattr(response, "content", [])
                texts: list[str] = []
                for block in content:
                    text = getattr(block, "text", None)
                    if text:
                        texts.append(str(text))
                return "\n".join(texts).strip()
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
            "final": "I cannot call Anthropic right now, but the framework is operational.",
        }
        return json.dumps(payload)
