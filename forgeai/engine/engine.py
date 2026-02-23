"""Execution engine for managed agent runs."""

from __future__ import annotations

import asyncio
import logging
import uuid

from forgeai.agent.base import Agent
from forgeai.observability.metrics import Metrics


class Engine:
    """Controls retries, iteration limits, logging, and metrics."""

    def __init__(
        self,
        max_iterations: int = 5,
        max_retries: int = 2,
        logger: logging.Logger | None = None,
    ) -> None:
        self.max_iterations = max_iterations
        self.max_retries = max_retries
        self.logger = logger
        self.metrics = Metrics()

    async def run(self, agent: Agent, initial_input: str = "") -> str:
        """Run an agent with retry and max-iteration controls."""
        run_id = str(uuid.uuid4())
        current_input = initial_input
        last_output = ""

        for iteration in range(1, self.max_iterations + 1):
            attempt = 0
            while attempt <= self.max_retries:
                try:
                    self.metrics.start_step()
                    self._log(
                        "info",
                        "engine_step_start",
                        {
                            "run_id": run_id,
                            "agent": agent.name,
                            "iteration": iteration,
                            "attempt": attempt + 1,
                        },
                    )
                    output = await agent.run(current_input)
                    self.metrics.end_step()
                    self.metrics.track_tokens(len(output.split()))
                    self.metrics.track_provider_calls(agent.last_provider_calls)
                    self.metrics.track_tool_calls(agent.last_tool_calls)
                    self._log(
                        "info",
                        "engine_step_complete",
                        {
                            "run_id": run_id,
                            "agent": agent.name,
                            "iteration": iteration,
                            **self.metrics.snapshot(),
                        },
                    )
                    if self._should_stop(output=output, previous_output=last_output):
                        last_output = output
                        self._log(
                            "info",
                            "engine_early_stop",
                            {
                                "run_id": run_id,
                                "agent": agent.name,
                                "iteration": iteration,
                            },
                        )
                        return last_output

                    last_output = output
                    current_input = output
                    break
                except Exception as exc:  # noqa: BLE001
                    attempt += 1
                    self._log(
                        "error",
                        "engine_step_failed",
                        {
                            "run_id": run_id,
                            "agent": agent.name,
                            "iteration": iteration,
                            "attempt": attempt,
                            "error": str(exc),
                        },
                    )
                    if attempt > self.max_retries:
                        raise
                    await asyncio.sleep(0.25 * attempt)

        return last_output

    def _log(self, level: str, message: str, data: dict[str, object]) -> None:
        if not self.logger:
            return
        log_fn = getattr(self.logger, level, self.logger.info)
        log_fn(message, extra={"extra_data": data})

    @staticmethod
    def _should_stop(output: str, previous_output: str) -> bool:
        current = output.strip()
        prior = previous_output.strip()
        if not current:
            return True
        if prior and current == prior:
            return True
        return current.lower().startswith("final:")
