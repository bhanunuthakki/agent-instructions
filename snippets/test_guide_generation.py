"""Tests for the AGENTS_GUIDE.md self-update logic in sync_agent_stubs.py.

Structural assertions only — never the exact prose of a generated table, which changes as
skills/agents/projects come and go. We assert: the right sections exist, counts/names match the
live filesystem, marker injection preserves surrounding prose, and re-rendering is idempotent.

Run:  python -m pytest C:\\Users\\Bhanu\\.gemini\\snippets\\test_guide_generation.py
"""

from __future__ import annotations

import os
import sys
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
    configured_scratch = os.environ.get("BHANU_SCRATCH_ROOT")
    expected_scratch = (
        Path(configured_scratch).expanduser().resolve()
        if configured_scratch
        else expected_root / "antigravity" / "scratch"
    )
    assert s.SCRATCH == expected_scratch


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


def test_mac_bootstrap_uses_the_clone_and_home_directories() -> None:
    bootstrap = (s.ROOT_REPO / "snippets" / "bootstrap_mac.sh").read_text(
        encoding="utf-8"
    )

    assert 'ROOT_REPO=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)' in bootstrap
    assert 'DEVELOPER_ROOT=${BHANU_DEVELOPER_ROOT:-"$HOME/Developer"}' in bootstrap
    assert 'for PROJECT_DIR in "$DEVELOPER_ROOT"/*' in bootstrap
    assert "--check --artifacts-only" in bootstrap
    assert "BHANU_SCRATCH_ROOT" not in bootstrap
    assert "C:/Users/" not in bootstrap
    assert "C:\\Users\\" not in bootstrap


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
    earnings_local = (
        s.SCRATCH / "earnings-summary" / ".githooks" / "pre-push"
    ).read_text(encoding="utf-8")
    assert shared.count('run python "$stubs" --check') == 1
    assert "sync_agent_stubs.py" not in earnings_local


def test_command_artifacts_share_one_canonical_source() -> None:
    claude = s.build_claude_artifacts()
    codex = s.build_codex_skill_artifacts()
    for command, source in s.COMMAND_SOURCES.items():
        expected = source.read_text(encoding="utf-8", errors="replace")
        assert claude[s.COMMANDS_DIR / f"{command}.md"] == expected
        codex_name = "harden" if command == "harden" else f"source-command-{command}"
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
    for child in sorted(s.SCRATCH.iterdir()):
        if (
            not child.is_dir()
            or child.name.startswith(".")
            or child.name.startswith(s.SKIP_PREFIXES)
            or child.name in s.SKIP_PROJECT_NAMES
            or s.is_linked_git_worktree(child)
        ):
            continue
        assert child.name in body  # every real project surfaces, wired or not


def test_projects_section_excludes_hidden_and_temp_dirs() -> None:
    body = s.build_guide_sections()["projects"]
    for child in s.SCRATCH.iterdir():
        if child.is_dir() and (
            child.name.startswith(".") or child.name.startswith(s.SKIP_PREFIXES)
            or child.name in s.SKIP_PROJECT_NAMES
            or s.is_linked_git_worktree(child)
        ):
            assert (
                child.name not in body
            )  # Drive temp/hidden dirs never leak into the map


def test_project_discovery_checks_unwired_projects_too() -> None:
    expected = {
        child
        for child in s.SCRATCH.iterdir()
        if child.is_dir()
        and not child.name.startswith(".")
        and not child.name.startswith(s.SKIP_PREFIXES)
        and child.name not in s.SKIP_PROJECT_NAMES
        and not s.is_linked_git_worktree(child)
    }
    assert set(s.project_dirs()) == expected


def test_demo_sandbox_is_preserved_but_excluded_from_active_projects() -> None:
    assert "demo_sandbox" in s.SKIP_PROJECT_NAMES
    assert all(project.name != "demo_sandbox" for project in s.project_dirs())


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


def test_generated_project_wrappers_are_import_only() -> None:
    assert s.claude_stub("AGENTS.md") == "# Claude Code\n\n@./AGENTS.md\n"
    assert s.GEMINI_STUB == "# Gemini\n\n@./AGENTS.md\n"


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
    fleet = sorted(s.PROCEDURES_AGENTS_DIR.glob("*.md"))
    assert fleet, "expected fleet criteria in procedures/agents/"
    for ag in fleet:
        assert s.AGENTS_DIR / ag.name in arts
    assert all(content.strip() for content in arts.values())


def test_fleet_agents_default_to_execution_tier() -> None:
    fleet = sorted(s.PROCEDURES_AGENTS_DIR.glob("*.md"))
    assert fleet
    for agent in fleet:
        model = s.parse_frontmatter(agent.read_text(encoding="utf-8")).get("model")
        assert model in {"sonnet", "haiku"}, (
            f"{agent.name} pins {model!r}; Fable/Sol belong to the orchestrator, "
            "not routine fleet workers"
        )


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


def test_progressive_disclosure_skills_are_generated_for_both_runtimes() -> None:
    names = {
        "agent-operations",
        "code-change",
        "context-engineering",
        "external-practice",
        "linear-pipeline-hygiene",
        "linear-pr-sync",
    }
    assert names <= set(s.OUR_SKILLS)
    claude = s.build_claude_artifacts()
    codex = s.build_codex_skill_artifacts()
    for name in names:
        source = s.PROCEDURES_DIR / f"{name}.md"
        assert source.exists()
        assert s.SKILLS_DIR / name / "SKILL.md" in claude
        assert s.CODEX_SKILLS_DIR / name / "SKILL.md" in codex


def test_codex_gets_harden_as_a_skill_without_duplicating_claude_command() -> None:
    source = s.PROCEDURES_DIR / "harden.md"
    codex_target = s.CODEX_SKILLS_DIR / "harden" / "SKILL.md"
    assert codex_target in s.build_codex_skill_artifacts()
    assert s.SKILLS_DIR / "harden" / "SKILL.md" not in s.build_claude_artifacts()
    assert s.COMMANDS_DIR / "harden.md" in s.build_claude_artifacts()
    assert s.build_codex_skill_artifacts()[codex_target] == source.read_text(
        encoding="utf-8", errors="replace"
    )


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
    for skill, names in references.items():
        for name in names:
            assert s.SKILLS_DIR / skill / name in claude
            assert s.CODEX_SKILLS_DIR / skill / name in codex


def test_live_tree_has_no_artifact_or_doc_path_drift() -> None:
    """After a sync the generated Claude tree matches procedures/, and no rulebook doc names the
    hooks dir with a stale leading dot. These are the guards the pre-push --check relies on."""
    assert s.detect_artifact_drift() == []
    assert s.detect_codex_skill_drift() == []
    assert s.detect_doc_path_drift() == []


def test_generated_claude_files_use_lf_newlines() -> None:
    """Path.write_text CRLF-translates on Windows; the generator writes raw LF bytes so the Claude
    artifacts stay byte-identical to their LF procedures/ sources. Guard that regression."""
    targets = list(s.SKILLS_DIR.glob("*/SKILL.md")) + list(s.AGENTS_DIR.glob("*.md"))
    targets += list(s.CODEX_SKILLS_DIR.glob("*/SKILL.md"))
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


def test_gemini_triggers_row_per_procedure_pointing_at_procedures() -> None:
    table = s.build_gemini_triggers()
    for name in s.OUR_SKILLS:
        if (s.PROCEDURES_DIR / f"{name}.md").exists():
            assert name in table
            assert f"procedures/{name}.md" in table
    assert (
        "harden" in table and "procedures/agents/" in table
    )  # the fleet pointer surfaces


def test_gemini_trigger_table_is_a_compact_registry() -> None:
    table = s.build_gemini_triggers()
    assert "frontmatter 'use when'" not in table
    assert "Trigger" in table and "Procedure" in table


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
