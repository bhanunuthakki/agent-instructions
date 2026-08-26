"""Bounded shadow evaluation for the frontend-quality instruction contract.

Run from the instruction repository after the managed Codex membership transport is
available. The runner is intentionally opt-in and writes a receipt only after a
schema-valid model result; it does not claim invocation coverage.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "frontend_quality" / "shadow_cases.json"
RECEIPTS = ROOT / "evals" / "frontend_quality" / "receipts"
PAIR_FLAG_VOCABULARY = frozenset(
    {
        "redundant-container",
        "decorative-accent",
        "stacked-hierarchy",
        "decorative-list",
        "redundant-subtitle",
    }
)
TRAJECTORY_CONTRACT_FLAG_VOCABULARY = frozenset(
    {
        "baseline-render",
        "reobserve",
        "reduction-pass",
        "evidence-record",
        "rendered-evidence",
        "stack-inference",
        "deterministic-proof",
        "no-render-claim",
        "verification-gap",
        "no-visual-success-claim",
    }
)
MATERIALITY_DEFINITION = (
    "A material frontend change adds, removes, rearranges, or materially restyles a visible "
    "region, control, hierarchy, navigation path, state, or responsive behavior. Typo-only copy "
    "corrections, nonvisual handler changes, and mechanically regenerated mirrors with no rendered "
    "delta are not material."
)


def load_cases(path: Path = CASES) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.1" or payload.get("mode") != "shadow":
        raise ValueError("frontend-quality shadow cases have an unsupported schema")
    if not isinstance(payload.get("restraint_pairs"), list) or not isinstance(payload.get("task_trajectories"), list):
        raise ValueError("frontend-quality shadow cases are missing representative cases")
    return payload


def validate_response(value: object, case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("judge response must be a JSON object")
    case_id = str(case["id"])
    pair = "variant_a" in case
    required = (
        {"case_id", "type", "preferred_variant", "variant_a_flags", "variant_b_flags", "reason"}
        if pair
        else {"case_id", "type", "material", "ux_hypothesis", "rendered_evidence", "reduction_pass", "verification_gap", "verdict", "findings", "contract_flags"}
    )
    expected_type = "restraint_pair" if pair else "task_trajectory"
    if set(value) != required or value["case_id"] != case_id or value["type"] != expected_type:
        raise ValueError("judge response does not match the frontend-quality response schema")
    if pair:
        if value["preferred_variant"] not in {"a", "b"}:
            raise ValueError("pair response has an invalid preferred variant")
        for key in ("variant_a_flags", "variant_b_flags"):
            if not isinstance(value[key], list) or not all(isinstance(flag, str) for flag in value[key]):
                raise ValueError("pair response has invalid structured flags")
            if not set(value[key]) <= PAIR_FLAG_VOCABULARY:
                raise ValueError(f"case {case_id}: invalid pair flag")
        if not isinstance(value["reason"], str):
            raise ValueError("pair response has an invalid reason")
        return value
    if not isinstance(value["material"], bool):
        raise ValueError(f"case {case_id}: invalid materiality")
    if value["verdict"] not in {"PASS", "BLOCK", "HOLD", "ABSTAIN", "ADVISORY"}:
        raise ValueError(f"case {case_id}: invalid verdict")
    if not isinstance(value["contract_flags"], list) or not all(isinstance(flag, str) for flag in value["contract_flags"]):
        raise ValueError("trajectory response has invalid contract flags")
    if not set(value["contract_flags"]) <= TRAJECTORY_CONTRACT_FLAG_VOCABULARY:
        raise ValueError(f"case {case_id}: invalid trajectory contract flag")
    for key in required - {"case_id", "type", "material", "verdict", "contract_flags"}:
        if not isinstance(value[key], (str, list)):
            raise ValueError(f"judge response field {key} has an invalid type")
    return value


def score_case(case: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Score exact, hidden rubric flags; mismatch is visible but never coverage proof."""
    rubric = case["expected_rubric"]
    if "variant_a" in case:
        checks = {
            "preferred_variant": response["preferred_variant"] == rubric["preferred_variant"],
            "variant_a_flags": set(rubric["variant_a_flags"]) <= set(response["variant_a_flags"]),
            "variant_b_flags": set(rubric["variant_b_flags"]) <= set(response["variant_b_flags"]),
        }
    else:
        checks = {
            "material": response["material"] == rubric["material"],
            "contract_flags": set(rubric["contract_flags"]) <= set(response["contract_flags"]),
        }
    return {"case_id": case["id"], "status": "MATCH" if all(checks.values()) else "MISMATCH", "checks": checks}


def prompt_for(case: dict[str, Any]) -> str:
    if "variant_a" in case:
        payload = {"case_id": case["id"], "type": "restraint_pair", "surface": case["surface"], "variants": {"a": case["variant_a"], "b": case["variant_b"]}}
        schema = (
            "case_id (string), type (literal restraint_pair), preferred_variant (a|b), "
            "variant_a_flags (array of strings), variant_b_flags (array of strings), reason (string)"
        )
        vocabulary = f" Allowed pair flags for either variant: {sorted(PAIR_FLAG_VOCABULARY)}."
    else:
        payload = {"case_id": case["id"], "type": "task_trajectory", "prompt": case["prompt"]}
        schema = (
            "case_id (string), type (literal task_trajectory), material (boolean), "
            "ux_hypothesis (string or array of strings), rendered_evidence (string or array of strings), "
            "reduction_pass (string or array of strings), verification_gap (string or array of strings), "
            "verdict (PASS|BLOCK|ADVISORY|HOLD|ABSTAIN), findings (string or array of strings), "
            "contract_flags (array of strings)"
        )
        vocabulary = (
            f" Materiality definition: {MATERIALITY_DEFINITION} "
            f"Allowed contract_flags: {sorted(TRAJECTORY_CONTRACT_FLAG_VOCABULARY)}."
        )
    return (
        "Evaluate this frontend-quality shadow case. Return JSON only with exactly: "
        + schema
        + vocabulary
        + ". Do not claim universal invocation coverage.\n"
        + json.dumps(payload, sort_keys=True)
    )


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "snippets"))
    from codex_cli import call_codex  # noqa: PLC0415

    raw = call_codex(prompt_for(case))
    return validate_response(json.loads(raw), case)


def receipt_target(run_identifier: str) -> Path:
    return RECEIPTS / f"{run_identifier}_shadow.json"


def validate_receipt(value: object, cases: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version",
        "mode",
        "coverage_claim",
        "executed_at",
        "run_identifier",
        "results",
        "rubric_scores",
    }
    if not isinstance(value, dict):
        raise TypeError("frontend-quality receipt must be a JSON object")
    if set(value) != required:
        raise ValueError("frontend-quality receipt does not match the current schema")
    if value["schema_version"] != "1.0" or value["mode"] != "shadow":
        raise ValueError("frontend-quality receipt has unsupported metadata")
    run_identifier = value["run_identifier"]
    if not isinstance(run_identifier, str) or not run_identifier:
        raise ValueError("frontend-quality receipt is missing its run identifier")
    if (
        not isinstance(value["coverage_claim"], str)
        or "unproven" not in value["coverage_claim"]
    ):
        raise ValueError("frontend-quality receipt overclaims invocation coverage")
    if not isinstance(value["executed_at"], str):
        raise TypeError("frontend-quality receipt execution time must be a string")
    datetime.fromisoformat(value["executed_at"])

    case_by_id = {
        str(case["id"]): case
        for case in [*cases["restraint_pairs"], *cases["task_trajectories"]]
    }
    if not isinstance(value["results"], list) or not isinstance(
        value["rubric_scores"], list
    ):
        raise TypeError("frontend-quality receipt results must be lists")
    if len(value["results"]) != len(value["rubric_scores"]):
        raise ValueError("frontend-quality receipt result and score counts differ")

    observed_ids: list[str] = []
    for result, recorded_score in zip(
        value["results"], value["rubric_scores"], strict=True
    ):
        if not isinstance(result, dict) or not isinstance(result.get("case_id"), str):
            raise TypeError("frontend-quality receipt has an invalid result")
        case_id = result["case_id"]
        case = case_by_id.get(case_id)
        if case is None:
            raise ValueError(
                f"frontend-quality receipt references unknown case {case_id}"
            )
        validated_result = validate_response(result, case)
        expected_score = score_case(case, validated_result)
        if recorded_score != expected_score:
            raise ValueError(
                f"frontend-quality receipt score does not replay for {case_id}"
            )
        observed_ids.append(case_id)
    if len(observed_ids) != len(set(observed_ids)):
        raise ValueError("frontend-quality receipt repeats a case")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="call the managed Codex transport")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    cases = load_cases()
    selected = [*cases["restraint_pairs"], *cases["task_trajectories"]][: args.limit]
    if not args.execute:
        print(json.dumps({"mode": "dry-run", "selected": [case["id"] for case in selected]}))
        return
    results = [run_case(case) for case in selected]
    now = datetime.now(UTC)
    run_identifier = now.strftime("%Y%m%dT%H%M%S%fZ")
    receipt = {
        "schema_version": "1.0",
        "mode": "shadow",
        "coverage_claim": cases["coverage_claim"],
        "executed_at": now.isoformat(),
        "run_identifier": run_identifier,
        "results": results,
        "rubric_scores": [
            score_case(case, result)
            for case, result in zip(selected, results, strict=True)
        ],
    }
    validate_receipt(receipt, cases)
    if args.write_receipt:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        target = receipt_target(run_identifier)
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
