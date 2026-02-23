"""Simple forgeai usage example."""

from __future__ import annotations

import asyncio

from forgeai.agent.base import Agent
from forgeai.config import ForgeAIConfig
from forgeai.engine.engine import Engine
from forgeai.memory.short_term import ShortTermMemory
from forgeai.observability.logger import get_logger
from forgeai.providers.factory import create_provider
from forgeai.tools.python_tool import PythonTool


async def main() -> None:
    config = ForgeAIConfig.from_env()
    logger = get_logger("forgeai-example")
    tool = PythonTool()
    memory = ShortTermMemory(max_entries=10)
    provider = create_provider(
        config.default_provider,
        model=config.default_model,
        timeout_s=config.provider_timeout_s,
        retries=config.provider_retries,
        host="http://localhost:11434",
    )

    agent = Agent(
        name="ForgeBuilder",
        role="Senior Python Architect",
        goal="Write a hello world FastAPI app",
        tools=[tool],
        memory=memory,
        provider=provider,
    )

    engine = Engine(max_iterations=config.max_iterations, max_retries=config.max_retries, logger=logger)
    result = await engine.run(agent, initial_input="Create the app code and explain it briefly.")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
