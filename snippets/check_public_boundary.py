"""Fail when machine-specific or private operational artifacts are tracked."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

FORBIDDEN_PATH_PARTS = (
    "MAC_MIGRATION_PLAN.md",
    "docs/mac_workspace_backup.md",
    "launchd/",
    "mcp_registry.json",
    "backup_mac_workspace.py",
)
FORBIDDEN_PATH_PREFIXES = (
    ".private-state/",
    "governance/",
)
FORBIDDEN_FILENAMES = frozenset(
    {
        "judge_issuance.jsonl",
        "judge_ledger.jsonl",
        "judge_outcomes.jsonl",
        "per_case_outputs.jsonl",
    }
)
PUBLIC_CAPABILITY_REGISTRY = "config/harden_capability_registry.json"
PUBLIC_EVAL_POLICY = "config/harden_eval_policy.json"
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
        if (
            relative.startswith(FORBIDDEN_PATH_PREFIXES)
            or path.name in FORBIDDEN_FILENAMES
            or any(part in relative for part in FORBIDDEN_PATH_PARTS)
        ):
            found.append(relative)
            continue
        if relative == PUBLIC_CAPABILITY_REGISTRY:
            try:
                registry = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                found.append(relative)
                continue
            if registry.get("qualifications") != []:
                found.append(relative)
            continue
        if relative == PUBLIC_EVAL_POLICY:
            try:
                policy = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                found.append(relative)
                continue
            if (
                policy.get("ratified") is not False
                or policy.get("ratified_at") is not None
                or policy.get("ratifier") is not None
            ):
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
