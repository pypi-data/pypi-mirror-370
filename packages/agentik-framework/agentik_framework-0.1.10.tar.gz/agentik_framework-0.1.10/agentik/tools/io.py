from __future__ import annotations

import json
from typing import Any, Dict


def shape_tool_result(tool_name: str, result: Any) -> Dict[str, Any]:
    """
    Normalize any tool output into a consistent envelope:
      {
        "ok": bool,
        "data": <arbitrary JSON-serializable>,
        "error": str | None,
        "meta": {"tool": tool_name}
      }
    If the tool already returns this shape, keep it, just ensure meta.tool.
    """
    # Already shaped?
    if isinstance(result, dict) and "ok" in result and ("data" in result or "error" in result):
        shaped = dict(result)  # shallow copy
        meta = shaped.get("meta") or {}
        if "tool" not in meta:
            meta["tool"] = tool_name
        shaped["meta"] = meta
        # Ensure fields exist
        shaped.setdefault("error", None if shaped.get("ok") else (shaped.get("error") or ""))
        shaped.setdefault("data", None)
        return shaped

    # Best-effort wrap
    return {
        "ok": True,
        "data": result,
        "error": None,
        "meta": {"tool": tool_name},
    }


def summarize_for_observation(payload: Any, max_chars: int = 1200) -> str:
    """
    Produce a compact string preview for planner context.
    """
    try:
        s = json.dumps(payload, ensure_ascii=False)
    except Exception:
        s = str(payload)
    if len(s) > max_chars:
        return s[:max_chars] + "…"
    return s
