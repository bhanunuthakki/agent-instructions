"""Resolve the machine-local state root used by governance runtimes."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

PRIVATE_STATE_ENV = "AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT"
DEFAULT_PRIVATE_STATE_DIR = ".private-state"


def private_state_root(
    repository_root: Path,
    *,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Return one explicit, ignored authority for mutable local state.

    The in-repository default keeps migration simple while `.gitignore` and the
    public-boundary gate keep it out of Git. An override must be absolute so a
    scheduler or another checkout cannot silently write to a different cwd.
    """
    env = os.environ if environ is None else environ
    configured = env.get(PRIVATE_STATE_ENV)
    if not configured:
        return (repository_root / DEFAULT_PRIVATE_STATE_DIR).resolve()
    path = Path(configured).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{PRIVATE_STATE_ENV} must be an absolute path")
    return path.resolve()
