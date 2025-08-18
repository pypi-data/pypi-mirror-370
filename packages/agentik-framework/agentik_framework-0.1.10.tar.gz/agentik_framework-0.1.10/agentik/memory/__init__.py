from __future__ import annotations
from typing import Protocol
from pathlib import Path

from .base import MemoryBase
from .dict_store import DictMemory
from .json_store import JSONMemory

def make_memory(mem_type: str, path: str | None) -> MemoryBase:
    if mem_type == "dict":
        return DictMemory()
    if mem_type == "json":
        return JSONMemory(path or "./memory/agentik.json")
    # default fallback
    return DictMemory()
