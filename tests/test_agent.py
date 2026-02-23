from __future__ import annotations

from forgeai.agent.base import Agent
from forgeai.memory.short_term import ShortTermMemory
from forgeai.providers.base import BaseProvider
from forgeai.tools.base import BaseTool


class DummyProvider(BaseProvider):
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = outputs

    async def generate(self, prompt: str) -> str:
        _ = prompt
        return self._outputs.pop(0)


class EchoTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="echo", description="echo tool")

    async def run(self, input: str) -> str:
        return f"echo:{input}"


async def test_agent_runs_tool_when_requested() -> None:
    provider = DummyProvider(
        [
            '{"status":"in_progress","tool_call":{"tool":"echo","input":"hello"}}',
            '{"status":"completed","final":"done"}',
        ]
    )
    agent = Agent(
        name="t1",
        role="tester",
        goal="run tools",
        tools=[EchoTool()],
        memory=ShortTermMemory(),
        provider=provider,
    )

    result = await agent.run("start")
    assert result == "done"
    assert agent.last_provider_calls == 2
    assert agent.last_tool_calls == 1


async def test_agent_handles_non_json_output() -> None:
    provider = DummyProvider(["plain text output"])
    agent = Agent(
        name="t2",
        role="tester",
        goal="return text",
        tools=[EchoTool()],
        memory=ShortTermMemory(),
        provider=provider,
    )

    result = await agent.run("start")
    assert result == "plain text output"
