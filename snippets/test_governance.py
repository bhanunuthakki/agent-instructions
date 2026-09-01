"""Regression tests for shared vocabulary and J0-J3 evidence governance."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import definition_governance as definitions  # noqa: E402
import judge_governance as judges  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def proof(check_id: str = "tests") -> dict[str, object]:
    return {
        "check_id": check_id,
        "status": "passed",
        "evidence_ref": "sha256:abc123",
        "observed_at": "2026-08-13T12:00:00Z",
    }


def judge(
    judge_id: str, verdict: str = "PASS", purpose: str | None = None
) -> dict[str, object]:
    selected_purpose = purpose or (
        "risk" if judge_id in {"two", "evals", "risk"} else "specialist"
    )
    return {
        "judge_id": judge_id,
        "independent": True,
        "verdict": verdict,
        "purpose": selected_purpose,
        "registry_version": "1.1.0",
        "rubric_version": f"judge-{selected_purpose}-1.1.0",
        "evidence_refs": ["sha256:abc123"],
    }


def audit(
    finding: str = "none",
    *,
    routing_correct: bool = True,
    execution_correct: bool = True,
) -> dict[str, object]:
    return {
        "auditor_id": "independent-auditor",
        "audit_session_id": "019ffe89-93ba-7913-99a8-5c94345e4255",
        "independent_context": True,
        "rubric_version": "judge-audit-1.1.0",
        "evidence_refs": ["sha256:abc123"],
        "finding": finding,
        "reason": "Independent routing and execution review.",
        "routing_correct": routing_correct,
        "execution_correct": execution_correct,
        "completed_at": "2026-08-13T12:00:00Z",
    }


def seal_receipts(receipts: list[dict[str, object]], path: Path) -> None:
    for receipt in receipts:
        draft = {**receipt, "verdict": "PENDING"}
        judges.issue_receipt(draft, path)


def test_router_uses_deterministic_proof_when_it_is_complete() -> None:
    assert judges.route_tier({"deterministic_complete": True}) == "J0"


def test_cli_defaults_to_configured_private_state_root(tmp_path: Path) -> None:
    state_root = tmp_path / "private-state"
    env = {
        **os.environ,
        "AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT": str(state_root),
    }
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "snippets" / "judge_governance.py"),
            "begin",
            "--task-id",
            "synthetic-private-state-test",
            "--task-class",
            "coding",
            "--signals",
            "deterministic_complete",
            "--repository-id",
            "synthetic-repository",
            "--work-anchor",
            "synthetic-work-anchor",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    issuance = state_root / "governance" / "judge_issuance.jsonl"
    assert issuance.is_file()
    payload = json.loads(issuance.read_text(encoding="utf-8"))
    assert payload["repository_id"] == "synthetic-repository"


def test_router_uses_j2_for_two_independent_uncertainty_signals() -> None:
    assert judges.route_tier({"multi_scope": True, "missing_oracle": True}) == "J2"


def test_router_does_not_double_count_correlated_signals() -> None:
    assert (
        judges.route_tier({"multi_scope": True, "concurrent_dirty_state": True}) == "J1"
    )


def test_router_uses_direct_j2_signal_for_observed_regression() -> None:
    assert judges.route_tier({"prior_regression": True}) == "J2"


def test_router_rejects_deterministic_complete_with_unresolved_risk() -> None:
    with pytest.raises(ValueError, match="deterministic_complete"):
        judges.route_tier({"deterministic_complete": True, "missing_oracle": True})


@pytest.mark.parametrize("signal", sorted(judges.HARD_J3_SIGNALS))
def test_router_hard_escalates_j3(signal: str) -> None:
    assert judges.route_tier({signal: True}) == "J3"


def test_representative_routing_eval_corpus() -> None:
    cases = (ROOT / "evals" / "agent_system" / "routing_cases.jsonl").read_text(
        encoding="utf-8"
    )
    for raw in cases.splitlines():
        case = json.loads(raw)
        assert judges.route_tier(case["signals"]) == case["expected_tier"], case[
            "case_id"
        ]


def test_unknown_signal_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown signal"):
        judges.route_tier({"production_mutatoin": True})


def test_schema_version_and_typed_timestamps_are_enforced() -> None:
    receipt = judges.new_receipt(
        task_id="bad-schema", task_class="coding", signals={}, actual_tier="J1"
    )
    receipt.update(
        {
            "schema_version": "garbage",
            "deterministic_evidence": [{**proof(), "observed_at": "not-a-time"}],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    errors = judges.validate_receipt(receipt)
    assert any("schema_version" in error for error in errors)
    assert any("deterministic_evidence" in error for error in errors)


def test_single_j2_signal_stays_j1_and_two_reach_j2() -> None:
    assert judges.route_tier({"multi_scope": True}) == "J1"
    assert judges.route_tier({"multi_scope": True, "missing_oracle": True}) == "J2"


def test_budget_failure_cannot_pass() -> None:
    receipt = judges.new_receipt(
        task_id="budget-case",
        task_class="research",
        signals={},
        actual_tier="J1",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof("citations")],
            "judges": [judge("one")],
            "verdict": "PASS",
            "failure_code": "BUDGET_EXCEEDED",
        }
    )
    assert "cannot PASS" in " ".join(judges.validate_receipt(receipt))


def test_final_receipt_rejects_pending_and_untyped_evidence() -> None:
    receipt = judges.new_receipt(
        task_id="draft", task_class="coding", signals={"deterministic_complete": True}
    )
    receipt["deterministic_evidence"] = [None]
    errors = judges.validate_receipt(receipt)
    assert any("PENDING" in error for error in errors)
    assert any("typed proof" in error for error in errors)


def test_owner_denial_cannot_approve_j3() -> None:
    receipt = judges.new_receipt(
        task_id="owner-gate",
        task_class="coding",
        signals={"high_impact_production_action": True},
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one"), judge("two")],
            "owner_approval": {
                "approver": "Bhanu",
                "decision": "denied",
                "scope": "production migration",
                "approved_at": "2026-08-13T12:00:00Z",
            },
            "verdict": "PASS",
        }
    )
    assert judges.gate_verdict(receipt) == "HOLD"
    assert judges.validate_receipt(receipt)


def test_j3_block_is_valid_without_owner_approval() -> None:
    receipt = judges.new_receipt(
        task_id="blocked-owner-gate",
        task_class="coding",
        signals={"security_boundary_action": True},
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one", "BLOCK"), judge("two", "BLOCK")],
            "verdict": "BLOCK",
        }
    )
    assert judges.gate_verdict(receipt) == "BLOCK"
    assert judges.validate_receipt(receipt) == []


def test_j3_owner_approval_timestamp_must_be_parseable() -> None:
    receipt = judges.new_receipt(
        task_id="bad-approval-time",
        task_class="coding",
        signals={"high_impact_production_action": True},
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one"), judge("two")],
            "owner_approval": {
                "approver": "owner",
                "decision": "approved",
                "scope": "this action",
                "approved_at": "not-a-time",
            },
            "verdict": "PASS",
        }
    )
    assert any("owner approval" in error for error in judges.validate_receipt(receipt))


def test_unknown_failure_code_fails_closed() -> None:
    receipt = judges.new_receipt(
        task_id="timeout", task_class="research", signals={}, actual_tier="J1"
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "failure_code": "JUDGE_TIMEOUT",
            "verdict": "PASS",
        }
    )
    assert judges.gate_verdict(receipt) == "ABSTAIN"
    assert judges.validate_receipt(receipt)


def test_j2_normally_requires_one_specialist_judge() -> None:
    receipt = judges.new_receipt(
        task_id="specialist-review",
        task_class="coding",
        signals={"missing_oracle": True},
        actual_tier="J2",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("evidence-specialist")],
            "verdict": "PASS",
        }
    )
    assert judges.validate_receipt(receipt) == []


def test_j2_prior_regression_requires_two_independent_same_family_judges() -> None:
    receipt = judges.new_receipt(
        task_id="dual-review",
        task_class="coding",
        signals={"prior_regression": True},
        actual_tier="J2",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [
                {**judge("architecture"), "provider": "same"},
                {**judge("evals"), "provider": "same"},
            ],
            "verdict": "PASS",
        }
    )
    assert judges.validate_receipt(receipt) == []


def test_gate_cannot_average_away_a_blocking_judge() -> None:
    receipt = judges.new_receipt(
        task_id="blocked-dual",
        task_class="coding",
        signals={"multi_scope": True, "missing_oracle": True},
        actual_tier="J2",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [
                judge("one"),
                judge("two", "BLOCK"),
            ],
            "verdict": "PASS",
        }
    )
    assert judges.gate_verdict(receipt) == "BLOCK"
    assert any(
        "deterministic gate" in error for error in judges.validate_receipt(receipt)
    )


def test_unregistered_judge_purpose_and_rubric_fail_closed() -> None:
    receipt = judges.new_receipt(
        task_id="fake-judge", task_class="coding", signals={}, actual_tier="J1"
    )
    fake = judge("invented")
    fake.update({"purpose": "universal_genius", "rubric_version": "made-up"})
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [fake],
            "verdict": "PASS",
        }
    )
    errors = judges.validate_receipt(receipt)
    assert any("registered purpose" in error for error in errors)
    assert any("missing required judge purpose" in error for error in errors)


def test_sampling_is_total_for_j3_disagreement_overrides_and_policy_changes() -> None:
    base = judges.new_receipt(
        task_id="sample", task_class="coding", signals={}, actual_tier="J1"
    )
    for update in (
        {"actual_tier": "J3"},
        {"disagreement": True},
        {"owner_override": {"decision": "override", "reason": "owner decision"}},
        {"policy_change": {"kind": "revision", "change_id": "policy-1.1"}},
    ):
        receipt = {**base, **update}
        selected, _reason = judges.audit_selection(receipt)
        assert selected


def test_ordinary_sampling_stays_shadow_until_owner_sets_statistical_targets() -> None:
    receipt = judges.new_receipt(
        task_id="shadow-sample", task_class="coding", signals={}, actual_tier="J1"
    )
    assert receipt["sampling"]["selected"] is False
    assert receipt["sampling"]["selection_state"] == "shadow_pending_parameters"
    assert "rate" not in receipt["sampling"]


def test_retry_and_task_rename_cannot_change_sampling_unit() -> None:
    original = judges.new_receipt(
        task_id="original-name", task_class="coding", signals={}, actual_tier="J1"
    )
    retry = judges.new_receipt(
        task_id="renamed-task",
        task_class="coding",
        signals={},
        actual_tier="J1",
        retry_of=original,
    )
    assert original["root_episode_id"] == retry["root_episode_id"]
    assert original["sampling"]["sampling_unit"] == retry["sampling"]["sampling_unit"]


def test_retry_cannot_change_policy_or_task_class() -> None:
    original = judges.new_receipt(
        task_id="original", task_class="coding", signals={}, actual_tier="J1"
    )
    with pytest.raises(ValueError, match="task_class"):
        judges.new_receipt(
            task_id="changed-class",
            task_class="research",
            signals={},
            actual_tier="J1",
            retry_of=original,
        )
    changed_policy = {**original, "policy_version": "1.0.0"}
    with pytest.raises(ValueError, match="policy_version"):
        judges.new_receipt(
            task_id="changed-policy",
            task_class="coding",
            signals={},
            actual_tier="J1",
            retry_of=changed_policy,
        )
    with pytest.raises(ValueError, match="work_anchor"):
        judges.new_receipt(
            task_id="changed-anchor",
            task_class="coding",
            signals={},
            actual_tier="J1",
            retry_of=original,
            work_anchor="different",
        )


@pytest.mark.parametrize(
    ("tolerable_error", "confidence", "expected"),
    [(0.10, 0.95, 29), (0.05, 0.95, 59), (0.02, 0.95, 149)],
)
def test_sample_size_is_derived_from_error_tolerance_and_confidence(
    tolerable_error: float, confidence: float, expected: int
) -> None:
    assert (
        judges.required_zero_failure_sample_size(tolerable_error, confidence)
        == expected
    )


def test_active_policy_is_a_versioned_shadow_snapshot_without_static_rates() -> None:
    pointer = json.loads(
        (ROOT / "config" / "judge_policy.json").read_text(encoding="utf-8")
    )
    policy = judges.load_policy()
    assert pointer["active_policy_version"] == policy["policy_version"]
    assert policy["enforcement_mode"] == "shadow"
    assert "ordinary_audit_rates" not in policy
    sampling = policy["statistical_sampling"]
    assert sampling["status"] == "pending_owner_tolerances"
    assert sampling["confidence"] is None
    assert all(
        tolerance is None
        for by_class in sampling["tolerable_error_rates"].values()
        for tolerance in by_class.values()
    )
    assert policy["invocation_coverage"]["status"].startswith("pending_")
    registry = judges.load_judge_registry(
        policy["judge_requirements"]["registry_version"]
    )
    assert registry["enforcement_mode"] == "shadow"
    assert all(
        purpose["calibration_status"] == "shadow"
        for purpose in registry["purposes"].values()
    )


def test_policy_version_cannot_escape_the_snapshot_directory() -> None:
    with pytest.raises(ValueError, match="semantic version"):
        judges.load_policy(version="../../outside")


def test_dynamic_sampling_selects_a_derived_count_without_replacement() -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.95
    policy["statistical_sampling"]["tolerable_error_rates"]["J1"]["coding"] = 0.10
    receipts = [
        judges.new_receipt(
            task_id=f"ordinary-{index}",
            task_class="coding",
            signals={},
            actual_tier="J1",
        )
        for index in range(40)
    ]
    research = judges.new_receipt(
        task_id="research-excluded",
        task_class="research",
        signals={},
        actual_tier="J1",
    )
    retry = judges.new_receipt(
        task_id="ordinary-retry",
        task_class="coding",
        signals={},
        actual_tier="J1",
        retry_of=receipts[0],
    )
    selected = judges.plan_ordinary_audits(
        [*receipts, research, retry],
        tier="J1",
        task_class="coding",
        policy=policy,
    )
    assert len(selected) == 29
    assert len(selected) == len(set(selected))
    assert research["root_episode_id"] not in selected


def test_only_terminal_retry_attempt_enters_a_sampling_stratum() -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.50
    policy["statistical_sampling"]["tolerable_error_rates"]["J1"]["coding"] = 0.50
    policy["statistical_sampling"]["tolerable_error_rates"]["J2"]["coding"] = 0.50
    original = judges.new_receipt(
        task_id="attempt-one", task_class="coding", signals={}, actual_tier="J1"
    )
    retry = judges.new_receipt(
        task_id="attempt-two",
        task_class="coding",
        signals={"prior_regression": True},
        actual_tier="J2",
        retry_of=original,
    )

    assert (
        judges.plan_ordinary_audits(
            [original, retry], tier="J1", task_class="coding", policy=policy
        )
        == []
    )
    assert judges.plan_ordinary_audits(
        [original, retry], tier="J2", task_class="coding", policy=policy
    ) == [original["root_episode_id"]]


def test_root_with_any_mandatory_attempt_never_enters_ordinary_sampling() -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.50
    policy["statistical_sampling"]["tolerable_error_rates"]["J1"]["coding"] = 0.50
    original = judges.new_receipt(
        task_id="j3-attempt",
        task_class="coding",
        signals={"high_impact_production_action": True},
        actual_tier="J3",
    )
    retry = judges.new_receipt(
        task_id="safe-redesign",
        task_class="coding",
        signals={},
        actual_tier="J1",
        retry_of=original,
    )

    assert (
        judges.plan_ordinary_audits(
            [original, retry], tier="J1", task_class="coding", policy=policy
        )
        == []
    )


def test_ledger_enforces_dynamic_batch_selection(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.95
    policy["statistical_sampling"]["tolerable_error_rates"]["J1"]["coding"] = 0.10
    monkeypatch.setattr(judges, "load_policy", lambda *args, **kwargs: policy)
    receipts = [
        judges.new_receipt(
            task_id=f"batch-{index}",
            task_class="coding",
            signals={},
            actual_tier="J1",
        )
        for index in range(40)
    ]
    for receipt in receipts:
        receipt.update(
            {
                "deterministic_evidence": [proof()],
                "judges": [judge("one")],
                "verdict": "PASS",
            }
        )
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(
        "\n".join(json.dumps(receipt) for receipt in receipts) + "\n",
        encoding="utf-8",
    )

    assert judges.audit_ledger(ledger)["sampled_audits_due"] == 29


def test_adding_risk_never_lowers_tier_or_mandatory_audit() -> None:
    baseline = judges.new_receipt(task_id="monotonic", task_class="coding", signals={})
    elevated = judges.new_receipt(
        task_id="monotonic",
        task_class="coding",
        signals={"high_impact_production_action": True},
    )
    assert judges.TIERS.index(elevated["actual_tier"]) >= judges.TIERS.index(
        baseline["actual_tier"]
    )
    assert int(elevated["sampling"]["selected"]) >= int(
        baseline["sampling"]["selected"]
    )


def test_sampling_is_bound_to_immutable_policy_snapshot() -> None:
    receipt = judges.new_receipt(
        task_id="policy-snapshot", task_class="research", signals={}
    )
    assert receipt["sampling"]["policy_hash"] == judges.policy_hash(
        judges.load_policy(version=receipt["policy_version"])
    )
    receipt["policy_version"] = "missing-version"
    assert any(
        "sampling policy unavailable" in error
        for error in judges.validate_receipt(receipt)
    )


def test_policy_review_derives_findings_from_the_ledger(tmp_path: Path) -> None:
    receipt = judges.new_receipt(
        task_id="material-miss",
        task_class="coding",
        signals={"prior_regression": True},
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one"), judge("two")],
            "verdict": "PASS",
            "audit": audit(
                "material_miss", routing_correct=True, execution_correct=False
            ),
        }
    )
    receipt["sampling"] = judges.sampling_record(receipt)
    ledger = tmp_path / "ledger.jsonl"
    issuance = tmp_path / "issuance.jsonl"
    seal_receipts([receipt], issuance)
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J2",
        signals={"prior_regression": True},
        issuance_path=issuance,
    )
    assert review["action"] == "owner_review"
    assert review["recommended_tier"] == "J3"
    assert review["evidence"]["material_misses"] == 1
    assert review["automatic_change"] is False


def test_policy_review_promotes_on_typed_material_outcome(tmp_path: Path) -> None:
    receipt = judges.new_receipt(
        task_id="later-miss",
        task_class="research",
        signals={},
        actual_tier="J1",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
            "outcome": {
                "status": "material_miss",
                "observed_at": "2026-08-14T12:00:00Z",
                "evidence_refs": ["sha256:abc123"],
            },
        }
    )
    ledger = tmp_path / "ledger.jsonl"
    issuance = tmp_path / "issuance.jsonl"
    seal_receipts([receipt], issuance)
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J1",
        signals={},
        issuance_path=issuance,
    )
    assert review["action"] == "owner_review"
    assert review["recommended_tier"] == "J2"
    assert review["evidence"]["outcome_material_misses"] == 1


def test_later_append_only_outcome_event_promotes_policy_review(tmp_path: Path) -> None:
    issuance = tmp_path / "issuance.jsonl"
    ledger = tmp_path / "ledger.jsonl"
    outcomes = tmp_path / "outcomes.jsonl"
    receipt = judges.new_receipt(
        task_id="later-event",
        task_class="research",
        signals={},
        actual_tier="J1",
    )
    judges.issue_receipt(receipt, issuance)
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    judges.complete_receipt(receipt, ledger_path=ledger, issuance_path=issuance)
    judges.record_outcome(
        root_episode_id=receipt["root_episode_id"],
        status="material_miss",
        evidence_refs=["sha256:abc123"],
        observed_at="2026-08-14T12:00:00Z",
        outcome_path=outcomes,
        issuance_path=issuance,
    )

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J1",
        signals={},
        issuance_path=issuance,
        outcome_path=outcomes,
    )
    assert review["recommended_tier"] == "J2"
    assert review["evidence"]["outcome_material_misses"] == 1


def test_policy_review_holds_when_statistical_targets_are_unset(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text("", encoding="utf-8")
    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J2",
        signals={"prior_regression": True},
        issuance_path=tmp_path / "issuance.jsonl",
    )
    assert review["action"] == "hold"
    assert review["reason"] == "insufficient_evidence"
    assert review["automatic_change"] is False


def test_audit_finding_must_match_routing_and_execution_booleans() -> None:
    receipt = judges.new_receipt(
        task_id="contradictory-audit",
        task_class="coding",
        signals={},
        actual_tier="J1",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
            "audit": audit("none", execution_correct=False),
        }
    )
    assert not judges.audit_is_complete(receipt)


def test_policy_review_uses_only_the_current_tier(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.95
    for task_class in judges.TASK_CLASSES:
        policy["statistical_sampling"]["tolerable_error_rates"]["J2"][task_class] = 0.10
    monkeypatch.setattr(judges, "load_policy", lambda *args, **kwargs: policy)
    other_tier = judges.new_receipt(
        task_id="wrong-tier",
        task_class="coding",
        signals={},
        actual_tier="J1",
    )
    other_tier.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
            "audit": audit(),
        }
    )
    ledger = tmp_path / "ledger.jsonl"
    issuance = tmp_path / "issuance.jsonl"
    seal_receipts([other_tier], issuance)
    ledger.write_text(json.dumps(other_tier) + "\n", encoding="utf-8")

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J2",
        signals={"multi_scope": True},
        issuance_path=issuance,
    )
    assert review["action"] == "hold"
    assert review["evidence"]["audited_receipts"] == 0


def test_policy_review_recommends_demotion_only_after_zero_failure_targets(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.95
    for task_class in judges.TASK_CLASSES:
        policy["statistical_sampling"]["tolerable_error_rates"]["J2"][task_class] = 0.10
    monkeypatch.setattr(judges, "load_policy", lambda *args, **kwargs: policy)
    receipts = []
    for task_class in sorted(judges.TASK_CLASSES):
        for index in range(29):
            receipt = judges.new_receipt(
                task_id=f"{task_class}-{index}",
                task_class=task_class,
                signals={"multi_scope": True},
                actual_tier="J2",
            )
            receipt.update(
                {
                    "deterministic_evidence": [proof()],
                    "judges": [judge("one")],
                    "verdict": "PASS",
                    "audit": audit(),
                }
            )
            receipts.append(receipt)
    ledger = tmp_path / "ledger.jsonl"
    issuance = tmp_path / "issuance.jsonl"
    seal_receipts(receipts, issuance)
    ledger.write_text(
        "\n".join(json.dumps(receipt) for receipt in receipts) + "\n",
        encoding="utf-8",
    )

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J2",
        signals={"multi_scope": True},
        issuance_path=issuance,
    )
    assert review["action"] == "owner_review"
    assert review["recommended_tier"] == "J1"
    assert review["reason"] == "zero_failure_targets_met"
    assert review["automatic_change"] is False


def test_invalid_receipts_cannot_support_demotion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = judges.load_policy()
    policy["statistical_sampling"]["confidence"] = 0.50
    for task_class in judges.TASK_CLASSES:
        policy["statistical_sampling"]["tolerable_error_rates"]["J2"][task_class] = 0.50
    monkeypatch.setattr(judges, "load_policy", lambda *args, **kwargs: policy)
    receipts = []
    for task_class in sorted(judges.TASK_CLASSES):
        receipt = judges.new_receipt(
            task_id=f"invalid-{task_class}",
            task_class=task_class,
            signals={"multi_scope": True},
            actual_tier="J2",
        )
        receipt.update({"verdict": "PASS", "audit": audit()})
        receipts.append(receipt)
    ledger = tmp_path / "ledger.jsonl"
    issuance = tmp_path / "issuance.jsonl"
    seal_receipts(receipts, issuance)
    ledger.write_text(
        "\n".join(json.dumps(receipt) for receipt in receipts) + "\n",
        encoding="utf-8",
    )

    review = judges.review_policy_change(
        ledger_path=ledger,
        current_tier="J2",
        signals={"multi_scope": True},
        issuance_path=issuance,
    )
    assert review["action"] == "hold"
    assert review["reason"] == "invalid_ledger_evidence"
    assert review["evidence"]["invalid_receipts"] == 2


def test_owner_can_explicitly_request_a_second_judge() -> None:
    receipt = judges.new_receipt(
        task_id="owner-second",
        task_class="research",
        signals={"owner_requested_second_judge": True},
    )
    assert receipt["recommended_tier"] == "J2"
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    assert any("at least 2" in error for error in judges.validate_receipt(receipt))


def test_historical_policy_receipt_remains_valid(tmp_path: Path) -> None:
    historical = {
        "schema_version": "1.0.0",
        "policy_version": "1.0.0",
        "task_id": "synthetic-historical-policy-fixture",
        "task_class": "coding",
        "signals": {"missing_oracle": True, "multi_scope": True},
        "recommended_tier": "J2",
        "actual_tier": "J2",
        "deterministic_evidence": [proof("synthetic-check")],
        "judges": [judge("synthetic-one"), judge("synthetic-two")],
        "verdict": "PASS",
        "disagreement": False,
        "owner_override": None,
        "owner_approval": None,
        "policy_change": None,
        "failure_code": None,
        "outcome": None,
        "audit": None,
    }
    historical["sampling"] = judges.sampling_record(historical)
    assert historical["policy_version"] == "1.0.0"
    assert judges.validate_receipt(historical) == []
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(historical) + "\n", encoding="utf-8")
    report = judges.audit_ledger(ledger)
    assert report["receipts"] >= 1
    assert report["routing_failures"] == 0
    assert report["execution_failures"] == 0


def test_definition_chain_rejects_every_downstream_override(tmp_path: Path) -> None:
    root = tmp_path / "DEFINITIONS.md"
    child = tmp_path / "project" / "DEFINITIONS.md"
    child.parent.mkdir()
    root.write_text(
        "# Definitions\n\n**Scope:** global\n**Owner:** system\n**Inherits:** none\n\n"
        "## Judge\n\n**Definition.** Applies a rubric.\n",
        encoding="utf-8",
    )
    child.write_text(
        "# Definitions\n\n**Scope:** project\n**Owner:** project\n"
        "**Inherits:** ../DEFINITIONS.md\n\n"
        "## Judge\n\n**Definition.** A different meaning.\n",
        encoding="utf-8",
    )
    errors = definitions.validate_chain(root, [child])
    assert any("override" in error.lower() for error in errors)


def test_definition_parser_sees_legacy_bold_bullet_terms(tmp_path: Path) -> None:
    path = tmp_path / "DEFINITIONS.md"
    path.write_text(
        "# Definitions\n\n## Domain enums\n\n"
        "- **Verdict** — `buy`, `hold`, or `pass`.\n",
        encoding="utf-8",
    )
    _metadata, terms = definitions.parse_document(path)
    assert "Verdict" in terms


def test_sibling_definition_files_are_not_ancestors(tmp_path: Path) -> None:
    root = tmp_path / "DEFINITIONS.md"
    root.write_text(
        "# Definitions\n\n**Scope:** global\n**Owner:** system\n**Inherits:** none\n\n"
        "## Judge\n\n**Definition.** Applies a rubric.\n",
        encoding="utf-8",
    )
    siblings: list[Path] = []
    for name in ("one", "two"):
        path = tmp_path / name / "DEFINITIONS.md"
        path.parent.mkdir()
        path.write_text(
            "# Definitions\n\n**Scope:** project\n**Owner:** owner\n"
            "**Inherits:** ../DEFINITIONS.md\n\n"
            "- **Local term** — scoped meaning.\n",
            encoding="utf-8",
        )
        siblings.append(path)
    assert definitions.validate_chain(root, siblings) == []


def test_progressive_definition_discovery_loads_only_local_chain(
    tmp_path: Path,
) -> None:
    root = tmp_path / "DEFINITIONS.md"
    shared = tmp_path / "shared" / "DEFINITIONS.md"
    local = tmp_path / "workspace" / "project" / "DEFINITIONS.md"
    unrelated = tmp_path / "workspace" / "DEFINITIONS.md"
    shared.parent.mkdir()
    local.parent.mkdir(parents=True)
    root.write_text(
        "# Definitions\n\n**Scope:** global\n**Owner:** system\n**Inherits:** none\n",
        encoding="utf-8",
    )
    shared.write_text(
        "# Definitions\n\n**Scope:** cross-project\n**Owner:** shared\n"
        f"**Inherits:** {root}\n",
        encoding="utf-8",
    )
    local.write_text(
        "# Definitions\n\n**Scope:** project\n**Owner:** project\n"
        f"**Inherits:** {shared}\n",
        encoding="utf-8",
    )
    unrelated.write_text(
        "# Definitions\n\n**Scope:** project\n**Owner:** unrelated\n"
        f"**Inherits:** {root}\n",
        encoding="utf-8",
    )
    chain = definitions.discover_chain(
        local.parent / "src" / "feature.py", global_file=root
    )
    assert chain == [root.resolve(), shared.resolve(), local.resolve()]
    assert unrelated.resolve() not in chain


def test_definition_lifecycle_holds_override_until_owner_file_is_known(
    tmp_path: Path,
) -> None:
    root = tmp_path / "DEFINITIONS.md"
    root.write_text(
        "# Definitions\n\n**Scope:** global\n**Owner:** system\n**Inherits:** none\n",
        encoding="utf-8",
    )
    recommendation = definitions.recommend_definition_change(
        real_uses=12,
        project_count=3,
        identical_meaning=True,
        override_requests=1,
        owner_ratified=True,
        current_scope="global",
        current_maturity="ratified",
        current_definition_file=root,
        owning_definition_file=None,
    )
    assert recommendation["action"] == "hold"
    assert recommendation["reason"] == "owning_definition_file_required"


def test_definition_demotion_requires_strict_descendant_owner(tmp_path: Path) -> None:
    root = tmp_path / "DEFINITIONS.md"
    child = tmp_path / "project" / "DEFINITIONS.md"
    child.parent.mkdir()
    root.write_text(
        "# Definitions\n\n**Scope:** global\n**Owner:** system\n**Inherits:** none\n",
        encoding="utf-8",
    )
    child.write_text(
        "# Definitions\n\n**Scope:** project\n**Owner:** project\n"
        f"**Inherits:** {root}\n",
        encoding="utf-8",
    )
    common = {
        "real_uses": 12,
        "project_count": 3,
        "identical_meaning": True,
        "override_requests": 1,
        "owner_ratified": True,
        "current_scope": "global",
        "current_maturity": "ratified",
    }
    valid = definitions.recommend_definition_change(
        **common,
        current_definition_file=root,
        owning_definition_file=child,
    )
    equal = definitions.recommend_definition_change(
        **common,
        current_definition_file=root,
        owning_definition_file=root,
    )
    broader = definitions.recommend_definition_change(
        **common,
        current_definition_file=child,
        owning_definition_file=root,
    )
    assert valid["action"] == "demote_scope"
    assert valid["target_owner"] == "project"
    assert equal["action"] == "hold"
    assert broader["action"] == "hold"


def test_rollout_status_keeps_unresolved_repositories_visible(tmp_path: Path) -> None:
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    config = tmp_path / "rollout.json"
    config.write_text(
        json.dumps({"repositories": {"one": {"disposition": "adopt_now"}}}),
        encoding="utf-8",
    )
    rows = judges.rollout_status(tmp_path, config)
    assert rows["one"]["disposition"] == "adopt_now"
    assert rows["two"]["reminder"] is True


def test_rollout_cannot_claim_active_before_activation_prerequisites(
    tmp_path: Path,
) -> None:
    (tmp_path / "one").mkdir()
    config = tmp_path / "rollout.json"
    config.write_text(
        json.dumps({"repositories": {"one": {"mode": "active"}}}),
        encoding="utf-8",
    )
    row = judges.rollout_status(tmp_path, config)["one"]
    assert row["effective_mode"] == "blocked"
    assert "statistical_targets_not_ratified" in row["activation_blockers"]
    assert "judge_purposes_not_calibrated" in row["activation_blockers"]
    assert "verifier_backed_evidence_records_missing" in row["activation_blockers"]


def test_activation_validates_parameters_and_readiness_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = judges.load_policy()
    policy["enforcement_mode"] = "active"
    policy["statistical_sampling"]["status"] = "ratified"
    policy["invocation_coverage"]["active_blocking_allowed"] = True
    policy["evidence_verification"]["active_blocking_allowed"] = True
    registry = judges.load_judge_registry("1.1.0")
    for purpose in registry["purposes"].values():
        purpose["calibration_status"] = "calibrated"
    monkeypatch.setattr(judges, "load_policy", lambda *args, **kwargs: policy)
    monkeypatch.setattr(judges, "load_judge_registry", lambda *args, **kwargs: registry)

    blockers = judges._activation_blockers()
    assert "statistical_contract_invalid" in blockers
    assert "task_population_frame_artifact_invalid" in blockers
    assert "evidence_verifier_artifact_invalid" in blockers


def test_repository_activation_check_is_nonblocking_for_shadow() -> None:
    assert judges.activation_check(".gemini") == []


def test_active_rollout_requires_nonempty_ledger(tmp_path: Path) -> None:
    missing = judges.audit_ledger(tmp_path / "missing.jsonl")
    assert missing["ledger_missing"] == 1
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    assert judges.audit_ledger(empty)["empty_ledger"] == 1


def test_exclusive_issuance_seals_terminal_receipt_identity(tmp_path: Path) -> None:
    issuance = tmp_path / "issuance.jsonl"
    ledger = tmp_path / "ledger.jsonl"
    receipt = judges.new_receipt(
        task_id="sealed",
        task_class="coding",
        signals={},
        actual_tier="J1",
        repository_id="repo",
        work_anchor="work-1",
    )
    judges.issue_receipt(receipt, issuance)
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    judges.complete_receipt(receipt, ledger_path=ledger, issuance_path=issuance)
    judges.complete_receipt(receipt, ledger_path=ledger, issuance_path=issuance)
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1
    assert judges.audit_ledger(ledger, issuance)["issuance_failures"] == 0

    tampered = {**receipt, "work_anchor": "rank-shopping"}
    tampered_ledger = tmp_path / "tampered.jsonl"
    tampered_ledger.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
    assert judges.audit_ledger(tampered_ledger, issuance)["issuance_failures"] == 1


def test_post_issuance_mandatory_escalation_can_complete(tmp_path: Path) -> None:
    issuance = tmp_path / "issuance.jsonl"
    ledger = tmp_path / "ledger.jsonl"
    receipt = judges.new_receipt(
        task_id="escalated",
        task_class="coding",
        signals={},
        actual_tier="J1",
    )
    judges.issue_receipt(receipt, issuance)
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "disagreement": True,
            "verdict": "HOLD",
        }
    )
    receipt["sampling"] = judges.sampling_record(receipt)
    judges.complete_receipt(receipt, ledger_path=ledger, issuance_path=issuance)
    assert judges.audit_ledger(ledger, issuance)["issuance_failures"] == 0


def test_unissued_current_receipt_fails_ledger_audit(tmp_path: Path) -> None:
    receipt = judges.new_receipt(
        task_id="unissued", task_class="research", signals={}, actual_tier="J1"
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    assert (
        judges.audit_ledger(ledger, tmp_path / "missing.jsonl")["issuance_failures"]
        == 1
    )


def test_pending_and_conflicting_issuances_are_visible(tmp_path: Path) -> None:
    issuance = tmp_path / "issuance.jsonl"
    first = judges.new_receipt(
        task_id="first",
        task_class="coding",
        signals={},
        repository_id="repo",
        work_anchor="same-work",
    )
    second = judges.new_receipt(
        task_id="second",
        task_class="coding",
        signals={},
        repository_id="repo",
        work_anchor="same-work",
    )
    judges.issue_receipt(first, issuance)
    judges.issue_receipt(second, issuance)
    report = judges.audit_ledger(tmp_path / "missing-ledger.jsonl", issuance)
    assert report["pending_issuances"] == 2
    assert report["issuance_anchor_conflicts"] == 1
    scoped = judges.audit_ledger(
        tmp_path / "missing-ledger.jsonl",
        issuance,
        repository_id="different-repo",
    )
    assert scoped["pending_issuances"] == 0
    assert scoped["issuance_anchor_conflicts"] == 0


def test_ledger_rejects_duplicate_episode_ids(tmp_path: Path) -> None:
    receipt = judges.new_receipt(
        task_id="duplicate", task_class="coding", signals={}, actual_tier="J1"
    )
    receipt.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(
        json.dumps(receipt) + "\n" + json.dumps(receipt) + "\n",
        encoding="utf-8",
    )
    assert judges.audit_ledger(ledger)["lineage_failures"] > 0


def test_ledger_rejects_orphan_retry(tmp_path: Path) -> None:
    original = judges.new_receipt(
        task_id="original", task_class="coding", signals={}, actual_tier="J1"
    )
    retry = judges.new_receipt(
        task_id="orphan",
        task_class="coding",
        signals={},
        actual_tier="J1",
        retry_of=original,
    )
    retry.update(
        {
            "deterministic_evidence": [proof()],
            "judges": [judge("one")],
            "verdict": "PASS",
        }
    )
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(retry) + "\n", encoding="utf-8")
    assert judges.audit_ledger(ledger)["lineage_failures"] > 0


def test_ledger_audit_separates_routing_from_execution_and_sampling(
    tmp_path: Path,
) -> None:
    receipt = judges.new_receipt(
        task_id="boundary",
        task_class="coding",
        signals={"multi_scope": True, "missing_oracle": True},
        actual_tier="J2",
    )
    receipt.update(
        {
            "deterministic_evidence": [proof("targeted-tests")],
            "judges": [
                judge("one"),
            ],
            "verdict": "PASS",
            "policy_change": {"kind": "revision", "change_id": "policy-1.1"},
        }
    )
    # Recompute after the mandatory policy-change flag is known.
    receipt["sampling"] = judges.sampling_record(receipt)
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    report = judges.audit_ledger(ledger)
    assert report["routing_failures"] == 0
    assert report["execution_failures"] == 0
    assert report["sampled_audits_due"] == 1

    receipt["audit"] = audit()
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    assert judges.audit_ledger(ledger)["sampled_audits_due"] == 0

    receipt["audit"]["completed_at"] = None
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    assert judges.audit_ledger(ledger)["sampled_audits_due"] == 1
    receipt["audit"]["completed_at"] = "2026-08-13T12:00:00Z"

    del receipt["audit"]["rubric_version"]
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    assert judges.audit_ledger(ledger)["sampled_audits_due"] == 1
    receipt["audit"]["rubric_version"] = "judge-audit-1.1.0"

    receipt["audit"]["routing_correct"] = False
    receipt["audit"]["finding"] = "routing_miss"
    ledger.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    failed_report = judges.audit_ledger(ledger)
    assert failed_report["sampled_audits_due"] == 0
    assert failed_report["routing_failures"] == 1
