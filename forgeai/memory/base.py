"""Base memory interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseMemory(ABC):
    """Abstract asynchronous memory interface for agent context."""

    @abstractmethod
    async def add(self, entry: str) -> None:
        """Add a new entry to memory."""

    @abstractmethod
    async def get_context(self, query: str) -> str:
        """Return relevant context for a query."""

