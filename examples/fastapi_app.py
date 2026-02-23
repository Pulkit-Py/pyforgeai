"""FastAPI integration example for forgeai."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from forgeai.agent.base import Agent
from forgeai.engine.engine import Engine
from forgeai.memory.short_term import ShortTermMemory
from forgeai.observability.logger import get_logger
from forgeai.providers.factory import create_provider
from forgeai.tools.python_tool import PythonTool

app = FastAPI(title="forgeai API", version="0.1.0")
logger = get_logger("forgeai-api")


class RunRequest(BaseModel):
    prompt: str = Field(description="Task input for the agent.")
    provider: str = Field(default="ollama", description="Provider name (openai, ollama, ...).")
    model: str = Field(default="qwen3:4b", description="Model name for selected provider.")


class RunResponse(BaseModel):
    result: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
async def run_agent(payload: RunRequest) -> RunResponse:
    provider = create_provider(payload.provider, model=payload.model)
    agent = Agent(
        name="APIAgent",
        role="Production assistant",
        goal="Solve user requests reliably and clearly.",
        tools=[PythonTool()],
        memory=ShortTermMemory(max_entries=20),
        provider=provider,
    )
    engine = Engine(max_iterations=2, max_retries=1, logger=logger)
    result = await engine.run(agent, initial_input=payload.prompt)
    return RunResponse(result=result)
