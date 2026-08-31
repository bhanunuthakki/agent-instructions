"""Fail when machine-specific or private operational artifacts are tracked."""

from __future__ import annotations

import subprocess
from pathlib import Path

FORBIDDEN_PATH_PARTS = (
    "MAC_MIGRATION_PLAN.md",
    "docs/mac_workspace_backup.md",
    "launchd/",
    "mcp_registry.json",
    "backup_mac_workspace.py",
)
FORBIDDEN_TEXT = ("/Users/", "/home/", "C:\\Users\\")


def tracked_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=repo, check=True, capture_output=True
    )
    return [repo / item for item in result.stdout.decode().split("\0") if item]


def violations(repo: Path) -> list[str]:
    found: list[str] = []
    for path in tracked_files(repo):
        relative = path.relative_to(repo).as_posix()
        if not path.exists():
            continue
        if any(part in relative for part in FORBIDDEN_PATH_PARTS) and not relative.endswith(".gitkeep"):
            found.append(relative)
            continue
        if relative == "snippets/check_public_boundary.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(marker in text for marker in FORBIDDEN_TEXT):
            found.append(relative)
    return found


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    bad = violations(repo)
    if bad:
        raise SystemExit("Public-boundary violations: " + ", ".join(bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
