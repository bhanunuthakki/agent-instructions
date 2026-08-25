#!/usr/bin/env python3
"""Deterministically score a hardening capability run without qualifying it."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

SCORER_VERSION = "1.1.0"
REQUEST_SCHEMA = "internal://harden-capability-request/v2"
OUTPUT_SCHEMA = "internal://harden-capability-output/v2"
CASE_RESULT_SCHEMA = "internal://harden-capability-case-result/v2"
SCORE_SCHEMA = "internal://harden-capability-score/v2"
REQUIRED_SHAPES = {
    "normal", "empty", "long-context", "malformed", "adversarial",
    "degraded", "conflicting-evidence",
}


class ScoreError(ValueError):
    pass


def digest(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ScoreError(f"{path} line {number} is not JSON") from exc
        if not isinstance(value, dict):
            raise ScoreError(f"{path} line {number} is not an object")
        rows.append(value)
    return rows


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def rubric_bindings(
    cases: list[dict[str, Any]], rubrics_root: Path,
) -> tuple[dict[str, dict[str, str]], str]:
    bindings: dict[str, dict[str, str]] = {}
    for rubric_id in sorted({case["rubric_id"] for case in cases}):
        try:
            rubric_text = (rubrics_root / f"{rubric_id}.md").read_text(encoding="utf-8")
        except OSError as exc:
            raise ScoreError(f"rubric is missing: {rubric_id}") from exc
        if not rubric_text.strip():
            raise ScoreError(f"rubric is empty: {rubric_id}")
        bindings[rubric_id] = {
            "rubric_id": rubric_id,
            "rubric_hash": digest(rubric_text.encode()),
            "rubric_text": rubric_text,
        }
    manifest = {rubric_id: item["rubric_hash"] for rubric_id, item in bindings.items()}
    return bindings, digest(canonical(manifest))


def expected_request(
    case: dict[str, Any], rubric: dict[str, str], package_hash: str,
) -> dict[str, Any]:
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
            "verdict": sorted({"PASS", "BLOCK", "HOLD", "ABSTAIN", "ADVISORY", "N/A"}),
            "finding_ids": "array of non-empty strings",
            "rationale": "concise evidence-grounded string",
        },
    }


def _validate_candidate_output(
    raw: str, parsed: Any, parser_error: Any, request: dict[str, Any], case_id: str,
) -> tuple[bool, str | None]:
    try:
        reparsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        if parsed is not None or not isinstance(parser_error, str) or not parser_error:
            raise ScoreError(f"output {case_id} parser evidence is inconsistent with raw response")
        return False, None
    expected_keys = {
        "$schema", "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
        "input_hash", "verdict", "finding_ids", "rationale",
    }
    if not isinstance(reparsed, dict) or set(reparsed) != expected_keys:
        if parsed is not None or not isinstance(parser_error, str) or not parser_error:
            raise ScoreError(f"output {case_id} parser evidence is inconsistent with raw response")
        return False, None
    binding = request["binding"]
    expected_binding = {
        "case_id": binding["case_id"], "rubric_id": binding["rubric_id"],
        "rubric_hash": binding["rubric_hash"],
        "rubric_package_hash": binding["rubric_package_hash"],
        "input_hash": binding["input_hash"],
    }
    if any(reparsed[key] != value for key, value in expected_binding.items()):
        raise ScoreError(f"output {case_id} candidate response binding does not match its retained request")
    structurally_valid = (
        reparsed["$schema"] == OUTPUT_SCHEMA
        and reparsed["verdict"] in {"PASS", "BLOCK", "HOLD", "ABSTAIN", "ADVISORY", "N/A"}
        and isinstance(reparsed["finding_ids"], list)
        and all(isinstance(item, str) and item.strip() for item in reparsed["finding_ids"])
        and isinstance(reparsed["rationale"], str) and bool(reparsed["rationale"].strip())
    )
    if not structurally_valid:
        if parsed is not None or not isinstance(parser_error, str) or not parser_error:
            raise ScoreError(f"output {case_id} parser evidence is inconsistent with raw response")
        return False, None
    if parser_error is not None or parsed != reparsed:
        raise ScoreError(f"output {case_id} parsed response does not exactly reproduce raw response")
    return True, reparsed["verdict"]


def score(
    dataset: Path, outputs: Path, policy: Path, role: str, rubrics_root: Path,
) -> dict[str, Any]:
    cases = load_jsonl(dataset)
    results = load_jsonl(outputs)
    policy_value = json.loads(policy.read_text(encoding="utf-8"))
    if policy_value.get("$schema") != "internal://harden-eval-policy/v1":
        raise ScoreError("evaluation policy schema is invalid")
    if policy_value.get("scorer_version") != SCORER_VERSION:
        raise ScoreError("evaluation policy scorer version does not match this scorer")
    requirements = policy_value.get("corpus_requirements")
    if requirements != {
        "minimum_cases_per_rubric": 2,
        "required_shapes": sorted(REQUIRED_SHAPES),
        "minimum_long_context_characters": 16000,
        "minimum_long_context_sections": 16,
    }:
        raise ScoreError("evaluation policy corpus requirements are invalid")
    rubric_counts: dict[str, int] = {}
    for case in cases:
        required_case_keys = {
            "schema_version", "case_id", "rubric_id", "rung", "mode", "profile",
            "scenario", "evidence", "expected",
        }
        allowed_case_keys = (
            required_case_keys,
            required_case_keys | {"shape"},
            required_case_keys | {"shape", "context_sections"},
        )
        if set(case) not in allowed_case_keys or case.get("schema_version") != 1:
            raise ScoreError("dataset case contract is invalid")
        rubric = case.get("rubric_id")
        if not isinstance(rubric, str) or not rubric:
            raise ScoreError("dataset rubric IDs must be non-empty strings")
        rubric_counts[rubric] = rubric_counts.get(rubric, 0) + 1
    if not rubric_counts or min(rubric_counts.values()) < 2:
        raise ScoreError("dataset requires at least two cases per rubric")
    shapes = {case.get("shape") for case in cases if case.get("shape") is not None}
    if shapes != REQUIRED_SHAPES:
        raise ScoreError("dataset does not cover every required evidence shape")
    for case in cases:
        if case.get("shape") != "long-context":
            continue
        sections = case.get("context_sections")
        if not isinstance(sections, list) or len(sections) < requirements["minimum_long_context_sections"]:
            raise ScoreError(f"long-context case {case.get('case_id')} has too few structured sections")
        if len(canonical(sections).decode("utf-8")) < requirements["minimum_long_context_characters"]:
            raise ScoreError(f"long-context case {case.get('case_id')} is below the minimum retained context size")
    thresholds = policy_value.get("roles", {}).get(role)
    if not isinstance(thresholds, dict):
        raise ScoreError("role is not configured by the evaluation policy")
    expected_by_id = {case.get("case_id"): case for case in cases}
    if (
        len(expected_by_id) != len(cases)
        or not all(isinstance(case_id, str) and case_id for case_id in expected_by_id)
    ):
        raise ScoreError("dataset case IDs must be unique and non-empty")
    output_by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        case_id = result.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in output_by_id:
            raise ScoreError("outputs contain a blank or duplicate case binding")
        output_by_id[case_id] = result
    if set(output_by_id) != set(expected_by_id):
        raise ScoreError("outputs must exactly cover dataset case IDs without missing or extra bindings")
    identities = {
        (result.get("runtime"), result.get("model_id"), result.get("effort"))
        for result in results
    }
    if len(identities) != 1 or any(not item for item in next(iter(identities))):
        raise ScoreError("outputs must bind one non-empty runtime/model/effort tuple")
    rubrics, package_hash = rubric_bindings(cases, rubrics_root)
    schema_valid = 0
    correct = 0
    block_total = 0
    block_correct = 0
    uncertain_total = 0
    uncertain_correct = 0
    covered_rubrics: set[str] = set()
    per_case: list[dict[str, Any]] = []
    for case_id, case in expected_by_id.items():
        result = output_by_id[case_id]
        result_keys = {
            "$schema", "case_id", "rubric_id", "rubric_hash", "rubric_package_hash",
            "runtime", "model_id", "effort", "dataset_case_hash", "input_hash",
            "request", "request_hash", "raw_response", "parsed_response", "parser_error",
            "transport",
        }
        if not isinstance(result, dict) or set(result) != result_keys or result.get("$schema") != CASE_RESULT_SCHEMA:
            raise ScoreError(f"output {case_id} has an invalid case-result contract")
        rubric = rubrics[case["rubric_id"]]
        request = expected_request(case, rubric, package_hash)
        expected_bindings = {
            "rubric_id": case["rubric_id"],
            "rubric_hash": rubric["rubric_hash"],
            "rubric_package_hash": package_hash,
            "dataset_case_hash": digest(canonical(case)),
            "input_hash": request["binding"]["input_hash"],
            "request_hash": digest(canonical(request)),
        }
        if result["request"] != request or any(result[key] != value for key, value in expected_bindings.items()):
            raise ScoreError(f"output {case_id} does not bind the exact case, rubric, package, and request")
        transport = result["transport"]
        if (
            not isinstance(transport, dict)
            or set(transport) != {"exit_code", "timed_out", "stderr_present"}
            or not isinstance(transport["timed_out"], bool)
            or not isinstance(transport["stderr_present"], bool)
            or not (
                transport["exit_code"] is None
                or isinstance(transport["exit_code"], int) and not isinstance(transport["exit_code"], bool)
            )
        ):
            raise ScoreError(f"output {case_id} transport evidence is invalid")
        expected = case.get("expected", {}).get("verdict")
        valid, actual = _validate_candidate_output(
            result["raw_response"], result["parsed_response"], result["parser_error"],
            request, case_id,
        )
        is_correct = valid and actual == expected
        schema_valid += int(valid)
        correct += int(is_correct)
        block_total += int(expected == "BLOCK")
        block_correct += int(expected == "BLOCK" and is_correct)
        uncertain_total += int(expected in {"HOLD", "ABSTAIN"})
        uncertain_correct += int(expected in {"HOLD", "ABSTAIN"} and is_correct)
        if valid:
            covered_rubrics.add(case["rubric_id"])
        per_case.append(
            {
                "case_id": case_id,
                "rubric_id": case["rubric_id"],
                "rubric_hash": rubric["rubric_hash"],
                "rubric_package_hash": package_hash,
                "dataset_case_hash": expected_bindings["dataset_case_hash"],
                "input_hash": expected_bindings["input_hash"],
                "request_hash": expected_bindings["request_hash"],
                "expected": expected,
                "actual": actual,
                "schema_valid": valid,
                "correct": is_correct,
            }
        )
    dataset_rubrics = {case["rubric_id"] for case in cases}
    metrics = {
        "overall_accuracy": ratio(correct, len(cases)),
        "block_recall": ratio(block_correct, block_total),
        "hold_abstain_accuracy": ratio(uncertain_correct, uncertain_total),
        "schema_validity": ratio(schema_valid, len(cases)),
        "rubric_coverage": ratio(len(covered_rubrics), len(dataset_rubrics)),
    }
    if not all(math.isfinite(value) for value in metrics.values()):
        raise ScoreError("metrics must be finite")
    threshold_map = {
        "overall_accuracy": "minimum_overall_accuracy",
        "block_recall": "minimum_block_recall",
        "hold_abstain_accuracy": "minimum_hold_abstain_accuracy",
        "schema_validity": "minimum_schema_validity",
        "rubric_coverage": "minimum_rubric_coverage",
    }
    passing = all(metrics[key] >= thresholds[threshold_key] for key, threshold_key in threshold_map.items())
    runtime, model_id, effort = next(iter(identities))
    return {
        "$schema": SCORE_SCHEMA,
        "scorer_version": SCORER_VERSION,
        "purpose": "hardening-gate-verdict",
        "role": role,
        "runtime": runtime,
        "model_id": model_id,
        "effort": effort,
        "dataset_hash": digest(dataset.read_bytes()),
        "raw_output_hash": digest(outputs.read_bytes()),
        "policy_hash": digest(policy.read_bytes()),
        "rubric_package_hash": package_hash,
        "rubric_hashes": {rubric_id: item["rubric_hash"] for rubric_id, item in rubrics.items()},
        "metrics": metrics,
        "thresholds": thresholds,
        "result": "PASS" if passing else "FAIL",
        "qualification_status": "SHADOW",
        "ratification_eligible": bool(passing and policy_value.get("ratified") is True),
        "per_case": per_case,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--dataset", type=Path, required=True)
    result.add_argument("--outputs", type=Path, required=True)
    result.add_argument("--policy", type=Path, required=True)
    result.add_argument("--role", required=True)
    result.add_argument("--rubrics-root", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = score(args.dataset, args.outputs, args.policy, args.role, args.rubrics_root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ScoreError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"result": result["result"], "qualification_status": "SHADOW", "output": str(args.output), "sha256": digest(args.output.read_bytes())}, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
