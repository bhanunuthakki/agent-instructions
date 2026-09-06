from __future__ import annotations

import json
from pathlib import Path

import check_llm_usage_index


def test_canonical_usage_index_schema_is_valid() -> None:
    assert check_llm_usage_index.validate_index(check_projects=False) == []


def test_discovery_flags_unindexed_application_llm_project(tmp_path: Path) -> None:
    root = tmp_path / "agent-instructions"
    (root / "config").mkdir(parents=True)
    canonical_root = check_llm_usage_index.ROOT
    for name in ("llm_routing_policy.json", "llm_usage_index.json", "judge_registry.json"):
        (root / "config" / name).write_bytes((canonical_root / "config" / name).read_bytes())

    app = tmp_path / "new-app"
    (app / ".git").mkdir(parents=True)
    (app / "src").mkdir()
    (app / "src" / "llm.py").write_text(
        "from codex_cli import call_codex_with_usage\n",
        encoding="utf-8",
    )

    errors = check_llm_usage_index.validate_index(root=root, developer_root=tmp_path)

    assert any("new-app: application LLM use is not present" in error for error in errors)


def test_fleet_default_requires_the_shared_resolver(tmp_path: Path) -> None:
    root = tmp_path / "agent-instructions"
    (root / "config").mkdir(parents=True)
    canonical_root = check_llm_usage_index.ROOT
    for name in ("llm_routing_policy.json", "judge_registry.json"):
        (root / "config" / name).write_bytes((canonical_root / "config" / name).read_bytes())
    project = tmp_path / "one"
    (project / ".git").mkdir(parents=True)
    (project / "AGENTS.md").write_text("## LLM\n", encoding="utf-8")
    (project / "llm.py").write_text("from codex_cli import call_codex_with_usage\n", encoding="utf-8")
    index = {
        "$schema": "internal://llm-usage-index/v1",
        "schema_version": 1,
        "routing_policy": "config/llm_routing_policy.json",
        "judge_registry": "config/judge_registry.json",
        "projects": [{
            "project": "one",
            "instruction_section": "## LLM",
            "entrypoint": "llm.py",
            "purpose_registry": "llm.py",
            "ledger_authority": "llm.py",
            "budget_authority": None,
            "eval_authority": "llm.py",
            "workload_classes": ["application"],
            "application_route": "fleet_default",
            "judge_route_state": None,
            "judge_route_authority": None,
            "judge_independence_authority": None,
            "judge_migration_note": None,
            "migration_note": None,
        }],
    }
    (root / "config" / "llm_usage_index.json").write_text(
        json.dumps(index), encoding="utf-8"
    )

    errors = check_llm_usage_index.validate_index(root=root, developer_root=tmp_path)

    assert any("does not consume the shared resolver" in error for error in errors)


def test_discovery_requires_judge_workload_registration(tmp_path: Path) -> None:
    root = tmp_path / "agent-instructions"
    (root / "config").mkdir(parents=True)
    canonical_root = check_llm_usage_index.ROOT
    for name in ("llm_routing_policy.json", "judge_registry.json"):
        (root / "config" / name).write_bytes((canonical_root / "config" / name).read_bytes())
    project = tmp_path / "judge-app"
    (project / ".git").mkdir(parents=True)
    (project / "AGENTS.md").write_text("## LLM\n", encoding="utf-8")
    (project / "llm.py").write_text(
        'from codex_cli import call_codex_with_usage\nMODE = "LLM-judge"\n',
        encoding="utf-8",
    )
    index = {
        "$schema": "internal://llm-usage-index/v1",
        "schema_version": 1,
        "routing_policy": "config/llm_routing_policy.json",
        "judge_registry": "config/judge_registry.json",
        "projects": [{
            "project": "judge-app",
            "instruction_section": "## LLM",
            "entrypoint": "llm.py",
            "purpose_registry": "llm.py",
            "ledger_authority": "llm.py",
            "budget_authority": None,
            "eval_authority": "llm.py",
            "workload_classes": ["application"],
            "application_route": "migration_required",
            "judge_route_state": None,
            "judge_route_authority": None,
            "judge_independence_authority": None,
            "judge_migration_note": None,
            "migration_note": "Synthetic migration debt.",
        }],
    }
    (root / "config" / "llm_usage_index.json").write_text(
        json.dumps(index), encoding="utf-8"
    )

    errors = check_llm_usage_index.validate_index(root=root, developer_root=tmp_path)

    assert any("Judge LLM use is not registered" in error for error in errors)
