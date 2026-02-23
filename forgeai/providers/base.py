"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract asynchronous LLM provider interface."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""

