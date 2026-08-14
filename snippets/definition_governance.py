"""Validate tiered DEFINITIONS.md files and recommend vocabulary lifecycle changes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterable

METADATA_FIELDS = ("Scope", "Owner", "Inherits")
SCOPES = {"global", "cross-project", "project", "subtree"}
MATURITIES = ("observed", "candidate", "ratified")


def _entries(text: str) -> list[tuple[str, str]]:
    """Read both heading entries and the bold-bullet format used by older glossaries."""
    boundaries: list[tuple[int, int, str]] = []
    for match in re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE):
        boundaries.append((match.start(), match.end(), match.group(1).strip()))
    for match in re.finditer(r"^-\s+\*\*(.+?)\*\*\s*(?:—|–|-)\s*", text, re.MULTILINE):
        boundaries.append((match.start(), match.end(), match.group(1).strip()))
    boundaries.sort()
    entries: list[tuple[str, str]] = []
    for index, (_start, body_start, term) in enumerate(boundaries):
        body_end = (
            boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        )
        entries.append((term, text[body_start:body_end].strip()))
    return entries


def parse_document(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata: dict[str, str] = {}
    for field in METADATA_FIELDS:
        match = re.search(rf"^\*\*{field}:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
        if match:
            metadata[field] = match.group(1).strip()
    terms: dict[str, str] = {}
    for term, body in _entries(text):
        terms.setdefault(term, body)
    return metadata, terms


def normalize_term(term: str) -> str:
    return re.sub(r"\s+", " ", term.strip()).casefold()


def _inherit_path(path: Path, raw: str) -> Path | None:
    if raw.strip().casefold() == "none":
        return None
    # Markdown authored on Windows sometimes escaped each backslash. Normalize both forms.
    normalized = raw.replace("\\\\", "\\")
    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = path.parent / candidate
    return candidate.resolve()


def validate_document(path: Path, *, strict_entries: bool = False) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata, _terms = parse_document(path)
    errors = [
        f"{path}: missing metadata {field}"
        for field in METADATA_FIELDS
        if field not in metadata
    ]
    if metadata.get("Scope") not in SCOPES:
        errors.append(f"{path}: Scope must be one of {sorted(SCOPES)}")
    if not metadata.get("Owner", "").strip():
        errors.append(f"{path}: Owner must be non-empty")
    entries = _entries(text)
    for term, body in entries:
        if strict_entries and term.startswith(("Registered ", "Cross-project ")):
            continue
        if strict_entries and "**Definition.**" not in body:
            errors.append(f"{path}: {term!r} lacks **Definition.**")
    normalized = [normalize_term(term) for term, _body in entries]
    wrapper_counts: dict[str, int] = {}
    for index, (term, body) in enumerate(entries):
        next_is_same = index + 1 < len(entries) and normalize_term(
            entries[index + 1][0]
        ) == normalize_term(term)
        if re.match(rf"^-\s+\*\*{re.escape(term)}\*\*", body, re.IGNORECASE):
            key = normalize_term(term)
            wrapper_counts[key] = wrapper_counts.get(key, 0) + 1
        elif not body and next_is_same:
            key = normalize_term(term)
            wrapper_counts[key] = wrapper_counts.get(key, 0) + 1
    duplicates = sorted(
        {
            term
            for term in normalized
            if normalized.count(term) - wrapper_counts.get(term, 0) > 1
        }
    )
    for term in duplicates:
        errors.append(f"{path}: duplicate normalized definition term {term!r}")
    return errors


def validate_chain(root: Path, descendants: Iterable[Path]) -> list[str]:
    """Validate true parent topology; sibling files never become accidental ancestors."""
    root = root.resolve()
    documents = [root, *(path.resolve() for path in descendants)]
    errors = validate_document(root, strict_entries=True)
    root_metadata, _root_terms = parse_document(root)
    if (
        root_metadata.get("Scope") != "global"
        or _inherit_path(root, root_metadata.get("Inherits", "")) is not None
    ):
        errors.append(f"{root}: root must have Scope global and Inherits none")

    known = set(documents)
    parent_by_path: dict[Path, Path | None] = {root: None}
    for path in documents[1:]:
        errors.extend(validate_document(path))
        metadata, _terms = parse_document(path)
        parent = _inherit_path(path, metadata.get("Inherits", ""))
        parent_by_path[path] = parent
        if parent not in known:
            errors.append(
                f"{path}: Inherits target {parent} is not in the supplied chain"
            )

    for path in documents[1:]:
        _metadata, terms = parse_document(path)
        ancestors: dict[str, str] = {}
        seen: set[Path] = set()
        cursor = parent_by_path.get(path)
        while cursor is not None and cursor in known:
            if cursor in seen:
                errors.append(f"{path}: inheritance cycle at {cursor}")
                break
            seen.add(cursor)
            _ancestor_metadata, ancestor_terms = parse_document(cursor)
            ancestors.update({normalize_term(term): term for term in ancestor_terms})
            cursor = parent_by_path.get(cursor)
        for term in terms:
            normalized = normalize_term(term)
            if normalized in ancestors:
                errors.append(
                    f"{path}: downstream override of {ancestors[normalized]!r}; "
                    "use a distinct qualified term or narrow/remove the ancestor definition"
                )
    return errors


def discover_chain(target: Path, *, global_file: Path) -> list[Path]:
    """Return the declared global-to-closest definition chain for a task path."""
    target = target.resolve()
    global_file = global_file.resolve()
    start = target if target.is_dir() else target.parent
    closest: Path | None = None
    for directory in (start, *start.parents):
        candidate = directory / "DEFINITIONS.md"
        if candidate.exists() and candidate.resolve() != global_file:
            closest = candidate.resolve()
            break
    if closest is None:
        return [global_file]

    reverse_chain: list[Path] = []
    seen: set[Path] = set()
    cursor = closest
    while cursor != global_file:
        if cursor in seen:
            raise ValueError(f"definition inheritance cycle at {cursor}")
        seen.add(cursor)
        errors = validate_document(cursor)
        if errors:
            raise ValueError("; ".join(errors))
        reverse_chain.append(cursor)
        metadata, _terms = parse_document(cursor)
        parent = _inherit_path(cursor, metadata["Inherits"])
        if parent is None or not parent.exists():
            raise ValueError(f"{cursor}: declared Inherits target is unavailable")
        cursor = parent
    root_errors = validate_document(global_file, strict_entries=True)
    if root_errors:
        raise ValueError("; ".join(root_errors))
    return [global_file, *reversed(reverse_chain)]


def _is_strict_descendant(child: Path, ancestor: Path) -> bool:
    child = child.resolve()
    ancestor = ancestor.resolve()
    if child == ancestor:
        return False
    seen: set[Path] = set()
    cursor = child
    while cursor not in seen:
        seen.add(cursor)
        metadata, _terms = parse_document(cursor)
        parent = _inherit_path(cursor, metadata.get("Inherits", ""))
        if parent is None:
            return False
        if parent == ancestor:
            return True
        if not parent.exists():
            return False
        cursor = parent
    return False


def recommend_definition_change(
    *,
    real_uses: int,
    project_count: int,
    identical_meaning: bool,
    override_requests: int,
    owner_ratified: bool,
    current_scope: str,
    current_maturity: str,
    current_definition_file: Path,
    owning_definition_file: Path | None,
) -> dict[str, Any]:
    if min(real_uses, project_count, override_requests) < 0:
        raise ValueError("definition evidence counts must be non-negative")
    if current_scope not in SCOPES:
        raise ValueError(f"unknown definition scope {current_scope!r}")
    if current_maturity not in MATURITIES:
        raise ValueError(f"unknown definition maturity {current_maturity!r}")
    if override_requests:
        if owning_definition_file is None:
            return {
                "action": "hold",
                "target_scope": current_scope,
                "target_maturity": current_maturity,
                "reason": "owning_definition_file_required",
            }
        current_definition_file = current_definition_file.resolve()
        owning_definition_file = owning_definition_file.resolve()
        if not current_definition_file.exists() or not owning_definition_file.exists():
            return {
                "action": "hold",
                "target_scope": current_scope,
                "target_maturity": current_maturity,
                "reason": "definition_topology_unavailable",
            }
        owning_metadata, _terms = parse_document(owning_definition_file)
        target_scope = owning_metadata.get("Scope")
        if (
            target_scope not in SCOPES
            or not owning_metadata.get("Owner", "").strip()
            or not _is_strict_descendant(
                owning_definition_file, current_definition_file
            )
        ):
            return {
                "action": "hold",
                "target_scope": current_scope,
                "target_maturity": current_maturity,
                "reason": "owning_definition_must_be_strict_descendant",
            }
        return {
            "action": "demote_scope",
            "target_scope": target_scope,
            "target_owner": owning_metadata["Owner"],
            "target_definition_file": str(owning_definition_file),
            "target_maturity": current_maturity,
            "reason": "override_request_proves_meaning_is_not_shared",
        }

    target_maturity = "observed"
    if real_uses >= 2:
        target_maturity = "candidate"
    if real_uses >= 3 and owner_ratified:
        target_maturity = "ratified"
    target_scope = current_scope
    if real_uses >= 6 and project_count >= 2 and identical_meaning:
        target_scope = "global" if owner_ratified else "cross-project"
    action = "hold"
    if MATURITIES.index(target_maturity) > MATURITIES.index(current_maturity):
        action = "promote_maturity"
    if target_scope != current_scope:
        action = "promote_scope"
    return {
        "action": action,
        "target_scope": target_scope,
        "target_maturity": target_maturity,
        "reason": "usage_evidence",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("descendants", type=Path, nargs="*")
    args = parser.parse_args()
    errors = validate_chain(args.root, args.descendants)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("definition chain valid")


if __name__ == "__main__":
    main()
