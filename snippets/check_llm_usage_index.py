"""Validate the fleet LLM usage index and its delegated project authorities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from llm_policy import POLICY_PATH, RoutingPolicyError, load_policy

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "config" / "llm_usage_index.json"
_ROUTE_STATES = {"fleet_default", "migration_hold", "migration_required"}
_JUDGE_ROUTE_STATES = {
    "project_explicit",
    "shared_subscription",
    "migration_hold",
    "migration_required",
}
_WORKLOAD_CLASSES = {"application", "judge"}
_SCAN_MARKERS = (
    "from codex_cli import",
    "from claude_cli import",
    "call_codex_with_usage",
    "openrouter.ai/api/",
)
_JUDGE_MARKERS = (
    "backend_compare_judge",
    "judge_model",
    "LLM-judge",
    "specialist_judge",
)
_SKIP_PARTS = {
    ".git",
    ".next",
    ".tmp",
    ".venv",
    "build",
    "data",
    "dist",
    "node_modules",
    "venv",
}


def _reference_path(project_root: Path, reference: str) -> Path:
    relative, _, _symbol = reference.partition(":")
    return project_root / relative


def _contains_symbol(path: Path, reference: str) -> bool:
    _relative, separator, symbol = reference.partition(":")
    return not separator or symbol in path.read_text(encoding="utf-8", errors="replace")


def _discover_projects(developer_root: Path, markers: tuple[str, ...]) -> set[str]:
    discovered: set[str] = set()
    for project in developer_root.iterdir():
        # Only canonical checkouts own fleet registrations. Linked worktrees have
        # a .git file and inherit the canonical project's index entry.
        if not project.is_dir() or not (project / ".git").is_dir():
            continue
        for path in project.rglob("*"):
            if any(part in _SKIP_PARTS for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".ps1", ".ts"} or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(marker in text for marker in markers):
                discovered.add(project.name)
                break
    return discovered


def _discover_llm_projects(developer_root: Path) -> set[str]:
    return _discover_projects(developer_root, _SCAN_MARKERS)


def _discover_judge_projects(developer_root: Path) -> set[str]:
    return _discover_projects(developer_root, _JUDGE_MARKERS)


def validate_index(
    *,
    root: Path = ROOT,
    developer_root: Path | None = None,
    check_projects: bool = True,
) -> list[str]:
    errors: list[str] = []
    try:
        load_policy(root / POLICY_PATH.relative_to(ROOT))
    except RoutingPolicyError as exc:
        errors.append(str(exc))

    index_path = root / INDEX_PATH.relative_to(ROOT)
    try:
        raw = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["config/llm_usage_index.json is unavailable or invalid"]
    if not isinstance(raw, dict) or raw.get("$schema") != "internal://llm-usage-index/v1":
        return ["config/llm_usage_index.json has an unsupported schema"]
    if raw.get("routing_policy") != "config/llm_routing_policy.json":
        errors.append("the usage index must reference the canonical routing policy")
    if raw.get("judge_registry") != "config/judge_registry.json":
        errors.append("the usage index must reference the canonical Judge registry")

    projects = raw.get("projects")
    if not isinstance(projects, list):
        return [*errors, "the usage index projects field must be a list"]
    names: list[str] = []
    required = {
        "project",
        "instruction_section",
        "entrypoint",
        "purpose_registry",
        "ledger_authority",
        "budget_authority",
        "eval_authority",
        "workload_classes",
        "application_route",
        "judge_route_state",
        "judge_route_authority",
        "judge_independence_authority",
        "judge_migration_note",
        "migration_note",
    }
    active_developer_root = developer_root or root.parent
    for entry in projects:
        if not isinstance(entry, dict) or set(entry) != required:
            errors.append("every usage-index project entry must use the exact v1 fields")
            continue
        name = entry["project"]
        if not isinstance(name, str) or not name:
            errors.append("every usage-index project must have a non-empty name")
            continue
        names.append(name)
        workload_classes = entry["workload_classes"]
        if (
            not isinstance(workload_classes, list)
            or not workload_classes
            or len(workload_classes) != len(set(workload_classes))
            or not set(workload_classes) <= _WORKLOAD_CLASSES
        ):
            errors.append(f"{name}: workload_classes must be unique registered classes")
            workload_classes = []
        route_state = entry["application_route"]
        if "application" in workload_classes and route_state not in _ROUTE_STATES:
            errors.append(f"{name}: unsupported application_route {route_state!r}")
        if "application" not in workload_classes and route_state is not None:
            errors.append(f"{name}: Judge-only entries cannot define application_route")
        judge_state = entry["judge_route_state"]
        judge_note = entry["judge_migration_note"]
        if "judge" in workload_classes:
            if judge_state not in _JUDGE_ROUTE_STATES:
                errors.append(f"{name}: Judge workloads require a registered route state")
            if entry["judge_route_authority"] is None:
                errors.append(f"{name}: Judge workloads require a delegated route authority")
            if entry["judge_independence_authority"] is None:
                errors.append(f"{name}: Judge workloads require an independence authority")
            if judge_state in {"project_explicit", "shared_subscription"} and judge_note is not None:
                errors.append(f"{name}: current Judge routes cannot retain a migration note")
            if judge_state in {"migration_hold", "migration_required"} and not isinstance(
                judge_note, str
            ):
                errors.append(f"{name}: incomplete Judge routing requires a migration note")
        elif any(
            entry[field] is not None
            for field in (
                "judge_route_state",
                "judge_route_authority",
                "judge_independence_authority",
                "judge_migration_note",
            )
        ):
            errors.append(f"{name}: non-Judge entries cannot define Judge routing fields")
        note = entry["migration_note"]
        if route_state in {None, "fleet_default"} and note is not None:
            errors.append(f"{name}: current or Judge-only entries cannot retain a migration note")
        if route_state in {"migration_hold", "migration_required"} and not isinstance(note, str):
            errors.append(f"{name}: incomplete application routing requires a migration note")
        if not check_projects:
            continue

        project_root = active_developer_root / name
        if not project_root.is_dir():
            errors.append(f"{name}: repository is unavailable")
            continue
        instruction_section = entry["instruction_section"]
        rulebook = project_root / "AGENTS.md"
        if not isinstance(instruction_section, str) or not rulebook.is_file() or instruction_section not in rulebook.read_text(encoding="utf-8", errors="replace"):
            errors.append(f"{name}: delegated instruction section is missing")
        for field in (
            "entrypoint",
            "purpose_registry",
            "ledger_authority",
            "budget_authority",
            "eval_authority",
            "judge_route_authority",
            "judge_independence_authority",
        ):
            reference = entry[field]
            if reference is None:
                continue
            if not isinstance(reference, str):
                errors.append(f"{name}: {field} must be a path reference or null")
                continue
            path = _reference_path(project_root, reference)
            if not path.exists():
                errors.append(f"{name}: {field} target does not exist: {reference}")
            elif not _contains_symbol(path, reference):
                errors.append(f"{name}: {field} symbol does not exist: {reference}")
        if route_state == "fleet_default":
            entrypoint = _reference_path(project_root, entry["entrypoint"])
            if entrypoint.is_file():
                source = entrypoint.read_text(encoding="utf-8", errors="replace")
                consumes_policy = "llm_policy" in source or "fleet_policy" in source
                if not consumes_policy or "subscription_route" not in source:
                    errors.append(
                        f"{name}: fleet_default entry point does not consume the shared resolver"
                    )
        if judge_state == "shared_subscription":
            judge_path = _reference_path(project_root, entry["judge_route_authority"])
            if judge_path.is_file():
                source = judge_path.read_text(encoding="utf-8", errors="replace")
                if "WorkloadClass.JUDGE" not in source or "explicit_judge_route" not in source:
                    errors.append(
                        f"{name}: shared_subscription Judge route does not consume an explicit shared route"
                    )

    if len(names) != len(set(names)):
        errors.append("usage-index project names must be unique")
    if names != sorted(names):
        errors.append("usage-index projects must be sorted by name")
    if check_projects and active_developer_root.is_dir():
        missing = sorted(_discover_llm_projects(active_developer_root) - set(names))
        for name in missing:
            errors.append(f"{name}: application LLM use is not present in the fleet usage index")
        indexed_judges = {
            entry["project"]
            for entry in projects
            if isinstance(entry, dict) and "judge" in entry.get("workload_classes", [])
        }
        missing_judges = sorted(
            _discover_judge_projects(active_developer_root) - indexed_judges
        )
        for name in missing_judges:
            errors.append(f"{name}: Judge LLM use is not registered as a Judge workload")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--developer-root", type=Path)
    parser.add_argument("--schema-only", action="store_true")
    args = parser.parse_args(argv)
    errors = validate_index(
        root=args.root,
        developer_root=args.developer_root,
        check_projects=not args.schema_only,
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
