"""Core agent implementation."""

from __future__ import annotations

import ast
import json
import re
from typing import Sequence

from forgeai.memory.base import BaseMemory
from forgeai.providers.base import BaseProvider
from forgeai.schemas.agent_schema import AgentResponse, ToolCall
from forgeai.tools.base import BaseTool


class Agent:
    """Autonomous agent with tools, memory, and provider-backed reasoning."""

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        tools: Sequence[BaseTool],
        memory: BaseMemory,
        provider: BaseProvider,
    ) -> None:
        self.name = name
        self.role = role
        self.goal = goal
        self.tools: list[BaseTool] = list(tools)
        self.memory = memory
        self.provider = provider
        self.last_provider_calls = 0
        self.last_tool_calls = 0

    async def think(self, user_input: str = "") -> str:
        """Build a provider prompt from role, goal, memory, and optional user input."""
        context = await self.memory.get_context(user_input)
        tool_list = ", ".join(tool.name for tool in self.tools) or "none"
        return (
            f"Agent: {self.name}\n"
            f"Role: {self.role}\n"
            f"Goal: {self.goal}\n"
            f"User Input: {user_input or 'N/A'}\n"
            f"Available Tools: {tool_list}\n"
            f"Memory:\n{context}\n\n"
            "Respond as JSON with keys: thought (str), "
            "tool_call ({tool, input}) optional, final (str) optional."
        )

    async def act(self, provider_output: str) -> AgentResponse:
        """Parse provider output into a structured response."""
        candidate = self._extract_json(provider_output)
        if candidate:
            validated = self._validate_payload(candidate)
            if validated:
                return validated

        try:
            payload = json.loads(provider_output)
            parsed = AgentResponse.model_validate(payload)
            return parsed
        except Exception:  # noqa: BLE001
            return AgentResponse(final=provider_output)

    async def run(self, user_input: str = "") -> str:
        """
        Execute one full agent cycle:
        1) Build prompt
        2) Query provider
        3) Detect and execute tool call
        4) Persist results in memory
        5) Return final output
        """
        self.last_provider_calls = 0
        self.last_tool_calls = 0
        if user_input.strip():
            await self.memory.add(f"UserInput => {user_input}")

        prompt = await self.think(user_input)
        raw = await self.provider.generate(prompt)
        self.last_provider_calls += 1
        parsed = await self.act(raw)

        if parsed.tool_call:
            tool_result = await self._run_tool(parsed.tool_call)
            self.last_tool_calls += 1
            await self.memory.add(f"Tool[{parsed.tool_call.tool}] => {tool_result}")

            follow_up_prompt = (
                f"{prompt}\n\nTool result:\n{tool_result}\n"
                "Provide final answer as JSON with 'final' key."
            )
            raw_follow_up = await self.provider.generate(follow_up_prompt)
            self.last_provider_calls += 1
            parsed_follow_up = await self.act(raw_follow_up)
            final = parsed_follow_up.final or raw_follow_up
            await self.memory.add(final)
            return final

        final = parsed.final or raw
        await self.memory.add(final)
        return final

    async def _run_tool(self, call: ToolCall) -> str:
        for tool in self.tools:
            if tool.name == call.tool:
                return await tool.run(call.input)
        return f"Tool '{call.tool}' not found."

    @staticmethod
    def _extract_json(content: str) -> dict[str, object] | None:
        if not content.strip():
            return None

        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            return None

        candidate = match.group(0)
        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, dict):
                return loaded
            return None
        except Exception:
            pass

        try:
            loaded_literal = ast.literal_eval(candidate)
            if isinstance(loaded_literal, dict):
                return loaded_literal
        except Exception:
            return None
        return None

    @staticmethod
    def _validate_payload(payload: dict[str, object]) -> AgentResponse | None:
        tool_name = payload.get("tool")
        tool_input = payload.get("tool_input")
        if tool_name and tool_input and "tool_call" not in payload:
            payload = {
                **payload,
                "tool_call": {"tool": str(tool_name), "input": str(tool_input)},
            }
        try:
            return AgentResponse.model_validate(payload)
        except Exception:
            return None
