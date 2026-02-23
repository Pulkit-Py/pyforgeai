"""Basic runtime metrics collection."""

from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass(slots=True)
class Metrics:
    """Minimal metrics container for latency and token placeholders."""

    total_steps: int = 0
    total_latency_ms: float = 0.0
    token_usage: int = 0
    provider_calls: int = 0
    tool_calls: int = 0
    _started_at: float = field(default=0.0, repr=False)

    def start_step(self) -> None:
        self._started_at = time.perf_counter()

    def end_step(self) -> None:
        elapsed = (time.perf_counter() - self._started_at) * 1000
        self.total_steps += 1
        self.total_latency_ms += elapsed

    def track_tokens(self, count: int) -> None:
        self.token_usage += max(count, 0)

    def track_provider_calls(self, count: int = 1) -> None:
        self.provider_calls += max(count, 0)

    def track_tool_calls(self, count: int = 1) -> None:
        self.tool_calls += max(count, 0)

    @property
    def average_latency_ms(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return self.total_latency_ms / self.total_steps

    def snapshot(self) -> dict[str, float | int]:
        return {
            "total_steps": self.total_steps,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "token_usage": self.token_usage,
            "provider_calls": self.provider_calls,
            "tool_calls": self.tool_calls,
        }
