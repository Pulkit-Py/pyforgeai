"""Short-term memory implementation."""

from __future__ import annotations

import asyncio
from collections import Counter

from forgeai.memory.base import BaseMemory


class ShortTermMemory(BaseMemory):
    """Simple in-memory buffer with async-safe access."""

    def __init__(self, max_entries: int = 20, context_window: int = 6) -> None:
        self._entries: list[str] = []
        self._max_entries = max_entries
        self._context_window = context_window
        self._lock = asyncio.Lock()

    async def add(self, entry: str) -> None:
        async with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries :]

    async def get_context(self, query: str) -> str:
        async with self._lock:
            if not self._entries:
                return "No memory yet."
            if not query.strip():
                return "\n".join(self._entries[-self._context_window :])

            ranked = sorted(
                self._entries,
                key=lambda entry: self._score(query, entry),
                reverse=True,
            )
            selected = ranked[: self._context_window]
            return "\n".join(selected)

    @staticmethod
    def _score(query: str, entry: str) -> float:
        query_tokens = Counter(token.lower() for token in query.split())
        entry_tokens = Counter(token.lower() for token in entry.split())
        if not query_tokens:
            return 0.0
        overlap = sum((query_tokens & entry_tokens).values())
        return float(overlap) + (len(entry) / 10000.0)
