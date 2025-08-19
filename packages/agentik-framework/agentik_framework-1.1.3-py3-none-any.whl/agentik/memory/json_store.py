from __future__ import annotations
import json
from typing import List, Dict, Any
from pathlib import Path

class JSONMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def remember(self, event: Dict[str, Any]) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data.append(event)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def recall(self, n: int = 10) -> List[Dict[str, Any]]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data[-n:]

    def clear(self) -> None:
        self.path.write_text("[]", encoding="utf-8")

    def summarize(self, n: int = 20, max_chars: int = 1200) -> str:
        items = self.recall(n)
        out = []
        for i, e in enumerate(items, 1):
            role = e.get("role", e.get("name", "event"))
            content = e.get("content") or e.get("text") or str(e)
            out.append(f"{i}. {role}: {content}")
        s = "\n".join(out)
        return s[:max_chars]
