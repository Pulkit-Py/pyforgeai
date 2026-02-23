"""Built-in Python execution tool."""

from __future__ import annotations

import asyncio
from contextlib import redirect_stdout
from io import StringIO
import traceback

from forgeai.tools.base import BaseTool


class PythonTool(BaseTool):
    """Executes Python snippets in-process with best-effort output capture."""

    def __init__(self) -> None:
        super().__init__(
            name="python",
            description="Execute Python code and return captured stdout or errors.",
        )

    async def run(self, input: str) -> str:
        """Run Python code asynchronously by offloading to a worker thread."""
        return await asyncio.to_thread(self._execute, input)

    @staticmethod
    def _execute(code: str) -> str:
        buffer = StringIO()
        local_scope: dict[str, object] = {}
        try:
            with redirect_stdout(buffer):
                exec(code, {"__builtins__": __builtins__}, local_scope)
            output = buffer.getvalue().strip()
            return output or "Execution completed with no output."
        except Exception:  # noqa: BLE001
            return traceback.format_exc().strip()

