from __future__ import annotations

import inspect
import os
import sys
import hashlib
import traceback
from importlib.metadata import entry_points
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Dict, Type, Any, Optional

from .calculator import Calculator
from .filereader import FileReader
from .websearch import WebSearch
from .base import Tool


# -----------------------
# Debug helpers
# -----------------------
def _debug_enabled() -> bool:
    v = os.getenv("AGENTIK_DEBUG_TOOLS", "")
    return v not in ("", "0", "false", "False")

def _dbg(msg: str) -> None:
    if _debug_enabled():
        print(f"[agentik.tools] {msg}", file=sys.stderr)


# -----------------------
# Built-ins
# -----------------------
def builtin_tools() -> Dict[str, Type[Tool]]:
    return {
        "calculator": Calculator,
        "filereader": FileReader,
        "websearch": WebSearch,
    }


def _safe_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _looks_like_tool(cls: Any) -> bool:
    """
    Duck-typing check: must be a class with a callable run(...) and a non-empty string `name`.
    """
    if not inspect.isclass(cls):
        return False
    run = getattr(cls, "run", None)
    if not callable(run):
        return False
    name = getattr(cls, "name", None)
    if not isinstance(name, str) or not name.strip():
        return False
    return True


def _register_tool(found: Dict[str, Type[Tool]], cls: Type[Any], fallback_name: str = "") -> None:
    if not _looks_like_tool(cls):
        return
    name = _safe_lower(getattr(cls, "name", None)) or _safe_lower(fallback_name) or _safe_lower(cls.__name__)
    if not name:
        return
    # last-in wins → local overrides can shadow built-ins/plugins
    found[name] = cls  # type: ignore[assignment]


# -----------------------
# Discovery helpers
# -----------------------
def _discover_entrypoint_tools(found: Dict[str, Type[Tool]]) -> None:
    """
    Discover tools installed via Python entry points: group="agentik.tools".
    """
    try:
        eps = entry_points(group="agentik.tools")  # 3.10+
    except TypeError:
        eps = entry_points().get("agentik.tools", [])  # older API
    for ep in eps:
        try:
            cls = ep.load()
            _register_tool(found, cls, fallback_name=ep.name)
        except Exception:
            _dbg(f"entrypoint load failed for {getattr(ep, 'name', '?')}: {traceback.format_exc().strip()}")


def _search_dirs(root: Path) -> list[Path]:
    """
    Build the ordered list of directories to scan for local tools:
      1) <project>/tools
      2) <project>/.agentik/tools
      3) $HOME/.agentik/tools
      4) any extra paths from AGENTIK_TOOLS_PATHS (os.pathsep-separated)
    """
    candidates = [
        root / "tools",
        root / ".agentik" / "tools",
        Path.home() / ".agentik" / "tools",
    ]
    extra = os.getenv("AGENTIK_TOOLS_PATHS", "")
    for s in extra.split(os.pathsep):
        s = s.strip()
        if s:
            candidates.append(Path(s).expanduser())

    # de-duplicate while preserving order
    seen: set[str] = set()
    ordered: list[Path] = []
    for p in candidates:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            ordered.append(p)
    return ordered


def _discover_local_tools(found: Dict[str, Type[Tool]], root: Path) -> None:
    """
    Discover user/project-local tools from:
      - ./tools/*.py
      - ./.agentik/tools/*.py
      - ~/.agentik/tools/*.py
      - and any AGENTIK_TOOLS_PATHS entries

    This lets a developer scaffold a tool and use it immediately WITHOUT publishing
    a package or registering an entry point.
    """
    for p in _search_dirs(root):
        if not p.is_dir():
            continue
        _dbg(f"scanning: {p}")
        for file in sorted(p.glob("*.py")):
            stem = file.stem
            if stem.startswith("_") or stem in {"base", "registry"}:
                continue
            mod_name = f"agentik_local_tools.{stem}_{hashlib.sha1(str(file).encode('utf-8')).hexdigest()[:8]}"
            try:
                spec = spec_from_file_location(mod_name, file)
                if not spec or not spec.loader:
                    _dbg(f"no spec/loader for {file}")
                    continue
                mod = module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            except Exception:
                _dbg(f"import failed for {file} → {traceback.format_exc().strip()}")
                continue

            for _, obj in inspect.getmembers(mod, inspect.isclass):
                _register_tool(found, obj, fallback_name=stem)


# -----------------------
# Public API
# -----------------------
def discover_tools() -> Dict[str, Type[Tool]]:
    """
    Unified discovery order (later can override earlier on name clash):
      1) Built-ins (shipped with agentik)
      2) Third-party plugins (entry points)
      3) Local user/project tools (./tools, ./.agentik/tools, ~/.agentik/tools, + env)
    """
    found: Dict[str, Type[Tool]] = {}

    # 1) built-ins
    for k, v in builtin_tools().items():
        _register_tool(found, v, fallback_name=k)

    # 2) installed plugins via entry points
    _discover_entrypoint_tools(found)

    # 3) local project/user tools
    _discover_local_tools(found, Path.cwd())

    return found


def instantiate(name: str, **kwargs: Any) -> Tool:
    tools = discover_tools()
    key = _safe_lower(name)
    if key not in tools:
        raise KeyError(f"Unknown tool: {name}")
    return tools[key](**kwargs)
