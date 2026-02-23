from __future__ import annotations

from forgeai.memory.short_term import ShortTermMemory


async def test_short_term_memory_add_and_retrieve() -> None:
    memory = ShortTermMemory(max_entries=3, context_window=2)
    await memory.add("user asked about fastapi")
    await memory.add("tool returned hello world app")
    await memory.add("agent finalized response")

    context = await memory.get_context("fastapi app")
    assert "fastapi" in context.lower()


async def test_short_term_memory_respects_max_entries() -> None:
    memory = ShortTermMemory(max_entries=2, context_window=2)
    await memory.add("one")
    await memory.add("two")
    await memory.add("three")

    context = await memory.get_context("")
    assert "one" not in context
    assert "two" in context
    assert "three" in context
