"""Sync the AGENTS.md tool-agnostic instruction system across all scratch projects.

Idempotent. For every visible project directory under the scratch parent, report a missing
canonical AGENTS.md; when it exists, ensure both runtime wrappers exist so the repo's rules
load in *either* CLI:

  - CLAUDE.md  importing the local rulebook (Claude Code only reads CLAUDE.md up the tree)
  - GEMINI.md  importing AGENTS.md           (Gemini reads GEMINI.md natively)

For every git repo, point core.hooksPath at the shared githooks dir so the credential-scan
(pre-commit) and toolchain (pre-push) gates fire for both CLIs.

The procedures/ graph runs procedures -> runtime-native artifacts (see CANONICAL note below):
regenerate the Claude skills / the /harden command / the agent fleet and the Codex skills FROM the
canonical procedures/, regenerate the GEMINI.md skill-mimic trigger table, and regenerate the
inventory tables inside AGENTS_GUIDE.md's
<!-- BEGIN/END --> markers so the human map can never silently drift from the filesystem.

Run via:  python C:\\Users\\Bhanu\\.gemini\\snippets\\sync_agent_stubs.py [--dry-run | --check] [--artifacts-only]
Or the /sync-agent-stubs Claude command. --check is read-only and exits non-zero on any drift
(usable from CI / the pre-push hook). --artifacts-only skips project wrappers and hook wiring.
"""

from __future__ import annotations

import json
import re
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import definition_governance

SCRATCH = Path(r"C:\Users\Bhanu\.gemini\antigravity\scratch")
HOOKS_DIR = Path(r"C:\Users\Bhanu\.gemini\githooks")
ROOT_REPO = Path(r"C:\Users\Bhanu\.gemini")

# CANONICAL DIRECTION: procedures/ is the hand-authored SOURCE OF TRUTH. This script GENERATES the
# Claude and Codex skills, the /harden command, and the agent fleet FROM procedures/ — identity
# copies with only the directory layout remapped, so the round-trip is lossless. Gemini, Cursor,
# and local models can read procedures/ directly. Edit procedures/<name>.md — NEVER a generated
# ~/.claude/* or ~/.agents/* copy (it is overwritten).
CLAUDE_ROOT = Path(r"C:\Users\Bhanu\.claude")
SKILLS_DIR = CLAUDE_ROOT / "skills"
COMMANDS_DIR = CLAUDE_ROOT / "commands"
AGENTS_DIR = CLAUDE_ROOT / "agents"
CODEX_ROOT = Path(r"C:\Users\Bhanu\.agents")
CODEX_SKILLS_DIR = CODEX_ROOT / "skills"
PROCEDURES_DIR = Path(r"C:\Users\Bhanu\.gemini\procedures")
PROCEDURES_AGENTS_DIR = PROCEDURES_DIR / "agents"
AGENTS_MD = Path(r"C:\Users\Bhanu\.gemini\AGENTS.md")
GEMINI_MD = Path(r"C:\Users\Bhanu\.gemini\GEMINI.md")
CLAUDE_MD = Path(r"C:\Users\Bhanu\.gemini\CLAUDE.md")
OUR_SKILLS = [
    "agent-operations",
    "code-change",
    "context-engineering",
    "external-practice",
    "grill-me",
    "definitions",
    "judging",
    "llm-ops",
    "model-frontier",
    "log-redaction",
    "explain-change",
    "linear-pr-sync",
    "linear-pipeline-hygiene",
    "scaffold-auth",
    "scaffold-tenant-schema",
    "scaffold-design-system",
    "scaffold-secrets",
    "scaffold-deploy",
]
CODEX_ONLY_SKILLS = ["harden"]
COMMAND_SOURCES = {
    "harden": PROCEDURES_DIR / "harden.md",
    "refresh-frontier": PROCEDURES_DIR / "source-command-refresh-frontier.md",
    "sync-agent-stubs": PROCEDURES_DIR / "source-command-sync-agent-stubs.md",
}

MCP_REGISTRY = ROOT_REPO / "snippets" / "mcp_registry.json"
MCP_TARGETS: dict[str, Path] = {
    "gemini": ROOT_REPO / "config" / "mcp_config.json",
    "antigravity": ROOT_REPO / "antigravity" / "mcp_config.json",
    "claude": CLAUDE_ROOT / "mcp_config.json",
    "codex": CODEX_ROOT / "mcp_config.json",
}

# The human-facing system map. Its inventory tables (skills/commands/agents/procedures/projects)
# are regenerated from the filesystem between these markers so the counts can never silently drift;
# all prose OUTSIDE the markers is hand-written and left untouched.
GUIDE_PATH = Path(r"C:\Users\Bhanu\.gemini\AGENTS_GUIDE.md")
GUIDE_MARKERS = ("skills", "commands", "agents", "procedures", "projects")
# A healthy project CLAUDE.md/GEMINI.md is a thin @import wrapper. More than this much prose
# (beyond the title + import line) suggests a one-off leaked into the wrapper instead of the rulebook.
WRAPPER_MAX_CHARS = 500

# Temporary reconciliation/worktree directories are not projects. Every other visible
# scratch directory is an active project and must carry the standard AGENTS.md chain,
# including documentation-only repositories such as xr-glasses-dev-guide.
SKIP_PREFIXES = ("_presync", "_reconcile", "_redeploy", "localwip", "reconcile-backup")


def is_worktree_path(p: Path) -> bool:
    return ".claude" in p.parts and "worktrees" in p.parts


def rel_claude(p: Path) -> str:
    """Short, posix-style path under ~/.claude for readable action/drift lines."""
    try:
        return "~/.claude/" + p.relative_to(CLAUDE_ROOT).as_posix()
    except ValueError:
        return str(p)


def rel_codex(p: Path) -> str:
    """Short path under ~/.agents for readable action and drift lines."""
    try:
        return "~/.agents/" + p.relative_to(CODEX_ROOT).as_posix()
    except ValueError:
        return str(p)


def claude_stub(rulebook_name: str) -> str:
    return f"# Claude Code\n\n@./{rulebook_name}\n"


GEMINI_STUB = "# Gemini\n\n@./AGENTS.md\n"


def looks_generated(path: Path) -> bool:
    """True if the file is absent or a thin wrapper we own (safe to (re)write)."""
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    return "@./AGENTS.md" in text or "@./GEMINI.md" in text or len(text.strip()) < 120


def generated_wrapper_needs_update(path: Path, expected: str) -> bool:
    """True when a missing or generator-owned wrapper differs from the compact canonical stub."""
    if not path.exists():
        return True
    return looks_generated(path) and _norm(
        path.read_text(encoding="utf-8", errors="replace")
    ) != _norm(expected)


def project_dirs() -> list[Path]:
    out: list[Path] = []
    for child in sorted(SCRATCH.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name.startswith(SKIP_PREFIXES):
            continue
        out.append(child)
    return out


def ensure_wrappers(proj: Path, dry: bool) -> list[str]:
    actions: list[str] = []
    if not (proj / "AGENTS.md").exists():
        return actions
    rulebook = "AGENTS.md"

    claude_path = proj / "CLAUDE.md"
    expected_claude = claude_stub(rulebook)
    if generated_wrapper_needs_update(claude_path, expected_claude):
        actions.append(f"write {claude_path.name} (-> {rulebook}, import-only)")
        if not dry:
            claude_path.write_bytes(expected_claude.encode("utf-8"))

    # Only manage a GEMINI.md wrapper when the rulebook is AGENTS.md.
    if rulebook == "AGENTS.md":
        gemini_path = proj / "GEMINI.md"
        if generated_wrapper_needs_update(gemini_path, GEMINI_STUB):
            actions.append(f"write {gemini_path.name} (-> AGENTS.md, import-only)")
            if not dry:
                gemini_path.write_bytes(GEMINI_STUB.encode("utf-8"))
    return actions


def ensure_hooks(proj: Path, dry: bool) -> list[str]:
    if not (proj / ".git").exists():
        return []
    # One hooksPath can be active. Always point it at the shared safety hooks; those hooks
    # explicitly compose an optional project-local .githooks/<hook> instead of letting it
    # shadow credential scanning or the global instruction gate.
    target_hooks_val = HOOKS_DIR.as_posix()
    git_base = ["git", "-c", f"safe.directory={proj}", "-C", str(proj)]
    try:
        current = subprocess.run(
            [*git_base, "config", "--local", "core.hooksPath"],
            capture_output=True,
            text=True,
        ).stdout.strip()
    except FileNotFoundError:
        return ["git not found — skipped hook wiring"]
    if current == target_hooks_val:
        return []
    if not dry:
        subprocess.run(
            [
                *git_base,
                "config",
                "--local",
                "core.hooksPath",
                target_hooks_val,
            ],
            check=True,
        )
    return [f"set core.hooksPath -> {target_hooks_val}"]


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the single-line YAML frontmatter (name:, description:, tools:, ...). {} if absent.
    Values may themselves contain colons (descriptions do), so split on the first colon only."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line or line[:1].isspace() or ":" not in line:
            continue  # skip blanks and indented continuation lines
        key, _, val = line.partition(":")
        fields[key.strip()] = val.strip().strip('"')
    return fields


def first_sentence(desc: str, cap: int = 150) -> str:
    """The lead sentence of a frontmatter description, capped — keeps generated tables scannable."""
    desc = desc.strip()
    cut = desc.find(". ")
    if cut != -1:
        desc = desc[: cut + 1]
    if len(desc) > cap:
        desc = desc[: cap - 1].rstrip() + "…"
    return desc


def build_claude_artifacts() -> dict[Path, str]:
    """Pure: every Claude artifact path -> the exact content it SHOULD have, taken VERBATIM from its
    canonical procedures/ source (identity copy; only the directory layout is remapped). This is the
    inverse of the old build_procedures() — procedures/ is now the source, ~/.claude/* the output."""
    out: dict[Path, str] = {}

    # Skills: procedures/<name>.md -> skills/<name>/SKILL.md ; siblings procedures/<name>.<sib> -> skills/<name>/<sib>
    for name in OUR_SKILLS:
        proc = PROCEDURES_DIR / f"{name}.md"
        if not proc.exists():
            continue
        out[SKILLS_DIR / name / "SKILL.md"] = proc.read_text(
            encoding="utf-8", errors="replace"
        )
        for sib in sorted(PROCEDURES_DIR.glob(f"{name}.*.md")):
            sib_name = sib.name[
                len(name) + 1 :
            ]  # strip the "<name>." prefix -> REFERENCE.md
            content = sib.read_text(encoding="utf-8", errors="replace")
            out[SKILLS_DIR / name / sib_name] = content
            out[SKILLS_DIR / name / sib.name] = content

    # Commands: one canonical source per command, shared byte-for-byte with Codex.
    for command, source in COMMAND_SOURCES.items():
        if source.exists():
            out[COMMANDS_DIR / f"{command}.md"] = source.read_text(
                encoding="utf-8", errors="replace"
            )

    # Agent fleet: procedures/agents/<expert>.md -> agents/<expert>.md
    if PROCEDURES_AGENTS_DIR.exists():
        for ag in sorted(PROCEDURES_AGENTS_DIR.glob("*.md")):
            out[AGENTS_DIR / ag.name] = ag.read_text(encoding="utf-8", errors="replace")
    return out


def build_codex_skill_artifacts() -> dict[Path, str]:
    """Pure: canonical procedures mapped to Codex's native personal skill directory."""
    out: dict[Path, str] = {}
    for name in [*OUR_SKILLS, *CODEX_ONLY_SKILLS]:
        proc = PROCEDURES_DIR / f"{name}.md"
        if not proc.exists():
            continue
        out[CODEX_SKILLS_DIR / name / "SKILL.md"] = proc.read_text(
            encoding="utf-8", errors="replace"
        )
        for sibling in sorted(PROCEDURES_DIR.glob(f"{name}.*.md")):
            sibling_name = sibling.name[len(name) + 1 :]
            content = sibling.read_text(encoding="utf-8", errors="replace")
            out[CODEX_SKILLS_DIR / name / sibling_name] = content
            out[CODEX_SKILLS_DIR / name / sibling.name] = content
    for command, source in COMMAND_SOURCES.items():
        if not source.exists():
            continue
        skill_name = "harden" if command == "harden" else f"source-command-{command}"
        out[CODEX_SKILLS_DIR / skill_name / "SKILL.md"] = source.read_text(
            encoding="utf-8", errors="replace"
        )
    return out


def materialize_claude_artifacts(dry: bool) -> list[str]:
    """Write the Claude artifacts from procedures/ (overwrites — procedures/ is canonical). Compares
    and writes RAW BYTES with LF newlines, so a generated artifact is byte-identical to its LF
    source. (Path.write_text would translate LF->CRLF on Windows, silently breaking the identity
    copy — and _norm-based drift detection would never catch it.) Quiet on files already in sync."""
    arts = build_claude_artifacts()
    actions: list[str] = []
    for path, content in arts.items():
        data = content.encode(
            "utf-8"
        )  # content is LF — build_claude_artifacts read it universal-newline
        existing = path.read_bytes() if path.exists() else None
        if existing == data:
            continue
        actions.append(("write " if existing is None else "update ") + rel_claude(path))
        if not dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    actions += [
        f"SKIP {n} (procedures/{n}.md missing)"
        for n in OUR_SKILLS
        if not (PROCEDURES_DIR / f"{n}.md").exists()
    ]
    return actions


def materialize_codex_skill_artifacts(dry: bool) -> list[str]:
    """Write byte-identical Codex skill copies from canonical procedures/."""
    actions: list[str] = []
    for path, content in build_codex_skill_artifacts().items():
        data = content.encode("utf-8")
        existing = path.read_bytes() if path.exists() else None
        if existing == data:
            continue
        actions.append(("write " if existing is None else "update ") + rel_codex(path))
        if not dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return actions


def _norm(s: str) -> str:
    """Normalize newlines + trailing whitespace so a linter's reformat isn't mistaken for an edit."""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in s.split("\n")).strip("\n")


def detect_artifact_drift() -> list[str]:
    """A generated Claude artifact was hand-edited away from its procedures/ source, is missing, or is
    an orphan (an agent with no procedures/ source). Edit the procedure, not the generated copy."""
    arts = build_claude_artifacts()
    drift: list[str] = []
    for path, expected in arts.items():
        if not path.exists():
            drift.append(
                f"{rel_claude(path)}: MISSING — run sync to generate it from procedures/"
            )
        elif _norm(path.read_text(encoding="utf-8", errors="replace")) != _norm(
            expected
        ):
            drift.append(
                f"{rel_claude(path)}: diverged from its procedures/ source (hand-edited?) — "
                f"sync OVERWRITES it; edit the canonical procedures/ file, not the Claude copy"
            )
    # Orphan check on the agent fleet only — the whole agents/ dir is ours (the fleet). (Skills are
    # left alone: the user may keep personal Claude-only skills under skills/ that we don't generate.)
    if AGENTS_DIR.exists():
        for p in sorted(AGENTS_DIR.glob("*.md")):
            if p not in arts:
                drift.append(
                    f"{rel_claude(p)}: ORPHAN (no procedures/agents/ source) — "
                    f"add the procedure or delete the agent"
                )
    return drift


def detect_codex_skill_drift() -> list[str]:
    """Report missing or divergent Codex skills generated from procedures/."""
    drift: list[str] = []
    for path, expected in build_codex_skill_artifacts().items():
        if not path.exists():
            drift.append(
                f"{rel_codex(path)}: MISSING — run sync to generate it from procedures/"
            )
        elif _norm(path.read_text(encoding="utf-8", errors="replace")) != _norm(
            expected
        ):
            drift.append(
                f"{rel_codex(path)}: diverged from its procedures/ source — "
                "sync OVERWRITES it; edit the canonical procedure"
            )
    return drift


def _rel_target(p: Path) -> str:
    try:
        return "~/.claude/" + p.relative_to(CLAUDE_ROOT).as_posix()
    except ValueError:
        pass
    try:
        return "~/.agents/" + p.relative_to(CODEX_ROOT).as_posix()
    except ValueError:
        pass
    try:
        return p.relative_to(ROOT_REPO).as_posix()
    except ValueError:
        return str(p)


def build_mcp_configs() -> dict[Path, str]:
    """Pure: compile the canonical mcp_registry.json into target JSON config strings."""
    if not MCP_REGISTRY.exists():
        return {}
    data = json.loads(MCP_REGISTRY.read_text(encoding="utf-8"))
    servers = data.get("servers", {})
    configs: dict[Path, str] = {}
    for target_name, path in MCP_TARGETS.items():
        matched_servers: dict[str, Any] = {}
        for server_name, spec in sorted(servers.items()):
            targets = spec.get("targets", ["all"])
            if "all" in targets or target_name in targets:
                entry: dict[str, Any] = {}
                if "command" in spec:
                    entry["command"] = spec["command"]
                if "args" in spec:
                    entry["args"] = spec["args"]
                if "env" in spec:
                    entry["env"] = spec["env"]
                matched_servers[server_name] = entry
        payload = {"mcpServers": matched_servers}
        configs[path] = json.dumps(payload, indent=2) + "\n"
    return configs


def materialize_mcp_configs(dry: bool) -> list[str]:
    """Write target MCP configs derived from the canonical mcp_registry.json."""
    configs = build_mcp_configs()
    actions: list[str] = []
    for path, content in configs.items():
        data = content.encode("utf-8")
        existing = path.read_bytes() if path.exists() else None
        if existing == data:
            continue
        rel = _rel_target(path)
        actions.append(("write " if existing is None else "update ") + f"{rel} from mcp_registry.json")
        if not dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return actions


def detect_mcp_drift() -> list[str]:
    """Report drift between canonical mcp_registry.json and runtime MCP config files."""
    configs = build_mcp_configs()
    drift: list[str] = []
    for path, expected in configs.items():
        rel = _rel_target(path)
        if not path.exists():
            drift.append(
                f"{rel}: MISSING MCP config — run sync to generate it from mcp_registry.json"
            )
        elif _norm(path.read_text(encoding="utf-8", errors="replace")) != _norm(expected):
            drift.append(
                f"{rel}: diverged from canonical mcp_registry.json — "
                "run /sync-agent-stubs to regenerate"
            )
    return drift


def detect_command_orphans(
    commands_dir: Path = COMMANDS_DIR, codex_skills_dir: Path = CODEX_SKILLS_DIR
) -> list[str]:
    expected_commands = {f"{name}.md" for name in COMMAND_SOURCES}
    expected_codex = {
        f"source-command-{name}" for name in COMMAND_SOURCES if name != "harden"
    }
    findings: list[str] = []
    if commands_dir.exists():
        for path in sorted(commands_dir.glob("*.md")):
            if path.name not in expected_commands:
                findings.append(
                    f"{path}: ORPHAN command with no canonical COMMAND_SOURCES entry"
                )
    if codex_skills_dir.exists():
        for path in sorted(codex_skills_dir.glob("source-command-*")):
            if path.is_dir() and path.name not in expected_codex:
                findings.append(
                    f"{path}: ORPHAN source-command skill with no canonical command source"
                )
    return findings


def detect_definition_override_drift(
    root_definitions: Path = ROOT_REPO / "DEFINITIONS.md",
    definition_files: list[Path] | None = None,
) -> list[str]:
    if not root_definitions.exists():
        return [f"{root_definitions}: missing global definition registry"]
    _metadata, root_terms = definition_governance.parse_document(root_definitions)
    reserved = {
        definition_governance.normalize_term(term): term for term in root_terms
    }
    if definition_files is None:
        definition_files = []
        skipped = {
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".tmp",
            ".claude",
            "__pycache__",
            "build",
            "dist",
            "deployment",
            "deploy",
            "backups",
        }
        for project in project_dirs():
            for directory, children, files in os.walk(project):
                children[:] = [child for child in children if child not in skipped]
                if "DEFINITIONS.md" in files:
                    definition_files.append(Path(directory) / "DEFINITIONS.md")
    findings: list[str] = []
    for path in definition_files:
        _metadata, terms = definition_governance.parse_document(path)
        for term in terms:
            normalized = definition_governance.normalize_term(term)
            if normalized in reserved:
                findings.append(
                    f"{path}: downstream override of global term {reserved[normalized]!r}"
                )
    return findings


def detect_doc_path_drift() -> list[str]:
    """The rulebook prose names the hooks dir with a leading dot (`.githooks`) — the dir is `githooks`
    (HOOKS_DIR.name), wired per-repo via core.hooksPath. Flag the stale token so prose can't drift
    from the filesystem (the kind of mismatch the inventory generators otherwise prevent)."""
    drift: list[str] = []
    for doc in (AGENTS_MD, GEMINI_MD, CLAUDE_MD):
        if doc.exists() and ".githooks" in doc.read_text(
            encoding="utf-8", errors="replace"
        ):
            drift.append(
                f"{doc.name}: references `.githooks` but the hooks dir is "
                f"`{HOOKS_DIR.name}` (no dot) — fix the wording"
            )
    return drift


def detect_hook_capability_drift() -> list[str]:
    required = {
        "pre-commit": ("credential", ".githooks/pre-commit"),
        "pre-push": ("sync_agent_stubs.py", ".githooks/pre-push"),
    }
    findings: list[str] = []
    for hook, tokens in required.items():
        path = HOOKS_DIR / hook
        if not path.exists():
            findings.append(f"{path}: missing required shared hook")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                findings.append(f"{path}: missing required capability token {token!r}")
    return findings


def semantic_documents() -> list[Path]:
    docs = [AGENTS_MD, GEMINI_MD, CLAUDE_MD, GUIDE_PATH]
    docs.extend(sorted(PROCEDURES_DIR.rglob("*.md")))
    docs.extend(proj / "AGENTS.md" for proj in project_dirs())
    return [path for path in docs if path.exists()]


def detect_semantic_drift(
    docs: list[Path] | None = None, *, root_doc: Path = AGENTS_MD
) -> list[str]:
    """Catch meaning-level contradictions that byte identity cannot detect."""
    findings: list[str] = []
    paths = docs if docs is not None else semantic_documents()
    root_text = (
        root_doc.read_text(encoding="utf-8", errors="replace")
        if root_doc.exists()
        else ""
    )
    root_headings = {
        match.group(1).strip().casefold()
        for match in re.finditer(r"^##\s+(.+?)\s*$", root_text, re.MULTILINE)
    }
    reversed_direction = re.compile(
        r"(?:claude\s+)?skills?\s+(?:are|is)\s+(?:the\s+)?canonical|"
        r"procedures?\s+(?:are|is)\s+overwritten|overwrite(?:s|n)?\s+(?:the\s+)?procedures?",
        re.IGNORECASE,
    )
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if reversed_direction.search(text):
            findings.append(
                f"{path}: reverses canonical direction; procedures generate runtime artifacts"
            )
        if re.search(
            r"\bno\s+`?DEFINITIONS\.md`?\s+(?:yet|exists)", text, re.IGNORECASE
        ):
            if (path.parent / "DEFINITIONS.md").exists():
                findings.append(
                    f"{path}: claims no DEFINITIONS.md exists, but the file is present"
                )
        for heading in re.findall(r"\[\[root:([^\]]+)\]\]", text):
            if heading.strip().casefold() not in root_headings:
                findings.append(f"{path}: missing root heading reference {heading!r}")
        ordinary_refs = re.findall(
            r"(?:global\s+)?`AGENTS\.md`\s*§\s*([^\n.,;)]+)", text, re.IGNORECASE
        )
        ordinary_refs += re.findall(
            r"(?:global\s+)?`AGENTS\.md`\s*(?:→|->)\s*[\"“]([^\"”]+)",
            text,
            re.IGNORECASE,
        )
        for heading in ordinary_refs:
            if heading.strip().casefold() not in root_headings:
                findings.append(f"{path}: missing root heading reference {heading!r}")

        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            raw_path = target.partition("#")[0]
            if not raw_path or any(char in raw_path for char in "*<>"):
                continue
            resolved = (path.parent / raw_path).resolve()
            if not resolved.exists():
                findings.append(f"{path}: missing Markdown target {target!r}")

    frontier = PROCEDURES_DIR / "model-frontier.REFERENCE.md"
    if docs is None and frontier.exists():
        text = frontier.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"Next review:\s*(\d{4}-\d{2}-\d{2})", text)
        if not match:
            findings.append(f"{frontier}: missing machine-checkable Next review date")
        elif date.fromisoformat(match.group(1)) < date.today():
            findings.append(f"{frontier}: model frontier review is expired")
    return findings


def _md_table(header: tuple[str, str], rows: list[tuple[str, str]]) -> str:
    lines = [f"| {header[0]} | {header[1]} |", "|---|---|"]
    lines += [f"| {left} | {right} |" for left, right in rows]
    return "\n".join(lines)


def build_gemini_triggers() -> str:
    """Pure: compact Gemini procedure registry derived from canonical procedures/.

    Trigger descriptions already live in frontmatter. Repeating them in always-loaded GEMINI.md
    wastes context and can drift, so this table is navigation only.
    """
    entries = [(n, PROCEDURES_DIR / f"{n}.md") for n in sorted(OUR_SKILLS)]
    entries.append(("harden", PROCEDURES_DIR / "harden.md"))
    rows: list[tuple[str, str]] = []
    for name, p in entries:
        if not p.exists():
            continue
        target = f"`procedures/{name}.md`"
        if name == "model-frontier":
            target += " (+ `model-frontier.REFERENCE.md`)"
        if name == "harden":
            target += " (+ `procedures/agents/`)"
        rows.append((f"**{name}**", target))
    return _md_table(("Trigger", "Procedure"), rows)


def materialize_gemini_triggers(dry: bool) -> list[str]:
    """Regenerate GEMINI.md's trigger table inside its markers (prose preserved). Auto-fixed in SYNC."""
    if not GEMINI_MD.exists():
        return ["SKIP GEMINI.md (not found)"]
    current = GEMINI_MD.read_text(encoding="utf-8", errors="replace")
    try:
        updated = _replace_marked(current, "triggers", build_gemini_triggers())
    except ValueError as exc:
        return [
            f"GEMINI.md: {exc} — add <!-- BEGIN:triggers -->/<!-- END:triggers --> markers, then re-run"
        ]
    if (
        updated.encode("utf-8") == GEMINI_MD.read_bytes()
    ):  # byte-exact, incl. LF (heals CRLF drift)
        return []
    if not dry:
        GEMINI_MD.write_bytes(updated.encode("utf-8"))
    return ["GEMINI.md: regenerated skill-mimic trigger table from procedures/"]


def detect_gemini_drift() -> list[str]:
    """The Gemini trigger table fell out of sync with procedures/ (or lost its markers)."""
    if not GEMINI_MD.exists():
        return []
    current = GEMINI_MD.read_text(encoding="utf-8", errors="replace")
    try:
        updated = _replace_marked(current, "triggers", build_gemini_triggers())
    except ValueError as exc:
        return [f"GEMINI.md: {exc}"]
    if _norm(updated) != _norm(current):
        return [
            "GEMINI.md: trigger table stale vs procedures/ — run /sync-agent-stubs to regenerate"
        ]
    return []


def build_guide_sections() -> dict[str, str]:
    """Pure: the inventory tables AGENTS_GUIDE.md should hold, derived ENTIRELY from the filesystem
    (skills + the /harden command from the canonical procedures/, the agent fleet from
    procedures/agents/, projects from scratch). Because the counts + names are computed here, the
    human map can never silently fall out of step with what is actually on disk."""
    skill_rows: list[tuple[str, str]] = []
    for name in sorted(OUR_SKILLS):
        md = PROCEDURES_DIR / f"{name}.md"
        if not md.exists():
            continue
        desc = parse_frontmatter(md.read_text(encoding="utf-8", errors="replace")).get(
            "description", ""
        )
        skill_rows.append((f"**{name}**", first_sentence(desc)))
    skills = (
        f"**{len(skill_rows)} shared skills** — say the trigger, the agent runs the procedure. "
        f"Codex also exposes `harden` as a native skill; Claude exposes the same procedure as "
        f"`/harden`.\n\n" + _md_table(("Skill", "What it does"), skill_rows)
    )

    cmd_rows: list[tuple[str, str]] = []
    for md in sorted(COMMANDS_DIR.glob("*.md")):
        desc = parse_frontmatter(md.read_text(encoding="utf-8", errors="replace")).get(
            "description", ""
        )
        cmd_rows.append((f"`/{md.stem}`", first_sentence(desc)))
    commands = f"**{len(cmd_rows)} commands** — type these.\n\n" + _md_table(
        ("Command", "What it does"), cmd_rows
    )

    agent_rows: list[tuple[str, str]] = []
    for md in (
        sorted(PROCEDURES_AGENTS_DIR.glob("*.md"))
        if PROCEDURES_AGENTS_DIR.exists()
        else []
    ):
        desc = parse_frontmatter(md.read_text(encoding="utf-8", errors="replace")).get(
            "description", ""
        )
        agent_rows.append((f"`{md.stem}`", first_sentence(desc)))
    agents = (
        f"**{len(agent_rows)} audit agents** — criteria canonical in `procedures/agents/`, generated "
        f"into `~/.claude/agents/` for Claude's `/harden` dispatch (most are SaaS-grade and won't "
        f"fire on personal tools — that's the L1 cap).\n\n"
        + _md_table(("Agent", "Audits"), agent_rows)
    )

    proc_files = (
        sorted(p.name for p in PROCEDURES_DIR.glob("*.md"))
        if PROCEDURES_DIR.exists()
        else []
    )
    agent_files = (
        sorted(p.name for p in PROCEDURES_AGENTS_DIR.glob("*.md"))
        if PROCEDURES_AGENTS_DIR.exists()
        else []
    )
    procedures = (
        f"**{len(proc_files)} files** in `procedures/` (+ **{len(agent_files)} fleet criteria** "
        f"in `procedures/agents/`) — the **canonical, tool-neutral source**. "
        f"`sync_agent_stubs.py` generates {len(OUR_SKILLS)} shared Claude and Codex skills, "
        f"Codex's `harden` skill, Claude's `/harden` command, and the agent fleet FROM these, "
        f"so every runtime reads the same "
        f"markdown Claude runs:\n\n" + ", ".join(f"`{f}`" for f in proc_files)
    )

    wired_rows: list[tuple[str, str]] = []
    unwired: list[str] = []
    for child in sorted(SCRATCH.iterdir()):
        if (
            not child.is_dir()
            or child.name.startswith(".")
            or child.name.startswith(SKIP_PREFIXES)
        ):
            continue  # skip hidden/temp dirs (.git, .tmp.driveupload) and known non-project prefixes
        if (child / "AGENTS.md").exists() or (child / "GEMINI.md").exists():
            present = [
                n
                for n in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
                if (child / n).exists()
            ]
            wired_rows.append((child.name, ", ".join(present)))
        else:
            unwired.append(child.name)
    projects = (
        f"**{len(wired_rows)} projects** carry the rulebook — each layers its own `AGENTS.md` "
        f"on the global core, with thin `CLAUDE.md`/`GEMINI.md` wrappers:\n\n"
        + _md_table(("Project", "Rulebook files present"), wired_rows)
    )
    if unwired:
        projects += (
            "\n\n_Not wired (no `AGENTS.md`, so the global rulebook is not inherited — run "
            "`/sync-agent-stubs` after adding one): "
            + ", ".join(f"`{n}`" for n in unwired)
            + "._"
        )

    return {
        "skills": skills,
        "commands": commands,
        "agents": agents,
        "procedures": procedures,
        "projects": projects,
    }


def _replace_marked(text: str, key: str, body: str) -> str:
    begin, end = f"<!-- BEGIN:{key} -->", f"<!-- END:{key} -->"
    i, j = text.find(begin), text.find(end)
    if i == -1 or j == -1 or j < i:
        raise ValueError(f"missing or malformed <!-- BEGIN/END:{key} --> markers")
    return text[: i + len(begin)] + "\n" + body.strip("\n") + "\n" + text[j:]


def render_guide(current: str) -> str:
    """Inject each generated inventory section into its marked region; all prose stays untouched."""
    sections = build_guide_sections()
    for key in GUIDE_MARKERS:
        current = _replace_marked(current, key, sections[key])
    return current


def materialize_guide(dry: bool) -> list[str]:
    """Regenerate AGENTS_GUIDE.md's inventory tables in place (prose preserved). Auto-fixed in SYNC."""
    if not GUIDE_PATH.exists():
        return ["SKIP AGENTS_GUIDE.md (not found)"]
    current = GUIDE_PATH.read_text(encoding="utf-8", errors="replace")
    try:
        updated = render_guide(current)
    except ValueError as exc:
        return [f"AGENTS_GUIDE.md: {exc} — add the markers, then re-run"]
    if (
        updated.encode("utf-8") == GUIDE_PATH.read_bytes()
    ):  # byte-exact, incl. LF (heals CRLF drift)
        return []
    if not dry:
        GUIDE_PATH.write_bytes(updated.encode("utf-8"))
    return [
        "AGENTS_GUIDE.md: regenerated inventory tables (skills/commands/agents/procedures/projects)"
    ]


def detect_guide_drift() -> list[str]:
    """The human map's inventory tables fell out of sync with the filesystem (or lost its markers)."""
    if not GUIDE_PATH.exists():
        return []
    current = GUIDE_PATH.read_text(encoding="utf-8", errors="replace")
    try:
        updated = render_guide(current)
    except ValueError as exc:
        return [f"AGENTS_GUIDE.md: {exc}"]
    if _norm(updated) != _norm(current):
        return [
            "AGENTS_GUIDE.md: inventory tables stale vs filesystem — run /sync-agent-stubs to regenerate"
        ]
    return []


def detect_wrapper_drift(proj: Path) -> list[str]:
    """A project's CLAUDE.md / GEMINI.md should be a thin @import of the rulebook. Flag content
    that leaked into a wrapper (a one-off rule belongs in the rulebook, where every tool sees it)."""
    drift: list[str] = []
    if not (proj / "AGENTS.md").exists():
        return [
            f"{proj.name}/AGENTS.md: MISSING canonical project rulebook — "
            "author a minimal project-specific rulebook, then run sync"
        ]
    rulebook = "AGENTS.md"
    for n in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        if n == rulebook:
            continue  # the canonical rulebook is allowed to carry content
        p = proj / n
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "@" not in text:
            drift.append(
                f"{proj.name}/{n}: no @import of {rulebook} — should be a thin wrapper"
            )
            continue
        body_lines = [
            ln
            for ln in text.splitlines()
            if not ln.strip().startswith("@")
            and not (ln.strip().startswith("#") and not ln.strip().startswith("##"))
        ]
        body = "\n".join(body_lines).strip()
        reasons: list[str] = []
        if any(ln.strip().startswith("##") for ln in body_lines):
            reasons.append("has ## section(s)")
        if "```" in body:
            reasons.append("has a code block")
        if len(body) > WRAPPER_MAX_CHARS:
            reasons.append(f"{len(body)} chars of extra prose")
        if reasons:
            drift.append(
                f"{proj.name}/{n}: content leaked into a wrapper ({', '.join(reasons)}) — "
                f"move shared rules into {rulebook}; keep the wrapper thin"
            )
    return drift


def includes_project_wiring(argv: list[str]) -> bool:
    """Whether this invocation may update per-project wrappers and Git hooks."""
    return "--artifacts-only" not in argv


def main() -> None:
    dry = "--dry-run" in sys.argv
    check = (
        "--check" in sys.argv
    )  # read-only audit; exits non-zero if anything is off (CI/hook usable)
    readonly = dry or check
    if not SCRATCH.exists():
        print(f"scratch parent not found: {SCRATCH}")
        sys.exit(1)
    mode = "CHECK (read-only)" if check else ("DRY RUN" if dry else "SYNC")
    print(f"[{mode}] agent stubs under {SCRATCH}\n")

    pending = False
    drift: list[str] = []
    if includes_project_wiring(sys.argv):
        root_actions = ensure_hooks(ROOT_REPO, readonly)
        if root_actions:
            pending = True
            print("[.gemini]")
            for action in root_actions:
                print(f"  - {action}")
        for proj in project_dirs():
            if is_worktree_path(proj):
                continue
            actions = ensure_wrappers(proj, readonly) + ensure_hooks(proj, readonly)
            if actions:
                pending = True
                print(f"[{proj.name}]")
                for a in actions:
                    print(f"  - {a}")
            drift += detect_wrapper_drift(proj)

    claude_actions = materialize_claude_artifacts(readonly)
    if claude_actions:
        print(
            "[claude artifacts — generated from procedures/ (skills · /harden · agent fleet)]"
        )
        for a in claude_actions:
            print(f"  - {a}")
    if readonly:  # in SYNC mode artifacts are just overwritten (auto-fixed)
        drift += detect_artifact_drift()

    codex_actions = materialize_codex_skill_artifacts(readonly)
    if codex_actions:
        print("[codex skills — generated from procedures/]")
        for action in codex_actions:
            print(f"  - {action}")
    if readonly:
        drift += detect_codex_skill_drift()

    guide_actions = materialize_guide(readonly)
    if guide_actions:
        print(
            "[AGENTS_GUIDE.md — human map; inventory tables regenerated from the filesystem]"
        )
        for a in guide_actions:
            print(f"  - {a}")
    if readonly:  # in SYNC mode the guide tables are regenerated (auto-fixed)
        drift += detect_guide_drift()

    gemini_actions = materialize_gemini_triggers(readonly)
    if gemini_actions:
        print("[GEMINI.md — skill-mimic trigger table regenerated from procedures/]")
        for a in gemini_actions:
            print(f"  - {a}")
    if readonly:  # in SYNC mode the trigger table is regenerated (auto-fixed)
        drift += detect_gemini_drift()

    mcp_actions = materialize_mcp_configs(readonly)
    if mcp_actions:
        print("[mcp configs — synchronized from snippets/mcp_registry.json]")
        for a in mcp_actions:
            print(f"  - {a}")
    if readonly:
        drift += detect_mcp_drift()

    drift += (
        detect_doc_path_drift()
    )  # always read-only — a prose fix needs human attention
    drift += detect_hook_capability_drift()
    drift += detect_command_orphans()
    drift += detect_definition_override_drift()
    drift += detect_semantic_drift()

    if drift:
        print("\n[drift — needs YOUR attention (not auto-fixed):]")
        for d in drift:
            print(f"  ! {d}")
    else:
        print("\nno content drift detected.")
    print("done.")

    if check and (drift or pending):
        sys.exit(1)


if __name__ == "__main__":
    main()
