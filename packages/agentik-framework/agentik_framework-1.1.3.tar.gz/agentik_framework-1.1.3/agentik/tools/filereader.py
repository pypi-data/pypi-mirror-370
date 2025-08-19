from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from .base import ToolBase

class FileReader(ToolBase):
    name = "filereader"
    description = "Read text from a file path. Honors allow_filesystem flag."
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "encoding": {"type": "string"},
            "max_bytes": {"type": "integer"},
            "allow_filesystem": {"type": "boolean"}
        },
        "required": ["path"],
        "additionalProperties": True
    }

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        if not kwargs.get("allow_filesystem", True):
            return {"ok": False, "error": "Filesystem access disabled by policy."}
        path = kwargs.get("path")
        if not path:
            raise ValueError("Missing 'path'")
        enc = kwargs.get("encoding", "utf-8")
        max_bytes = kwargs.get("max_bytes")
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Not found: {p}")
        data = p.read_bytes()
        if isinstance(max_bytes, int) and max_bytes > 0:
            data = data[:max_bytes]
        text = data.decode(enc, errors="replace")
        return {"ok": True, "path": str(p), "text": text}
