from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

import pytest

from harden_state import ACTIVE_EXPERTS, PackageHold, validate_capability_receipt

ROOT = Path(__file__).resolve().parents[1]


def digest(raw: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bound_rows(
    runner: ModuleType, cases: list[dict[str, object]], rubrics_root: Path,
    *, runtime: str = "codex", model_id: str = "fixture-model", effort: str = "high",
) -> list[dict[str, object]]:
    bindings, package_hash = runner.load_rubric_bindings(cases, rubrics_root)
    rows: list[dict[str, object]] = []
    for case in cases:
        request = runner.request_for(case, bindings[case["rubric_id"]], package_hash)
        binding = request["binding"]
        response = {
            "$schema": runner.OUTPUT_SCHEMA,
            "case_id": binding["case_id"],
            "rubric_id": binding["rubric_id"],
            "rubric_hash": binding["rubric_hash"],
            "rubric_package_hash": binding["rubric_package_hash"],
            "input_hash": binding["input_hash"],
            "verdict": case["expected"]["verdict"],
            "finding_ids": [],
            "rationale": "fixture answer",
        }
        rows.append(
            {
                "$schema": runner.CASE_RESULT_SCHEMA,
                "case_id": binding["case_id"],
                "rubric_id": binding["rubric_id"],
                "rubric_hash": binding["rubric_hash"],
                "rubric_package_hash": binding["rubric_package_hash"],
                "runtime": runtime,
                "model_id": model_id,
                "effort": effort,
                "dataset_case_hash": binding["dataset_case_hash"],
                "input_hash": binding["input_hash"],
                "request": request,
                "request_hash": digest(runner.canonical(request)),
                "raw_response": json.dumps(response, sort_keys=True),
                "parsed_response": response,
                "parser_error": None,
                "transport": {"exit_code": 0, "timed_out": False, "stderr_present": False},
            }
        )
    return rows


@pytest.fixture()
def package(tmp_path: Path) -> tuple[Path, dict[str, object], dict[str, object]]:
    root = tmp_path / "package"
    for directory in ("runtime", "rubrics", "config", "evals", "receipts", "evidence/test-receipt"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "procedures" / "harden.md", root / "SKILL.md")
    shutil.copy2(ROOT / "snippets" / "harden_state.py", root / "runtime" / "harden_state.py")
    for expert in ACTIVE_EXPERTS:
        shutil.copy2(ROOT / "procedures" / "agents" / f"{expert}.md", root / "rubrics" / f"{expert}.md")
    for name in ("harden_state_v2.schema.json", "harden_mandatory_rules.json", "harden_capability_registry.json"):
        shutil.copy2(ROOT / "config" / name, root / "config" / name)
    policy = json.loads((ROOT / "config" / "harden_eval_policy.json").read_text(encoding="utf-8"))
    policy.update(ratified=True, ratified_at="2026-08-20T00:00:00Z", ratifier="owner-test")
    policy_path = root / "config" / "harden_eval_policy.json"
    policy_path.write_text(json.dumps(policy, sort_keys=True) + "\n", encoding="utf-8")
    dataset = root / "evals" / "cases.jsonl"
    shutil.copy2(ROOT / "evals" / "harden" / "cases.jsonl", dataset)
    runner = load_module("harden_fixture_runner", ROOT / "evals" / "harden" / "run_capability_eval.py")
    scorer = load_module("harden_fixture_scorer", ROOT / "evals" / "harden" / "score_capability_eval.py")
    cases = runner.load_cases(dataset)
    raw_path = root / "evidence" / "test-receipt" / "per_case_outputs.jsonl"
    rows = bound_rows(runner, cases, root / "rubrics", model_id="test-model")
    raw_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    score = scorer.score(dataset, raw_path, policy_path, "blocking-specialist", root / "rubrics")
    metrics = score["metrics"]
    score_path = root / "evidence" / "test-receipt" / "score.json"
    score_path.write_text(json.dumps(score, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "$schema": "internal://harden-capability-receipt/v2",
        "receipt_id": "test-receipt",
        "purpose": "hardening-gate-verdict",
        "status": "QUALIFIED",
        "ratified": True,
        "ratifier": "owner-test",
        "capability_role": "blocking-specialist",
        "provider": "test-provider",
        "provider_class": "hosted",
        "runtime": "codex",
        "model_id": "test-model",
        "effort": "high",
        "quantization": None,
        "tool_capabilities": ["filesystem-read"],
        "context_limit": 200000,
        "hardware": None,
        "dataset_hash": digest(dataset.read_bytes()),
        "rubric_hashes": {"sec-appsec": digest((root / "rubrics" / "sec-appsec.md").read_bytes())},
        "rubric_package_hash": score["rubric_package_hash"],
        "raw_output_hash": digest(raw_path.read_bytes()),
        "score_result_hash": digest(score_path.read_bytes()),
        "score_breakdown": metrics,
        "policy_hash": digest(policy_path.read_bytes()),
        "scorer_version": "1.1.0",
        "evaluated_at": "2026-08-20T00:00:00Z",
        "expires_at": "2099-08-20T00:00:00Z",
        "qualified_rubrics": ["sec-appsec"],
        "limitations": [],
    }
    receipt_path = root / "receipts" / "test-receipt.json"
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    entry = {"receipt_id": "test-receipt", "receipt_hash": digest(receipt_path.read_bytes())}
    return root, receipt, entry


def rewrite_receipt(root: Path, receipt: dict[str, object], entry: dict[str, object]) -> None:
    path = root / "receipts" / "test-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    entry["receipt_hash"] = digest(path.read_bytes())


def rewrite_score(root: Path, receipt: dict[str, object], mutate) -> None:
    path = root / "evidence" / "test-receipt" / "score.json"
    score = json.loads(path.read_text(encoding="utf-8"))
    mutate(score)
    path.write_text(json.dumps(score, sort_keys=True) + "\n", encoding="utf-8")
    receipt["score_result_hash"] = digest(path.read_bytes())


def test_success_receipt_binds_raw_score_policy_model_and_rubric(package) -> None:
    root, receipt, entry = package
    assert validate_capability_receipt(root, entry) == receipt


def test_malformed_receipt_is_hold(package) -> None:
    root, _, entry = package
    path = root / "receipts" / "test-receipt.json"
    path.write_text("{", encoding="utf-8")
    entry["receipt_hash"] = digest(path.read_bytes())
    with pytest.raises(PackageHold, match="malformed"):
        validate_capability_receipt(root, entry)


def test_forged_score_metrics_cannot_qualify(package) -> None:
    root, receipt, entry = package
    def lower_score(score: dict[str, object]) -> None:
        score["metrics"]["overall_accuracy"] = 0.1

    rewrite_score(root, receipt, lower_score)
    receipt["score_breakdown"]["overall_accuracy"] = 0.1
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="metrics do not reproduce"):
        validate_capability_receipt(root, entry)


def test_stale_receipt_cannot_qualify(package) -> None:
    root, receipt, entry = package
    receipt["expires_at"] = "2026-08-21T00:00:00Z"
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="stale"):
        validate_capability_receipt(root, entry)


def test_raw_evidence_hash_drift_cannot_qualify(package) -> None:
    root, _, entry = package
    (root / "evidence" / "test-receipt" / "per_case_outputs.jsonl").write_text("changed\n", encoding="utf-8")
    with pytest.raises(PackageHold, match="evidence hash drift"):
        validate_capability_receipt(root, entry)


def test_unratified_policy_cannot_qualify(package) -> None:
    root, receipt, entry = package
    path = root / "config" / "harden_eval_policy.json"
    policy = json.loads(path.read_text(encoding="utf-8"))
    policy.update(ratified=False, ratified_at=None, ratifier=None)
    path.write_text(json.dumps(policy, sort_keys=True) + "\n", encoding="utf-8")
    receipt["policy_hash"] = digest(path.read_bytes())
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="not owner-ratified"):
        validate_capability_receipt(root, entry)


def test_runtime_or_model_mismatch_with_score_cannot_qualify(package) -> None:
    root, receipt, entry = package
    receipt["model_id"] = "different-model"
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="binding mismatch"):
        validate_capability_receipt(root, entry)


def test_open_weight_receipt_requires_exact_runtime_hardware_and_quantization(package) -> None:
    root, receipt, entry = package
    receipt.update(provider_class="open-weight", hardware=None, quantization=None)
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="hardware/quantization"):
        validate_capability_receipt(root, entry)


def test_runner_blinds_expected_answer_from_candidate() -> None:
    runner = load_module("harden_eval_runner", ROOT / "evals" / "harden" / "run_capability_eval.py")
    case = json.loads((ROOT / "evals" / "harden" / "cases.jsonl").read_text(encoding="utf-8").splitlines()[0])
    bindings, package_hash = runner.load_rubric_bindings(
        [case], ROOT / "procedures" / "agents"
    )
    request = runner.request_for(case, bindings[case["rubric_id"]], package_hash)
    assert "expected" not in request["case"]
    assert request["purpose"] == "hardening-gate-verdict"
    assert request["rubric"]["rubric_id"] == case["rubric_id"]
    assert request["rubric"]["rubric_text"] == (
        ROOT / "procedures" / "agents" / f"{case['rubric_id']}.md"
    ).read_text(encoding="utf-8")
    assert request["rubric"]["rubric_hash"] == digest(
        request["rubric"]["rubric_text"].encode()
    )
    assert request["binding"]["rubric_package_hash"] == package_hash


def test_corpus_has_multiple_cases_per_rubric_and_all_required_shapes() -> None:
    runner = load_module("harden_eval_runner_shapes", ROOT / "evals" / "harden" / "run_capability_eval.py")
    cases = runner.load_cases(ROOT / "evals" / "harden" / "cases.jsonl")
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["rubric_id"]] = counts.get(case["rubric_id"], 0) + 1
    assert set(counts) == set(ACTIVE_EXPERTS)
    assert min(counts.values()) >= 2
    assert {case.get("shape") for case in cases if case.get("shape")} == {
        "normal", "empty", "long-context", "malformed", "adversarial",
        "degraded", "conflicting-evidence",
    }
    policy = json.loads((ROOT / "config" / "harden_eval_policy.json").read_text())
    minimum_characters = policy["corpus_requirements"]["minimum_long_context_characters"]
    minimum_sections = policy["corpus_requirements"]["minimum_long_context_sections"]
    for case in (item for item in cases if item.get("shape") == "long-context"):
        sections = case.get("context_sections")
        assert isinstance(sections, list) and len(sections) >= minimum_sections
        assert len(json.dumps(sections, ensure_ascii=False)) >= minimum_characters


def test_scorer_emits_shadow_result_and_never_self_ratifies(tmp_path: Path) -> None:
    scorer = load_module("harden_eval_scorer", ROOT / "evals" / "harden" / "score_capability_eval.py")
    dataset = ROOT / "evals" / "harden" / "cases.jsonl"
    outputs = tmp_path / "outputs.jsonl"
    runner = load_module("harden_eval_runner_for_scorer", ROOT / "evals" / "harden" / "run_capability_eval.py")
    cases = runner.load_cases(dataset)
    rows = bound_rows(runner, cases, ROOT / "procedures" / "agents")
    outputs.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    result = scorer.score(
        dataset,
        outputs,
        ROOT / "config" / "harden_eval_policy.json",
        "blocking-specialist",
        ROOT / "procedures" / "agents",
    )
    assert result["result"] == "PASS"
    assert result["qualification_status"] == "SHADOW"
    assert result["ratification_eligible"] is False


def test_scorer_rejects_claimed_rubric_hash_when_retained_request_omits_exact_text(
    tmp_path: Path,
) -> None:
    runner = load_module("harden_eval_runner_forged_prompt", ROOT / "evals" / "harden" / "run_capability_eval.py")
    scorer = load_module("harden_eval_scorer_forged_prompt", ROOT / "evals" / "harden" / "score_capability_eval.py")
    dataset = ROOT / "evals" / "harden" / "cases.jsonl"
    cases = runner.load_cases(dataset)
    rows = bound_rows(runner, cases, ROOT / "procedures" / "agents")
    rows[0]["request"]["rubric"]["rubric_text"] = "A different rubric was actually sent."
    rows[0]["request_hash"] = digest(runner.canonical(rows[0]["request"]))
    outputs = tmp_path / "forged-prompt.jsonl"
    outputs.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(scorer.ScoreError, match="exact case, rubric, package, and request"):
        scorer.score(
            dataset, outputs, ROOT / "config" / "harden_eval_policy.json",
            "blocking-specialist", ROOT / "procedures" / "agents",
        )


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra"])
def test_scorer_rejects_non_bijective_raw_case_bindings(
    tmp_path: Path, mutation: str,
) -> None:
    runner = load_module(f"harden_eval_runner_{mutation}", ROOT / "evals" / "harden" / "run_capability_eval.py")
    scorer = load_module(f"harden_eval_scorer_{mutation}", ROOT / "evals" / "harden" / "score_capability_eval.py")
    dataset = ROOT / "evals" / "harden" / "cases.jsonl"
    rows = bound_rows(runner, runner.load_cases(dataset), ROOT / "procedures" / "agents")
    if mutation == "duplicate":
        rows.append(dict(rows[0]))
    elif mutation == "missing":
        rows.pop()
    else:
        extra = dict(rows[0])
        extra["case_id"] = "extra-case"
        rows.append(extra)
    outputs = tmp_path / f"{mutation}.jsonl"
    outputs.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(scorer.ScoreError, match="duplicate|exactly cover"):
        scorer.score(
            dataset, outputs, ROOT / "config" / "harden_eval_policy.json",
            "blocking-specialist", ROOT / "procedures" / "agents",
        )


def test_receipt_revalidates_raw_request_binding_after_all_outer_hashes_are_resealed(
    package,
) -> None:
    root, receipt, entry = package
    raw_path = root / "evidence" / "test-receipt" / "per_case_outputs.jsonl"
    rows = [json.loads(line) for line in raw_path.read_text().splitlines() if line]
    rows[0]["request"]["rubric"]["rubric_text"] = "Rubric text omitted from the real request."
    rows[0]["request_hash"] = digest(json.dumps(
        rows[0]["request"], sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode())
    raw_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    score_path = root / "evidence" / "test-receipt" / "score.json"
    score = json.loads(score_path.read_text())
    score["raw_output_hash"] = digest(raw_path.read_bytes())
    score_path.write_text(json.dumps(score, sort_keys=True) + "\n", encoding="utf-8")
    receipt["raw_output_hash"] = digest(raw_path.read_bytes())
    receipt["score_result_hash"] = digest(score_path.read_bytes())
    rewrite_receipt(root, receipt, entry)
    with pytest.raises(PackageHold, match="raw case binding mismatch"):
        validate_capability_receipt(root, entry)


def test_long_context_policy_rejects_relabelled_short_case(tmp_path: Path) -> None:
    runner = load_module("harden_eval_runner_short_context", ROOT / "evals" / "harden" / "run_capability_eval.py")
    cases = runner.load_cases(ROOT / "evals" / "harden" / "cases.jsonl")
    target = next(case for case in cases if case.get("shape") == "long-context")
    target["context_sections"] = [{"section_id": "short", "content": "not long"}]
    requirements = runner.load_requirements(ROOT / "config" / "harden_eval_policy.json")
    with pytest.raises(runner.EvalInputError, match="too few structured sections"):
        runner.validate_long_context(cases, requirements)
