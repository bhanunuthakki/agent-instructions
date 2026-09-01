"""Tests for the AGENTS_GUIDE.md self-update logic in sync_agent_stubs.py.

Structural assertions only — never the exact prose of a generated table, which changes as
skills/agents/projects come and go. We assert: the right sections exist, counts/names match the
live filesystem, marker injection preserves surrounding prose, and re-rendering is idempotent.

Run:  python -m pytest <local-project>/snippets/test_guide_generation.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import sync_agent_stubs as s  # noqa: E402

MARKER_KEYS = ("skills", "commands", "agents", "procedures", "projects")


def test_hook_probe_marks_project_as_safe_for_sandboxed_runtimes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".git").mkdir()
    calls: list[list[str]] = []

    def record_run(args: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(args)
        return SimpleNamespace(stdout="")

    monkeypatch.setattr(s.subprocess, "run", record_run)

    s.ensure_hooks(tmp_path, dry=True)

    assert calls
    assert calls[0][1:3] == ["-c", f"safe.directory={tmp_path}"]


def test_instruction_paths_are_derived_instead_of_machine_bound() -> None:
    expected_root = Path(s.__file__).resolve().parents[1]

    assert s.ROOT_REPO == expected_root
    assert s.PROCEDURES_DIR == expected_root / "procedures"
    assert s.HOOKS_DIR == expected_root / "githooks"
    configured_root = os.environ.get("BHANU_DEVELOPER_ROOT")
    expected_project_root = (
        Path(configured_root).expanduser().resolve()
        if configured_root
        else expected_root.parent
    )
    assert s.PROJECT_ROOT == expected_project_root
    assert s.SCRATCH == expected_project_root


def test_global_runtime_rulebooks_are_generated_from_canonical_sources() -> None:
    artifacts = s.build_global_rulebook_artifacts()

    assert s.CODEX_GLOBAL_AGENTS in artifacts
    assert s.CLAUDE_GLOBAL_RULES in artifacts
    assert s.GEMINI_GLOBAL_RULES in artifacts
    assert s.AGENTS_MD.read_text(encoding="utf-8") in artifacts[s.CODEX_GLOBAL_AGENTS]
    assert "Generated from" in artifacts[s.CLAUDE_GLOBAL_RULES]
    if s.GEMINI_GLOBAL_RULES.resolve() == s.GEMINI_MD.resolve():
        assert artifacts[s.GEMINI_GLOBAL_RULES] == s.GEMINI_MD.read_text(
            encoding="utf-8"
        )
    else:
        assert "Generated from" in artifacts[s.GEMINI_GLOBAL_RULES]
        assert f"`{s.PROCEDURES_DIR}`" in artifacts[s.GEMINI_GLOBAL_RULES]
        assert "Canonical procedure root for manual fallback" in artifacts[
            s.GEMINI_GLOBAL_RULES
        ]


def test_mac_bootstrap_uses_the_clone_and_home_directories() -> None:
    bootstrap = (s.ROOT_REPO / "snippets" / "bootstrap_mac.sh").read_text(
        encoding="utf-8"
    )

    assert 'ROOT_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)' in bootstrap
    assert 'PROJECT_ROOT=${BHANU_DEVELOPER_ROOT:-"$(dirname "$ROOT_REPO")"}' in bootstrap
    assert 'for PROJECT_DIR in "$PROJECT_ROOT"/*' in bootstrap
    assert "project_agent_contract.py" in bootstrap
    assert "--check --artifacts-only" in bootstrap
    assert "BHANU_SCRATCH_ROOT" not in bootstrap
    assert "C:" + "/" + "Users/" not in bootstrap
    assert "C:" + "\\Users\\" not in bootstrap


def test_local_hook_directory_does_not_shadow_shared_safety_hooks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".githooks").mkdir()
    calls: list[list[str]] = []

    def record_run(args: list[str], **_kwargs: object) -> SimpleNamespace:
        calls.append(args)
        return SimpleNamespace(stdout=".githooks")

    monkeypatch.setattr(s.subprocess, "run", record_run)
    actions = s.ensure_hooks(tmp_path, dry=True)

    assert actions == [f"set core.hooksPath -> {s.HOOKS_DIR.as_posix()}"]


def test_shared_hooks_expose_required_composed_capabilities() -> None:
    assert s.detect_hook_capability_drift() == []


def test_shared_hook_is_the_only_owner_of_global_instruction_gate() -> None:
    shared = (s.HOOKS_DIR / "pre-push").read_text(encoding="utf-8")
    assert shared.count('run "$python_bin" "$stubs" --check') == 1
    earnings_hook = s.SCRATCH / "earnings-summary" / ".githooks" / "pre-push"
    if earnings_hook.exists():
        assert "sync_agent_stubs.py" not in earnings_hook.read_text(encoding="utf-8")


def test_shared_hooks_do_not_bypass_install_or_guess_project_validation() -> None:
    pre_commit = (s.HOOKS_DIR / "pre-commit").read_text(encoding="utf-8")
    pre_push = (s.HOOKS_DIR / "pre-push").read_text(encoding="utf-8")

    assert "no-verify" not in pre_commit
    assert "no-verify" not in pre_push
    for command in ("uv sync", "npm install", "ruff check", "pyright", "pytest -q"):
        assert command not in pre_push
    assert 'run sh "$local_hook" "$@"' in pre_push
    assert 'if [ "$root" = "$hook_repo" ]' in pre_push
    assert 'run "$python_bin" "$stubs" --check --artifacts-only' in pre_push


def test_pre_commit_blocks_inline_secret_without_echoing_value(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    secret_value = "-".join(("highly", "sensitive", "test", "token"))
    source = tmp_path / "settings.py"
    assignment = "api" + "_key = " + repr(secret_value)
    source.write_text(f"{assignment}\n", encoding="utf-8")
    subprocess.run(["git", "add", "settings.py"], cwd=tmp_path, check=True)

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-commit")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "settings.py" in completed.stderr
    assert secret_value not in completed.stderr


def test_pre_commit_allows_environment_variable_placeholder(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    source = tmp_path / "registry.json"
    source.write_text(
        '{"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "registry.json"], cwd=tmp_path, check=True)

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-commit")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_pre_commit_scans_staged_credential_renames(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    source = tmp_path / "settings.txt"
    source.write_text("safe fixture\n", encoding="utf-8")
    subprocess.run(["git", "add", "settings.txt"], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "mv", "settings.txt", "token.json"], cwd=tmp_path, check=True)

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-commit")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "token.json" in completed.stderr


def test_pre_commit_allows_canonical_secret_procedure(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    procedure = tmp_path / "procedures" / "scaffold-secrets.md"
    procedure.parent.mkdir()
    procedure.write_text("# Secret configuration procedure\n", encoding="utf-8")
    subprocess.run(["git", "add", procedure.relative_to(tmp_path)], cwd=tmp_path, check=True)

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-commit")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_instruction_push_gate_fails_closed_and_runs_the_full_suite() -> None:
    pre_push = (s.HOOKS_DIR / "pre-push").read_text(encoding="utf-8")

    override = pre_push.index('if [ -n "${PYTHON_BIN:-}" ]')
    python3_fallback = pre_push.index("elif has python3; then")
    python_fallback = pre_push.index("elif has python; then")
    assert override < python3_fallback < python_fallback
    for failure in (
        "no Python interpreter",
        "PYTHON_BIN is not executable",
        "instruction sync entrypoint is missing",
        "pytest is unavailable",
    ):
        assert failure in pre_push
    for test_file in (
        "test_guide_generation.py",
        "test_harden_state.py",
        "test_governance.py",
    ):
        assert test_file in pre_push
    assert 'run "$python_bin" -m pytest' in pre_push


def test_instruction_push_gate_honors_python_override(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_git = fake_bin / "git"
    fake_git.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$EXPECTED_ROOT"\n', encoding="utf-8"
    )
    fake_git.chmod(0o755)
    call_log = tmp_path / "python-calls.log"
    fake_python = tmp_path / "chosen-python"
    fake_python.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$*" >> "$PYTHON_LOG"\n', encoding="utf-8"
    )
    fake_python.chmod(0o755)
    instruction_home = tmp_path / "instruction-home"
    (instruction_home / "snippets").mkdir(parents=True)
    (instruction_home / "snippets" / "sync_agent_stubs.py").write_text(
        "# test stub\n", encoding="utf-8"
    )
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "EXPECTED_ROOT": str(s.ROOT_REPO),
        "AGENT_INSTRUCTIONS_HOME": str(instruction_home),
        "PYTHON_BIN": str(fake_python),
        "PYTHON_LOG": str(call_log),
    }

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-push")],
        cwd=s.ROOT_REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    calls = call_log.read_text(encoding="utf-8")
    assert "-c import pytest" in calls
    assert "sync_agent_stubs.py --check --artifacts-only" in calls
    assert "-m pytest" in calls
    assert "test_harden_state.py" in calls


def test_instruction_push_gate_rejects_invalid_python_override(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_git = fake_bin / "git"
    fake_git.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$EXPECTED_ROOT"\n', encoding="utf-8"
    )
    fake_git.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "EXPECTED_ROOT": str(s.ROOT_REPO),
        "PYTHON_BIN": str(tmp_path / "missing-python"),
    }

    completed = subprocess.run(
        ["sh", str(s.HOOKS_DIR / "pre-push")],
        cwd=s.ROOT_REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "PYTHON_BIN is not executable" in completed.stderr


def test_command_artifacts_share_one_canonical_source() -> None:
    claude = s.build_claude_artifacts()
    codex = s.build_codex_skill_artifacts()
    for command, source in s.COMMAND_SOURCES.items():
        expected = source.read_text(encoding="utf-8", errors="replace")
        codex_name = "harden" if command == "harden" else f"source-command-{command}"
        if command == "harden":
            assert claude[s.COMMANDS_DIR / "harden.md"] == s.harden_command_adapter()
            assert codex[s.CODEX_SKILLS_DIR / codex_name / "SKILL.md"] == (
                s.build_harden_package_artifacts(s.CODEX_SKILLS_DIR / "harden")[
                    s.CODEX_SKILLS_DIR / "harden" / "SKILL.md"
                ]
            )
        else:
            assert claude[s.COMMANDS_DIR / f"{command}.md"] == expected
            assert codex[s.CODEX_SKILLS_DIR / codex_name / "SKILL.md"] == expected


def test_semantic_linter_rejects_reversed_canonical_direction(tmp_path: Path) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(
        "Claude skills are canonical and procedures are overwritten.\n",
        encoding="utf-8",
    )
    findings = s.detect_semantic_drift([bad])
    assert any("canonical direction" in finding for finding in findings)


def test_semantic_linter_rejects_stale_definitions_pointer(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("No `DEFINITIONS.md` yet.\n", encoding="utf-8")
    (project / "DEFINITIONS.md").write_text("# Definitions\n", encoding="utf-8")
    findings = s.detect_semantic_drift([project / "AGENTS.md"])
    assert any("claims no DEFINITIONS.md" in finding for finding in findings)


def test_semantic_linter_validates_explicit_root_heading_refs(tmp_path: Path) -> None:
    root = tmp_path / "AGENTS.md"
    child = tmp_path / "child.md"
    root.write_text("# Rules\n\n## Existing\n", encoding="utf-8")
    child.write_text("Apply [[root:Missing]].\n", encoding="utf-8")
    findings = s.detect_semantic_drift([child], root_doc=root)
    assert any("missing root heading" in finding for finding in findings)


def test_semantic_linter_rejects_ordinary_stale_heading_reference(
    tmp_path: Path,
) -> None:
    root = tmp_path / "AGENTS.md"
    child = tmp_path / "child.md"
    root.write_text("# Rules\n\n## Existing\n", encoding="utf-8")
    child.write_text("Use global `AGENTS.md` §Missing Heading.\n", encoding="utf-8")
    findings = s.detect_semantic_drift([child], root_doc=root)
    assert any("missing root heading" in finding for finding in findings)


def test_semantic_linter_rejects_missing_local_markdown_link(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("Read [missing](missing.REFERENCE.md).\n", encoding="utf-8")
    findings = s.detect_semantic_drift([doc])
    assert any("missing Markdown target" in finding for finding in findings)


def test_semantic_linter_rejects_missing_backticked_procedure(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "Load `procedures/definitely-not-a-real-procedure.md`.\n",
        encoding="utf-8",
    )

    findings = s.detect_semantic_drift([doc])

    assert any("missing backticked procedure target" in finding for finding in findings)


def test_frontier_expiry_is_checked_with_explicit_artifact_docs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    frontier = tmp_path / "model-frontier.REFERENCE.md"
    frontier.write_text("Next review: 2000-01-01.\n", encoding="utf-8")
    doc = tmp_path / "AGENTS.md"
    doc.write_text("# Rules\n", encoding="utf-8")
    monkeypatch.setattr(s, "PROCEDURES_DIR", tmp_path)

    findings = s.detect_semantic_drift([doc], root_doc=doc)

    assert any("model frontier review is expired" in finding for finding in findings)


def test_root_routes_standalone_tool_and_integration_workflows() -> None:
    agents = s.AGENTS_MD.read_text(encoding="utf-8")

    for procedure in ("tool-selector.md", "external-integration.md"):
        assert f"`procedures/{procedure}`" in agents
        assert (s.PROCEDURES_DIR / procedure).exists()
        skill_name = Path(procedure).stem
        assert skill_name in s.OUR_SKILLS
        assert s.SKILLS_DIR / skill_name / "SKILL.md" in s.build_claude_artifacts()
        assert (
            s.CODEX_SKILLS_DIR / skill_name / "SKILL.md"
            in s.build_codex_skill_artifacts()
        )


def test_model_frontier_review_date_matches_near_term_refresh_gate() -> None:
    frontier = (s.PROCEDURES_DIR / "model-frontier.REFERENCE.md").read_text(
        encoding="utf-8"
    )
    assert "Next review: 2026-08-31" in frontier


def test_model_frontier_prices_match_blended_cost_and_sort_order() -> None:
    frontier = (s.PROCEDURES_DIR / "model-frontier.REFERENCE.md").read_text(
        encoding="utf-8"
    )
    rows: list[tuple[str, float, float, float]] = []
    for line in frontier.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(
            (cells[0].strip("`"), float(cells[2]), float(cells[3]), float(cells[4]))
        )

    expected_current_prices = {
        "gemini-3.5-flash-lite": (0.30, 2.50),
        "gpt-5.6-luna": (0.20, 1.20),
        "gpt-5.6-terra": (2.00, 12.00),
    }
    observed = {
        model_id: (input_price, output_price)
        for model_id, input_price, output_price, _ in rows
    }
    assert expected_current_prices.items() <= observed.items()

    blended_values: list[float] = []
    for _model_id, input_price, output_price, blended in rows:
        expected_blended = round((6 * input_price + output_price) / 7, 2)
        assert blended == expected_blended
        blended_values.append(blended)
    assert blended_values == sorted(blended_values)


def test_unmanaged_command_artifacts_are_orphans(tmp_path: Path) -> None:
    commands = tmp_path / "commands"
    skills = tmp_path / "skills"
    commands.mkdir()
    (skills / "source-command-orphan").mkdir(parents=True)
    (commands / "orphan.md").write_text("orphan", encoding="utf-8")
    (skills / "source-command-orphan" / "SKILL.md").write_text(
        "orphan", encoding="utf-8"
    )
    findings = s.detect_command_orphans(commands, skills)
    assert len(findings) == 2


def test_global_definition_override_is_semantic_drift_in_legacy_format(
    tmp_path: Path,
) -> None:
    root = tmp_path / "DEFINITIONS.md"
    child = tmp_path / "project" / "DEFINITIONS.md"
    child.parent.mkdir()
    root.write_text(
        "# Definitions\n\n## Judge Verdict\n\n**Definition.** Typed review result.\n",
        encoding="utf-8",
    )
    child.write_text(
        "# Definitions\n\n## Enums\n\n- **Judge Verdict** — another meaning.\n",
        encoding="utf-8",
    )
    findings = s.detect_definition_override_drift(root, [child])
    assert any("override" in finding for finding in findings)


def _synthetic_guide() -> str:
    parts = ["# Guide\n\nIntro prose that must survive.\n"]
    for k in MARKER_KEYS:
        parts.append(f"<!-- BEGIN:{k} -->\nSTALE PLACEHOLDER {k}\n<!-- END:{k} -->")
    parts.append("\nClosing prose that must survive.\n")
    return "\n".join(parts)


def test_every_section_present_and_nonempty() -> None:
    secs = s.build_guide_sections()
    assert set(secs) == set(MARKER_KEYS)
    for key, body in secs.items():
        assert body.strip(), f"section {key!r} is empty"


def test_skills_section_lists_every_skill_on_disk() -> None:
    body = s.build_guide_sections()["skills"]
    present = [n for n in s.OUR_SKILLS if (s.SKILLS_DIR / n / "SKILL.md").exists()]
    assert present, "expected at least one skill on disk"
    for name in present:
        assert name in body
    assert str(len(present)) in body  # the count is rendered and truthful


def test_agents_section_matches_disk_count_and_names() -> None:
    body = s.build_guide_sections()["agents"]
    stems = sorted(p.stem for p in s.AGENTS_DIR.glob("*.md"))
    assert stems, "expected agent files on disk"
    assert str(len(stems)) in body
    for stem in stems:
        assert stem in body


def test_projects_section_splits_wired_from_unwired() -> None:
    body = s.build_guide_sections()["projects"]
    for child in s.project_dirs():
        assert child.name in body  # every real project surfaces, wired or not


def test_projects_section_excludes_hidden_and_temp_dirs() -> None:
    body = s.build_guide_sections()["projects"]
    if not s.SCRATCH.is_dir():
        return
    for child in s.SCRATCH.iterdir():
        if child.is_dir() and (
            child.name.startswith(".") or child.name.startswith(s.SKIP_PREFIXES)
            or child.name in s.SKIP_PROJECT_NAMES
            or s.is_linked_git_worktree(child)
        ):
            assert (
                child.name not in body
            )  # Drive temp/hidden dirs never leak into the map


def test_project_discovery_excludes_non_repositories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "project"
    repository.mkdir()
    (repository / ".git").mkdir()
    (tmp_path / "Example.app").mkdir()
    (tmp_path / "Utilities").mkdir()

    monkeypatch.setattr(s, "SCRATCH", tmp_path)

    assert s.project_dirs() == [repository]


def test_project_discovery_checks_unwired_projects_too() -> None:
    if not s.SCRATCH.is_dir():
        assert s.project_dirs() == []
        return
    expected = {
        child
        for child in s.SCRATCH.iterdir()
        if child.is_dir()
        and (child / ".git").is_dir()
        and not child.name.startswith(".")
        and not child.name.startswith(s.SKIP_PREFIXES)
        and child.name not in s.SKIP_PROJECT_NAMES
        and not s.is_linked_git_worktree(child)
        and child.resolve() != s.ROOT_REPO.resolve()
    }
    assert set(s.project_dirs()) == expected


def test_interface_authority_audit_surfaces_legacy_projects_without_sync_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "legacy-ui"
    project.mkdir()
    (project / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    monkeypatch.setattr(s, "project_dirs", lambda: [project])

    assert s.interface_authority_warnings() == [
        "legacy-ui: missing ## Interface authority block"
    ]


def test_demo_sandbox_is_preserved_but_excluded_from_active_projects() -> None:
    assert "demo_sandbox" in s.SKIP_PROJECT_NAMES
    assert all(project.name != "demo_sandbox" for project in s.project_dirs())


def test_resume_wrappers_are_deferred_while_recovery_branch_is_held() -> None:
    assert "bhanu-resume-system" in s.DEFERRED_WRAPPER_PROJECT_NAMES


def test_linked_git_worktree_is_not_treated_as_a_separate_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    primary = tmp_path / "primary-project"
    primary.mkdir()
    (primary / ".git").mkdir()

    linked = tmp_path / "primary-project-feature"
    linked.mkdir()
    (linked / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")

    monkeypatch.setattr(s, "SCRATCH", tmp_path)

    assert s.project_dirs() == [primary]


def test_missing_project_rulebook_is_reported(tmp_path: Path) -> None:
    project = tmp_path / "unwired-project"
    project.mkdir()
    drift = s.detect_wrapper_drift(project)
    assert drift
    assert any("AGENTS.md" in finding for finding in drift)


def test_render_injects_and_preserves_prose() -> None:
    rendered = s.render_guide(_synthetic_guide())
    for key in MARKER_KEYS:
        assert f"<!-- BEGIN:{key} -->" in rendered
        assert f"<!-- END:{key} -->" in rendered
        assert f"STALE PLACEHOLDER {key}" not in rendered
    assert "Intro prose that must survive." in rendered
    assert "Closing prose that must survive." in rendered


def test_render_is_idempotent() -> None:
    once = s.render_guide(_synthetic_guide())
    twice = s.render_guide(once)
    assert s._norm(once) == s._norm(twice)


def test_missing_markers_raise() -> None:
    with pytest.raises(ValueError):
        s.render_guide("# A guide with no markers at all\n")


def test_frontmatter_parses_description_with_colons() -> None:
    fm = s.parse_frontmatter(
        "---\nname: x\ndescription: Do a thing: then another. Use when y.\n---\nbody"
    )
    assert fm["name"] == "x"
    assert fm["description"].startswith("Do a thing: then another.")


def test_first_sentence_truncates_long_text() -> None:
    long = "word " * 100
    out = s.first_sentence(long, cap=40)
    assert len(out) <= 40
    assert out.endswith("…")


def test_artifacts_only_mode_skips_project_wiring() -> None:
    assert not s.includes_project_wiring(["sync_agent_stubs.py", "--artifacts-only"])


def test_artifacts_only_mode_skips_machine_specific_inventory() -> None:
    assert not s.includes_machine_specific_inventory(
        ["sync_agent_stubs.py", "--artifacts-only"]
    )


def test_artifacts_only_check_still_validates_tracked_human_guide() -> None:
    assert s.includes_guide_validation(
        ["sync_agent_stubs.py", "--check", "--artifacts-only"]
    )
    assert not s.includes_guide_validation(
        ["sync_agent_stubs.py", "--artifacts-only"]
    )


def test_generated_project_wrappers_are_import_only() -> None:
    assert s.claude_stub("AGENTS.md") == "# Claude Code\n\n@./AGENTS.md\n"
    assert s.GEMINI_STUB == "# Gemini\n\n@./AGENTS.md\n"


def test_sync_regenerates_gemini_before_exporting_global_rulebooks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A global Gemini rulebook must include the current generated trigger table."""
    calls: list[str] = []

    monkeypatch.setattr(s.sys, "argv", ["sync_agent_stubs.py", "--artifacts-only"])
    monkeypatch.setattr(s, "materialize_claude_artifacts", lambda _dry: [])
    monkeypatch.setattr(s, "materialize_codex_skill_artifacts", lambda _dry: [])
    monkeypatch.setattr(s, "materialize_antigravity_skill_artifacts", lambda _dry: [])
    monkeypatch.setattr(
        s,
        "materialize_gemini_triggers",
        lambda _dry: calls.append("gemini") or [],
    )
    monkeypatch.setattr(
        s,
        "materialize_global_rulebook_artifacts",
        lambda _dry: calls.append("global") or [],
    )
    monkeypatch.setattr(s, "materialize_mcp_configs", lambda _dry: [])

    s.main()

    assert calls == ["gemini", "global"]


def test_legacy_generated_wrapper_is_refreshable(tmp_path: Path) -> None:
    wrapper = tmp_path / "CLAUDE.md"
    wrapper.write_text(
        "# Claude Code\n\n@./AGENTS.md\n\n"
        "Claude Code: this imports the repo rulebook.\n",
        encoding="utf-8",
    )
    assert s.generated_wrapper_needs_update(wrapper, s.claude_stub("AGENTS.md"))


# ----- Inverted graph: procedures/ is canonical; Claude artifacts are generated FROM it -----


def test_claude_artifacts_cover_skills_command_and_fleet() -> None:
    arts = s.build_claude_artifacts()
    for name in s.OUR_SKILLS:
        if (s.PROCEDURES_DIR / f"{name}.md").exists():
            assert s.SKILLS_DIR / name / "SKILL.md" in arts
    if (s.PROCEDURES_DIR / "harden.md").exists():
        assert s.COMMANDS_DIR / "harden.md" in arts
    fleet = sorted(
        ag
        for ag in s.PROCEDURES_AGENTS_DIR.glob("*.md")
        if ag.stem not in s.RETIRED_GENERATED_AGENTS
    )
    assert fleet, "expected fleet criteria in procedures/agents/"
    for ag in fleet:
        assert s.AGENTS_DIR / ag.name in arts
    assert all(content.strip() for content in arts.values())


def test_agent_routing_uses_capability_roles_not_provider_labels() -> None:
    procedure = (s.PROCEDURES_DIR / "agent-operations.md").read_text(
        encoding="utf-8"
    )
    for role in (
        "mechanical-worker",
        "implementation-worker",
        "blocking-specialist",
        "frontier-synthesizer",
    ):
        assert role in procedure
    for provider_label in (
        "Claude",
        "Codex",
        "Gemini",
        "Opus",
        "Fable",
        "Sol",
    ):
        assert provider_label not in procedure
    assert "capability receipt" in procedure
    assert "least expensive currently evaluated model" in procedure


def test_shared_scheduling_reference_has_no_project_specific_windows() -> None:
    reference = (s.PROCEDURES_DIR / "agent-operations.SCHEDULING.md").read_text(
        encoding="utf-8"
    )
    for stale in (
        "earnings-summary",
        "03:00",
        "04:00",
        "6–7 hours",
        "Claude",
        "Codex",
    ):
        assert stale not in reference
    assert "project registry" in reference
    assert "interactive reserve" in reference


def test_context_engineering_requires_dispositions_and_representative_routes() -> None:
    procedure = (s.PROCEDURES_DIR / "context-engineering.md").read_text(
        encoding="utf-8"
    )
    for disposition in ("keep", "move", "merge", "replace", "delete"):
        assert f"**{disposition}**" in procedure
    for route in (
        "simple change",
        "material feature",
        "frontend change",
        "high-risk operation",
    ):
        assert route in procedure
    assert "every relative reference is reachable" in procedure


def test_claude_artifacts_are_identity_copies_of_procedures() -> None:
    """The inversion's core invariant: a generated Claude artifact is byte-for-byte its procedures/
    source (only the directory layout is remapped). This is what makes the round-trip lossless."""
    arts = s.build_claude_artifacts()
    for name in s.OUR_SKILLS:
        src = s.PROCEDURES_DIR / f"{name}.md"
        if src.exists():
            assert arts[s.SKILLS_DIR / name / "SKILL.md"] == src.read_text(
                encoding="utf-8", errors="replace"
            )
    for ag in s.PROCEDURES_AGENTS_DIR.glob("*.md"):
        if ag.stem in s.RETIRED_GENERATED_AGENTS:
            continue
        assert arts[s.AGENTS_DIR / ag.name] == ag.read_text(
            encoding="utf-8", errors="replace"
        )
    ref = s.PROCEDURES_DIR / "model-frontier.REFERENCE.md"
    if (
        ref.exists()
    ):  # sibling: flattened in procedures/, nested under the skill in ~/.claude
        assert arts[s.SKILLS_DIR / "model-frontier" / "REFERENCE.md"] == ref.read_text(
            encoding="utf-8", errors="replace"
        )


def test_codex_skill_artifacts_are_identity_copies_of_procedures() -> None:
    arts = s.build_codex_skill_artifacts()
    for name in s.OUR_SKILLS:
        src = s.PROCEDURES_DIR / f"{name}.md"
        if src.exists():
            target = s.CODEX_SKILLS_DIR / name / "SKILL.md"
            assert arts[target] == src.read_text(encoding="utf-8", errors="replace")
    ref = s.PROCEDURES_DIR / "model-frontier.REFERENCE.md"
    if ref.exists():
        target = s.CODEX_SKILLS_DIR / "model-frontier" / "REFERENCE.md"
        assert arts[target] == ref.read_text(encoding="utf-8", errors="replace")


def test_antigravity_skill_artifacts_are_identity_copies_except_self_contained_harden() -> None:
    arts = s.build_antigravity_skill_artifacts()
    for name in [*s.OUR_SKILLS, *s.CODEX_ONLY_SKILLS]:
        src = s.PROCEDURES_DIR / f"{name}.md"
        if src.exists():
            target = s.ANTIGRAVITY_SKILLS_DIR / name / "SKILL.md"
            if name == "harden":
                expected = s.build_harden_package_artifacts(
                    s.ANTIGRAVITY_SKILLS_DIR / "harden"
                )[target]
            else:
                expected = src.read_text(encoding="utf-8", errors="replace")
            assert arts[target] == expected
    ref = s.PROCEDURES_DIR / "context-engineering.REFERENCE.md"
    if ref.exists():
        target = s.ANTIGRAVITY_SKILLS_DIR / "context-engineering" / "REFERENCE.md"
        assert arts[target] == ref.read_text(encoding="utf-8", errors="replace")
    assert s.build_antigravity_skill_config() == (
        '{\n'
        '  "entries": [\n'
        f'    {{\n      "path": "{s.ANTIGRAVITY_SKILLS_DIR}"\n    }}\n'
        '  ]\n'
        '}\n'
    )
def test_progressive_disclosure_skills_are_generated_for_both_runtimes() -> None:
    names = {
        "agent-operations",
        "code-change",
        "context-engineering",
        "data-foundation",
        "external-practice",
        "linear-pipeline-hygiene",
        "linear-pr-sync",
        "mockup-review",
        "product-feature",
        "frontend-quality",
        "iteration-shortcut",
    }
    assert names <= set(s.OUR_SKILLS)
    claude = s.build_claude_artifacts()
    codex = s.build_codex_skill_artifacts()
    for name in names:
        source = s.PROCEDURES_DIR / f"{name}.md"
        assert source.exists()
        assert s.SKILLS_DIR / name / "SKILL.md" in claude
        assert s.CODEX_SKILLS_DIR / name / "SKILL.md" in codex


def test_frontend_quality_has_one_canonical_route_and_no_stale_global_owner() -> None:
    procedure = (s.PROCEDURES_DIR / "frontend-quality.md").read_text(encoding="utf-8")
    agents = s.AGENTS_MD.read_text(encoding="utf-8")
    assert procedure.count("# Frontend Quality") == 1
    assert agents.count("`procedures/frontend-quality.md`") == 1
    assert "Frontend Correctness" not in agents
    assert "frontend-quality" in s.OUR_SKILLS
    assert "design-conformance-audit" not in s.OUR_SKILLS


def test_root_uses_one_clarification_economics_invariant() -> None:
    root = s.AGENTS_MD.read_text(encoding="utf-8")
    judging = (s.PROCEDURES_DIR / "judging.md").read_text(encoding="utf-8")
    context = (s.PROCEDURES_DIR / "context-engineering.md").read_text(encoding="utf-8")
    assert "## Effort calibration" not in root
    assert "quick reversible iteration" not in root
    assert "short answer is likely to prevent materially greater rework" in root
    assert "smallest reversible technical default" in root
    assert "J0 is the default when deterministic proof closes the task" in judging
    assert "confirm the expanded scope with the owner" in judging
    assert "expensive multi-model evaluation" in context


def test_frontend_workflows_route_to_the_canonical_quality_owner() -> None:
    for relative in (
        "procedures/code-change.md",
        "procedures/code-change.FRONTEND.md",
        "procedures/scaffold-design-system.md",
        "procedures/mockup-review.md",
        "procedures/harden.md",
        "procedures/agents/ux-design.md",
        "procedures/agents/frontend-web.md",
    ):
        assert "frontend-quality" in (s.ROOT_REPO / relative).read_text(encoding="utf-8"), relative
    stale = [
        path
        for path in s.PROCEDURES_DIR.rglob("*.md")
        if "Frontend Correctness" in path.read_text(encoding="utf-8", errors="replace")
    ]
    assert stale == []


def test_frontend_quality_shadow_cases_cover_restraint_and_trajectories() -> None:
    path = s.ROOT_REPO / "evals" / "frontend_quality" / "shadow_cases.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["mode"] == "shadow"
    assert "unproven" in payload["coverage_claim"]
    assert {case["id"] for case in payload["restraint_pairs"]} == {
        "container-economy", "semantic-rail", "type-economy", "structural-list", "subtitle-value"
    }
    assert {case["id"] for case in payload["task_trajectories"]} == {
        "material-existing-redesign", "small-visual-adjustment", "greenfield-scaffold", "nonvisual-frontend-behavior", "unrunnable-preview"
    }
    for case in payload["restraint_pairs"]:
        assert set(case) == {"id", "surface", "variant_a", "variant_b", "expected_rubric"}
        assert case["expected_rubric"]["preferred_variant"] in {"a", "b"}
    for case in payload["task_trajectories"]:
        assert set(case) == {"id", "prompt", "expected_rubric"}
        assert isinstance(case["expected_rubric"]["material"], bool)


def test_frontend_quality_shadow_runner_has_a_schema_checked_dry_run(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    runner_path = s.ROOT_REPO / "evals" / "frontend_quality" / "run_shadow_eval.py"
    spec = spec_from_file_location("frontend_quality_shadow", runner_path)
    assert spec and spec.loader
    runner = module_from_spec(spec)
    spec.loader.exec_module(runner)

    valid = {
        "case_id": "case",
        "material": True,
        "ux_hypothesis": "task first",
        "rendered_evidence": "preview",
        "reduction_pass": "removed a box",
        "verification_gap": "none",
        "verdict": "PASS",
        "findings": [], "contract_flags": ["baseline-render"], "type": "task_trajectory",
    }
    assert runner.validate_response(valid, {"id": "case", "prompt": "x"}) == valid
    advisory = {**valid, "verdict": "ADVISORY"}
    assert runner.validate_response(advisory, {"id": "case", "prompt": "x"}) == advisory
    with pytest.raises(ValueError, match="case case: invalid verdict"):
        runner.validate_response({**valid, "verdict": "UNKNOWN"}, {"id": "case", "prompt": "x"})
    with pytest.raises(ValueError, match="response schema"):
        runner.validate_response({"case_id": "case"}, {"id": "case", "prompt": "x"})
    pair = {"id": "pair", "surface": "test", "variant_a": "a", "variant_b": "b", "expected_rubric": {"preferred_variant": "a", "variant_a_flags": [], "variant_b_flags": ["decorative-accent"]}}
    pair_response = {"case_id": "pair", "type": "restraint_pair", "preferred_variant": "a", "variant_a_flags": [], "variant_b_flags": ["decorative-accent"], "reason": "less clutter"}
    assert runner.score_case(pair, runner.validate_response(pair_response, pair))["status"] == "MATCH"
    pair_prompt = runner.prompt_for(pair)
    trajectory_prompt = runner.prompt_for({"id": "case", "prompt": "x"})
    assert "expected_rubric" not in pair_prompt
    assert '"preferred_variant": "a"' not in pair_prompt
    assert "preferred_variant (a|b)" in pair_prompt
    assert "redundant-container" in pair_prompt
    assert "verdict (PASS|BLOCK|ADVISORY|HOLD|ABSTAIN)" in trajectory_prompt
    assert runner.MATERIALITY_DEFINITION in trajectory_prompt
    assert "baseline-render" in trajectory_prompt
    with pytest.raises(ValueError, match="case pair: invalid pair flag"):
        runner.validate_response({**pair_response, "variant_b_flags": ["unknown"]}, pair)
    with pytest.raises(ValueError, match="case case: invalid trajectory contract flag"):
        runner.validate_response({**valid, "contract_flags": ["unknown"]}, {"id": "case", "prompt": "x"})
    assert runner.receipt_target("run-one") != runner.receipt_target("run-two")
    monkeypatch.setattr(sys, "argv", ["run_shadow_eval.py", "--limit", "1"])
    runner.main()
    assert json.loads(capsys.readouterr().out)["selected"] == ["container-economy"]


def test_committed_frontend_quality_receipts_match_current_schema() -> None:
    runner_path = s.ROOT_REPO / "evals" / "frontend_quality" / "run_shadow_eval.py"
    spec = spec_from_file_location("frontend_quality_shadow_receipts", runner_path)
    assert spec and spec.loader
    runner = module_from_spec(spec)
    spec.loader.exec_module(runner)
    cases = runner.load_cases()

    receipts = sorted(
        (s.ROOT_REPO / "evals" / "frontend_quality" / "receipts").glob("*.json")
    )
    assert receipts
    for path in receipts:
        receipt = runner.validate_receipt(
            json.loads(path.read_text(encoding="utf-8")), cases
        )
        assert path.name == runner.receipt_target(receipt["run_identifier"]).name


def test_retired_generated_skill_is_exactly_detected_and_pruned(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    roots = {
        "SKILLS_DIR": tmp_path / "claude",
        "CODEX_SKILLS_DIR": tmp_path / "codex",
        "LEGACY_CODEX_SKILLS_DIR": tmp_path / "legacy-codex",
        "ANTIGRAVITY_SKILLS_DIR": tmp_path / "antigravity",
    }
    for name, root in roots.items():
        monkeypatch.setattr(s, name, root)
    retired = roots["SKILLS_DIR"] / "design-conformance-audit" / "SKILL.md"
    legacy_retired = roots["LEGACY_CODEX_SKILLS_DIR"] / "design-conformance-audit" / "SKILL.md"
    unrelated = roots["SKILLS_DIR"] / "personal-skill" / "SKILL.md"
    retired.parent.mkdir(parents=True)
    legacy_retired.parent.mkdir(parents=True)
    unrelated.parent.mkdir(parents=True)
    retired.write_text("retired", encoding="utf-8")
    legacy_retired.write_text("retired", encoding="utf-8")
    unrelated.write_text("keep", encoding="utf-8")

    assert s.detect_retired_skill_artifact_drift("claude")
    assert s.detect_retired_skill_artifact_drift("legacy-codex")
    assert s.materialize_retired_skill_artifacts("claude", dry=True) == [
        f"remove retired {retired}"
    ]
    assert retired.exists()
    s.materialize_retired_skill_artifacts("claude", dry=False)
    s.materialize_retired_skill_artifacts("legacy-codex", dry=False)
    assert not retired.exists()
    assert not legacy_retired.exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert not s.detect_retired_skill_artifact_drift("claude")


def test_retired_generated_agents_are_exactly_pruned(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(s, "AGENTS_DIR", tmp_path)
    retired = tmp_path / "infra-sre.md"
    unrelated = tmp_path / "personal-agent.md"
    retired.write_text("retired", encoding="utf-8")
    unrelated.write_text("keep", encoding="utf-8")

    assert s.detect_retired_agent_artifact_drift()
    s.materialize_retired_agent_artifacts(dry=False)
    assert not retired.exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert not s.detect_retired_agent_artifact_drift()


def test_guide_omits_retired_discovery_and_legacy_scaffold_framework(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(s, "project_dirs", lambda: [])
    sections = s.build_guide_sections()
    assert "design-conformance-audit" not in sections["skills"]
    assert "design-conformance-audit.md" not in sections["procedures"]
    assert "frontend-quality" in sections["skills"]
    assert "Radix" not in sections["skills"]


def test_scaffolds_are_profile_and_stack_detected_not_framework_templates() -> None:
    auth = (s.PROCEDURES_DIR / "scaffold-auth.md").read_text(encoding="utf-8")
    deploy = (s.PROCEDURES_DIR / "scaffold-deploy.md").read_text(encoding="utf-8")
    secrets = (s.PROCEDURES_DIR / "scaffold-secrets.md").read_text(encoding="utf-8")
    tenant = (s.PROCEDURES_DIR / "scaffold-tenant-schema.md").read_text(encoding="utf-8")

    assert "Do not inject a universal framework" in auth
    assert "FastAPI" not in auth and "PostgreSQL" not in auth
    assert "Do not emit a generic Dockerfile" in deploy
    assert "Railway" not in deploy
    assert "Do not blanket-ignore databases" in secrets
    assert "*.db" not in secrets and "*.sqlite3" not in secrets
    assert "only after `multi_tenant` is an explicit profile requirement" in tenant
    assert "`run_id` is lineage, not a universal business key" in tenant


def test_harden_is_self_contained_in_each_runtime_and_claude_command_stays_thin() -> None:
    codex_target = s.CODEX_SKILLS_DIR / "harden" / "SKILL.md"
    assert codex_target in s.build_codex_skill_artifacts()
    assert s.SKILLS_DIR / "harden" / "SKILL.md" in s.build_claude_artifacts()
    assert s.COMMANDS_DIR / "harden.md" in s.build_claude_artifacts()
    assert s.build_claude_artifacts()[s.COMMANDS_DIR / "harden.md"] == (
        s.harden_command_adapter()
    )
    for package_root, artifacts in (
        (s.SKILLS_DIR / "harden", s.build_claude_artifacts()),
        (s.CODEX_SKILLS_DIR / "harden", s.build_codex_skill_artifacts()),
        (s.ANTIGRAVITY_SKILLS_DIR / "harden", s.build_antigravity_skill_artifacts()),
    ):
        expected = s.build_harden_package_artifacts(package_root)
        assert expected.items() <= artifacts.items()


def test_llm_ops_details_are_progressively_disclosed() -> None:
    main = (s.PROCEDURES_DIR / "llm-ops.md").read_text(encoding="utf-8")
    for name in ("CONTRACTS.md", "EVALS.md", "TRANSPORTS.md"):
        source = s.PROCEDURES_DIR / f"llm-ops.{name}"
        assert source.exists()
        assert f"[llm-ops.{name}](llm-ops.{name})" in main
        assert s.SKILLS_DIR / "llm-ops" / name in s.build_claude_artifacts()
        assert s.CODEX_SKILLS_DIR / "llm-ops" / name in s.build_codex_skill_artifacts()


def test_prefixed_reference_links_resolve_in_generated_skills() -> None:
    references = {
        "agent-operations": ["agent-operations.SCHEDULING.md"],
        "code-change": ["code-change.FRONTEND.md", "code-change.REVIEW.md"],
        "context-engineering": ["context-engineering.REFERENCE.md"],
        "llm-ops": [
            "llm-ops.CONTRACTS.md",
            "llm-ops.EVALS.md",
            "llm-ops.TRANSPORTS.md",
        ],
        "judging": ["judging.EVALS.md", "judging.REFERENCE.md"],
    }
    claude = s.build_claude_artifacts()
    codex = s.build_codex_skill_artifacts()
    antigravity = s.build_antigravity_skill_artifacts()
    for skill, names in references.items():
        for name in names:
            assert s.SKILLS_DIR / skill / name in claude
            assert s.CODEX_SKILLS_DIR / skill / name in codex
            assert s.ANTIGRAVITY_SKILLS_DIR / skill / name in antigravity


def test_live_tree_has_no_artifact_or_doc_path_drift() -> None:
    """After a sync the generated Claude tree matches procedures/, and no rulebook doc names the
    hooks dir with a stale leading dot. These are the guards the pre-push --check relies on."""
    assert s.detect_artifact_drift() == []
    assert s.detect_codex_skill_drift() == []
    assert s.detect_antigravity_skill_drift() == []
    assert s.detect_doc_path_drift() == []


def test_generated_claude_files_use_lf_newlines() -> None:
    """Path.write_text CRLF-translates on Windows; the generator writes raw LF bytes so the Claude
    artifacts stay byte-identical to their LF procedures/ sources. Guard that regression."""
    targets = list(s.SKILLS_DIR.glob("*/SKILL.md")) + list(s.AGENTS_DIR.glob("*.md"))
    targets += list(s.CODEX_SKILLS_DIR.glob("*/SKILL.md"))
    targets += list(s.ANTIGRAVITY_SKILLS_DIR.glob("*/SKILL.md"))
    # files the generator writes: the /harden command + the docs whose tables it regenerates
    targets += [
        p
        for p in (s.COMMANDS_DIR / "harden.md", s.GEMINI_MD, s.GUIDE_PATH)
        if p.exists()
    ]
    assert targets, "expected generated Claude artifacts on disk"
    offenders = [str(p) for p in targets if b"\r" in p.read_bytes()]
    assert not offenders, (
        f"CR bytes (CRLF) in generated artifacts — generator must write LF: {offenders}"
    )


def test_gemini_routing_marker_inherits_the_canonical_table() -> None:
    marker = s.build_gemini_triggers()
    assert marker == "Procedure routing is inherited from `AGENTS.md`."
    assert "| Trigger |" not in marker
    assert "procedures/agents/" not in marker


def test_mcp_registry_builds_valid_configs_for_all_targets() -> None:
    configs = s.build_mcp_configs()
    assert len(configs) == len(s.MCP_TARGETS)
    for path, content in configs.items():
        assert content.endswith("\n")
        assert b"\r" not in content.encode("utf-8")
        parsed = s.json.loads(content)
        assert "mcpServers" in parsed
        assert isinstance(parsed["mcpServers"], dict)
        for universal in ("github", "linear", "fmp"):
            assert universal in parsed["mcpServers"]


def test_live_mcp_configs_have_no_drift() -> None:
    assert s.detect_mcp_drift() == []
