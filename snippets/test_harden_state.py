from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

import harden_state
from harden_state import (
    ACTIVE_EXPERTS,
    SCHEMA,
    StateError,
    current_fingerprints,
    overall_outcome,
    preflight,
    run_allowlisted_verifier,
    selected_gates,
    validate_state,
    worktree_fingerprint,
)

INSTRUCTIONS_ROOT = Path(__file__).resolve().parents[1]


def profile(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "deployment": "local",
        "identity": "none",
        "commerce": "personal",
        "surfaces": ["web"],
        "data": ["durable"],
        "llm": "none",
        "scheduled_work": False,
    }
    value.update(overrides)
    return value


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "product"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    (root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "app.py"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
    return root


@pytest.fixture()
def package(tmp_path: Path) -> Path:
    root = tmp_path / "package"
    (root / "runtime").mkdir(parents=True)
    (root / "rubrics").mkdir()
    (root / "config").mkdir()
    (root / "evals").mkdir()
    shutil.copy2(INSTRUCTIONS_ROOT / "procedures" / "harden.md", root / "SKILL.md")
    shutil.copy2(INSTRUCTIONS_ROOT / "snippets" / "harden_state.py", root / "runtime" / "harden_state.py")
    for expert in ACTIVE_EXPERTS:
        shutil.copy2(
            INSTRUCTIONS_ROOT / "procedures" / "agents" / f"{expert}.md",
            root / "rubrics" / f"{expert}.md",
        )
    for name in (
        "harden_state_v2.schema.json",
        "harden_mandatory_rules.json",
        "harden_eval_policy.json",
        "harden_capability_registry.json",
    ):
        shutil.copy2(INSTRUCTIONS_ROOT / "config" / name, root / "config" / name)
    registry_path = root / "config" / "harden_capability_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["qualifications"] = []
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(INSTRUCTIONS_ROOT / "evals" / "harden" / "cases.jsonl", root / "evals" / "cases.jsonl")
    return root


def digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def test_repo_layout_resolves_harden_evidence_from_private_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "instructions"
    repo.mkdir()
    state_root = tmp_path / "private-state"
    monkeypatch.setenv("AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT", str(state_root))
    assert harden_state._config_path(
        repo, "harden_capability_registry.json"
    ) == repo / "config" / "harden_capability_registry.json"
    private_registry = state_root / "config" / "harden_capability_registry.json"
    private_registry.parent.mkdir(parents=True)
    private_registry.write_text("{}", encoding="utf-8")
    assert harden_state._config_path(
        repo, "harden_capability_registry.json"
    ) == private_registry
    assert harden_state._config_path(
        repo, "harden_eval_policy.json"
    ) == repo / "config" / "harden_eval_policy.json"
    private_policy = state_root / "config" / "harden_eval_policy.json"
    private_policy.write_text("{}", encoding="utf-8")
    assert harden_state._config_path(repo, "harden_eval_policy.json") == private_policy
    assert harden_state._receipt_path(repo, "synthetic") == (
        state_root
        / "governance"
        / "harden_capability_receipts"
        / "synthetic.json"
    )


def test_active_matrix_is_exactly_nineteen_mece_rubrics() -> None:
    assert len(ACTIVE_EXPERTS) == len(set(ACTIVE_EXPERTS)) == 19
    assert "data-engineer" not in ACTIVE_EXPERTS
    assert {"data-foundation", "tenant-boundaries", "operations-readiness"} <= set(ACTIVE_EXPERTS)


def test_personal_l1_selects_recovery_without_tenant_ceremony() -> None:
    gates = selected_gates(profile(), "L1")
    assert gates["data-foundation"]["applicability"] == "APPLICABLE"
    assert gates["operations-readiness"]["mode"] == "B"
    assert "tenant-boundaries" not in gates
    assert gates["sec-authz"]["applicability"] == "N/A"


def test_paid_single_user_desktop_does_not_become_multi_tenant() -> None:
    gates = selected_gates(
        profile(
            deployment="distributed-client",
            identity="single-user",
            commerce="paid",
            surfaces=["native"],
        ),
        "L3",
    )
    assert gates["tenant-boundaries"]["applicability"] == "N/A"
    assert gates["payments"]["applicability"] == "APPLICABLE"
    assert gates["frontend-web"]["applicability"] == "N/A"


def test_clean_product_empty_registry_holds_before_worker_spend(repo: Path, package: Path) -> None:
    report, code = preflight(repo, package, "codex", profile(), "L1")
    assert code == 3
    assert report["outcome"] == "HOLD"
    assert report["operator_error"] is False
    assert report["missing_capabilities"]
    assert all(check["status"] != "BLOCK" for check in report["checks"])


def test_exposed_credential_blocks_even_when_registry_is_empty(repo: Path, package: Path) -> None:
    (repo / "app.py").write_text(
        'API_TOKEN = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8"
    )
    report, code = preflight(repo, package, "codex", profile(), "L1")
    assert code == 4
    assert report["outcome"] == "BLOCK"
    assert report["missing_capabilities"]
    evidence = next(check for check in report["checks"] if check["id"] == "product.exposed-credential-diff")["evidence"]
    assert evidence == ["app.py:1: credential-shaped value detected; value suppressed"]
    assert "sk-" not in json.dumps(report)


def test_unchanged_credential_shaped_fixture_in_modified_file_does_not_block(
    repo: Path, package: Path
) -> None:
    fixture = repo / "fixture.txt"
    fixture.write_text(
        "historical fixture: sk-abcdefghijklmnopqrstuvwxyz123456\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "fixture.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "add fixture"], cwd=repo, check=True)
    fixture.write_text(fixture.read_text(encoding="utf-8") + "safe change\n", encoding="utf-8")

    report, code = preflight(repo, package, "codex", profile(), "L1")

    assert code == 3
    assert report["outcome"] == "HOLD"
    secret_check = next(
        check for check in report["checks"] if check["id"] == "product.exposed-credential-diff"
    )
    assert secret_check["status"] == "PASS"


def test_untracked_credential_remains_a_product_block(repo: Path, package: Path) -> None:
    (repo / "new_secret.txt").write_text(
        "sk-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8"
    )

    report, code = preflight(repo, package, "codex", profile(), "L1")

    assert code == 4
    assert report["outcome"] == "BLOCK"


def test_missing_rubric_is_harness_hold_never_product_block(repo: Path, package: Path) -> None:
    (package / "rubrics" / "frontend-web.md").unlink()
    report, code = preflight(repo, package, "codex", profile(), "L1")
    assert code == 3
    assert report["outcome"] == "HOLD"
    assert report["checks"][0]["id"] == "package-closure"


def test_malformed_package_config_is_operator_error(repo: Path, package: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (package / "config" / "harden_eval_policy.json").write_text("{", encoding="utf-8")
    code = harden_state.main(
        [
            "preflight", "--repo", str(repo), "--package-root", str(package),
            "--runtime", "codex", "--profile-json", json.dumps(profile()), "--rung", "L1",
        ]
    )
    report = json.loads(capsys.readouterr().out)
    assert code == 2
    assert report["outcome"] == "HOLD"
    assert report["operator_error"] is True


def test_preflight_invokes_only_closed_allowlisted_subprocess(
    repo: Path, package: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_run = subprocess.run
    calls: list[list[str]] = []
    expected = [
        [
            "git", "-c", "core.quotepath=false", "diff", "--no-ext-diff", "--no-color",
            "--unified=0", "--no-renames", "HEAD", "--",
        ],
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
    ]

    def guarded(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(command)
        assert command == expected[len(calls) - 1]
        assert kwargs.get("shell") is False
        assert kwargs.get("timeout") == 10
        return real_run(command, **kwargs)

    monkeypatch.setattr(harden_state.subprocess, "run", guarded)
    report, code = preflight(repo, package, "codex", profile(), "L1")
    assert code == 3 and report["outcome"] == "HOLD"
    assert calls == expected


def test_unregistered_verifier_is_rejected_without_subprocess(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        harden_state.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("subprocess must not run"),
    )
    with pytest.raises(StateError, match="unregistered deterministic verifier rejected"):
        run_allowlisted_verifier("arbitrary-command", repo, {})


def deterministic_block_state(repo: Path, package: Path) -> dict[str, object]:
    product_profile = profile()
    fingerprints = current_fingerprints(repo, package, product_profile)
    gates: dict[str, dict[str, object]] = {}
    for rung in ("L0", "L1"):
        gates[rung] = {}
        for expert, selection in selected_gates(product_profile, rung).items():
            applicable = selection["applicability"] == "APPLICABLE"
            gate: dict[str, object] = {
                "mode": selection["mode"],
                "applicability": selection["applicability"],
                "rationale": selection["rationale"],
                "verdict": "HOLD" if applicable else "N/A",
                "verdict_basis": "none",
                "open_findings": [],
                "finding_rules": {},
                "evidence": [],
                "evidence_hashes": {},
                "capability_receipt": "",
                "run_at": "2020-01-01T00:00:00Z",
                "fingerprints": fingerprints,
            }
            gates[rung][expert] = gate
    source = repo / "app.py"
    gates["L1"]["sec-appsec"].update(
        verdict="BLOCK",
        verdict_basis="deterministic_mandatory",
        open_findings=["SEC-001"],
        finding_rules={"SEC-001": "product.exposed-credential-diff"},
        evidence=["app.py"],
        evidence_hashes={"app.py": digest(source)},
    )
    return {
        "$schema": SCHEMA,
        "target_rung": "L1",
        "profile": product_profile,
        "fingerprints": fingerprints,
        "capabilities": [],
        "gates": gates,
    }


def test_receipt_free_block_requires_registered_reproduced_rule(repo: Path, package: Path) -> None:
    (repo / "app.py").write_text(
        'API_TOKEN = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8"
    )
    state = deterministic_block_state(repo, package)
    validate_state(state, repo, package)
    assert overall_outcome(state) == "BLOCK"

    state["gates"]["L1"]["sec-appsec"]["finding_rules"]["SEC-001"] = "free-form-rule"
    with pytest.raises(StateError, match="unregistered or inapplicable rule"):
        validate_state(state, repo, package)


def test_model_basis_cannot_self_mint_capability(repo: Path, package: Path) -> None:
    (repo / "app.py").write_text(
        'API_TOKEN = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8"
    )
    state = deterministic_block_state(repo, package)
    gate = state["gates"]["L1"]["sec-appsec"]
    gate.update(
        verdict_basis="model_receipt",
        finding_rules={},
        capability_receipt="self-asserted",
    )
    with pytest.raises(StateError, match="lacks a qualified model receipt"):
        validate_state(state, repo, package)


def test_worktree_fingerprint_ignores_hardening_reports_but_not_product(repo: Path) -> None:
    before = worktree_fingerprint(repo)
    (repo / ".harden").mkdir()
    (repo / ".harden" / "state.json").write_text("{}\n", encoding="utf-8")
    assert worktree_fingerprint(repo) == before
    (repo / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
    assert worktree_fingerprint(repo) != before
