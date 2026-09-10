"""Prepare and score blind rendered comparisons for frontend creative quality.

The runner deliberately does not generate designs or choose a model. Supply paired screenshot
sets and deterministic evidence from the current and candidate instruction treatments, then give
the blinded packet to an independent human or purpose-qualified Critic. Scores remain shadow
evidence until the owner ratifies an acceptance threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import zlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evals" / "frontend_quality" / "creative_cases.json"
POSTURES = frozenset({"conform", "evolve", "explore"})
WINNERS = frozenset({"a", "b", "tie"})
EVIDENCE_STATUSES = frozenset({"pass", "fail", "unverified"})
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
VIEWPORT_PATTERN = re.compile(r"^(?P<width>[1-9]\d*)x(?P<height>[1-9]\d*)$")


def load_cases(path: Path = CASES) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "mode",
        "coverage_claim",
        "dimensions",
        "blockers",
        "cases",
    }
    if set(payload) != required or payload["schema_version"] != "1.0" or payload["mode"] != "shadow":
        raise ValueError("frontend creative cases have an unsupported schema")
    if not isinstance(payload["coverage_claim"], str) or "unproven" not in payload["coverage_claim"]:
        raise ValueError("frontend creative cases overclaim capability coverage")
    for field in ("dimensions", "blockers"):
        values = payload[field]
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(item, str) and item for item in values)
            or len(values) != len(set(values))
        ):
            raise ValueError(f"frontend creative cases need a unique {field} vocabulary")
    if not isinstance(payload["cases"], list) or not payload["cases"]:
        raise ValueError("frontend creative cases need representative cases")
    seen: set[str] = set()
    for case in payload["cases"]:
        if not isinstance(case, dict) or set(case) != {
            "id",
            "posture",
            "prompt",
            "brief",
            "continuity_constraints",
            "required_axes",
        }:
            raise ValueError("frontend creative case does not match the case schema")
        if case["id"] in seen or case["posture"] not in POSTURES:
            raise ValueError("frontend creative case has duplicate identity or invalid posture")
        if not all(isinstance(case[key], str) and case[key] for key in ("id", "prompt", "brief")):
            raise ValueError("frontend creative case has invalid text")
        if not all(isinstance(case[key], list) for key in ("continuity_constraints", "required_axes")):
            raise ValueError("frontend creative case has invalid constraints")
        if not all(
            isinstance(item, str) and item
            for key in ("continuity_constraints", "required_axes")
            for item in case[key]
        ):
            raise ValueError("frontend creative case constraints must be non-empty strings")
        seen.add(case["id"])
    return payload


def _case_map(cases: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {case["id"]: case for case in cases["cases"]}


def _png_artifact(value: object) -> dict[str, Any]:
    if not isinstance(value, str) or not value:
        raise ValueError("comparison image path must be a non-empty string")
    path = Path(value).expanduser()
    if path.suffix.lower() != ".png" or not path.is_file():
        raise ValueError(f"comparison image is missing or not PNG: {value}")
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"comparison image has an invalid PNG signature: {value}")

    offset = len(PNG_SIGNATURE)
    width = height = channels = bit_depth = 0
    compressed = bytearray()
    saw_iend = False
    valid_channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f"comparison image has a truncated PNG chunk: {value}")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(data):
            raise ValueError(f"comparison image has a truncated PNG payload: {value}")
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length : chunk_end])[0]
        if zlib.crc32(chunk_type + payload) & 0xFFFFFFFF != expected_crc:
            raise ValueError(f"comparison image has an invalid PNG checksum: {value}")
        if chunk_type == b"IHDR":
            if offset != len(PNG_SIGNATURE) or length != 13:
                raise ValueError(f"comparison image has an invalid PNG header: {value}")
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if (
                width <= 0
                or height <= 0
                or color_type not in valid_channels
                or bit_depth not in {8, 16}
                or compression != 0
                or filtering != 0
                or interlace != 0
            ):
                raise ValueError(f"comparison image uses an unsupported PNG encoding: {value}")
            channels = valid_channels[color_type]
        elif chunk_type == b"IDAT":
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            if length != 0 or chunk_end != len(data):
                raise ValueError(f"comparison image has an invalid PNG ending: {value}")
            saw_iend = True
        offset = chunk_end
    if not saw_iend or not compressed or not width or not height:
        raise ValueError(f"comparison image is incomplete: {value}")
    try:
        pixels = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise ValueError(f"comparison image has invalid compressed pixels: {value}") from exc
    row_bytes = (width * channels * bit_depth + 7) // 8
    if len(pixels) != height * (row_bytes + 1):
        raise ValueError(f"comparison image has an invalid decoded pixel size: {value}")
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
    }


def _validate_capture_matrix(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("shared conditions need a capture matrix")
    normalized: list[dict[str, str]] = []
    keys: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {"state", "viewport"}:
            raise ValueError("capture matrix item does not match the matrix schema")
        state, viewport = item["state"], item["viewport"]
        if not isinstance(state, str) or not state or not isinstance(viewport, str) or not viewport:
            raise ValueError("capture matrix values must be non-empty strings")
        if VIEWPORT_PATTERN.fullmatch(viewport) is None:
            raise ValueError("capture matrix viewport must use WIDTHxHEIGHT pixels")
        key = (state, viewport)
        if key in keys:
            raise ValueError("capture matrix repeats a state and viewport")
        keys.add(key)
        normalized.append({"state": state, "viewport": viewport})
    return normalized


def _validate_evidence(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "task_replay",
        "accessibility",
        "responsive_states",
        "repository_checks",
    }:
        raise ValueError("deterministic evidence does not match the evidence schema")

    def evidence_item(item: object) -> dict[str, str]:
        if not isinstance(item, dict) or set(item) != {"status", "reference"}:
            raise ValueError("deterministic evidence item does not match the item schema")
        if item["status"] not in EVIDENCE_STATUSES or not isinstance(item["reference"], str):
            raise ValueError("deterministic evidence item has invalid values")
        return {"status": item["status"], "reference": item["reference"]}

    checks = value["repository_checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("deterministic evidence needs repository checks")
    return {
        "task_replay": evidence_item(value["task_replay"]),
        "accessibility": evidence_item(value["accessibility"]),
        "responsive_states": evidence_item(value["responsive_states"]),
        "repository_checks": [evidence_item(check) for check in checks],
    }


def _validate_treatment(value: object, matrix: list[dict[str, str]]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "instruction_revision",
        "images",
        "deterministic_evidence",
    }:
        raise ValueError("creative treatment does not match the treatment schema")
    revision = value["instruction_revision"]
    if not isinstance(revision, str) or not revision:
        raise ValueError("creative treatment needs an instruction revision")
    images = value["images"]
    if not isinstance(images, list):
        raise TypeError("creative treatment images must be a list")
    normalized_images: list[dict[str, Any]] = []
    observed: set[tuple[str, str]] = set()
    for image in images:
        if not isinstance(image, dict) or set(image) != {"state", "viewport", "path"}:
            raise ValueError("creative treatment image does not match the image schema")
        key = (image["state"], image["viewport"])
        if key in observed or not all(isinstance(item, str) and item for item in key):
            raise ValueError("creative treatment image has invalid or duplicate coordinates")
        observed.add(key)
        artifact = _png_artifact(image["path"])
        viewport_match = VIEWPORT_PATTERN.fullmatch(image["viewport"])
        if viewport_match is None:
            raise ValueError("creative treatment image viewport must use WIDTHxHEIGHT pixels")
        expected_size = (
            int(viewport_match.group("width")),
            int(viewport_match.group("height")),
        )
        if (artifact["width"], artifact["height"]) != expected_size:
            raise ValueError(
                "creative treatment image dimensions do not match its viewport: "
                f"{image['path']} is {artifact['width']}x{artifact['height']}, "
                f"expected {image['viewport']}"
            )
        normalized_images.append({**image, "artifact": artifact})
    expected = {(item["state"], item["viewport"]) for item in matrix}
    if observed != expected:
        raise ValueError("creative treatment images do not cover the shared capture matrix")
    return {
        "instruction_revision": revision,
        "images": normalized_images,
        "deterministic_evidence": _validate_evidence(value["deterministic_evidence"]),
    }


def validate_manifest(value: object, cases: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"run_identifier", "comparisons"}:
        raise ValueError("creative comparison manifest does not match the manifest schema")
    run_identifier = value["run_identifier"]
    comparisons = value["comparisons"]
    if not isinstance(run_identifier, str) or not run_identifier:
        raise ValueError("creative comparison manifest needs a run identifier")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("creative comparison manifest needs at least one comparison")
    available = _case_map(cases)
    observed: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for comparison in comparisons:
        if not isinstance(comparison, dict) or set(comparison) != {
            "case_id",
            "shared_conditions",
            "family_reference_images",
            "baseline",
            "candidate",
        }:
            raise ValueError("creative comparison does not match the comparison schema")
        case_id = comparison["case_id"]
        if not isinstance(case_id, str) or case_id not in available or case_id in observed:
            raise ValueError("creative comparison references an unknown or duplicate case")
        observed.add(case_id)
        shared = comparison["shared_conditions"]
        if not isinstance(shared, dict) or set(shared) != {
            "project_fixture",
            "model_runtime",
            "generation_seed",
            "capture_matrix",
        }:
            raise ValueError("shared conditions do not match the shared-condition schema")
        if not all(
            isinstance(shared[field], str) and shared[field]
            for field in ("project_fixture", "model_runtime", "generation_seed")
        ):
            raise ValueError("shared condition provenance must be non-empty")
        matrix = _validate_capture_matrix(shared["capture_matrix"])
        references = comparison["family_reference_images"]
        if not isinstance(references, list):
            raise TypeError("family reference images must be a list")
        normalized_references = [_png_artifact(reference) for reference in references]
        if available[case_id]["posture"] in {"conform", "evolve"} and not normalized_references:
            raise ValueError("conform and evolve comparisons need a family reference image")
        normalized.append(
            {
                "case_id": case_id,
                "shared_conditions": {**shared, "capture_matrix": matrix},
                "family_reference_images": normalized_references,
                "baseline": _validate_treatment(comparison["baseline"], matrix),
                "candidate": _validate_treatment(comparison["candidate"], matrix),
            }
        )
    return {"run_identifier": run_identifier, "comparisons": normalized}


def _assignment(run_identifier: str, case_id: str) -> dict[str, str]:
    digest = hashlib.sha256(f"{run_identifier}:{case_id}".encode()).digest()
    return {"a": "candidate", "b": "baseline"} if digest[0] & 1 else {"a": "baseline", "b": "candidate"}


def _comparison_provenance(comparison: dict[str, Any]) -> dict[str, Any]:
    provenance = {
        "case_id": comparison["case_id"],
        "shared_conditions": comparison["shared_conditions"],
        "family_reference_hashes": [item["sha256"] for item in comparison["family_reference_images"]],
        "treatments": {
            treatment: {
                "instruction_revision": comparison[treatment]["instruction_revision"],
                "artifacts": [
                    {
                        "state": item["state"],
                        "viewport": item["viewport"],
                        "sha256": item["artifact"]["sha256"],
                        "width": item["artifact"]["width"],
                        "height": item["artifact"]["height"],
                    }
                    for item in comparison[treatment]["images"]
                ],
                "deterministic_evidence": comparison[treatment]["deterministic_evidence"],
            }
            for treatment in ("baseline", "candidate")
        },
    }
    encoded = json.dumps(provenance, sort_keys=True, separators=(",", ":")).encode()
    return {**provenance, "comparison_sha256": hashlib.sha256(encoded).hexdigest()}


def prepare_review(
    manifest: object,
    cases: dict[str, Any] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    cases = cases or load_cases()
    normalized = validate_manifest(manifest, cases)
    available = _case_map(cases)
    packet_root = output_dir or ROOT / ".tmp" / "frontend_quality_creative"
    blind_run_id = hashlib.sha256(normalized["run_identifier"].encode()).hexdigest()[:16]
    blind_root = packet_root / blind_run_id
    blind_root.mkdir(parents=True, exist_ok=True)
    packets: list[dict[str, Any]] = []
    for comparison in normalized["comparisons"]:
        case = available[comparison["case_id"]]
        assignment = _assignment(normalized["run_identifier"], case["id"])
        blinded_images: dict[str, list[dict[str, str]]] = {"a": [], "b": []}
        for slot, treatment in assignment.items():
            for index, image in enumerate(comparison[treatment]["images"], start=1):
                source = Path(image["artifact"]["path"])
                target = blind_root / f"{case['id']}-{slot}-{index}.png"
                shutil.copyfile(source, target)
                blinded_images[slot].append(
                    {"state": image["state"], "viewport": image["viewport"], "path": str(target.resolve())}
                )
        blinded_references: list[str] = []
        for index, reference in enumerate(comparison["family_reference_images"], start=1):
            target = blind_root / f"{case['id']}-reference-{index}.png"
            shutil.copyfile(reference["path"], target)
            blinded_references.append(str(target.resolve()))
        packets.append(
            {
                "case_id": case["id"],
                "posture": case["posture"],
                "prompt": case["prompt"],
                "brief": case["brief"],
                "continuity_constraints": case["continuity_constraints"],
                "required_axes": case["required_axes"],
                "shared_conditions": comparison["shared_conditions"],
                "family_reference_images": blinded_references,
                "images": blinded_images,
                "deterministic_evidence": {
                    slot: comparison[treatment]["deterministic_evidence"]
                    for slot, treatment in assignment.items()
                },
                "dimensions": cases["dimensions"],
                "blocker_vocabulary": cases["blockers"],
                "comparison_sha256": _comparison_provenance(comparison)["comparison_sha256"],
                "review_instruction": (
                    "Review the treatments blind to identity. Choose a, b, or tie overall and for "
                    "each positive quality dimension. A blocker cannot be averaged away. Judge "
                    "directed distinctiveness against the brief; unusual but task-obscuring work "
                    "does not win. Use family references for continuity and deterministic evidence "
                    "for task, accessibility, responsive-state, and repository-check claims."
                ),
            }
        )
    return {
        "schema_version": "1.0",
        "mode": "blind_review",
        "coverage_claim": cases["coverage_claim"],
        "run_identifier": normalized["run_identifier"],
        "comparisons": packets,
    }


def _validate_response(
    value: object,
    case_id: str,
    dimensions: list[str],
    blocker_vocabulary: set[str],
) -> dict[str, Any]:
    required = {"case_id", "preferred", "dimension_winners", "blockers", "reason"}
    if not isinstance(value, dict) or set(value) != required or value["case_id"] != case_id:
        raise ValueError("creative review response does not match the response schema")
    if value["preferred"] not in WINNERS or not isinstance(value["reason"], str):
        raise ValueError("creative review response has an invalid preference or reason")
    winners = value["dimension_winners"]
    if not isinstance(winners, dict) or set(winners) != set(dimensions):
        raise ValueError("creative review response has invalid dimension winners")
    if not all(winner in WINNERS for winner in winners.values()):
        raise ValueError("creative review response has an invalid dimension winner")
    blockers = value["blockers"]
    if not isinstance(blockers, dict) or set(blockers) != {"a", "b"}:
        raise ValueError("creative review response has invalid blockers")
    for flags in blockers.values():
        if not isinstance(flags, list) or not set(flags) <= blocker_vocabulary:
            raise ValueError("creative review response has an unknown blocker")
    return value


def _deterministic_blockers(evidence: dict[str, Any]) -> list[str]:
    blockers = [
        f"{field}:{item['status']}"
        for field, item in evidence.items()
        if field != "repository_checks" and item["status"] != "pass"
    ]
    blockers.extend(
        f"repository_check:{index}:{item['status']}"
        for index, item in enumerate(evidence["repository_checks"], start=1)
        if item["status"] != "pass"
    )
    return blockers


def _empty_posture_summary(dimensions: list[str]) -> dict[str, Any]:
    return {
        "comparison_count": 0,
        "preference_counts": {"win": 0, "loss": 0, "tie": 0, "blocked": 0},
        "dimension_counts": {
            dimension: {"win": 0, "loss": 0, "tie": 0} for dimension in dimensions
        },
    }


def score_responses(
    manifest: object,
    responses: object,
    cases: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cases = cases or load_cases()
    normalized = validate_manifest(manifest, cases)
    if not isinstance(responses, list):
        raise TypeError("creative review responses must be a list")
    if not all(isinstance(response, dict) and isinstance(response.get("case_id"), str) for response in responses):
        raise ValueError("creative review responses must use string case identifiers")
    by_id = {response["case_id"]: response for response in responses}
    expected_ids = {item["case_id"] for item in normalized["comparisons"]}
    if len(by_id) != len(responses) or set(by_id) != expected_ids:
        raise ValueError("creative review responses must cover every comparison exactly once")

    available = _case_map(cases)
    outcomes: list[dict[str, Any]] = []
    by_posture = {posture: _empty_posture_summary(cases["dimensions"]) for posture in sorted(POSTURES)}
    for comparison in normalized["comparisons"]:
        case_id = comparison["case_id"]
        posture = available[case_id]["posture"]
        response = _validate_response(by_id[case_id], case_id, cases["dimensions"], set(cases["blockers"]))
        assignment = _assignment(normalized["run_identifier"], case_id)
        candidate_slot = next(slot for slot, treatment in assignment.items() if treatment == "candidate")
        baseline_slot = next(slot for slot, treatment in assignment.items() if treatment == "baseline")
        candidate_blockers = [
            *response["blockers"][candidate_slot],
            *_deterministic_blockers(comparison["candidate"]["deterministic_evidence"]),
        ]
        baseline_blockers = [
            *response["blockers"][baseline_slot],
            *_deterministic_blockers(comparison["baseline"]["deterministic_evidence"]),
        ]
        if candidate_blockers:
            outcome = "blocked"
        elif baseline_blockers:
            outcome = "win"
        elif response["preferred"] == "tie":
            outcome = "tie"
        else:
            outcome = "win" if assignment[response["preferred"]] == "candidate" else "loss"

        dimension_outcomes: dict[str, str] = {}
        for dimension, winner in response["dimension_winners"].items():
            if winner == "tie":
                dimension_outcome = "tie"
            else:
                dimension_outcome = "win" if assignment[winner] == "candidate" else "loss"
            dimension_outcomes[dimension] = dimension_outcome
            by_posture[posture]["dimension_counts"][dimension][dimension_outcome] += 1
        by_posture[posture]["comparison_count"] += 1
        by_posture[posture]["preference_counts"][outcome] += 1
        outcomes.append(
            {
                "case_id": case_id,
                "posture": posture,
                "candidate_preference": outcome,
                "dimension_outcomes": dimension_outcomes,
                "candidate_blockers": candidate_blockers,
                "baseline_blockers": baseline_blockers,
                "reason": response["reason"],
                "provenance": _comparison_provenance(comparison),
            }
        )
    return {
        "schema_version": "1.0",
        "mode": "shadow_score",
        "coverage_claim": cases["coverage_claim"],
        "automatic_gate": "disabled",
        "comparison_count": len(outcomes),
        "by_posture": by_posture,
        "results": outcomes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--responses", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    cases = load_cases()
    if args.manifest is None:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "cases": [case["id"] for case in cases["cases"]],
                    "dimensions": cases["dimensions"],
                    "manifest_schema": {
                        "run_identifier": "string",
                        "comparisons": [
                            {
                                "case_id": "registered case id",
                                "shared_conditions": {
                                    "project_fixture": "stable fixture or revision",
                                    "model_runtime": "model and runtime revision",
                                    "generation_seed": "shared seed",
                                    "capture_matrix": [{"state": "populated", "viewport": "1440x900"}],
                                },
                                "family_reference_images": ["reference.png"],
                                "baseline": "treatment object",
                                "candidate": "treatment object",
                            }
                        ],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = (
        prepare_review(manifest, cases, args.output_dir)
        if args.responses is None
        else score_responses(
            manifest,
            json.loads(args.responses.read_text(encoding="utf-8")),
            cases,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
