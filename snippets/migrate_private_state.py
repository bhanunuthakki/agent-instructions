#!/usr/bin/env python3
"""Copy legacy tracked governance state to the ignored private state root."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from private_state import private_state_root

ROOT = Path(__file__).resolve().parents[1]
STATE_FILES = (
    Path("governance/judge_ledger.jsonl"),
    Path("governance/judge_issuance.jsonl"),
    Path("governance/judge_outcomes.jsonl"),
    Path("config/harden_capability_registry.json"),
)
STATE_TREES = (
    Path("governance/harden_capability_receipts"),
    Path("governance/harden_capability_evidence"),
)


@dataclass(frozen=True)
class MigrationResult:
    copied: int
    unchanged: int


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_files(source_root: Path) -> list[Path]:
    files = [relative for relative in STATE_FILES if (source_root / relative).is_file()]
    for tree in STATE_TREES:
        root = source_root / tree
        if not root.is_dir():
            continue
        files.extend(
            path.relative_to(source_root)
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.name != ".gitkeep"
        )
    return files


def migrate(source_root: Path, state_root: Path) -> MigrationResult:
    """Copy known mutable files, preserving the source until the Git update.

    Existing identical destinations are accepted. A different destination is
    never overwritten because either side may contain the newer authority.
    """
    copied = 0
    unchanged = 0
    for relative in _source_files(source_root):
        source = source_root / relative
        destination = state_root / relative
        if destination.exists():
            if not destination.is_file() or _digest(destination) != _digest(source):
                raise RuntimeError(
                    f"refusing to overwrite different private state: {relative}"
                )
            unchanged += 1
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if _digest(destination) != _digest(source):
            raise RuntimeError(f"private state verification failed: {relative}")
        copied += 1
    return MigrationResult(copied=copied, unchanged=unchanged)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--state-root", type=Path)
    args = parser.parse_args()
    state_root = args.state_root or private_state_root(args.source_root)
    if not state_root.is_absolute():
        parser.error("--state-root must be an absolute path")
    result = migrate(args.source_root.resolve(), state_root.resolve())
    print(
        "Private-state migration verified: "
        f"{result.copied} copied, {result.unchanged} already identical."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
