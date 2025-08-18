from __future__ import annotations

import time
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Set


_DEFAULT_EXCLUDES = [
    ".git/**", ".hg/**", ".svn/**",
    "__pycache__/**", "*.pyc", "*.pyo",
    ".mypy_cache/**", ".pytest_cache/**",
    ".ruff_cache/**",
    ".venv/**", "venv/**", "env/**",
    "node_modules/**",
    ".idea/**", ".vscode/**",
    ".DS_Store",
    "runs/**",
]


def _normalize_globs(globs: Iterable[str]) -> List[str]:
    return [g.replace("\\", "/") for g in globs]


def _match_any(path: Path, patterns: List[str]) -> bool:
    p = path.as_posix()
    return any(fnmatch(p, pat) for pat in patterns)


def _iter_files(paths: Iterable[Path]) -> Iterator[Path]:
    for base in paths:
        if base.is_file():
            yield base
        elif base.is_dir():
            for f in base.rglob("*"):
                if f.is_file():
                    yield f


def _visible_files(
    roots: List[Path],
    include_globs: List[str],
    exclude_globs: List[str],
) -> List[Path]:
    inc = _normalize_globs(include_globs) if include_globs else ["**/*"]
    exc = _normalize_globs(_DEFAULT_EXCLUDES + (exclude_globs or []))

    files: List[Path] = []
    for f in _iter_files(roots):
        if not _match_any(f, inc):
            continue
        if _match_any(f, exc):
            continue
        files.append(f)
    return files


def watch_for_changes(
    paths: List[str],
    include: List[str] | None = None,
    exclude: List[str] | None = None,
    interval: float = 0.6,
    debounce: float = 0.5,
) -> Iterator[Set[Path]]:
    """
    Polling-based watcher. Yields a set of changed file paths after debouncing.
    """
    roots = [Path(p).resolve() for p in (paths or ["."])]
    mtimes: Dict[Path, float] = {}

    # prime
    for f in _visible_files(roots, include or ["**/*"], exclude or []):
        try:
            mtimes[f] = f.stat().st_mtime
        except FileNotFoundError:
            pass

    while True:
        changed: Set[Path] = set()
        current_files = _visible_files(roots, include or ["**/*"], exclude or [])

        # detect deletions/new files/changes
        current_set = set(current_files)
        known_set = set(mtimes.keys())

        # new or modified
        for f in current_set:
            try:
                m = f.stat().st_mtime
            except FileNotFoundError:
                continue
            old = mtimes.get(f)
            if old is None or m > old:
                mtimes[f] = m
                changed.add(f)

        # deleted
        for f in known_set - current_set:
            mtimes.pop(f, None)
            changed.add(f)

        if changed:
            # debounce burst of quick writes
            t0 = time.time()
            union = set(changed)
            while time.time() - t0 < debounce:
                time.sleep(min(interval, 0.2))
                burst: Set[Path] = set()
                current_files = _visible_files(roots, include or ["**/*"], exclude or [])
                for f in current_files:
                    try:
                        m = f.stat().st_mtime
                    except FileNotFoundError:
                        continue
                    old = mtimes.get(f)
                    if old is None or m > old:
                        mtimes[f] = m
                        burst.add(f)
                union |= burst
            yield union
        time.sleep(interval)
