"""Pydantic schemas for agent I/O."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Model for provider-suggested tool execution."""

    tool: str = Field(description="Tool name to execute.")
    input: str = Field(description="Tool input payload.")


class AgentResponse(BaseModel):
    """Normalized structured response from agent execution."""

    status: Literal["in_progress", "completed"] = Field(
        default="completed",
        description="Execution status for orchestration engines.",
    )
    thought: str | None = Field(default=None, description="Optional reasoning summary.")
    tool_call: ToolCall | None = Field(default=None, description="Optional tool call.")
    final: str | None = Field(default=None, description="Final user-facing response.")
