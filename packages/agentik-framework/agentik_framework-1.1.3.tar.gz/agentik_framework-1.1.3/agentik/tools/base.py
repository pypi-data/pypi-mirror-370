from __future__ import annotations
from typing import Protocol, Any, Dict

class Tool(Protocol):
    """Simple tool protocol: a name, descr, and a run(**kwargs) -> Any."""
    name: str
    description: str
    def run(self, **kwargs: Any) -> Any: ...

class ToolBase:
    """Optional convenience base with common helpers."""
    name: str = "tool"
    description: str = ""
    def run(self, **kwargs: Any) -> Any:  # pragma: no cover
        raise NotImplementedError()
    @staticmethod
    def as_dict(result: Any) -> Dict[str, Any]:
        return result if isinstance(result, dict) else {"result": result}
