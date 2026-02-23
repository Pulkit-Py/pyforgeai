from __future__ import annotations

from forgeai.agent.base import Agent
from forgeai.engine.engine import Engine
from forgeai.memory.short_term import ShortTermMemory
from forgeai.observability.logger import get_logger
from forgeai.providers.base import BaseProvider
from forgeai.tools.base import BaseTool


class RepeatingProvider(BaseProvider):
    async def generate(self, prompt: str) -> str:
        _ = prompt
        return '{"status":"completed","final":"stable"}'


class NoopTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="noop", description="noop")

    async def run(self, input: str) -> str:
        _ = input
        return "ok"


async def test_engine_early_stops_on_repeated_output() -> None:
    agent = Agent(
        name="engine-agent",
        role="tester",
        goal="be stable",
        tools=[NoopTool()],
        memory=ShortTermMemory(),
        provider=RepeatingProvider(),
    )
    engine = Engine(max_iterations=5, max_retries=0, logger=get_logger("test-engine"))

    result = await engine.run(agent, initial_input="go")
    assert result == "stable"
    assert engine.metrics.total_steps <= 2
