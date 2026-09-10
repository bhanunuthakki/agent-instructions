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


def test_sync_gate_includes_the_llm_usage_index() -> None:
    assert sync.detect_llm_usage_index_drift(check_projects=False) == []


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


def test_private_ratified_policy_overrides_public_template_in_runtime_package(
    tmp_path: Path, monkeypatch
) -> None:
    state_root = tmp_path / "private-state"
    private_policy = state_root / "config" / "harden_eval_policy.json"
    private_policy.parent.mkdir(parents=True)
    private_policy.write_text(
        json.dumps(
            {
                "$schema": "internal://harden-eval-policy/v1",
                "schema_version": 1,
                "purpose": "hardening-gate-verdict",
                "ratified": True,
                "ratified_at": "2099-01-01T00:00:00Z",
                "ratifier": "Synthetic Owner",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(sync, "PRIVATE_STATE_ROOT", state_root)

    package_root = tmp_path / "harden"
    artifacts = relative_map(
        package_root, sync.build_harden_package_artifacts(package_root)
    )

    assert (
        json.loads(artifacts["config/harden_eval_policy.json"])["ratifier"]
        == "Synthetic Owner"
    )


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


def test_global_links_resolve_from_each_runtime_and_validate_recursive_closure(
    tmp_path, monkeypatch
) -> None:
    source = tmp_path / "source clone"
    procedures = source / "procedures"
    procedures.mkdir(parents=True)
    global_doc = source / "GLOBAL.md"
    global_doc.write_text(
        "# Shared\n[Catalog](procedures/INDEX.md)\n"
        "[Machine](procedures/machine-operations.md)\n"
        "Use `procedures/machine-operations.md`.\n"
    )
    (procedures / "INDEX.md").write_text("[Machine](machine-operations.md)\n")
    machine = procedures / "machine-operations.md"
    machine.write_text("[Detail](detail.md)\n")
    detail = procedures / "detail.md"
    detail.write_text("[Cycle](INDEX.md)\n")
    local = source / "AGENTS.md"
    local.write_text("# Private to this repository\nLOCAL ONLY\n")
    claude = source / "CLAUDE.md"
    claude.write_text("# Claude\n@AGENTS.md\nClaude runtime mechanics.\n")
    gemini = source / "GEMINI.md"
    gemini.write_text("# Gemini\n@./AGENTS.md\nGemini runtime mechanics.\n")
    for name, value in {
        "GLOBAL_MD": global_doc, "AGENTS_MD": local, "CLAUDE_MD": claude,
        "GEMINI_MD": gemini, "PROCEDURES_DIR": procedures,
        "CODEX_GLOBAL_AGENTS": tmp_path / "codex/AGENTS.md",
        "CLAUDE_GLOBAL_RULES": tmp_path / "claude/CLAUDE.md",
        "GEMINI_GLOBAL_RULES": tmp_path / "gemini/GEMINI.md",
    }.items():
        monkeypatch.setattr(sync, name, value)
    artifacts = sync.build_global_rulebook_artifacts()
    assert len(artifacts) == 3
    for text in artifacts.values():
        assert "LOCAL ONLY" not in text
        assert "@AGENTS" not in text and "@./AGENTS" not in text
        assert f"<{procedures / 'INDEX.md'}>" in text
        assert f"<{machine}>" in text
    assert sync.detect_global_reference_drift(artifacts) == []
    detail.write_text("[Missing nested reference](missing.md)\n")
    assert any("missing.md" in problem for problem in sync.detect_global_reference_drift(artifacts))
    assert local.read_text() == "# Private to this repository\nLOCAL ONLY\n"


def test_source_destination_collision_stops_before_any_mutation(tmp_path, monkeypatch) -> None:
    import pytest

    source = tmp_path / "GEMINI.md"
    source.write_text("@./AGENTS.md\n")
    monkeypatch.setattr(sync, "GEMINI_MD", source)
    monkeypatch.setattr(sync, "GEMINI_GLOBAL_RULES", source)
    monkeypatch.setattr(sync, "ensure_hooks", lambda *_args: pytest.fail("mutated hooks"))
    monkeypatch.setattr(sync, "materialize_claude_artifacts", lambda *_args: pytest.fail("mutated artifacts"))
    with pytest.raises(RuntimeError, match="Move the instruction source checkout"):
        sync.main()
    assert source.read_text() == "@./AGENTS.md\n"


def test_machine_operations_is_discoverable_in_all_skill_runtimes() -> None:
    for directory, artifacts in (
        (sync.SKILLS_DIR, sync.build_claude_artifacts()),
        (sync.CODEX_SKILLS_DIR, sync.build_codex_skill_artifacts()),
        (sync.ANTIGRAVITY_SKILLS_DIR, sync.build_antigravity_skill_artifacts()),
    ):
        skill = artifacts[directory / "machine-operations/SKILL.md"]
        assert "OpenRouter" in skill and "Linear" in skill
        assert "description:" in skill


def test_windows_drive_links_remain_in_local_reference_closure() -> None:
    # Generated Windows links are local files, not URL schemes named C or D.
    assert sync.local_markdown_target("<C:/Agent Rules/procedures/INDEX.md#routes>") == (
        "C:/Agent Rules/procedures/INDEX.md", "#routes"
    )
    assert sync.local_markdown_target(r"D:\agent-instructions\GLOBAL.md") == (
        r"D:\agent-instructions\GLOBAL.md", ""
    )
    assert sync.local_markdown_target("https://example.com/INDEX.md") is None
    assert sync.local_markdown_target("skill://package/INDEX.md") is None


def test_project_instruction_portability_gate_covers_rulebooks_skills_and_memory(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    (project / ".agents" / "skills" / "review").mkdir(parents=True)
    (project / "memory").mkdir()
    (project / ".claude" / "skills" / "adapter").mkdir(parents=True)
    (project / "AGENTS.md").write_text("Always ask Codex to review this.\n")
    (project / ".agents" / "skills" / "review" / "SKILL.md").write_text(
        "Use the Claude Code CLI.\n"
    )
    (project / "memory" / "MEMORY.md").write_text("Prefer GPT-5.6 for this task.\n")
    (project / ".claude" / "skills" / "adapter" / "SKILL.md").write_text(
        "Claude-only adapter mechanics are allowed here.\n"
    )

    findings = sync.detect_instruction_portability_drift([project])

    assert len(findings) == 3
    assert any("AGENTS.md:1" in finding for finding in findings)
    assert any("SKILL.md:1" in finding for finding in findings)
    assert any("MEMORY.md:1" in finding for finding in findings)


def test_project_instruction_portability_gate_accepts_capability_language(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text(
        "Use the active agent and the shared subscription route.\n"
    )

    assert sync.detect_instruction_portability_drift([project]) == []


def test_narrow_portability_mode_resolves_exact_project(tmp_path: Path) -> None:
    assert sync.requested_portability_project(
        ["sync_agent_stubs.py", "--check-project-portability", str(tmp_path)]
    ) == tmp_path.resolve()
