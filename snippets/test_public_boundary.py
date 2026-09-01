import json
import subprocess
from pathlib import Path

import pytest

from snippets.check_public_boundary import violations


def test_public_boundary_is_clean() -> None:
    assert violations(Path(__file__).resolve().parents[1]) == []


@pytest.fixture()
def tracked_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    return tmp_path


def track(repo: Path, relative: str, content: str = "fixture\n") -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "-f", relative], cwd=repo, check=True)


@pytest.mark.parametrize(
    "relative",
    [
        "governance/judge_ledger.jsonl",
        "governance/harden_capability_evidence/run/per_case_outputs.jsonl",
        ".private-state/governance/judge_outcomes.jsonl",
        "elsewhere/judge_issuance.jsonl",
    ],
)
def test_live_governance_state_is_forbidden_anywhere(
    tracked_repo: Path, relative: str
) -> None:
    track(tracked_repo, relative)
    assert relative in violations(tracked_repo)


def test_empty_public_capability_registry_is_allowed(tracked_repo: Path) -> None:
    registry = {
        "$schema": "internal://harden-capability-registry/v1",
        "schema_version": 1,
        "purpose": "hardening-gate-verdict",
        "qualifications": [],
    }
    track(
        tracked_repo,
        "config/harden_capability_registry.json",
        json.dumps(registry),
    )
    assert violations(tracked_repo) == []


def test_live_capability_registry_is_forbidden(tracked_repo: Path) -> None:
    registry = {
        "$schema": "internal://harden-capability-registry/v1",
        "schema_version": 1,
        "purpose": "hardening-gate-verdict",
        "qualifications": [
            {
                "receipt_id": "live-run",
                "receipt_hash": "sha256:" + "a" * 64,
            }
        ],
    }
    track(
        tracked_repo,
        "config/harden_capability_registry.json",
        json.dumps(registry),
    )
    assert "config/harden_capability_registry.json" in violations(tracked_repo)


def policy(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "$schema": "internal://harden-eval-policy/v1",
        "schema_version": 1,
        "purpose": "hardening-gate-verdict",
        "ratified": False,
        "ratified_at": None,
        "ratifier": None,
    }
    value.update(overrides)
    return value


def test_unratified_public_policy_template_is_allowed(tracked_repo: Path) -> None:
    track(
        tracked_repo,
        "config/harden_eval_policy.json",
        json.dumps(policy()),
    )
    assert violations(tracked_repo) == []


@pytest.mark.parametrize(
    "mutation",
    [
        {"ratified": True},
        {"ratifier": "Synthetic Owner"},
        {"ratified_at": "2099-01-01T00:00:00Z"},
    ],
)
def test_public_policy_rejects_mutable_ratification_state(
    tracked_repo: Path, mutation: dict[str, object]
) -> None:
    relative = "config/harden_eval_policy.json"
    track(tracked_repo, relative, json.dumps(policy(**mutation)))
    assert relative in violations(tracked_repo)
