"""Google Gemini provider implementation."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from forgeai.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini provider using Google GenAI SDK if available."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: str | None = None,
        timeout_s: float = 30.0,
        retries: int = 1,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.timeout_s = timeout_s
        self.retries = retries

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            return self._fallback_response(prompt, reason="GEMINI_API_KEY or GOOGLE_API_KEY not set")

        try:
            from google import genai  # type: ignore
        except Exception:
            return self._fallback_response(prompt, reason="google-genai package not installed")

        client = genai.Client(api_key=self.api_key)
        attempts = self.retries + 1
        last_error = "unknown"
        for attempt in range(attempts):
            try:
                response: Any = await asyncio.wait_for(
                    client.aio.models.generate_content(model=self.model, contents=prompt),
                    timeout=self.timeout_s,
                )
                text = getattr(response, "text", None)
                return str(text or "").strip()
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
            "final": "I cannot call Gemini right now, but the framework is operational.",
        }
        return json.dumps(payload)
