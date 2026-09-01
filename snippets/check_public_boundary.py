"""Fail when machine-specific or private operational artifacts are tracked."""

from __future__ import annotations

import json
import re
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
PERSONAL_EMAIL = re.compile(
    r"\b(?:bhanu|nuthakki)[^@\s]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", re.IGNORECASE
)
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
HIGH_CONFIDENCE_SECRET = re.compile(
    r"(?<![A-Za-z0-9])(?:AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}"
    r"|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    r"|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}"
    r"|xox[baprs]-[A-Za-z0-9-]{10,})"
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password)"
    r"\s*[=:]\s*[\"'](?P<value>[^\"'\s]{12,})[\"']",
    re.IGNORECASE,
)
SYNTHETIC_SECRET = re.compile(
    r"(?:dummy|example|fake|fixture|placeholder|redacted|changeme|not-a-real|test-token)",
    re.IGNORECASE,
)
PERSONAL_ACCOUNT_FACT = re.compile(
    r"\b(?:my|owner|personal|brokerage|portfolio|holding|account)\b.{0,80}"
    r"\b(?:cost[ _-]*basis|account[ _-]*balance|position[ _-]*(?:value|size)"
    r"|share[ _-]*quantity|shares|account[ _-]*(?:id|number))\b.{0,40}[$€£]?\d",
    re.IGNORECASE,
)
ACCOUNT_FACT_SUFFIXES = {".csv", ".json", ".md", ".tsv", ".txt", ".yaml", ".yml"}
UNSCANNABLE_PRIVATE_SUFFIXES = {".db", ".docx", ".pdf", ".sqlite", ".xlsx", ".zip"}


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
            or path.suffix.lower() in UNSCANNABLE_PRIVATE_SUFFIXES
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
        has_secret = (
            PRIVATE_KEY.search(text) is not None
            or HIGH_CONFIDENCE_SECRET.search(text) is not None
        )
        if not has_secret:
            has_secret = any(
                not SYNTHETIC_SECRET.search(match.group("value"))
                for match in CREDENTIAL_ASSIGNMENT.finditer(text)
            )
        has_account_fact = (
            path.suffix.lower() in ACCOUNT_FACT_SUFFIXES
            and PERSONAL_ACCOUNT_FACT.search(text) is not None
        )
        if (
            any(marker in text for marker in FORBIDDEN_TEXT)
            or PERSONAL_EMAIL.search(text) is not None
            or has_secret
            or has_account_fact
        ):
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
