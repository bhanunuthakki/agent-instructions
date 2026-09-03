"""Audit and initialize the project-owned interface authority handshake.

The shared frontend procedure owns composition rules. Every project declares its
interface profile through a compact ``## Interface`` block in its closest
``AGENTS.md``; visual projects also name their exact contract, executable authority,
render recipe, and deterministic gate.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

PROFILES = frozenset({"dense-desktop", "editorial-reading", "touch-first", "none"})
FIELDS = ("Profile", "Contract", "Executable authority", "Render", "Gate")
LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


@dataclass(frozen=True, slots=True)
class ContractResult:
    repo: Path
    findings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.findings


def _interface_section(text: str) -> str | None:
    match = re.search(r"^## Interface\s*$", text, re.MULTILINE)
    if match is None:
        return None
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.MULTILINE)
    return tail[: next_heading.start()] if next_heading else tail


def without_interface_section(text: str) -> str:
    """Remove a repository-local Interface section from text exported globally."""
    match = re.search(r"^## Interface\s*$", text, re.MULTILINE)
    if match is None:
        return text.strip()
    tail = text[match.end() :]
    next_heading = re.search(r"^##\s+", tail, re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return (text[: match.start()] + text[end:]).strip()


def parse_interface(text: str) -> dict[str, str] | None:
    section = _interface_section(text)
    if section is None:
        return None
    values: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*-\s+([^:]+):\s*(.*?)\s*$", line)
        if match and match.group(1) in FIELDS:
            values[match.group(1)] = match.group(2).strip().strip("`")
    return values


def _relative_file(repo: Path, raw: str, label: str) -> tuple[Path | None, list[str]]:
    findings: list[str] = []
    if not raw:
        return None, [f"Interface {label} is empty"]
    candidate = Path(raw)
    if candidate.is_absolute():
        return None, [f"Interface {label} must be repository-relative: {raw}"]
    resolved = (repo / candidate).resolve()
    try:
        resolved.relative_to(repo.resolve())
    except ValueError:
        return None, [f"Interface {label} escapes the repository: {raw}"]
    if not resolved.is_file():
        findings.append(f"Interface {label} does not exist: {raw}")
    return resolved, findings


def check_repo(repo: Path) -> ContractResult:
    repo = repo.resolve()
    rulebook = repo / "AGENTS.md"
    if not rulebook.is_file():
        return ContractResult(repo, ("missing AGENTS.md",))
    interface = parse_interface(rulebook.read_text(encoding="utf-8", errors="replace"))
    if interface is None:
        return ContractResult(repo, ("missing ## Interface authority block",))

    findings = []
    profile = interface.get("Profile", "")
    if "Profile" not in interface:
        findings.append("Interface field is missing: Profile")
    if profile not in PROFILES:
        findings.append(
            f"Interface Profile must be one of {', '.join(sorted(PROFILES))}: {profile or '<empty>'}"
        )
    if profile == "none":
        for field in FIELDS[1:]:
            if field in interface:
                findings.append(
                    f"Interface {field} must be omitted when Profile is `none`"
                )
        return ContractResult(repo, tuple(findings))

    findings.extend(
        f"Interface field is missing: {field}"
        for field in FIELDS[1:]
        if field not in interface
    )

    contract_path, contract_findings = _relative_file(
        repo, interface.get("Contract", ""), "Contract"
    )
    findings.extend(contract_findings)
    authorities = [
        value.strip().strip("`")
        for value in interface.get("Executable authority", "").split(",")
        if value.strip()
    ]
    if not authorities:
        findings.append("Interface Executable authority is empty")
    for authority in authorities:
        _path, authority_findings = _relative_file(
            repo, authority, "Executable authority"
        )
        findings.extend(authority_findings)
    for field in ("Render", "Gate"):
        if not interface.get(field) or interface.get(field) == "none":
            findings.append(f"Interface {field} must name a runnable project command")

    if contract_path and contract_path.is_file():
        contract = contract_path.read_text(encoding="utf-8", errors="replace")
        for target in LINK.findall(contract):
            target = target.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith("#"):
                continue
            linked = Path(target)
            if linked.is_absolute():
                findings.append(
                    f"Interface Contract contains an absolute local link: {target}"
                )
                continue
            resolved = (contract_path.parent / linked).resolve()
            try:
                resolved.relative_to(repo)
            except ValueError:
                findings.append(
                    f"Interface Contract links outside the repository: {target}"
                )
                continue
            if not resolved.exists():
                findings.append(f"Interface Contract link does not exist: {target}")
    return ContractResult(repo, tuple(findings))


def check_estate_repo(repo: Path) -> ContractResult:
    """Apply the same explicit interface-declaration contract estate-wide."""
    return check_repo(repo)


def project_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return [
        child
        for child in sorted(root.iterdir())
        if child.is_dir()
        and (child / ".git").exists()
        and not child.name.startswith(".")
    ]


def render_block(profile: str) -> str:
    if profile == "none":
        return "## Interface\n- Profile: none\n"
    return (
        "## Interface\n"
        f"- Profile: {profile}\n"
        "- Contract: docs/UI_CONTRACT.md\n"
        "- Executable authority: TODO/project-owned-style-or-token-path\n"
        "- Render: TODO runnable command and primary viewport\n"
        "- Gate: TODO deterministic contract check\n"
    )


def render_contract(profile: str) -> str:
    return (
        "# Interface contract\n\n"
        f"Profile seed: `{profile}`. This project-owned document is the continuing authority; "
        "the shared profile is only a starting hypothesis.\n\n"
        "Define the primary task, density and viewport, semantic typography, spacing, controls, "
        "state feedback, responsive behavior, sanctioned exceptions, and rendered evidence here.\n"
    )


def initialize(repo: Path, profile: str) -> None:
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    rulebook = repo / "AGENTS.md"
    if not rulebook.is_file():
        raise ValueError(f"missing AGENTS.md: {rulebook}")
    current = rulebook.read_text(encoding="utf-8")
    if parse_interface(current) is not None:
        raise ValueError(f"Interface block already exists: {rulebook}")
    contract = repo / "docs" / "UI_CONTRACT.md"
    if profile != "none" and contract.exists():
        raise ValueError(f"Interface contract already exists: {contract}")
    rulebook.write_text(
        current.rstrip() + "\n\n" + render_block(profile), encoding="utf-8"
    )
    if profile != "none":
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(render_contract(profile), encoding="utf-8")


def _print_result(result: ContractResult) -> None:
    status = "OK" if result.ok else "WARN"
    print(f"[{status}] {result.repo}")
    for finding in result.findings:
        print(f"  - {finding}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--repo", type=Path, required=True)
    estate = subparsers.add_parser("check-estate")
    estate.add_argument("--root", type=Path, required=True)
    estate.add_argument("--strict", action="store_true")
    init = subparsers.add_parser("init")
    init.add_argument("--repo", type=Path, required=True)
    init.add_argument("--profile", choices=sorted(PROFILES), required=True)
    args = parser.parse_args()

    if args.command == "init":
        initialize(args.repo.resolve(), args.profile)
        _print_result(check_repo(args.repo))
        return 0
    if args.command == "check":
        result = check_repo(args.repo)
        _print_result(result)
        return 0 if result.ok else 1
    results = [check_estate_repo(repo) for repo in project_dirs(args.root.resolve())]
    for result in results:
        _print_result(result)
    failures = sum(not result.ok for result in results)
    print(
        f"checked {len(results)} repositories; {failures} need an Interface declaration"
    )
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
