"""Tests for the AGENTS_GUIDE.md self-update logic in sync_agent_stubs.py.

Structural assertions only — never the exact prose of a generated table, which changes as
skills/agents/projects come and go. We assert: the right sections exist, counts/names match the
live filesystem, marker injection preserves surrounding prose, and re-rendering is idempotent.

Run:  python -m pytest C:\\Users\\Bhanu\\.gemini\\snippets\\test_guide_generation.py
"""

from __future__ import annotations

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
        ):
            continue
        assert child.name in body  # every real project surfaces, wired or not


def test_projects_section_excludes_hidden_and_temp_dirs() -> None:
    body = s.build_guide_sections()["projects"]
    for child in s.SCRATCH.iterdir():
        if child.is_dir() and (
            child.name.startswith(".") or child.name.startswith(s.SKIP_PREFIXES)
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
    }
    assert set(s.project_dirs()) == expected


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
