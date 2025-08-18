from __future__ import annotations
import os
from pathlib import Path
from .config import CFG

def _is_within(child: Path, parent: Path) -> bool:
    # Both should be absolute, resolved
    child_r = child.resolve()
    parent_r = parent.resolve()
    try:
        # Python 3.9+: Path.is_relative_to
        return child_r.is_relative_to(parent_r)  # type: ignore[attr-defined]
    except Exception:
        # Fallback: commonpath
        return os.path.commonpath([str(child_r), str(parent_r)]) == str(parent_r)

def ensure_allowed(path: Path) -> Path:
    """
    Validate that an existing path is inside an allowed root.
    Returns the resolved absolute path on success.
    """
    p = path.expanduser().resolve()
    for root in CFG.allowed_roots:
        if _is_within(p, root):
            return p
    raise PermissionError(f"Path not allowed: {p}")

def ensure_allowed_for_write(path: Path) -> Path:
    """
    Validate that a *target* (which may not exist yet) is inside an allowed root.
    Checks the parent directory.
    """
    p = path.expanduser().resolve()
    parent = p if p.is_dir() else p.parent
    for root in CFG.allowed_roots:
        if _is_within(parent, root):
            return p
    raise PermissionError(f"Write path not allowed: {p}")