#!/usr/bin/env python3
"""Run the typed hardening capability corpus through an explicit local adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

DATASET_SCHEMA_VERSION = 1
REQUEST_SCHEMA = "internal://harden-capability-request/v2"
OUTPUT_SCHEMA = "internal://harden-capability-output/v2"
CASE_RESULT_SCHEMA = "internal://harden-capability-case-result/v2"
ALLOWED_VERDICTS = {"PASS", "BLOCK", "HOLD", "ADVISORY", "N/A"}
REQUIRED_SHAPES = {
    "normal", "empty", "long-context", "malformed", "adversarial",
    "degraded", "conflicting-evidence",
}


class EvalInputError(ValueError):
    pass


def digest(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvalInputError(f"dataset line {line_number} is not JSON") from exc
        required = {
            "schema_version", "case_id", "rubric_id", "rung", "mode", "profile",
            "scenario", "evidence", "expected",
        }
        if not isinstance(case, dict) or not required <= set(case) <= required | {"shape", "context_sections"}:
            raise EvalInputError(f"dataset line {line_number} has an invalid contract")
        if case["schema_version"] != DATASET_SCHEMA_VERSION:
            raise EvalInputError(f"dataset line {line_number} has an unsupported schema")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise EvalInputError(f"dataset line {line_number} has a blank or duplicate case_id")
        if case["expected"].get("verdict") not in ALLOWED_VERDICTS:
            raise EvalInputError(f"dataset line {line_number} has an invalid expected verdict")
        sections = case.get("context_sections")
        if sections is not None:
            if not isinstance(sections, list) or not sections:
                raise EvalInputError(f"dataset line {line_number} context_sections must be a non-empty list")
            section_ids: set[str] = set()
            for section in sections:
                if not isinstance(section, dict) or set(section) != {"section_id", "content"}:
                    raise EvalInputError(f"dataset line {line_number} has an invalid context section")
                section_id, content = section["section_id"], section["content"]
                if (
                    not isinstance(section_id, str) or not section_id.strip()
                    or section_id in section_ids
                    or not isinstance(content, str) or not content.strip()
                ):
                    raise EvalInputError(f"dataset line {line_number} has a blank or duplicate context section")
                section_ids.add(section_id)
        seen.add(case_id)
        cases.append(case)
    if not cases:
        raise EvalInputError("dataset is empty")
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["rubric_id"]] = counts.get(case["rubric_id"], 0) + 1
    if min(counts.values()) < 2:
        raise EvalInputError("dataset requires at least two cases per rubric")
    shapes = {case.get("shape") for case in cases if case.get("shape") is not None}
    if shapes != REQUIRED_SHAPES:
        raise EvalInputError("dataset does not cover every required evidence shape")
    return cases


def load_requirements(path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvalInputError("evaluation policy is missing or malformed") from exc
    requirements = policy.get("corpus_requirements") if isinstance(policy, dict) else None
    expected_keys = {
        "minimum_cases_per_rubric", "required_shapes",
        "minimum_long_context_characters", "minimum_long_context_sections",
    }
    if not isinstance(requirements, dict) or set(requirements) != expected_keys:
        raise EvalInputError("evaluation policy corpus requirements are invalid")
    if (
        requirements["minimum_cases_per_rubric"] != 2
        or requirements["required_shapes"] != sorted(REQUIRED_SHAPES)
        or not isinstance(requirements["minimum_long_context_characters"], int)
        or requirements["minimum_long_context_characters"] <= 0
        or not isinstance(requirements["minimum_long_context_sections"], int)
        or requirements["minimum_long_context_sections"] <= 0
    ):
        raise EvalInputError("evaluation policy corpus requirements are invalid")
    return requirements


def validate_long_context(cases: list[dict[str, Any]], requirements: dict[str, Any]) -> None:
    for case in cases:
        if case.get("shape") != "long-context":
            continue
        sections = case.get("context_sections")
        if not isinstance(sections, list) or len(sections) < requirements["minimum_long_context_sections"]:
            raise EvalInputError(f"long-context case {case['case_id']} has too few structured sections")
        if len(canonical(sections).decode("utf-8")) < requirements["minimum_long_context_characters"]:
            raise EvalInputError(f"long-context case {case['case_id']} is below the minimum retained context size")


def load_rubric_bindings(
    cases: list[dict[str, Any]], rubrics_root: Path,
) -> tuple[dict[str, dict[str, str]], str]:
    bindings: dict[str, dict[str, str]] = {}
    for rubric_id in sorted({case["rubric_id"] for case in cases}):
        path = rubrics_root / f"{rubric_id}.md"
        try:
            rubric_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvalInputError(f"rubric is missing: {rubric_id}") from exc
        if not rubric_text.strip():
            raise EvalInputError(f"rubric is empty: {rubric_id}")
        bindings[rubric_id] = {
            "rubric_id": rubric_id,
            "rubric_hash": digest(rubric_text.encode()),
            "rubric_text": rubric_text,
        }
    package_manifest = {
        rubric_id: binding["rubric_hash"] for rubric_id, binding in bindings.items()
    }
    return bindings, digest(canonical(package_manifest))


def request_for(
    case: dict[str, Any], rubric: dict[str, str], package_hash: str,
) -> dict[str, Any]:
    """Build the blind request. The expected answer never reaches the candidate."""
    blind_case = {key: value for key, value in case.items() if key != "expected"}
    input_hash = digest(canonical(blind_case))
    return {
        "$schema": REQUEST_SCHEMA,
        "purpose": "hardening-gate-verdict",
        "binding": {
            "case_id": case["case_id"],
            "dataset_case_hash": digest(canonical(case)),
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
            "verdict": sorted(ALLOWED_VERDICTS),
            "finding_ids": "array of non-empty strings",
            "rationale": "concise evidence-grounded string",
        },
    }


def parse_response(
    raw: str, case: dict[str, Any], rubric: dict[str, str], package_hash: str,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc.msg}"
    expected_keys = {
        "$schema", "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
        "input_hash", "verdict", "finding_ids", "rationale",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        return None, "response keys do not match the typed contract"
    if value["$schema"] != OUTPUT_SCHEMA:
        return None, "response schema is invalid"
    if value["case_id"] != case["case_id"] or value["rubric_id"] != case["rubric_id"]:
        return None, "response case or rubric binding is invalid"
    if (
        value["rubric_hash"] != rubric["rubric_hash"]
        or value["rubric_package_hash"] != package_hash
        or value["input_hash"] != digest(canonical({key: item for key, item in case.items() if key != "expected"}))
    ):
        return None, "response input or rubric hash binding is invalid"
    if value["verdict"] not in ALLOWED_VERDICTS:
        return None, "response verdict is invalid"
    if not isinstance(value["finding_ids"], list) or not all(
        isinstance(item, str) and item.strip() for item in value["finding_ids"]
    ):
        return None, "finding_ids must contain non-empty strings"
    if not isinstance(value["rationale"], str) or not value["rationale"].strip():
        return None, "rationale must be non-empty"
    return value, None


def run(
    cases: list[dict[str, Any]], command: list[str], runtime: str, model_id: str,
    effort: str, timeout_seconds: float, rubric_bindings: dict[str, dict[str, str]],
    package_hash: str,
) -> list[dict[str, Any]]:
    if not command or not all(isinstance(item, str) and item for item in command):
        raise EvalInputError("command-json must be a non-empty JSON array of strings")
    records: list[dict[str, Any]] = []
    for case in cases:
        rubric = rubric_bindings[case["rubric_id"]]
        request = request_for(case, rubric, package_hash)
        request_raw = canonical(request)
        try:
            completed = subprocess.run(
                command,
                input=request_raw,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False,
                shell=False,
            )
            raw_response = completed.stdout.decode(errors="replace").strip()
            parsed, parser_error = parse_response(raw_response, case, rubric, package_hash)
            transport = {
                "exit_code": completed.returncode,
                "timed_out": False,
                "stderr_present": bool(completed.stderr),
            }
        except subprocess.TimeoutExpired:
            raw_response = ""
            parsed, parser_error = None, "adapter timed out"
            transport = {"exit_code": None, "timed_out": True, "stderr_present": False}
        records.append(
            {
                "$schema": CASE_RESULT_SCHEMA,
                "case_id": case["case_id"],
                "rubric_id": case["rubric_id"],
                "rubric_hash": rubric["rubric_hash"],
                "rubric_package_hash": package_hash,
                "runtime": runtime,
                "model_id": model_id,
                "effort": effort,
                "dataset_case_hash": digest(canonical(case)),
                "input_hash": request["binding"]["input_hash"],
                "request": request,
                "request_hash": digest(request_raw),
                "raw_response": raw_response,
                "parsed_response": parsed,
                "parser_error": parser_error,
                "transport": transport,
            }
        )
    return records


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--dataset", type=Path, required=True)
    result.add_argument("--rubrics-root", type=Path, required=True)
    result.add_argument("--policy", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    result.add_argument("--runtime", required=True)
    result.add_argument("--model-id", required=True)
    result.add_argument("--effort", required=True)
    result.add_argument("--command-json", required=True)
    result.add_argument("--timeout-seconds", type=float, default=120.0)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        command = json.loads(args.command_json)
        if not isinstance(command, list):
            raise EvalInputError("command-json must decode to an array")
        if args.timeout_seconds <= 0 or args.timeout_seconds > 600:
            raise EvalInputError("timeout-seconds must be in (0, 600]")
        cases = load_cases(args.dataset)
        validate_long_context(cases, load_requirements(args.policy))
        rubric_bindings, package_hash = load_rubric_bindings(cases, args.rubrics_root)
        records = run(
            cases, command, args.runtime, args.model_id, args.effort,
            args.timeout_seconds, rubric_bindings, package_hash,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, EvalInputError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"cases": len(records), "output": str(args.output), "sha256": digest(args.output.read_bytes())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
