#!/usr/bin/env python3
"""Validate hardening state v2 and run its deterministic, fail-closed preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "internal://harden-state/v2"
MANDATORY_SCHEMA = "internal://harden-mandatory-rules/v1"
POLICY_SCHEMA = "internal://harden-eval-policy/v1"
REGISTRY_SCHEMA = "internal://harden-capability-registry/v1"
RECEIPT_SCHEMA = "internal://harden-capability-receipt/v2"
SCORE_SCHEMA = "internal://harden-capability-score/v2"
CASE_RESULT_SCHEMA = "internal://harden-capability-case-result/v2"
REQUEST_SCHEMA = "internal://harden-capability-request/v2"
OUTPUT_SCHEMA = "internal://harden-capability-output/v2"
GATE_PURPOSE = "hardening-gate-verdict"
PRIVATE_STATE_ENV = "AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT"
RUNGS = ("L0", "L1", "L2", "L3")
RUNTIMES = ("claude", "codex", "gemini", "antigravity")
VERDICTS = {"PASS", "BLOCK", "ADVISORY", "HOLD", "N/A"}
VERDICT_BASES = {"none", "model_receipt", "deterministic_mandatory"}
MODES = {"B", "A", "R"}
ACTIVE_EXPERTS = (
    "idea-evaluator", "product-feature", "architecture-reviewer", "data-foundation",
    "qa-test-strategy", "ux-design", "frontend-web", "llm-evals-orchestrator",
    "sec-appsec", "sec-authz", "sec-llm", "api-surface-designer",
    "legal-compliance", "operations-readiness", "tenant-boundaries",
    "product-analytics", "docs-support-readiness", "finops-pricing", "payments",
)
MATRIX: dict[str, dict[str, str]] = {
    "idea-evaluator": {"L0": "B"},
    "product-feature": {"L0": "A", "L1": "B", "L2": "R", "L3": "R"},
    "architecture-reviewer": {"L0": "A", "L1": "B", "L2": "R", "L3": "R"},
    "data-foundation": {"L1": "B", "L2": "R", "L3": "R"},
    "qa-test-strategy": {"L1": "B", "L2": "R", "L3": "B"},
    "ux-design": {"L1": "B", "L2": "R", "L3": "B"},
    "frontend-web": {"L1": "B", "L2": "R", "L3": "B"},
    "llm-evals-orchestrator": {"L1": "B", "L2": "R", "L3": "R"},
    "sec-appsec": {"L1": "B", "L2": "R", "L3": "R"},
    "sec-authz": {"L1": "B", "L2": "R", "L3": "R"},
    "sec-llm": {"L1": "B", "L2": "R", "L3": "R"},
    "api-surface-designer": {"L1": "A", "L2": "B", "L3": "R"},
    "legal-compliance": {"L0": "A", "L1": "A", "L2": "B", "L3": "R"},
    "operations-readiness": {"L1": "B", "L2": "B", "L3": "R"},
    "tenant-boundaries": {"L2": "B", "L3": "R"},
    "product-analytics": {"L2": "A", "L3": "B"},
    "docs-support-readiness": {"L1": "B", "L2": "B", "L3": "R"},
    "finops-pricing": {"L0": "A", "L1": "A", "L2": "A", "L3": "B"},
    "payments": {"L3": "B"},
}
PROFILE_ENUMS = {
    "deployment": {"local", "distributed-client", "hosted-single-customer", "hosted-shared"},
    "identity": {"none", "single-user", "multi-user", "multi-tenant"},
    "commerce": {"personal", "free", "paid"},
    "llm": {"none", "read-only", "tool-using"},
}
SURFACES = {"cli", "api", "web", "native"}
DATA_KINDS = {"durable", "external", "sensitive"}
CAPABILITY_CASE_SHAPES = {
    "normal", "empty", "long-context", "malformed", "adversarial",
    "degraded", "conflicting-evidence",
}
FINGERPRINT_KEYS = {"worktree", "profile", "matrix", "rubrics"}
CAPABILITY_ROLES = {"mechanical-worker", "implementation-worker", "blocking-specialist", "frontier-synthesizer"}
CAPABILITY_STATUSES = {"AVAILABLE", "UNAVAILABLE", "UNCALIBRATED"}
CAPABILITY_KEYS = {"receipt_id", "status", "role", "runtime", "model_id", "effort", "qualified_rubrics", "limitations", "receipt_hash"}
GATE_KEYS = {
    "mode", "applicability", "rationale", "verdict", "verdict_basis",
    "open_findings", "finding_rules", "evidence", "evidence_hashes",
    "capability_receipt", "run_at", "fingerprints",
}
STATIC_PACKAGE_FILES = (
    "SKILL.md", "runtime/harden_state.py", "config/harden_state_v2.schema.json",
    "config/harden_mandatory_rules.json", "config/harden_eval_policy.json",
    "config/harden_capability_registry.json", "evals/cases.jsonl",
)
ALLOWED_VERIFIER = {
    "kind": "builtin",
    "subprocesses": [
        {
            "executable": "git",
            "arguments": [
                "-c", "core.quotepath=false", "diff", "--no-ext-diff", "--no-color",
                "--unified=0", "--no-renames", "HEAD", "--",
            ],
            "timeout_seconds": 10,
            "expected_exits": {"0": "SCAN", "other": "ERROR"},
            "output_schema": "git-unified-diff-v1",
        },
        {
            "executable": "git",
            "arguments": ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
            "timeout_seconds": 10,
            "expected_exits": {"0": "SCAN", "other": "ERROR"},
            "output_schema": "git-status-porcelain-v1-z",
        },
    ],
}
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
)


class StateError(ValueError):
    """The supplied state or authority cannot be trusted."""


class PackageHold(RuntimeError):
    """Required harness evidence is unavailable; no product defect is proven."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _digest(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _utc_timestamp(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{where} must be a non-empty UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise StateError(f"{where} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise StateError(f"{where} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _require_keys(value: dict[str, Any], expected: set[str], where: str) -> None:
    if set(value) != expected:
        raise StateError(f"{where} keys must be exactly {sorted(expected)}")


def _load_json(path: Path, where: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PackageHold(f"missing {where}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"{where} is malformed JSON: {path}") from exc
    if not isinstance(value, dict):
        raise StateError(f"{where} must be a JSON object")
    return value


def _contained_file(root: Path, relative_value: Any, where: str) -> Path:
    if not isinstance(relative_value, str) or not relative_value.strip():
        raise StateError(f"{where} must be a non-empty relative path")
    relative = Path(relative_value)
    if relative.is_absolute() or ".." in relative.parts:
        raise StateError(f"{where} must stay inside its authority root")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise StateError(f"{where} must stay inside its authority root") from exc
    if not path.is_file():
        raise PackageHold(f"{where} is missing")
    return path


def validate_profile(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StateError("profile must be an object")
    required = {*PROFILE_ENUMS, "surfaces", "data", "scheduled_work"}
    _require_keys(value, required, "profile")
    for key, allowed in PROFILE_ENUMS.items():
        if value[key] not in allowed:
            raise StateError(f"profile.{key} must be one of {sorted(allowed)}")
    if not isinstance(value["surfaces"], list) or not set(value["surfaces"]) <= SURFACES:
        raise StateError(f"profile.surfaces must be a list drawn from {sorted(SURFACES)}")
    if not isinstance(value["data"], list) or not set(value["data"]) <= DATA_KINDS:
        raise StateError(f"profile.data must be a list drawn from {sorted(DATA_KINDS)}")
    if len(value["surfaces"]) != len(set(value["surfaces"])) or len(value["data"]) != len(set(value["data"])):
        raise StateError("profile list values must be unique")
    if not isinstance(value["scheduled_work"], bool):
        raise StateError("profile.scheduled_work must be boolean")
    return value


def profile_fingerprint(profile: dict[str, Any]) -> str:
    return _digest(_canonical(validate_profile(profile)))


def matrix_fingerprint() -> str:
    return _digest(_canonical({"experts": ACTIVE_EXPERTS, "matrix": MATRIX, "version": 2}))


def _is_package(root: Path) -> bool:
    return (root / "rubrics").is_dir() or (root / "runtime" / "harden_state.py").is_file()


def _private_state_root(root: Path) -> Path:
    raw = os.environ.get(PRIVATE_STATE_ENV)
    if not raw:
        return (root / ".private-state").resolve()
    configured = Path(raw).expanduser()
    if not configured.is_absolute():
        raise StateError(f"{PRIVATE_STATE_ENV} must be an absolute path")
    return configured.resolve()


def _rubric_path(root: Path, expert: str) -> Path:
    return root / "rubrics" / f"{expert}.md" if _is_package(root) else root / "procedures" / "agents" / f"{expert}.md"


def _config_path(root: Path, name: str) -> Path:
    if not _is_package(root) and name in {
        "harden_capability_registry.json",
        "harden_eval_policy.json",
    }:
        private = _private_state_root(root) / "config" / name
        if private.is_file():
            return private
    return root / "config" / name


def _dataset_path(root: Path) -> Path:
    return root / "evals" / "cases.jsonl" if _is_package(root) else root / "evals" / "harden" / "cases.jsonl"


def _receipt_path(root: Path, receipt_id: str) -> Path:
    if _is_package(root):
        return root / "receipts" / f"{receipt_id}.json"
    return (
        _private_state_root(root)
        / "governance"
        / "harden_capability_receipts"
        / f"{receipt_id}.json"
    )


def _evidence_path(root: Path, receipt_id: str, name: str) -> Path:
    if _is_package(root):
        return root / "evidence" / receipt_id / name
    return (
        _private_state_root(root)
        / "governance"
        / "harden_capability_evidence"
        / receipt_id
        / name
    )


def _registry_entries(root: Path) -> list[dict[str, Any]]:
    registry = _load_json(_config_path(root, "harden_capability_registry.json"), "capability registry")
    _require_keys(registry, {"$schema", "schema_version", "purpose", "qualifications"}, "capability registry")
    if registry["$schema"] != REGISTRY_SCHEMA or registry["schema_version"] != 1 or registry["purpose"] != GATE_PURPOSE:
        raise StateError("capability registry schema or purpose is invalid")
    if not isinstance(registry["qualifications"], list):
        raise StateError("capability registry qualifications must be a list")
    seen: set[str] = set()
    for entry in registry["qualifications"]:
        if not isinstance(entry, dict):
            raise StateError("capability registry entries must be objects")
        _require_keys(entry, {"receipt_id", "receipt_hash"}, "capability registry entry")
        if not isinstance(entry["receipt_id"], str) or not entry["receipt_id"] or entry["receipt_id"] in seen:
            raise StateError("capability registry receipt IDs must be unique and non-empty")
        if not isinstance(entry["receipt_hash"], str):
            raise StateError("capability registry receipt hash must be a string")
        seen.add(entry["receipt_id"])
    return registry["qualifications"]


def authority_fingerprint(root: Path) -> str:
    paths = [_rubric_path(root, expert) for expert in ACTIVE_EXPERTS]
    paths.extend(_config_path(root, name) for name in (
        "harden_state_v2.schema.json", "harden_mandatory_rules.json",
        "harden_eval_policy.json", "harden_capability_registry.json",
    ))
    paths.append(_dataset_path(root))
    if not _is_package(root):
        paths.extend(root / "procedures" / name for name in ("harden.md", "frontend-quality.md", "agent-operations.md"))
    for entry in _registry_entries(root):
        receipt_id = entry["receipt_id"]
        paths.extend((_receipt_path(root, receipt_id), _evidence_path(root, receipt_id, "per_case_outputs.jsonl"), _evidence_path(root, receipt_id, "score.json")))
    payload = bytearray(b"harden-authority-v2\0")
    for path in sorted(paths, key=lambda item: item.as_posix()):
        if not path.is_file():
            raise PackageHold(f"hardening authority dependency is missing: {path}")
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            relative = path.as_posix()
        payload.extend(relative.encode() + b"\0" + path.read_bytes() + b"\0")
    return _digest(bytes(payload))


def package_fingerprint(package_root: Path) -> str:
    payload = bytearray(b"harden-package-v1\0")
    for path in sorted(item for item in package_root.rglob("*") if item.is_file()):
        relative = path.relative_to(package_root).as_posix()
        if "__pycache__" in path.parts or relative.endswith(".pyc"):
            continue
        payload.extend(relative.encode() + b"\0" + path.read_bytes() + b"\0")
    return _digest(bytes(payload))


def _git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, shell=False, timeout=30)
    if result.returncode:
        raise StateError(f"git {' '.join(args)} failed without usable evidence")
    return result.stdout


def _excluded(relative: str) -> bool:
    return relative == ".harden" or relative.startswith(".harden/") or relative.startswith("docs/hardening/")


def worktree_fingerprint(repo: Path) -> str:
    repo = repo.resolve()
    paths = _git(repo, "ls-files", "-co", "--exclude-standard", "-z").split(b"\0")
    payload = bytearray(b"harden-product-tree-v2\0")
    for raw in sorted(set(path for path in paths if path)):
        relative = raw.decode(errors="surrogateescape")
        if _excluded(relative):
            continue
        path = repo / relative
        if not path.exists() and not path.is_symlink():
            continue
        executable = b"1" if path.lstat().st_mode & 0o111 else b"0"
        payload.extend(b"path\0" + raw + b"\0exec\0" + executable + b"\0")
        if path.is_symlink():
            payload.extend(b"symlink\0" + path.readlink().as_posix().encode() + b"\0")
        elif path.is_file():
            payload.extend(b"file\0" + path.read_bytes() + b"\0")
    return _digest(bytes(payload))


def current_fingerprints(repo: Path, authority_root: Path, profile: dict[str, Any]) -> dict[str, str]:
    return {"worktree": worktree_fingerprint(repo), "profile": profile_fingerprint(profile), "matrix": matrix_fingerprint(), "rubrics": authority_fingerprint(authority_root)}


def _applicability(expert: str, profile: dict[str, Any], rung: str) -> tuple[bool, str]:
    surfaces, data = set(profile["surfaces"]), set(profile["data"])
    if expert == "data-foundation":
        return bool(data), "selected for durable, external, or sensitive data" if data else "no persistent or external data"
    if expert == "ux-design":
        human = surfaces & {"web", "native", "cli"}
        return bool(human), "selected for a human-facing interface" if human else "no human-facing interface"
    if expert == "frontend-web":
        return "web" in surfaces, "selected for a web surface" if "web" in surfaces else "no web surface"
    if expert in {"llm-evals-orchestrator", "sec-llm"}:
        applies = profile["llm"] != "none"
        return applies, "selected because the product calls an LLM" if applies else "no LLM call"
    if expert == "sec-authz":
        if profile["identity"] != "none":
            return True, "selected because the profile declares an identity boundary"
        remote = profile["deployment"] != "local" and bool(surfaces & {"web", "api"})
        return (True, "selected because a non-local web/API product surface requires an explicit access-control decision") if remote else (False, "no declared identity or non-local web/API product surface")
    if expert == "api-surface-designer":
        return "api" in surfaces, "selected for a product-owned API surface" if "api" in surfaces else "no product-owned API surface"
    if expert == "tenant-boundaries":
        applies = profile["identity"] == "multi-tenant"
        return applies, "selected for genuine multi-tenancy" if applies else "profile is not multi-tenant"
    if expert == "operations-readiness":
        applies = bool(data) or profile["scheduled_work"] or profile["deployment"] != "local"
        return applies, "selected for durable state, scheduled work, distribution, or hosting" if applies else "no durable state, scheduler, distribution, or hosting"
    if expert == "legal-compliance":
        applies = bool(data & {"external", "sensitive"}) or profile["identity"] in {"multi-user", "multi-tenant"} or profile["deployment"] != "local" or profile["commerce"] == "paid"
        return applies, "selected for data, users, distribution, or commerce obligations" if applies else "no identified obligation trigger"
    if expert == "product-analytics":
        applies = rung in {"L2", "L3"} and (profile["commerce"] != "personal" or profile["identity"] in {"multi-user", "multi-tenant"} or profile["deployment"] != "local")
        return applies, "selected for an external learning loop" if applies else "personal/local profile has no external learning gate"
    if expert == "payments":
        applies = profile["commerce"] == "paid"
        return applies, "selected for paid entitlement or billing state" if applies else "product does not take payment"
    return True, "selected by the maturity matrix"


def selected_gates(profile: dict[str, Any], rung: str) -> dict[str, dict[str, str]]:
    validate_profile(profile)
    if rung not in RUNGS:
        raise StateError(f"rung must be one of {RUNGS}")
    selected: dict[str, dict[str, str]] = {}
    for expert in ACTIVE_EXPERTS:
        mode = MATRIX[expert].get(rung)
        if mode is None:
            continue
        applies, rationale = _applicability(expert, profile, rung)
        if expert == "finops-pricing" and rung == "L3" and profile["commerce"] != "paid":
            mode, rationale = "A", "cost and opportunity-cost advice; product is not paid"
        selected[expert] = {"mode": mode, "applicability": "APPLICABLE" if applies else "N/A", "rationale": rationale}
    return selected


def _validate_rules(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    value = _load_json(_config_path(root, "harden_mandatory_rules.json"), "mandatory rules")
    _require_keys(value, {"$schema", "schema_version", "verifiers", "rules"}, "mandatory rules")
    if value["$schema"] != MANDATORY_SCHEMA or value["schema_version"] != 1:
        raise StateError("mandatory rules schema is invalid")
    if value["verifiers"] != {"tracked-diff-secret-scan": ALLOWED_VERIFIER}:
        raise StateError("mandatory verifier allowlist is not the closed v1 contract")
    required = {"id", "owner_rubric", "rungs", "profile_selector", "severity", "verifier_id", "expected_exit_semantics", "evidence_type"}
    by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(value["rules"], list):
        raise StateError("mandatory rules.rules must be a list")
    for index, rule in enumerate(value["rules"]):
        if not isinstance(rule, dict):
            raise StateError("mandatory rule must be an object")
        _require_keys(rule, required, f"mandatory rules.rules[{index}]")
        if rule["id"] in by_id or rule["owner_rubric"] not in ACTIVE_EXPERTS:
            raise StateError("mandatory rule ID or owner is invalid")
        if not isinstance(rule["rungs"], list) or not set(rule["rungs"]) <= set(RUNGS):
            raise StateError("mandatory rule rungs are invalid")
        if rule["profile_selector"] != {} or rule["verifier_id"] != "tracked-diff-secret-scan" or rule["expected_exit_semantics"] != {"0": "PASS", "4": "BLOCK", "2": "ERROR"}:
            raise StateError("mandatory v1 rule is outside the closed contract")
        by_id[rule["id"]] = rule
    if set(by_id) != {"product.exposed-credential-diff"}:
        raise StateError("mandatory rule IDs are not the closed v1 set")
    return value, by_id


def _untracked_paths_from_status(raw: bytes) -> list[str]:
    paths: list[str] = []
    skip_source = False
    for record in raw.split(b"\0"):
        if not record:
            continue
        if skip_source:
            skip_source = False
            continue
        if len(record) < 4 or record[2:3] != b" ":
            continue
        status = record[:2]
        if status == b"??":
            paths.append(record[3:].decode(errors="surrogateescape"))
        if b"R" in status or b"C" in status:
            skip_source = True
    return paths


def _added_lines_from_patch(raw: bytes) -> list[tuple[str, int, bytes]]:
    """Return only added tracked lines from the closed unified-diff command."""
    added: list[tuple[str, int, bytes]] = []
    current_path: str | None = None
    new_line = 0
    for line in raw.splitlines():
        if line.startswith(b"+++ "):
            value = line[4:]
            if value == b"/dev/null":
                current_path = None
                continue
            if value.startswith(b"b/"):
                value = value[2:]
            current_path = value.decode(errors="surrogateescape")
            continue
        if line.startswith(b"@@ "):
            match = re.search(rb"\+(\d+)(?:,\d+)? @@", line)
            current_path = current_path if match else None
            new_line = int(match.group(1)) if match else 0
            continue
        if current_path is None or line.startswith(b"\\ No newline"):
            continue
        if line.startswith(b"+") and not line.startswith(b"+++"):
            added.append((current_path, new_line, line[1:]))
            new_line += 1
        elif line.startswith(b" "):
            new_line += 1
    return added


def run_allowlisted_verifier(verifier_id: str, repo: Path, verifier_spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the one closed v1 verifier; no caller-controlled command is accepted."""
    if verifier_id != "tracked-diff-secret-scan" or verifier_spec != ALLOWED_VERIFIER:
        raise StateError("unregistered deterministic verifier rejected")
    outputs: dict[str, bytes] = {}
    for command in verifier_spec["subprocesses"]:
        try:
            completed = subprocess.run(
                [command["executable"], *command["arguments"]], cwd=repo,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=command["timeout_seconds"], check=False, shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PackageHold("allowlisted credential scanner was unavailable") from exc
        if completed.returncode != 0:
            raise PackageHold("allowlisted credential scanner did not return usable evidence")
        outputs[command["output_schema"]] = completed.stdout
    findings: list[dict[str, Any]] = []
    found_paths: set[str] = set()
    for relative, line, added_line in _added_lines_from_patch(
        outputs["git-unified-diff-v1"]
    ):
        if relative in found_paths or _excluded(relative) or relative.startswith(".git/"):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(added_line):
                findings.append({"rule_id": "product.exposed-credential-diff", "path": relative, "line": line, "evidence": f"{relative}:{line}: credential-shaped value detected; value suppressed"})
                found_paths.add(relative)
                break
    for relative in _untracked_paths_from_status(outputs["git-status-porcelain-v1-z"]):
        if _excluded(relative) or relative.startswith(".git/"):
            continue
        path = repo / relative
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 5_000_000:
            continue
        raw = path.read_bytes()
        if b"\0" in raw[:4096]:
            continue
        for pattern in SECRET_PATTERNS:
            match = pattern.search(raw)
            if match:
                line = raw.count(b"\n", 0, match.start()) + 1
                findings.append({"rule_id": "product.exposed-credential-diff", "path": relative, "line": line, "evidence": f"{relative}:{line}: credential-shaped value detected; value suppressed"})
                break
    return findings


def _validate_dataset(root: Path) -> None:
    path = _dataset_path(root)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PackageHold(f"capability dataset is missing: {path}") from exc
    rubrics: set[str] = set()
    case_ids: set[str] = set()
    verdicts: set[str] = set()
    shapes: set[str] = set()
    rubric_counts: dict[str, int] = {expert: 0 for expert in ACTIVE_EXPERTS}
    required = {"schema_version", "case_id", "rubric_id", "rung", "mode", "profile", "scenario", "evidence", "expected"}
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise StateError(f"capability dataset line {number} is malformed") from exc
        if (
            not isinstance(case, dict)
            or not required <= set(case) <= required | {"shape", "context_sections"}
            or case.get("schema_version") != 1
        ):
            raise StateError(f"capability dataset line {number} has an invalid contract")
        validate_profile(case["profile"])
        if case["rubric_id"] not in ACTIVE_EXPERTS or case["rung"] not in RUNGS or case["mode"] not in MODES:
            raise StateError(f"capability dataset line {number} has invalid routing fields")
        if not isinstance(case["case_id"], str) or not case["case_id"] or case["case_id"] in case_ids:
            raise StateError("capability dataset case IDs must be unique and non-empty")
        verdict = case.get("expected", {}).get("verdict")
        if verdict not in VERDICTS:
            raise StateError("capability dataset expected verdict is invalid")
        shape = case.get("shape")
        if shape is not None and shape not in CAPABILITY_CASE_SHAPES:
            raise StateError(f"capability dataset line {number} has an invalid case shape")
        sections = case.get("context_sections")
        if sections is not None:
            if not isinstance(sections, list) or not sections:
                raise StateError(f"capability dataset line {number} context_sections are invalid")
            section_ids: set[str] = set()
            for section in sections:
                if not isinstance(section, dict) or set(section) != {"section_id", "content"}:
                    raise StateError(f"capability dataset line {number} has an invalid context section")
                section_id, content = section["section_id"], section["content"]
                if (
                    not isinstance(section_id, str) or not section_id.strip()
                    or section_id in section_ids
                    or not isinstance(content, str) or not content.strip()
                ):
                    raise StateError(f"capability dataset line {number} has a blank or duplicate context section")
                section_ids.add(section_id)
        if shape == "long-context":
            if not isinstance(sections, list) or len(sections) < 16:
                raise PackageHold(f"long-context case {case['case_id']} has too few structured sections")
            if len(_canonical(sections).decode("utf-8")) < 16000:
                raise PackageHold(f"long-context case {case['case_id']} is below the minimum retained context size")
        case_ids.add(case["case_id"]); rubrics.add(case["rubric_id"]); verdicts.add(verdict)
        rubric_counts[case["rubric_id"]] += 1
        if shape is not None:
            shapes.add(shape)
    if rubrics != set(ACTIVE_EXPERTS):
        raise PackageHold("capability dataset does not cover all 19 active rubrics")
    if not {"PASS", "BLOCK", "HOLD"} <= verdicts:
        raise PackageHold("capability dataset lacks positive, negative, or HOLD cases")
    if any(count < 2 for count in rubric_counts.values()):
        raise PackageHold("capability dataset requires at least two cases per active rubric")
    if shapes != CAPABILITY_CASE_SHAPES:
        raise PackageHold("capability dataset does not cover every required evidence shape")


def _capability_cases(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(_dataset_path(root).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PackageHold(f"capability dataset line {number} is malformed") from exc
        if not isinstance(value, dict):
            raise PackageHold(f"capability dataset line {number} is not an object")
        rows.append(value)
    return rows


def _capability_rubric_bindings(
    root: Path, cases: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, str]], str]:
    bindings: dict[str, dict[str, str]] = {}
    for rubric_id in sorted({case["rubric_id"] for case in cases}):
        try:
            rubric_text = _rubric_path(root, rubric_id).read_text(encoding="utf-8")
        except OSError as exc:
            raise PackageHold(f"capability rubric is missing: {rubric_id}") from exc
        bindings[rubric_id] = {
            "rubric_id": rubric_id,
            "rubric_hash": _digest(rubric_text.encode()),
            "rubric_text": rubric_text,
        }
    manifest = {rubric_id: item["rubric_hash"] for rubric_id, item in bindings.items()}
    return bindings, _digest(_canonical(manifest))


def _expected_capability_request(
    case: dict[str, Any], rubric: dict[str, str], package_hash: str,
) -> dict[str, Any]:
    blind_case = {key: value for key, value in case.items() if key != "expected"}
    input_hash = _digest(_canonical(blind_case))
    return {
        "$schema": REQUEST_SCHEMA,
        "purpose": GATE_PURPOSE,
        "binding": {
            "case_id": case["case_id"],
            "dataset_case_hash": _digest(_canonical(case)),
            "input_hash": input_hash,
            "rubric_id": rubric["rubric_id"],
            "rubric_hash": rubric["rubric_hash"],
            "rubric_package_hash": package_hash,
        },
        "rubric": rubric,
        "case": blind_case,
        "response_contract": {
            "$schema": OUTPUT_SCHEMA,
            "case_id": case["case_id"],
            "rubric_id": case["rubric_id"],
            "rubric_hash": rubric["rubric_hash"],
            "rubric_package_hash": package_hash,
            "input_hash": input_hash,
            "verdict": sorted(VERDICTS),
            "finding_ids": "array of non-empty strings",
            "rationale": "concise evidence-grounded string",
        },
    }


def _jsonl_objects(raw: bytes, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(raw.decode(errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PackageHold(f"{label} line {number} is malformed") from exc
        if not isinstance(value, dict):
            raise PackageHold(f"{label} line {number} is not an object")
        rows.append(value)
    return rows


def _validate_capability_case_bindings(
    root: Path, raw_outputs: bytes, score: dict[str, Any], receipt_id: str,
) -> str:
    cases = _capability_cases(root)
    rubrics, package_hash = _capability_rubric_bindings(root, cases)
    expected_by_id = {case["case_id"]: case for case in cases}
    results_by_id: dict[str, dict[str, Any]] = {}
    for result in _jsonl_objects(raw_outputs, f"capability raw evidence {receipt_id}"):
        case_id = result.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in results_by_id:
            raise PackageHold(f"capability raw evidence has a blank or duplicate case binding: {receipt_id}")
        results_by_id[case_id] = result
    if set(results_by_id) != set(expected_by_id):
        raise PackageHold(f"capability raw evidence has missing or extra case bindings: {receipt_id}")
    result_keys = {
        "$schema", "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
        "runtime", "model_id", "effort", "dataset_case_hash", "input_hash",
        "request", "request_hash", "raw_response", "parsed_response", "parser_error",
        "transport",
    }
    observed: dict[str, tuple[bool, str | None, bool]] = {}
    for case_id, case in expected_by_id.items():
        result = results_by_id[case_id]
        rubric = rubrics[case["rubric_id"]]
        request = _expected_capability_request(case, rubric, package_hash)
        binding = request["binding"]
        if (
            set(result) != result_keys
            or result.get("$schema") != CASE_RESULT_SCHEMA
            or result.get("rubric_id") != case["rubric_id"]
            or result.get("rubric_hash") != rubric["rubric_hash"]
            or result.get("rubric_package_hash") != package_hash
            or result.get("dataset_case_hash") != binding["dataset_case_hash"]
            or result.get("input_hash") != binding["input_hash"]
            or result.get("request") != request
            or result.get("request_hash") != _digest(_canonical(request))
        ):
            raise PackageHold(f"capability raw case binding mismatch: {receipt_id}/{case_id}")
        parsed = result.get("parsed_response")
        if parsed is not None:
            try:
                reparsed = json.loads(result.get("raw_response"))
            except (json.JSONDecodeError, TypeError) as exc:
                raise PackageHold(f"capability raw response binding mismatch: {receipt_id}/{case_id}") from exc
            if reparsed != parsed or result.get("parser_error") is not None:
                raise PackageHold(f"capability parsed response drift: {receipt_id}/{case_id}")
            output_keys = {
                "$schema", "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
                "input_hash", "verdict", "finding_ids", "rationale",
            }
            if (
                not isinstance(parsed, dict)
                or set(parsed) != output_keys
                or parsed.get("$schema") != OUTPUT_SCHEMA
                or parsed.get("verdict") not in VERDICTS
                or not isinstance(parsed.get("finding_ids"), list)
                or not all(isinstance(item, str) and item.strip() for item in parsed["finding_ids"])
                or not isinstance(parsed.get("rationale"), str)
                or not parsed["rationale"].strip()
            ):
                raise PackageHold(f"capability parsed response contract is invalid: {receipt_id}/{case_id}")
            for key in ("case_id", "rubric_id", "rubric_hash", "rubric_package_hash", "input_hash"):
                expected = binding[key]
                if parsed.get(key) != expected:
                    raise PackageHold(f"capability candidate response binding mismatch: {receipt_id}/{case_id}/{key}")
            actual, valid = parsed["verdict"], True
        else:
            if not isinstance(result.get("parser_error"), str) or not result["parser_error"].strip():
                raise PackageHold(f"capability parser failure evidence is invalid: {receipt_id}/{case_id}")
            actual, valid = None, False
        observed[case_id] = (
            valid, actual, bool(valid and actual == case.get("expected", {}).get("verdict"))
        )
    score_rubrics = score.get("rubric_hashes")
    expected_hashes = {rubric_id: item["rubric_hash"] for rubric_id, item in rubrics.items()}
    if score.get("rubric_package_hash") != package_hash or score_rubrics != expected_hashes:
        raise PackageHold(f"capability score rubric-package binding mismatch: {receipt_id}")
    score_cases = score.get("per_case")
    if not isinstance(score_cases, list):
        raise PackageHold(f"capability score per-case evidence is invalid: {receipt_id}")
    score_by_id: dict[str, dict[str, Any]] = {}
    for item in score_cases:
        case_id = item.get("case_id") if isinstance(item, dict) else None
        if not isinstance(case_id, str) or not case_id or case_id in score_by_id:
            raise PackageHold(f"capability score has a blank or duplicate case binding: {receipt_id}")
        score_by_id[case_id] = item
    if set(score_by_id) != set(expected_by_id):
        raise PackageHold(f"capability score has missing or extra case bindings: {receipt_id}")
    score_case_keys = {
        "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
        "dataset_case_hash", "input_hash", "request_hash", "expected", "actual",
        "schema_valid", "correct",
    }
    for case_id, case in expected_by_id.items():
        request = _expected_capability_request(case, rubrics[case["rubric_id"]], package_hash)
        binding = request["binding"]
        item = score_by_id[case_id]
        if (
            set(item) != score_case_keys
            or item.get("rubric_id") != binding["rubric_id"]
            or item.get("rubric_hash") != binding["rubric_hash"]
            or item.get("rubric_package_hash") != package_hash
            or item.get("dataset_case_hash") != binding["dataset_case_hash"]
            or item.get("input_hash") != binding["input_hash"]
            or item.get("request_hash") != _digest(_canonical(request))
            or item.get("expected") != case.get("expected", {}).get("verdict")
            or item.get("actual") != observed[case_id][1]
            or item.get("schema_valid") is not observed[case_id][0]
            or item.get("correct") is not observed[case_id][2]
        ):
            raise PackageHold(f"capability score case binding mismatch: {receipt_id}/{case_id}")
    total = len(cases)
    correct = sum(int(item[2]) for item in observed.values())
    block_ids = [case["case_id"] for case in cases if case.get("expected", {}).get("verdict") == "BLOCK"]
    uncertain_ids = [case["case_id"] for case in cases if case.get("expected", {}).get("verdict") == "HOLD"]
    covered = {
        expected_by_id[case_id]["rubric_id"]
        for case_id, item in observed.items() if item[0]
    }
    recomputed_metrics = {
        "overall_accuracy": correct / total,
        "block_recall": sum(int(observed[case_id][2]) for case_id in block_ids) / len(block_ids),
        "hold_abstain_accuracy": sum(int(observed[case_id][2]) for case_id in uncertain_ids) / len(uncertain_ids),
        "schema_validity": sum(int(item[0]) for item in observed.values()) / total,
        "rubric_coverage": len(covered) / len(rubrics),
    }
    if score.get("metrics") != recomputed_metrics:
        raise PackageHold(f"capability score metrics do not reproduce from raw evidence: {receipt_id}")
    return package_hash


def _validate_policy(root: Path) -> dict[str, Any]:
    policy = _load_json(_config_path(root, "harden_eval_policy.json"), "evaluation policy")
    required = {"$schema", "schema_version", "purpose", "dataset_version", "scorer_version", "qualification_ttl_days", "ratified", "ratified_at", "ratifier", "corpus_requirements", "roles"}
    _require_keys(policy, required, "evaluation policy")
    if policy["$schema"] != POLICY_SCHEMA or policy["schema_version"] != 1 or policy["purpose"] != GATE_PURPOSE:
        raise StateError("evaluation policy schema or purpose is invalid")
    if set(policy["roles"]) != {"blocking-specialist", "frontier-synthesizer"}:
        raise StateError("evaluation policy roles are invalid")
    if policy["corpus_requirements"] != {
        "minimum_cases_per_rubric": 2,
        "required_shapes": sorted(CAPABILITY_CASE_SHAPES),
        "minimum_long_context_characters": 16000,
        "minimum_long_context_sections": 16,
    }:
        raise StateError("evaluation policy corpus requirements are invalid")
    threshold_keys = {"minimum_overall_accuracy", "minimum_block_recall", "minimum_hold_abstain_accuracy", "minimum_schema_validity", "minimum_rubric_coverage"}
    for role, thresholds in policy["roles"].items():
        if not isinstance(thresholds, dict):
            raise StateError(f"evaluation policy role {role} is invalid")
        _require_keys(thresholds, threshold_keys, f"evaluation policy role {role}")
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1 for value in thresholds.values()):
            raise StateError("evaluation thresholds must be ratios")
    return policy


def validate_capability_receipt(root: Path, entry: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    _validate_dataset(root)
    receipt_id = entry["receipt_id"]
    path = _receipt_path(root, receipt_id)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PackageHold(f"capability receipt is missing: {receipt_id}") from exc
    if entry["receipt_hash"] != _digest(raw):
        raise PackageHold(f"capability receipt hash drift: {receipt_id}")
    try:
        receipt = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PackageHold(f"capability receipt is malformed: {receipt_id}") from exc
    required = {
        "$schema", "receipt_id", "purpose", "status", "ratified", "ratifier",
        "capability_role", "provider", "provider_class", "runtime", "model_id", "effort",
        "quantization", "tool_capabilities", "context_limit", "hardware", "dataset_hash",
        "rubric_hashes", "rubric_package_hash", "raw_output_hash", "score_result_hash", "score_breakdown",
        "policy_hash", "scorer_version", "evaluated_at", "expires_at", "qualified_rubrics", "limitations",
    }
    if not isinstance(receipt, dict) or set(receipt) != required:
        raise PackageHold(f"capability receipt contract is invalid: {receipt_id}")
    if receipt["$schema"] != RECEIPT_SCHEMA or receipt["receipt_id"] != receipt_id or receipt["purpose"] != GATE_PURPOSE:
        raise PackageHold(f"capability receipt identity is invalid: {receipt_id}")
    if receipt["status"] != "QUALIFIED" or receipt["ratified"] is not True or not isinstance(receipt["ratifier"], str) or not receipt["ratifier"].strip():
        raise PackageHold(f"capability receipt is not ratified: {receipt_id}")
    if receipt["capability_role"] not in {"blocking-specialist", "frontier-synthesizer"}:
        raise PackageHold(f"capability receipt role is invalid: {receipt_id}")
    for key in ("provider", "provider_class", "runtime", "model_id", "effort", "scorer_version"):
        if not isinstance(receipt[key], str) or not receipt[key].strip():
            raise PackageHold(f"capability receipt {key} is invalid: {receipt_id}")
    if receipt["provider_class"] not in {"hosted", "open-weight"}:
        raise PackageHold(f"capability provider class is invalid: {receipt_id}")
    if receipt["provider_class"] == "open-weight" and (not isinstance(receipt["hardware"], str) or not receipt["hardware"].strip() or not isinstance(receipt["quantization"], str) or not receipt["quantization"].strip()):
        raise PackageHold(f"open-weight capability lacks hardware/quantization binding: {receipt_id}")
    if not isinstance(receipt["context_limit"], int) or isinstance(receipt["context_limit"], bool) or receipt["context_limit"] <= 0:
        raise PackageHold(f"capability context limit is invalid: {receipt_id}")
    if not isinstance(receipt["tool_capabilities"], list) or not all(isinstance(item, str) for item in receipt["tool_capabilities"]):
        raise PackageHold(f"capability tools are invalid: {receipt_id}")
    if not isinstance(receipt["limitations"], list) or not all(isinstance(item, str) for item in receipt["limitations"]):
        raise PackageHold(f"capability limitations are invalid: {receipt_id}")
    rubrics = receipt["qualified_rubrics"]
    if not isinstance(rubrics, list) or not rubrics or len(rubrics) != len(set(rubrics)) or not set(rubrics) <= set(ACTIVE_EXPERTS):
        raise PackageHold(f"capability qualified rubrics are invalid: {receipt_id}")
    if not isinstance(receipt["rubric_hashes"], dict) or set(receipt["rubric_hashes"]) != set(rubrics):
        raise PackageHold(f"capability rubric hashes are incomplete: {receipt_id}")
    for rubric in rubrics:
        if receipt["rubric_hashes"][rubric] != _digest(_rubric_path(root, rubric).read_bytes()):
            raise PackageHold(f"capability rubric hash drift: {receipt_id}/{rubric}")
    policy_path = _config_path(root, "harden_eval_policy.json")
    policy = _validate_policy(root)
    if policy["ratified"] is not True or not policy["ratifier"] or not policy["ratified_at"]:
        raise PackageHold("capability policy is not owner-ratified")
    if receipt["policy_hash"] != _digest(policy_path.read_bytes()) or receipt["scorer_version"] != policy["scorer_version"]:
        raise PackageHold(f"capability policy/scorer binding drift: {receipt_id}")
    dataset_path = _dataset_path(root)
    raw_path = _evidence_path(root, receipt_id, "per_case_outputs.jsonl")
    score_path = _evidence_path(root, receipt_id, "score.json")
    if receipt["dataset_hash"] != _digest(dataset_path.read_bytes()):
        raise PackageHold(f"capability dataset hash drift: {receipt_id}")
    try:
        raw_outputs, raw_score = raw_path.read_bytes(), score_path.read_bytes()
    except OSError as exc:
        raise PackageHold(f"capability evidence is missing: {receipt_id}") from exc
    if receipt["raw_output_hash"] != _digest(raw_outputs) or receipt["score_result_hash"] != _digest(raw_score):
        raise PackageHold(f"capability raw/scorer evidence hash drift: {receipt_id}")
    try:
        score = json.loads(raw_score)
    except json.JSONDecodeError as exc:
        raise PackageHold(f"capability score is malformed: {receipt_id}") from exc
    if not isinstance(score, dict) or score.get("$schema") != SCORE_SCHEMA or score.get("result") != "PASS":
        raise PackageHold(f"capability score did not pass: {receipt_id}")
    package_hash = _validate_capability_case_bindings(root, raw_outputs, score, receipt_id)
    if receipt["rubric_package_hash"] != package_hash:
        raise PackageHold(f"capability receipt rubric-package binding mismatch: {receipt_id}")
    score_rubric_hashes = score.get("rubric_hashes")
    if not isinstance(score_rubric_hashes, dict) or any(
        score_rubric_hashes.get(rubric) != receipt["rubric_hashes"][rubric]
        for rubric in rubrics
    ):
        raise PackageHold(f"capability receipt claims a rubric absent from scored raw evidence: {receipt_id}")
    bindings = {"purpose": "purpose", "capability_role": "role", "runtime": "runtime", "model_id": "model_id", "effort": "effort", "dataset_hash": "dataset_hash", "rubric_package_hash": "rubric_package_hash", "raw_output_hash": "raw_output_hash", "policy_hash": "policy_hash", "scorer_version": "scorer_version", "score_breakdown": "metrics"}
    for receipt_key, score_key in bindings.items():
        if receipt[receipt_key] != score.get(score_key):
            raise PackageHold(f"capability score binding mismatch: {receipt_id}/{receipt_key}")
    metrics = score.get("metrics")
    thresholds = policy["roles"][receipt["capability_role"]]
    threshold_map = {
        "overall_accuracy": "minimum_overall_accuracy",
        "block_recall": "minimum_block_recall",
        "hold_abstain_accuracy": "minimum_hold_abstain_accuracy",
        "schema_validity": "minimum_schema_validity",
        "rubric_coverage": "minimum_rubric_coverage",
    }
    if not isinstance(metrics, dict) or set(metrics) != set(threshold_map):
        raise PackageHold(f"capability score metrics are invalid: {receipt_id}")
    if any(
        not isinstance(metrics[name], (int, float))
        or isinstance(metrics[name], bool)
        or not math.isfinite(float(metrics[name]))
        or metrics[name] < thresholds[threshold]
        for name, threshold in threshold_map.items()
    ):
        raise PackageHold(f"capability score is below policy threshold: {receipt_id}")
    evaluated = _utc_timestamp(receipt["evaluated_at"], f"receipt {receipt_id}.evaluated_at")
    expires = _utc_timestamp(receipt["expires_at"], f"receipt {receipt_id}.expires_at")
    if evaluated > now or expires <= now or expires <= evaluated:
        raise PackageHold(f"capability receipt is stale: {receipt_id}")
    return receipt


def _validate_package(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    missing = [relative for relative in STATIC_PACKAGE_FILES if not (root / relative).is_file()]
    rubric_dir = root / "rubrics"
    actual = {path.stem for path in rubric_dir.glob("*.md")} if rubric_dir.is_dir() else set()
    if missing or actual != set(ACTIVE_EXPERTS):
        details = [*missing, *(f"rubrics/{name}.md" for name in sorted(set(ACTIVE_EXPERTS) - actual)), *(f"unexpected-rubric:{name}" for name in sorted(actual - set(ACTIVE_EXPERTS)))]
        raise PackageHold("package closure incomplete: " + ", ".join(details))
    schema = _load_json(root / "config" / "harden_state_v2.schema.json", "state schema")
    if schema.get("$id") != SCHEMA:
        raise StateError("state schema ID does not match runtime contract")
    rules, by_id = _validate_rules(root)
    policy = _validate_policy(root)
    entries = _registry_entries(root)
    _validate_dataset(root)
    return rules, by_id, policy, entries


def validate_state(state: Any, repo: Path, authority_root: Path) -> None:
    if not isinstance(state, dict):
        raise StateError("state must be an object")
    _require_keys(state, {"$schema", "target_rung", "profile", "fingerprints", "capabilities", "gates"}, "state")
    if state["$schema"] != SCHEMA or state["target_rung"] not in RUNGS:
        raise StateError("state schema or target_rung is invalid")
    profile = validate_profile(state["profile"])
    if not isinstance(state["fingerprints"], dict):
        raise StateError("fingerprints must be an object")
    _require_keys(state["fingerprints"], FINGERPRINT_KEYS, "fingerprints")
    expected = current_fingerprints(repo, authority_root, profile)
    if state["fingerprints"] != expected:
        stale = sorted(key for key in FINGERPRINT_KEYS if state["fingerprints"].get(key) != expected[key])
        raise StateError(f"stale hardening evidence; fingerprint mismatch: {', '.join(stale)}")
    rules_config, mandatory = _validate_rules(authority_root)
    live = {entry["receipt_id"]: validate_capability_receipt(authority_root, entry) for entry in _registry_entries(authority_root)}
    if not isinstance(state["capabilities"], list):
        raise StateError("capabilities must be a list")
    capabilities: dict[str, dict[str, Any]] = {}
    for index, capability in enumerate(state["capabilities"]):
        if not isinstance(capability, dict):
            raise StateError(f"capabilities[{index}] must be an object")
        _require_keys(capability, CAPABILITY_KEYS, f"capabilities[{index}]")
        if capability["receipt_id"] in capabilities or capability["status"] not in CAPABILITY_STATUSES or capability["role"] not in CAPABILITY_ROLES:
            raise StateError("capability identity, status, or role is invalid")
        receipt = live.get(capability["receipt_id"])
        if capability["status"] == "AVAILABLE":
            if receipt is None:
                raise StateError("available capability is not in the live registry")
            expected_capability = {
                "receipt_id": receipt["receipt_id"], "status": "AVAILABLE", "role": receipt["capability_role"],
                "runtime": receipt["runtime"], "model_id": receipt["model_id"], "effort": receipt["effort"],
                "qualified_rubrics": receipt["qualified_rubrics"], "limitations": receipt["limitations"],
                "receipt_hash": _digest(_receipt_path(authority_root, capability["receipt_id"]).read_bytes()),
            }
            if capability != expected_capability:
                raise StateError("state capability does not exactly match its ratified receipt")
        capabilities[capability["receipt_id"]] = capability
    target_index = RUNGS.index(state["target_rung"])
    required_rungs = set(RUNGS[: target_index + 1])
    if not isinstance(state["gates"], dict) or set(state["gates"]) != required_rungs:
        raise StateError("gates must contain exactly the rungs through target_rung")
    now = datetime.now(timezone.utc)
    deterministic: list[dict[str, Any]] | None = None
    for rung, gates in state["gates"].items():
        selection = selected_gates(profile, rung)
        if not isinstance(gates, dict) or set(gates) != set(selection):
            raise StateError(f"gates.{rung} must exactly cover selected gates")
        for expert, gate in gates.items():
            if not isinstance(gate, dict):
                raise StateError(f"gates.{rung}.{expert} must be an object")
            _require_keys(gate, GATE_KEYS, f"gates.{rung}.{expert}")
            selected = selection[expert]
            if gate["mode"] != selected["mode"] or gate["applicability"] != selected["applicability"] or gate["rationale"] != selected["rationale"]:
                raise StateError(f"gates.{rung}.{expert} does not match current selection")
            if gate["verdict"] not in VERDICTS or gate["verdict_basis"] not in VERDICT_BASES:
                raise StateError(f"gates.{rung}.{expert} has an invalid verdict or basis")
            if gate["applicability"] == "N/A" and (gate["verdict"], gate["verdict_basis"]) != ("N/A", "none"):
                raise StateError(f"gates.{rung}.{expert} must use N/A with basis none")
            if gate["applicability"] == "APPLICABLE" and gate["verdict"] == "N/A":
                raise StateError(f"gates.{rung}.{expert} cannot use N/A")
            if gate["mode"] in {"B", "R"} and gate["verdict"] == "ADVISORY":
                raise StateError(f"gates.{rung}.{expert} cannot use ADVISORY for a blocking gate")
            findings = gate["open_findings"]
            if not isinstance(findings, list) or not all(isinstance(item, str) and item.strip() for item in findings) or len(findings) != len(set(findings)):
                raise StateError(f"gates.{rung}.{expert}.open_findings must contain unique IDs")
            expected_rules = set(findings) if gate["verdict_basis"] == "deterministic_mandatory" else set()
            if not isinstance(gate["finding_rules"], dict) or set(gate["finding_rules"]) != expected_rules:
                raise StateError(f"gates.{rung}.{expert}.finding_rules does not match verdict basis")
            if gate["verdict"] in {"PASS", "ADVISORY"} and findings:
                raise StateError(f"gates.{rung}.{expert} cannot pass with open findings")
            evidence = gate["evidence"]
            if not isinstance(evidence, list) or not all(isinstance(item, str) and item for item in evidence) or len(evidence) != len(set(evidence)):
                raise StateError(f"gates.{rung}.{expert}.evidence must contain unique paths")
            if not isinstance(gate["evidence_hashes"], dict) or set(gate["evidence_hashes"]) != set(evidence):
                raise StateError(f"gates.{rung}.{expert}.evidence_hashes must exactly cover evidence")
            if gate["fingerprints"] != expected:
                raise StateError(f"gates.{rung}.{expert} receipt fingerprints are stale")
            if _utc_timestamp(gate["run_at"], f"gates.{rung}.{expert}.run_at") > now:
                raise StateError(f"gates.{rung}.{expert}.run_at cannot be in the future")
            if gate["verdict_basis"] == "none":
                if gate["verdict"] not in {"HOLD", "N/A"} or findings or gate["capability_receipt"]:
                    raise StateError(f"gates.{rung}.{expert} basis none is only for HOLD/N/A")
            elif gate["verdict_basis"] == "model_receipt":
                if gate["verdict"] not in {"PASS", "BLOCK", "ADVISORY"}:
                    raise StateError(f"gates.{rung}.{expert} model receipt cannot support {gate['verdict']}")
                receipt = live.get(gate["capability_receipt"])
                if receipt is None or expert not in receipt["qualified_rubrics"]:
                    raise StateError(f"gates.{rung}.{expert} lacks a qualified model receipt")
                if gate["verdict"] == "BLOCK" and not findings:
                    raise StateError(f"gates.{rung}.{expert} block requires an open finding")
            else:
                if gate["verdict"] != "BLOCK" or not findings or gate["capability_receipt"]:
                    raise StateError(f"gates.{rung}.{expert} deterministic basis supports only receipt-free BLOCK")
                for finding_id, rule_id in gate["finding_rules"].items():
                    rule = mandatory.get(rule_id)
                    if rule is None or rule["owner_rubric"] != expert or rung not in rule["rungs"]:
                        raise StateError(f"gates.{rung}.{expert} finding {finding_id} cites an unregistered or inapplicable rule")
                if deterministic is None:
                    deterministic = run_allowlisted_verifier("tracked-diff-secret-scan", repo, rules_config["verifiers"]["tracked-diff-secret-scan"])
                found_paths = {item["path"] for item in deterministic}
                if not found_paths or not found_paths <= set(evidence):
                    raise StateError(f"gates.{rung}.{expert} deterministic finding no longer reproduces")
            if gate["verdict"] in {"PASS", "BLOCK", "ADVISORY"} and not evidence:
                raise StateError(f"gates.{rung}.{expert} {gate['verdict'].lower()} requires evidence")
            for item in evidence:
                path = _contained_file(repo, item, f"gates.{rung}.{expert} evidence path")
                if gate["evidence_hashes"].get(item) != _digest(path.read_bytes()):
                    raise StateError(f"gates.{rung}.{expert} evidence hash mismatch: {item}")


def overall_outcome(state: dict[str, Any]) -> str:
    has_hold = False
    for gates in state["gates"].values():
        for gate in gates.values():
            if gate["verdict"] == "BLOCK":
                return "BLOCK"
            if gate["verdict"] == "HOLD":
                has_hold = True
    return "HOLD" if has_hold else "PASS"


def _report(*, outcome: str, runtime: str, rung: str, profile_hash: str, package_hash: str, selected: list[str], checks: list[dict[str, Any]], missing: list[dict[str, str]], operator_error: bool = False) -> dict[str, Any]:
    return {"schema_version": 1, "outcome": outcome, "runtime": runtime, "rung": rung, "profile_hash": profile_hash, "package_hash": package_hash, "selected_gates": selected, "checks": checks, "missing_capabilities": missing, "operator_error": operator_error}


def preflight(repo: Path, package_root: Path, runtime: str, profile: dict[str, Any], rung: str) -> tuple[dict[str, Any], int]:
    profile = validate_profile(profile)
    if runtime not in RUNTIMES or rung not in RUNGS:
        raise StateError("preflight runtime or rung is invalid")
    package_hash = package_fingerprint(package_root) if package_root.is_dir() else _digest(b"")
    selection = selected_gates(profile, rung)
    applicable = [expert for expert, item in selection.items() if item["applicability"] == "APPLICABLE"]
    try:
        rules, _, policy, entries = _validate_package(package_root)
    except PackageHold as exc:
        return _report(outcome="HOLD", runtime=runtime, rung=rung, profile_hash=profile_fingerprint(profile), package_hash=package_hash, selected=applicable, checks=[{"id": "package-closure", "status": "HOLD", "evidence": [str(exc)]}], missing=[]), 3
    checks: list[dict[str, Any]] = [{"id": "package-closure", "status": "PASS", "evidence": ["all exact runtime dependencies present"]}]
    deterministic = run_allowlisted_verifier("tracked-diff-secret-scan", repo, rules["verifiers"]["tracked-diff-secret-scan"])
    checks.append({"id": "product.exposed-credential-diff", "status": "BLOCK" if deterministic else "PASS", "evidence": [item["evidence"] for item in deterministic] or ["allowlisted tracked-diff scan found no credential-shaped value"]})
    receipts: list[dict[str, Any]] = []
    holds: list[str] = []
    if policy["ratified"] is not True:
        holds.append("evaluation policy is not owner-ratified")
    for entry in entries:
        try:
            receipts.append(validate_capability_receipt(package_root, entry))
        except (PackageHold, StateError) as exc:
            holds.append(str(exc))
    missing: list[dict[str, str]] = []
    for expert in applicable:
        if not any(receipt["runtime"] == runtime and expert in receipt["qualified_rubrics"] for receipt in receipts):
            reason = "no current ratified receipt for runtime and rubric"
            if holds:
                reason += "; " + holds[0]
            missing.append({"gate": expert, "purpose": GATE_PURPOSE, "reason": reason})
    checks.append({"id": "capability-qualification", "status": "HOLD" if missing else "PASS", "evidence": holds or (["all applicable gates have current ratified receipts"] if not missing else ["registry has no matching live qualification"])})
    if deterministic:
        outcome, code = "BLOCK", 4
    elif missing:
        outcome, code = "HOLD", 3
    else:
        outcome, code = "PASS", 0
    return _report(outcome=outcome, runtime=runtime, rung=rung, profile_hash=profile_fingerprint(profile), package_hash=package_hash, selected=applicable, checks=checks, missing=missing), code


def _load_json_argument(value: str) -> Any:
    candidate = Path(value)
    return json.loads(candidate.read_text(encoding="utf-8")) if candidate.is_file() else json.loads(value)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--repo", type=Path, required=True)
    authority = validate.add_mutually_exclusive_group(required=True)
    authority.add_argument("--package-root", type=Path)
    authority.add_argument("--instructions-root", type=Path)
    validate.add_argument("--state", type=Path)
    matrix = sub.add_parser("matrix")
    matrix.add_argument("--profile-json", required=True); matrix.add_argument("--rung", choices=RUNGS, required=True)
    fingerprints = sub.add_parser("fingerprints")
    fingerprints.add_argument("--repo", type=Path, required=True); fingerprints.add_argument("--package-root", type=Path, required=True); fingerprints.add_argument("--profile-json", required=True)
    before = sub.add_parser("preflight")
    before.add_argument("--repo", type=Path, required=True); before.add_argument("--package-root", type=Path, required=True); before.add_argument("--runtime", choices=RUNTIMES, required=True); before.add_argument("--profile-json", required=True); before.add_argument("--rung", choices=RUNGS, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "matrix":
            print(json.dumps(selected_gates(_load_json_argument(args.profile_json), args.rung), indent=2, sort_keys=True)); return 0
        if args.command == "fingerprints":
            profile = validate_profile(_load_json_argument(args.profile_json)); print(json.dumps(current_fingerprints(args.repo, args.package_root, profile), indent=2, sort_keys=True)); return 0
        if args.command == "preflight":
            report, code = preflight(args.repo, args.package_root, args.runtime, _load_json_argument(args.profile_json), args.rung); print(json.dumps(report, sort_keys=True)); return code
        root = args.package_root or args.instructions_root
        state_path = args.state or args.repo / ".harden" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8")); validate_state(state, args.repo, root)
        print(f"VALID {state_path} outcome={overall_outcome(state)}"); return 0
    except PackageHold as error:
        if args.command == "preflight":
            print(json.dumps(_report(outcome="HOLD", runtime=getattr(args, "runtime", "unknown"), rung=getattr(args, "rung", "unknown"), profile_hash="", package_hash="", selected=[], checks=[{"id": "harness-evidence", "status": "HOLD", "evidence": [str(error)]}], missing=[]), sort_keys=True)); return 3
        print(f"INVALID: {error}", file=sys.stderr); return 2
    except (OSError, json.JSONDecodeError, StateError) as error:
        if args.command == "preflight":
            print(json.dumps(_report(outcome="HOLD", runtime=getattr(args, "runtime", "unknown"), rung=getattr(args, "rung", "unknown"), profile_hash="", package_hash="", selected=[], checks=[{"id": "operator-input", "status": "HOLD", "evidence": [str(error)]}], missing=[], operator_error=True), sort_keys=True)); return 2
        print(f"INVALID: {error}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
