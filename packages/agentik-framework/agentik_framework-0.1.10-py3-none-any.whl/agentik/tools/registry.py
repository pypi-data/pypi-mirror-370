from __future__ import annotations

import inspect
import os
import sys
from importlib import import_module
from importlib.metadata import entry_points
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from typing import Dict, Type, Any, Optional

from .calculator import Calculator
from .filereader import FileReader
from .websearch import WebSearch
from .base import Tool


def builtin_tools() -> Dict[str, Type[Tool]]:
    # Built-ins shipped with the package
    return {
        "calculator": Calculator,
        "filereader": FileReader,
        "websearch": WebSearch,
    }


def _safe_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _register_tool(found: Dict[str, Type[Tool]], cls: Type[Tool], fallback_name: str = "") -> None:
    if not inspect.isclass(cls) or not issubclass(cls, Tool) or cls is Tool:
        return
    name = _safe_lower(getattr(cls, "name", None)) or _safe_lower(fallback_name) or _safe_lower(cls.__name__)
    if not name:
        return
    found[name] = cls


def _discover_entrypoint_tools(found: Dict[str, Type[Tool]]) -> None:
    """
    Discover tools installed as plugins via Python entry points (agentik.tools).
    This supports third-party packages installed from PyPI.
    """
    try:
        eps = entry_points(group="agentik.tools")  # Python 3.10+
    except TypeError:
        eps = entry_points().get("agentik.tools", [])  # older API
    for ep in eps:
        try:
            cls = ep.load()
            _register_tool(found, cls, fallback_name=ep.name)
        except Exception:
            # Don't break global discovery if one plugin fails
            continue


def _discover_local_tools(found: Dict[str, Type[Tool]], root: Path) -> None:
    """
    Discover project-local tools from ./tools/*.py in the current working directory.
    This lets users who installed agentik from PyPI scaffold a tool and use it
    immediately without creating a package/entry point.
    """
    tools_dir = root / "tools"
    if not tools_dir.is_dir():
        return

    # Allow overriding/adding search dirs via env (optional)
    extra_dirs = os.getenv("AGENTIK_TOOLS_PATHS", "")
    for p in [tools_dir] + [Path(s).expanduser() for s in extra_dirs.split(os.pathsep) if s.strip()]:
        if not p.is_dir():
            continue

        for file in sorted(p.glob("*.py")):
            # Skip dunder/private and common non-tool files
            stem = file.stem
            if stem.startswith("_") or stem in {"base", "registry"}:
                continue

            # Import module under a unique namespace to avoid collisions
            mod_name = f"agentik_local_tools.{stem}"
            try:
                spec = spec_from_file_location(mod_name, file)
                if not spec or not spec.loader:
                    continue
                mod = module_from_spec(spec)
                # Ensure subsequent imports see this module
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            except Exception:
                # Don't fail discovery if one local file has errors
                continue

            # Register every subclass of Tool defined in this module
            for _, obj in inspect.getmembers(mod, inspect.isclass):
                if issubclass(obj, Tool) and obj is not Tool:
                    _register_tool(found, obj, fallback_name=stem)


def discover_tools() -> Dict[str, Type[Tool]]:
    """
    Unified discovery:
      1) Built-in tools (shipped with agentik)
      2) Third-party tools installed via entry points (agentik.tools)
      3) Project-local tools in ./tools/*.py (CWD), for immediate local use
    Local tools take precedence over built-ins/plugins on name clashes.
    """
    found: Dict[str, Type[Tool]] = {}

    # 1) built-ins
    for k, v in builtin_tools().items():
        _register_tool(found, v, fallback_name=k)

    # 2) installed plugins via entry points
    _discover_entrypoint_tools(found)

    # 3) local project tools (current working directory)
    _discover_local_tools(found, Path.cwd())

    return found


def instantiate(name: str, **kwargs: Any) -> Tool:
    tools = discover_tools()
    key = _safe_lower(name)
    if key not in tools:
        raise KeyError(f"Unknown tool: {name}")
    return tools[key](**kwargs)
