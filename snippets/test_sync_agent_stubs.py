from __future__ import annotations

import json
import re
from pathlib import Path

import sync_agent_stubs as sync


def relative_map(root: Path, artifacts: dict[Path, str]) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): content
        for path, content in artifacts.items()
    }


def expected_static_paths() -> set[str]:
    return {
        "SKILL.md",
        "runtime/harden_state.py",
        "evals/cases.jsonl",
        *(f"config/{name}" for name in sync.HARDEN_PACKAGE_CONFIGS),
        *(f"rubrics/{name}.md" for name in sync.HARDEN_ACTIVE_RUBRICS),
    }


def test_hardening_package_has_exact_nineteen_rubrics_and_runtime_closure(
    tmp_path: Path,
) -> None:
    root = tmp_path / "harden"
    artifacts = relative_map(root, sync.build_harden_package_artifacts(root))
    assert set(artifacts) == expected_static_paths()
    assert len([path for path in artifacts if path.startswith("rubrics/")]) == 19
    assert "rubrics/RETIRED.md" not in artifacts
    assert "procedures/agents/" not in artifacts["SKILL.md"]
    assert "snippets/harden_state.py" not in artifacts["SKILL.md"]
    assert "runtime/harden_state.py" in artifacts["SKILL.md"]
    assert "config/harden_capability_registry.json" in artifacts["SKILL.md"]


def test_all_four_runtime_layouts_are_byte_identical_by_relative_path(
    tmp_path: Path,
) -> None:
    roots = [
        tmp_path / "claude" / "skills" / "harden",
        tmp_path / "agents" / "skills" / "harden",
        tmp_path / "antigravity" / "skills" / "harden",
        tmp_path / "runtime" / "harden",
    ]
    packages = [
        relative_map(root, sync.build_harden_package_artifacts(root)) for root in roots
    ]
    assert all(package == packages[0] for package in packages[1:])


def test_private_capability_state_is_bundled_into_local_runtime_only(
    tmp_path: Path, monkeypatch
) -> None:
    state_root = tmp_path / "private-state"
    receipt_id = "synthetic-capability"
    registry = {
        "$schema": "internal://harden-capability-registry/v1",
        "schema_version": 1,
        "purpose": "hardening-gate-verdict",
        "qualifications": [
            {"receipt_id": receipt_id, "receipt_hash": "sha256:" + "a" * 64}
        ],
    }
    registry_path = state_root / "config" / "harden_capability_registry.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    receipt_path = (
        state_root / "governance" / "harden_capability_receipts" / f"{receipt_id}.json"
    )
    evidence_dir = state_root / "governance" / "harden_capability_evidence" / receipt_id
    receipt_path.parent.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    receipt_path.write_text('{"fixture":"synthetic"}', encoding="utf-8")
    (evidence_dir / "per_case_outputs.jsonl").write_text(
        '{"fixture":"synthetic"}\n', encoding="utf-8"
    )
    (evidence_dir / "score.json").write_text(
        '{"fixture":"synthetic"}', encoding="utf-8"
    )
    monkeypatch.setattr(sync, "PRIVATE_STATE_ROOT", state_root)

    package_root = tmp_path / "harden"
    artifacts = relative_map(
        package_root, sync.build_harden_package_artifacts(package_root)
    )
    assert (
        json.loads(artifacts["config/harden_capability_registry.json"])[
            "qualifications"
        ][0]["receipt_id"]
        == receipt_id
    )
    assert f"receipts/{receipt_id}.json" in artifacts
    assert f"evidence/{receipt_id}/per_case_outputs.jsonl" in artifacts
    assert f"evidence/{receipt_id}/score.json" in artifacts


def test_materialized_direct_package_detects_missing_dependency(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "runtime" / "harden"
    monkeypatch.setattr(sync, "DIRECT_HARDEN_PACKAGE_DIR", root)
    actions = sync.materialize_direct_harden_package(False)
    assert actions
    assert sync.detect_direct_harden_package_drift() == []
    (root / "rubrics" / "frontend-web.md").unlink()
    drift = sync.detect_direct_harden_package_drift()
    assert any("frontend-web.md" in finding for finding in drift)


def test_claude_command_is_thin_adapter_to_package() -> None:
    adapter = sync.harden_command_adapter()
    assert "../skills/harden/SKILL.md" in adapter
    assert "../skills/harden/runtime/harden_state.py" in adapter
    assert "# Hardening" not in adapter


def test_generated_runtime_package_contains_no_unresolved_tracked_relative_reference(
    tmp_path: Path,
) -> None:
    root = tmp_path / "harden"
    artifacts = relative_map(root, sync.build_harden_package_artifacts(root))
    skill = artifacts["SKILL.md"]
    for reference in (
        "runtime/harden_state.py",
        "config/harden_capability_registry.json",
        "rubrics/",
    ):
        assert reference in skill
    relative_files = re.findall(
        r"`((?:runtime|config|evals|rubrics|receipts|evidence)/[^`<>]+)`",
        skill,
    )
    for reference in relative_files:
        if reference.endswith("/"):
            assert any(path.startswith(reference) for path in artifacts)
        else:
            assert reference in artifacts, reference
    assert set(sync.HARDEN_ACTIVE_RUBRICS) == {
        Path(path).stem for path in artifacts if path.startswith("rubrics/")
    }
