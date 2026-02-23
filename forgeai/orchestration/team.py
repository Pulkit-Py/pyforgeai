"""Multi-agent orchestration primitives."""

from __future__ import annotations

from collections.abc import Sequence

from forgeai.agent.base import Agent


class AgentTeam:
    """Runs agents sequentially, forwarding each output to the next agent."""

    def __init__(self, agents: Sequence[Agent]) -> None:
        self.agents = list(agents)

    async def run(self, initial_input: str = "") -> str:
        current = initial_input
        for agent in self.agents:
            current = await agent.run(current)
        return current

