<!-- Header -->
<p align="center">
  <h1 align="center">PYFORGEAI</h1>
  <h4 align="center">AI AGENT FRAMEWORK</h4>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.1.0-green?style=for-the-badge" alt="version">
  <img src="https://img.shields.io/github/license/Pulkit-Py/pyforgeai?style=for-the-badge" alt="license">
  <img src="https://img.shields.io/github/stars/Pulkit-Py/pyforgeai?style=for-the-badge" alt="stars">
  <img src="https://img.shields.io/github/issues/Pulkit-Py/pyforgeai?color=red&style=for-the-badge" alt="issues">
  <img src="https://img.shields.io/github/forks/Pulkit-Py/pyforgeai?color=teal&style=for-the-badge" alt="forks">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Author-Pulkit--py-cyan?style=flat-square" alt="author">
  <img src="https://img.shields.io/badge/Open%20Source-Yes-cyan?style=flat-square" alt="open source">
  <img src="https://img.shields.io/badge/MADE%20IN-INDIA-blue?colorA=%23ff0000&colorB=%23017e40&style=flat-square" alt="made in india">
  <img src="https://img.shields.io/badge/Written%20In-Python-cyan?style=flat-square" alt="python">
</p>

`pyforgeai` is the PyPI package for the `forgeai` Python framework, a lightweight production-first toolkit for building autonomous AI agents with:
- async execution
- pluggable tools
- memory abstraction
- multi-provider LLM support
- structured observability
- simple orchestration

It is designed for clean architecture and easy extension, without unnecessary abstractions.

Repository: https://github.com/Pulkit-Py/pyforgeai

## Table of Contents
- [Why pyforgeai](#why-pyforgeai)
- [Author and Profiles](#author-and-profiles)
- [Core Concepts](#core-concepts)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Providers](#providers)
- [FastAPI Integration](#fastapi-integration)
- [Observability](#observability)
- [Testing and Quality](#testing-and-quality)
- [How to Extend](#how-to-extend)
- [Current Limitations](#current-limitations)
- [Troubleshooting](#troubleshooting)

## Why pyforgeai
- Async-first runtime (`asyncio`) for modern Python services.
- Strong typing and Pydantic schemas for reliable interfaces.
- Minimal, modular architecture that is easy to reason about.
- Provider-agnostic model layer (`BaseProvider`).
- Developer-friendly defaults and fallbacks for local/offline development.

## Author and Profiles
- GitHub: https://github.com/Pulkit-Py
- Instagram: https://www.instagram.com/pulkit_py/
- LinkedIn: https://www.linkedin.com/in/pulkit-py/

## Core Concepts
- `Agent`: reasons over goal + role + memory + user input, then optionally calls tools.
- `Engine`: controls retries, iteration limits, early stop behavior, and metrics.
- `BaseTool`: async tool interface (`run(input: str) -> str`).
- `BaseMemory`: async memory interface (`add`, `get_context`).
- `BaseProvider`: async LLM interface (`generate(prompt: str) -> str`).
- `AgentTeam`: sequential multi-agent orchestration (output of agent A -> input of agent B).

## Project Structure
```text
forgeai/
├── agent/
│   └── base.py
├── config.py
├── engine/
│   └── engine.py
├── memory/
│   ├── base.py
│   └── short_term.py
├── observability/
│   ├── logger.py
│   └── metrics.py
├── orchestration/
│   └── team.py
├── providers/
│   ├── base.py
│   ├── factory.py
│   ├── openai_provider.py
│   ├── ollama_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   ├── deepseek_provider.py
│   └── grok_provider.py
├── schemas/
│   └── agent_schema.py
└── tools/
    ├── base.py
    └── python_tool.py
```

## Installation

### 1) Python version
- Python `3.11+` is required.

### 2) Install package
```bash
pip install -e .
```

Install from PyPI:
```bash
pip install pyforgeai
```

### 3) Install provider extras (optional)
```bash
pip install -e .[ollama]
pip install -e .[openai]
pip install -e .[anthropic]
pip install -e .[gemini]
pip install -e .[api]
```

### 4) Full development install
```bash
pip install -e .[dev,all]
```

## Quick Start

### Run local example
`example_usage.py` uses provider factory + environment config.

```bash
python example_usage.py
```

By default, this project is configured for Ollama local usage in `forgeai/config.py`.

## Configuration
Configuration is loaded via `ForgeAIConfig.from_env()` from `forgeai/config.py`.

Supported env vars:
- `FORGEAI_DEFAULT_PROVIDER` (default: `ollama`)
- `FORGEAI_DEFAULT_MODEL` (default: `qwen3:4b`)
- `FORGEAI_PROVIDER_TIMEOUT_S` (default: `30.0`)
- `FORGEAI_PROVIDER_RETRIES` (default: `1`)
- `FORGEAI_MAX_ITERATIONS` (default: `5`)
- `FORGEAI_MAX_RETRIES` (default: `2`)
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `DEEPSEEK_API_KEY`
- `XAI_API_KEY`

Example:
```bash
set FORGEAI_DEFAULT_PROVIDER=ollama
set FORGEAI_DEFAULT_MODEL=qwen3:4b
set FORGEAI_MAX_ITERATIONS=2
python example_usage.py
```

## Providers

Use `create_provider(...)` from `forgeai.providers.factory`:

```python
from forgeai.providers.factory import create_provider

provider = create_provider("ollama", model="qwen3:4b", host="http://localhost:11434")
```

Supported names:
- `openai`
- `ollama`
- `anthropic`
- `gemini`
- `deepseek`
- `grok` (or `xai`)

All providers implement:
```python
class BaseProvider:
    async def generate(self, prompt: str) -> str: ...
```

## FastAPI Integration
A ready example exists at `examples/fastapi_app.py`.

Run:
```bash
uvicorn examples.fastapi_app:app --reload
```

Endpoints:
- `GET /health`
- `POST /run`

Request body example:
```json
{
  "prompt": "Write a hello world FastAPI app",
  "provider": "ollama",
  "model": "qwen3:4b"
}
```

## Observability
`forgeai` includes JSON structured logging and basic metrics:
- per-step latency
- token usage placeholder
- provider/tool call counters
- run correlation id in engine logs

Use logger:
```python
from forgeai.observability.logger import get_logger

logger = get_logger("forgeai-service")
```

## Testing and Quality

Run checks:
```bash
ruff check .
mypy forgeai
pytest -q
```

Current test coverage includes:
- memory behavior
- agent tool-flow behavior
- engine early-stop behavior
- provider factory and fallback behavior

## How to Extend

### Add a custom tool
```python
from forgeai.tools.base import BaseTool

class MyTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="my_tool", description="Does something useful")

    async def run(self, input: str) -> str:
        return f"processed: {input}"
```

### Add a custom memory backend
Implement `BaseMemory`:
- `async add(entry: str) -> None`
- `async get_context(query: str) -> str`

### Add a new provider
Implement `BaseProvider.generate(prompt: str) -> str`, then register it in:
- `forgeai/providers/factory.py`
- `forgeai/providers/__init__.py`

## Current Limitations
- `PythonTool` uses `exec` and is not sandboxed. For untrusted input, run in an isolated runtime.
- Metrics are intentionally lightweight and not yet integrated with Prometheus/OpenTelemetry.
- Memory is short-term in-process only (no persistent/vector memory by design right now).

## Troubleshooting

- `No module named pytest`
  - Install dev deps: `pip install -e .[dev]`

- Provider returns fallback response
  - Check API key env vars.
  - Ensure relevant SDK is installed (`pip install -e .[provider]`).

- Ollama connection issues
  - Ensure Ollama is running locally and model is pulled.
  - Verify host URL (`http://localhost:11434` by default).

## License
MIT

## Support
If you found this project helpful, consider:
- Giving it a ⭐ on GitHub
- Following me on social media
- Sharing it with others who might find it useful

GitHub Repository: https://github.com/Pulkit-Py/pyforgeai

For support, please open an issue on the GitHub repository.

---
Made with love by [GitHub](https://github.com/Pulkit-Py) | [Instagram](https://www.instagram.com/pulkit_py/) | [LinkedIn](https://www.linkedin.com/in/pulkit-py/) in India.
