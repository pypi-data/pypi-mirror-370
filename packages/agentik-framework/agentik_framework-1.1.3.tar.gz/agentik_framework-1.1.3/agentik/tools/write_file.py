from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


class WriteFileTool:
    """
    Safe writer for small artifacts. Sandboxes to CWD by default.
    Honors policy: allow_filesystem (bool).
    """

    name = "write_file"
    description = "Write text content to a file with sandboxing and overwrite controls."
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target path (relative to CWD by default)"},
            "content": {"type": "string", "description": "Text content to write"},
            "encoding": {"type": "string", "default": "utf-8"},
            "overwrite": {"type": "boolean", "default": False},
            "allow_abs": {"type": "boolean", "default": False, "description": "Allow absolute paths (still guarded)"},
            "allow_filesystem": {"type": "boolean", "default": False},
        },
        "required": ["path", "content"]
    }

    _DISALLOWED_PREFIXES_POSIX = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/etc", "/dev", "/proc", "/sys"]
    _DISALLOWED_PREFIXES_WIN = [r"C:\Windows", r"C:\Program Files", r"C:\Program Files (x86)"]

    def _is_system_path(self, p: Path) -> bool:
        sp = str(p.resolve())
        if os.name == "nt":
            for pref in self._DISALLOWED_PREFIXES_WIN:
                if sp.lower().startswith(pref.lower()):
                    return True
        else:
            for pref in self._DISALLOWED_PREFIXES_POSIX:
                if sp.startswith(pref):
                    return True
        return False

    def run(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        overwrite: bool = False,
        allow_abs: bool = False,
        allow_filesystem: bool = False,
        **_: Any,
    ) -> Dict[str, Any]:
        if not allow_filesystem:
            return {
                "ok": False,
                "data": None,
                "error": "Filesystem is disabled by policy (allow_filesystem=False).",
                "meta": {"tool": self.name},
            }

        raw = Path(path)
        cwd = Path.cwd().resolve()

        if raw.is_absolute():
            if not allow_abs:
                return {
                    "ok": False,
                    "data": None,
                    "error": "Absolute paths are not allowed (set allow_abs=True to permit).",
                    "meta": {"tool": self.name},
                }
            target = raw.resolve()
        else:
            target = (cwd / raw).resolve()

        # sandbox: must stay within CWD if not explicitly absolute
        if not allow_abs:
            try:
                target.relative_to(cwd)
            except Exception:
                return {
                    "ok": False,
                    "data": None,
                    "error": "Refusing to write outside the working directory.",
                    "meta": {"tool": self.name},
                }

        # system directories guard
        if self._is_system_path(target):
            return {
                "ok": False,
                "data": None,
                "error": f"Refusing to write into protected system path: {target}",
                "meta": {"tool": self.name},
            }

        if target.exists() and not overwrite:
            return {
                "ok": False,
                "data": None,
                "error": f"Target already exists: {target}. Use overwrite=True to replace.",
                "meta": {"tool": self.name},
            }

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding=encoding, newline="") as f:
                f.write(content)
            return {
                "ok": True,
                "data": {"path": str(target), "bytes_written": len(content.encode(encoding))},
                "error": None,
                "meta": {"tool": self.name},
            }
        except Exception as e:
            return {
                "ok": False,
                "data": None,
                "error": f"Write failed: {e}",
                "meta": {"tool": self.name},
            }
