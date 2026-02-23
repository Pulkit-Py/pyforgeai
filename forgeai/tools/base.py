"""Base tool interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Abstract asynchronous interface for agent tools."""

    name: str
    description: str

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    async def run(self, input: str) -> str:
        """Run the tool with a string input and return a string response."""

