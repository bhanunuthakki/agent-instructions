"""Deterministic routing, receipts, sampling, and adaptation controls for J0-J3."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "judge_policy.json"
POLICY_DIR = ROOT / "config" / "judge_policies"
JUDGE_REGISTRY_DIR = ROOT / "config" / "judge_registries"
ROLLOUT_PATH = ROOT / "config" / "judge_rollout.json"
ISSUANCE_PATH = ROOT / "governance" / "judge_issuance.jsonl"
OUTCOME_PATH = ROOT / "governance" / "judge_outcomes.jsonl"
TIERS = ("J0", "J1", "J2", "J3")
FINAL_VERDICTS = {"PASS", "BLOCK", "HOLD", "ABSTAIN"}
TASK_CLASSES = {"coding", "research"}

LEGACY_HARD_J3_SIGNALS = {
    "irreversible",
    "production_mutation",
    "security_boundary",
    "external_publication",
    "capital_action",
    "legal_action",
    "owner_requested_j3",
    "unresolved_j2_disagreement",
    "low_judge_calibration",
}
LEGACY_J2_SIGNALS = {
    "multi_scope",
    "ambiguous_requirements",
    "conflicting_evidence",
    "missing_oracle",
    "unfamiliar_dependency",
    "concurrent_dirty_state",
    "prior_regression",
    "material_cost_or_latency",
}
HARD_J3_SIGNALS = {
    "irreversible_side_effect",
    "high_impact_production_action",
    "security_boundary_action",
    "external_publication_action",
    "capital_action",
    "legal_action",
    "owner_requested_j3",
    "unresolved_j2_disagreement",
}
J2_SIGNAL_GROUPS = {
    "material_ambiguity": "evidence_uncertainty",
    "conflicting_evidence": "evidence_uncertainty",
    "missing_oracle": "evidence_uncertainty",
    "multi_scope": "scope_state",
    "concurrent_dirty_state": "scope_state",
    "unfamiliar_dependency": "novelty",
    "prior_regression": "observed_failure",
    "material_cost_or_latency": "economics",
    "owner_requested_second_judge": "governance",
}
J2_SIGNALS = set(J2_SIGNAL_GROUPS)
ALL_SIGNALS = HARD_J3_SIGNALS | J2_SIGNALS | {"deterministic_complete"}
FAILURE_CODES = {
    "BUDGET_EXCEEDED",
    "INSUFFICIENT_EVIDENCE",
    "JUDGE_SCHEMA_FAILURE",
    "JUDGE_TIMEOUT",
    "PROVIDER_FAILURE",
    "SETUP_FAILURE",
}
OUTCOME_STATUSES = {"success", "material_miss", "critical_miss", "unknown"}


def load_policy(
    path: Path = POLICY_PATH, *, version: str | None = None
) -> dict[str, Any]:
    if version is None:
        pointer = json.loads(path.read_text(encoding="utf-8"))
        version = str(pointer["active_policy_version"])
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("policy version must be a numeric semantic version")
    policy = json.loads((POLICY_DIR / f"{version}.json").read_text(encoding="utf-8"))
    if policy.get("policy_version") != version:
        raise ValueError(f"policy snapshot {version!r} has mismatched version")
    return policy


def policy_hash(policy: Mapping[str, Any]) -> str:
    canonical = json.dumps(policy, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_judge_registry(version: str) -> dict[str, Any]:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("judge registry version must be a numeric semantic version")
    registry = json.loads(
        (JUDGE_REGISTRY_DIR / f"{version}.json").read_text(encoding="utf-8")
    )
    if registry.get("registry_version") != version:
        raise ValueError(f"judge registry {version!r} has mismatched version")
    return registry


def _signal_contract(policy: Mapping[str, Any]) -> tuple[set[str], dict[str, str]]:
    routing = policy.get("routing")
    if not isinstance(routing, dict):
        return LEGACY_HARD_J3_SIGNALS, {signal: signal for signal in LEGACY_J2_SIGNALS}
    return set(routing["j3_signals"]), dict(routing["j2_signal_groups"])


def _validate_signals(
    signals: Mapping[str, bool], *, policy: Mapping[str, Any]
) -> None:
    j3_signals, j2_groups = _signal_contract(policy)
    allowed = j3_signals | set(j2_groups) | {"deterministic_complete"}
    unknown = sorted(set(signals) - allowed)
    if unknown:
        raise ValueError(f"unknown signal(s): {', '.join(unknown)}")
    if not all(isinstance(value, bool) for value in signals.values()):
        raise ValueError("signal values must be boolean")
    active = {name for name, enabled in signals.items() if enabled}
    if "deterministic_complete" in active and len(active) > 1:
        raise ValueError(
            "deterministic_complete cannot coexist with unresolved risk signals"
        )


def route_tier(signals: Mapping[str, bool], *, version: str | None = None) -> str:
    """Return the minimum rigor tier. Model identity never affects this choice."""
    policy = load_policy(version=version)
    _validate_signals(signals, policy=policy)
    j3_signals, j2_groups = _signal_contract(policy)
    if any(signals.get(name, False) for name in j3_signals):
        return "J3"
    routing = policy.get("routing")
    if not isinstance(routing, dict):
        if sum(bool(signals.get(name, False)) for name in j2_groups) >= 2:
            return "J2"
    else:
        direct = set(routing["j2_direct_signals"])
        if any(signals.get(name, False) for name in direct):
            return "J2"
        groups = {
            group for signal, group in j2_groups.items() if signals.get(signal, False)
        }
        if len(groups) >= int(routing["j2_minimum_distinct_groups"]):
            return "J2"
    if signals.get("deterministic_complete", False):
        return "J0"
    return "J1"


def routing_profile(
    signals: Mapping[str, bool], *, version: str | None = None
) -> dict[str, Any]:
    policy = load_policy(version=version)
    _validate_signals(signals, policy=policy)
    _j3_signals, j2_groups = _signal_contract(policy)
    active_groups = sorted(
        {group for signal, group in j2_groups.items() if signals.get(signal, False)}
    )
    routing = policy.get("routing")
    boundary_side: str | None = None
    if isinstance(routing, dict):
        direct = set(routing["j2_direct_signals"])
        has_direct = any(signals.get(name, False) for name in direct)
        tier = route_tier(signals, version=version)
        if not has_direct and len(active_groups) == 1 and tier == "J1":
            boundary_side = "j1_one_group"
        elif not has_direct and len(active_groups) == 2 and tier == "J2":
            boundary_side = "j2_two_groups"
    return {"risk_groups": active_groups, "boundary_side": boundary_side}


def _legacy_bucket(receipt: Mapping[str, Any]) -> float:
    key = f"{receipt.get('task_id', '')}:{receipt.get('policy_version', '')}"
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:13], 16) / float(
        0xFFFFFFFFFFFFF
    )


def _valid_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def _sampling_unit(receipt: Mapping[str, Any]) -> str:
    root_episode_id = receipt.get("root_episode_id")
    if isinstance(root_episode_id, str) and root_episode_id.strip():
        return root_episode_id
    return str(receipt.get("task_id", ""))


def _is_mandatory_control(receipt: Mapping[str, Any]) -> bool:
    return bool(
        receipt.get("actual_tier") == "J3"
        or receipt.get("disagreement")
        or receipt.get("owner_override")
        or receipt.get("policy_change")
    )


def _terminal_receipts(
    receipts: list[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    terminal: dict[str, Mapping[str, Any]] = {}
    for receipt in receipts:
        unit = _sampling_unit(receipt)
        prior = terminal.get(unit)
        if prior is None or int(receipt.get("attempt", 1)) >= int(
            prior.get("attempt", 1)
        ):
            terminal[unit] = receipt
    return list(terminal.values())


def _ordinary_terminal_receipts(
    receipts: list[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    mandatory_units = {
        _sampling_unit(receipt)
        for receipt in receipts
        if _is_mandatory_control(receipt)
    }
    return [
        receipt
        for receipt in _terminal_receipts(receipts)
        if _sampling_unit(receipt) not in mandatory_units
    ]


def _rank(receipt: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    key = f"{policy_hash(policy)}:{_sampling_unit(receipt)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def required_zero_failure_sample_size(tolerable_error: float, confidence: float) -> int:
    """Return n where zero failures has the requested one-sided confidence."""
    if not math.isfinite(tolerable_error) or not 0.0 < tolerable_error < 1.0:
        raise ValueError("tolerable_error must be finite and between 0 and 1")
    if not math.isfinite(confidence) or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")
    return math.ceil(math.log(1.0 - confidence) / math.log(1.0 - tolerable_error))


def _statistical_target(
    policy: Mapping[str, Any], tier: str, task_class: str
) -> int | None:
    sampling = policy.get("statistical_sampling")
    if not isinstance(sampling, dict):
        return None
    confidence = sampling.get("confidence")
    tolerances = sampling.get("tolerable_error_rates")
    if confidence is None or not isinstance(tolerances, dict):
        return None
    tier_tolerances = tolerances.get(tier)
    if not isinstance(tier_tolerances, dict):
        return None
    tolerance = tier_tolerances.get(task_class)
    if tolerance is None:
        return None
    return required_zero_failure_sample_size(float(tolerance), float(confidence))


def plan_ordinary_audits(
    receipts: list[Mapping[str, Any]],
    *,
    tier: str,
    task_class: str,
    policy: Mapping[str, Any] | None = None,
) -> list[str]:
    """Select an exact, derived sample without replacement from sealed episodes."""
    if tier not in {"J0", "J1", "J2"}:
        raise ValueError("ordinary statistical sampling applies only to J0-J2")
    if task_class not in TASK_CLASSES:
        raise ValueError(f"task_class must be one of {sorted(TASK_CLASSES)}")
    selected_policy = dict(policy or load_policy())
    target = _statistical_target(selected_policy, tier, task_class)
    if target is None:
        raise ValueError("statistical targets are not owner-ratified")
    eligible: dict[str, Mapping[str, Any]] = {}
    for receipt in _ordinary_terminal_receipts(receipts):
        if (
            receipt.get("actual_tier") != tier
            or receipt.get("task_class") != task_class
            or _is_mandatory_control(receipt)
        ):
            continue
        unit = _sampling_unit(receipt)
        if not _valid_uuid(unit):
            raise ValueError("ordinary sampling requires sealed UUID episode IDs")
        eligible[unit] = receipt
    ranked = sorted(eligible, key=lambda unit: _rank(eligible[unit], selected_policy))
    return ranked[: min(target, len(ranked))]


def _legacy_boundary_case(receipt: Mapping[str, Any]) -> bool:
    signals = receipt.get("signals")
    if not isinstance(signals, dict):
        return False
    j2_count = sum(bool(signals.get(name, False)) for name in LEGACY_J2_SIGNALS)
    return j2_count == 2


def sampling_record(receipt: Mapping[str, Any]) -> dict[str, Any]:
    version = str(receipt.get("policy_version", ""))
    policy = load_policy(version=version)
    tier = str(receipt.get("actual_tier", "J1"))
    special_reason: str | None = None
    if tier == "J3":
        special_reason = "all_j3"
    elif receipt.get("disagreement"):
        special_reason = "all_disagreements"
    elif receipt.get("owner_override"):
        special_reason = "all_owner_overrides"
    elif receipt.get("policy_change"):
        special_reason = "all_policy_changes"
    if "ordinary_audit_rates" in policy:
        if special_reason is None and _legacy_boundary_case(receipt):
            special_reason = "all_boundary_cases"
        bucket = _legacy_bucket(receipt)
        rate = 1.0 if special_reason else float(policy["ordinary_audit_rates"][tier])
        reason = special_reason or f"ordinary_{tier.lower()}_{rate:.0%}"
        return {
            "selected": bucket < rate,
            "reason": reason,
            "rate": rate,
            "bucket": bucket,
            "policy_version": version,
            "policy_hash": policy_hash(policy),
        }
    unit = _sampling_unit(receipt)
    if special_reason:
        return {
            "selected": True,
            "selection_state": "mandatory",
            "reason": special_reason,
            "method": "census_control",
            "sampling_unit": unit,
            "policy_version": version,
            "policy_hash": policy_hash(policy),
        }
    task_class = str(receipt.get("task_class", ""))
    target = _statistical_target(policy, tier, task_class)
    return {
        "selected": False,
        "selection_state": (
            "shadow_pending_parameters" if target is None else "pending_batch_plan"
        ),
        "reason": (
            "ordinary_sampling_not_claimed"
            if target is None
            else "ordinary_dynamic_sample_pending"
        ),
        "method": "derived_sample_count_without_replacement",
        "required_sample_count": target,
        "sampling_unit": unit,
        "policy_version": version,
        "policy_hash": policy_hash(policy),
    }


def audit_selection(receipt: Mapping[str, Any]) -> tuple[bool, str]:
    record = sampling_record(receipt)
    return bool(record["selected"]), str(record["reason"])


def new_receipt(
    *,
    task_id: str,
    task_class: str,
    signals: Mapping[str, bool],
    actual_tier: str | None = None,
    retry_of: Mapping[str, Any] | None = None,
    repository_id: str | None = None,
    work_anchor: str | None = None,
) -> dict[str, Any]:
    if task_class not in TASK_CLASSES:
        raise ValueError(f"task_class must be one of {sorted(TASK_CLASSES)}")
    policy = load_policy()
    recommended = route_tier(signals, version=str(policy["policy_version"]))
    tier = actual_tier or recommended
    if tier not in TIERS:
        raise ValueError(f"actual_tier must be one of {TIERS}")
    if TIERS.index(tier) < TIERS.index(recommended):
        raise ValueError("actual_tier cannot be below recommended_tier")
    episode_id = str(uuid4())
    root_episode_id = episode_id
    attempt = 1
    if retry_of is not None:
        if retry_of.get("task_class") != task_class:
            raise ValueError("retry_of task_class must match the new attempt")
        if retry_of.get("policy_version") != policy["policy_version"]:
            raise ValueError("retry_of policy_version must match the active policy")
        prior_repository = str(retry_of.get("repository_id", ""))
        prior_anchor = str(retry_of.get("work_anchor", ""))
        if repository_id is not None and repository_id != prior_repository:
            raise ValueError("retry_of repository_id must remain sealed")
        if work_anchor is not None and work_anchor != prior_anchor:
            raise ValueError("retry_of work_anchor must remain sealed")
        prior_root = retry_of.get("root_episode_id") or retry_of.get("episode_id")
        if not _valid_uuid(prior_root):
            raise ValueError("retry_of must identify a sealed root episode UUID")
        root_episode_id = str(prior_root)
        prior_attempt = retry_of.get("attempt", 1)
        if not isinstance(prior_attempt, int) or isinstance(prior_attempt, bool):
            raise ValueError("retry_of attempt must be an integer")
        attempt = prior_attempt + 1
        if repository_id is None:
            repository_id = prior_repository
        if work_anchor is None:
            work_anchor = prior_anchor
    repository_id = repository_id or ROOT.name
    work_anchor = work_anchor or task_id
    receipt: dict[str, Any] = {
        "schema_version": "1.1.0",
        "policy_version": policy["policy_version"],
        "episode_id": episode_id,
        "root_episode_id": root_episode_id,
        "attempt": attempt,
        "repository_id": repository_id,
        "work_anchor": work_anchor,
        "issued_at": datetime.now().astimezone().isoformat(),
        "task_id": task_id,
        "task_class": task_class,
        "signals": dict(sorted(signals.items())),
        "routing_profile": routing_profile(
            signals, version=str(policy["policy_version"])
        ),
        "recommended_tier": recommended,
        "actual_tier": tier,
        "deterministic_evidence": [],
        "judges": [],
        "verdict": "PENDING",
        "disagreement": False,
        "owner_override": None,
        "owner_approval": None,
        "policy_change": None,
        "failure_code": None,
        "outcome": None,
        "audit": None,
    }
    receipt["sampling"] = sampling_record(receipt)
    return receipt


def _append_jsonl_exclusive(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"exclusive ledger writer is busy: {lock_path}") from exc
    try:
        with os.fdopen(lock_fd, "w", encoding="utf-8") as lock_file:
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            os.fsync(lock_file.fileno())
        with path.open("a", encoding="utf-8", newline="\n") as ledger:
            ledger.write(json.dumps(value, sort_keys=True, separators=(",", ":")))
            ledger.write("\n")
            ledger.flush()
            os.fsync(ledger.fileno())
    finally:
        lock_path.unlink(missing_ok=True)


def issue_receipt(
    receipt: Mapping[str, Any], issuance_path: Path = ISSUANCE_PATH
) -> None:
    if receipt.get("verdict") != "PENDING":
        raise ValueError("only a new PENDING receipt can be issued")
    immutable_fields = (
        "schema_version",
        "policy_version",
        "episode_id",
        "root_episode_id",
        "attempt",
        "repository_id",
        "work_anchor",
        "issued_at",
        "task_id",
        "task_class",
        "signals",
        "routing_profile",
        "recommended_tier",
        "actual_tier",
        "sampling",
    )
    event = {"event_type": "issued"}
    event.update({field: receipt.get(field) for field in immutable_fields})
    _append_jsonl_exclusive(issuance_path, event)


def complete_receipt(
    receipt: Mapping[str, Any],
    *,
    ledger_path: Path,
    issuance_path: Path = ISSUANCE_PATH,
) -> None:
    errors = validate_receipt(receipt)
    if errors:
        raise ValueError("invalid terminal receipt: " + "; ".join(errors))
    if _issuance_failures([receipt], issuance_path) != 0:
        raise ValueError("terminal receipt has no matching sealed issuance event")
    _append_terminal_idempotent(ledger_path, receipt)


def record_outcome(
    *,
    root_episode_id: str,
    status: str,
    evidence_refs: list[str],
    observed_at: str | None = None,
    outcome_path: Path = OUTCOME_PATH,
    issuance_path: Path = ISSUANCE_PATH,
) -> dict[str, Any]:
    if not _valid_uuid(root_episode_id):
        raise ValueError("root_episode_id must be a sealed UUID")
    event = {
        "event_type": "outcome",
        "event_id": str(uuid4()),
        "root_episode_id": root_episode_id,
        "status": status,
        "observed_at": observed_at or datetime.now().astimezone().isoformat(),
        "evidence_refs": evidence_refs,
    }
    if not _outcome_is_valid(
        {
            "status": event["status"],
            "observed_at": event["observed_at"],
            "evidence_refs": event["evidence_refs"],
        }
    ):
        raise ValueError("outcome event must have typed status, time, and evidence")
    issued_roots = {
        str(item.get("root_episode_id"))
        for item in _read_ledger(issuance_path)
        if item.get("event_type") == "issued"
    }
    if root_episode_id not in issued_roots:
        raise ValueError("outcome root has no sealed issuance")
    _append_jsonl_exclusive(outcome_path, event)
    return event


def _append_terminal_idempotent(path: Path, receipt: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(f"exclusive ledger writer is busy: {lock_path}") from exc
    try:
        with os.fdopen(lock_fd, "w", encoding="utf-8") as lock_file:
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            os.fsync(lock_file.fileno())
        existing = _read_ledger(path)
        matches = [
            item
            for item in existing
            if item.get("episode_id") == receipt.get("episode_id")
        ]
        if matches:
            if len(matches) == 1 and matches[0] == dict(receipt):
                return
            raise ValueError("episode_id already has a conflicting terminal receipt")
        with path.open("a", encoding="utf-8", newline="\n") as ledger:
            ledger.write(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
            ledger.write("\n")
            ledger.flush()
            os.fsync(ledger.fileno())
    finally:
        lock_path.unlink(missing_ok=True)


def _proof_is_valid(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    required = {"check_id", "status", "evidence_ref", "observed_at"}
    return (
        required.issubset(item)
        and item.get("status") == "passed"
        and all(
            isinstance(item.get(key), str) and item[key].strip() for key in required
        )
        and _valid_timestamp(item.get("observed_at"))
    )


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _approval_is_valid(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"approver", "decision", "scope", "approved_at"}
    return (
        required.issubset(value)
        and value.get("decision") == "approved"
        and all(
            isinstance(value.get(key), str) and value[key].strip() for key in required
        )
        and _valid_timestamp(value.get("approved_at"))
    )


def _judge_is_valid(value: object, policy: Mapping[str, Any]) -> bool:
    if not isinstance(value, dict):
        return False
    valid = (
        isinstance(value.get("judge_id"), str)
        and bool(value["judge_id"].strip())
        and value.get("verdict") in FINAL_VERDICTS
        and isinstance(value.get("rubric_version"), str)
        and bool(value["rubric_version"].strip())
        and isinstance(value.get("evidence_refs"), list)
        and bool(value["evidence_refs"])
        and all(isinstance(ref, str) and ref.strip() for ref in value["evidence_refs"])
    )
    if "material_finding" in value and not isinstance(
        value.get("material_finding"), bool
    ):
        return False
    configured = policy.get("judge_requirements")
    if not isinstance(configured, dict) or "registry_version" not in configured:
        return valid
    registry_version = str(configured["registry_version"])
    if value.get("registry_version") != registry_version:
        return False
    purpose = value.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        return False
    try:
        registry = load_judge_registry(registry_version)
    except (FileNotFoundError, KeyError, ValueError):
        return False
    purpose_config = registry.get("purposes", {}).get(purpose)
    if not isinstance(purpose_config, dict):
        return False
    if value.get("rubric_version") not in purpose_config.get("rubric_versions", []):
        return False
    if (
        policy.get("enforcement_mode") == "active"
        and purpose_config.get("calibration_status") != "calibrated"
    ):
        return False
    return valid


def _outcome_is_valid(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, dict):
        return False
    evidence_refs = value.get("evidence_refs")
    return (
        value.get("status") in OUTCOME_STATUSES
        and isinstance(value.get("observed_at"), str)
        and bool(value["observed_at"].strip())
        and _valid_timestamp(value.get("observed_at"))
        and isinstance(evidence_refs, list)
        and bool(evidence_refs)
        and all(isinstance(ref, str) and ref.strip() for ref in evidence_refs)
    )


def _required_judges(receipt: Mapping[str, Any], policy: Mapping[str, Any]) -> int:
    actual = str(receipt.get("actual_tier"))
    configured = policy.get("judge_requirements")
    if not isinstance(configured, dict):
        return {"J0": 0, "J1": 1, "J2": 2, "J3": 2}.get(actual, 1)
    required = int(configured["base_counts"][actual])
    if actual == "J2":
        signals = receipt.get("signals")
        signal_values = signals if isinstance(signals, dict) else {}
        second_signals = set(configured["j2_second_judge_signals"])
        values = receipt.get("judges")
        judges = values if isinstance(values, list) else []
        if any(signal_values.get(name, False) for name in second_signals) or any(
            isinstance(judge, dict) and judge.get("material_finding") is True
            for judge in judges
        ):
            required = 2
    return required


def gate_verdict(receipt: Mapping[str, Any]) -> str:
    """Reconcile typed proof and judge payloads; never accept a model's overall score."""
    if receipt.get("failure_code") is not None:
        return "ABSTAIN"
    evidence = receipt.get("deterministic_evidence")
    if (
        not isinstance(evidence, list)
        or not evidence
        or not all(_proof_is_valid(item) for item in evidence)
    ):
        return "HOLD"
    if receipt.get("disagreement"):
        return "HOLD"
    try:
        policy = load_policy(version=str(receipt.get("policy_version", "")))
    except (FileNotFoundError, KeyError, ValueError):
        return "HOLD"
    values = receipt.get("judges")
    judges = values if isinstance(values, list) else []
    if not all(_judge_is_valid(judge, policy) for judge in judges):
        return "HOLD"
    verdicts = [judge["verdict"] for judge in judges]
    if "BLOCK" in verdicts:
        return "BLOCK"
    if "HOLD" in verdicts:
        return "HOLD"
    if "ABSTAIN" in verdicts:
        return "ABSTAIN"
    actual = receipt.get("actual_tier")
    if actual == "J0":
        return "PASS"
    required_judges = _required_judges(receipt, policy)
    if len(verdicts) < required_judges:
        return "HOLD"
    configured = policy.get("judge_requirements")
    if isinstance(configured, dict):
        required_purposes = set(
            configured.get("required_purposes", {}).get(str(actual), [])
        )
        purposes = {judge.get("purpose") for judge in judges if isinstance(judge, dict)}
        if not required_purposes.issubset(purposes):
            return "HOLD"
        if (
            required_judges >= 2
            and configured.get("distinct_purposes_when_multiple") is True
            and len(purposes) < required_judges
        ):
            return "HOLD"
    if actual == "J3" and not _approval_is_valid(receipt.get("owner_approval")):
        return "HOLD"
    return "PASS"


def validate_receipt(receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "policy_version",
        "task_id",
        "task_class",
        "signals",
        "recommended_tier",
        "actual_tier",
        "deterministic_evidence",
        "judges",
        "verdict",
        "sampling",
    }
    missing = sorted(required - receipt.keys())
    if missing:
        return [f"missing required field: {name}" for name in missing]
    if receipt.get("task_class") not in TASK_CLASSES:
        errors.append(f"task_class must be one of {sorted(TASK_CLASSES)}")

    version = str(receipt.get("policy_version", ""))
    try:
        policy = load_policy(version=version)
    except (FileNotFoundError, KeyError, ValueError) as exc:
        return [f"sampling policy unavailable or invalid: {exc}"]
    if "routing" in policy:
        if receipt.get("schema_version") != version:
            errors.append(f"schema_version must equal policy version {version}")
        for field in ("episode_id", "root_episode_id"):
            if not _valid_uuid(receipt.get(field)):
                errors.append(f"{field} must be a sealed UUID")
        attempt = receipt.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            errors.append("attempt must be a positive integer")
        for field in ("repository_id", "work_anchor"):
            if not isinstance(receipt.get(field), str) or not receipt[field].strip():
                errors.append(f"{field} must be a nonempty sealed identity")
        if not _valid_timestamp(receipt.get("issued_at")):
            errors.append("issued_at must be a parseable timestamp")

    signals = receipt.get("signals")
    if not isinstance(signals, dict):
        errors.append("signals must be an object of boolean values")
        signals = {}
    try:
        recommended = route_tier(signals, version=version)
    except ValueError as exc:
        errors.append(str(exc))
        recommended = "J3"
    if receipt.get("recommended_tier") != recommended:
        errors.append(
            f"recommended_tier must be deterministic router result {recommended}"
        )
    if "routing" in policy:
        expected_profile = routing_profile(signals, version=version)
        if receipt.get("routing_profile") != expected_profile:
            errors.append("routing_profile must match the policy-derived risk groups")
    actual = receipt.get("actual_tier")
    if actual not in TIERS:
        errors.append(f"actual_tier must be one of {TIERS}")
        return errors
    if TIERS.index(actual) < TIERS.index(recommended):
        errors.append("actual_tier cannot be below recommended_tier")

    evidence = receipt.get("deterministic_evidence")
    if (
        not isinstance(evidence, list)
        or not evidence
        or not all(_proof_is_valid(item) for item in evidence)
    ):
        errors.append(
            "deterministic_evidence must contain typed proof items with passed status"
        )

    values = receipt.get("judges")
    judges = values if isinstance(values, list) else []
    if not isinstance(values, list):
        errors.append("judges must be a list")
    required_judges = _required_judges(receipt, policy)
    if len(judges) < required_judges:
        errors.append(f"{actual} requires at least {required_judges} judge(s)")
    identities: list[str] = []
    for judge in judges:
        if not _judge_is_valid(judge, policy):
            errors.append(
                "every judge must have a registered purpose, rubric, typed verdict, and evidence refs"
            )
            continue
        identities.append(judge["judge_id"])
        if required_judges >= 2 and judge.get("independent") is not True:
            errors.append("J2/J3 judges must attest independent review")
    if required_judges >= 2 and len(identities) != len(set(identities)):
        errors.append("J2/J3 judge_id values must be distinct")
    configured = policy.get("judge_requirements")
    if isinstance(configured, dict):
        purposes = {judge.get("purpose") for judge in judges if isinstance(judge, dict)}
        required_purposes = set(
            configured.get("required_purposes", {}).get(str(actual), [])
        )
        missing_purposes = sorted(required_purposes - purposes)
        if missing_purposes:
            errors.append(
                "missing required judge purpose(s): " + ", ".join(missing_purposes)
            )
        if (
            required_judges >= 2
            and configured.get("distinct_purposes_when_multiple") is True
            and len(purposes) < required_judges
        ):
            errors.append("multiple judges require distinct registered purposes")
    owner_override = receipt.get("owner_override")
    if owner_override is not None and (
        not isinstance(owner_override, dict)
        or owner_override.get("decision") != "override"
        or not isinstance(owner_override.get("reason"), str)
        or not owner_override["reason"].strip()
    ):
        errors.append("owner_override must be a typed override decision with reason")
    policy_change = receipt.get("policy_change")
    if policy_change is not None and (
        not isinstance(policy_change, dict)
        or policy_change.get("kind") not in {"promotion", "demotion", "revision"}
        or not isinstance(policy_change.get("change_id"), str)
        or not policy_change["change_id"].strip()
    ):
        errors.append(
            "policy_change must identify a typed promotion, demotion, or revision"
        )
    if "audit_schema" in policy and not _outcome_is_valid(receipt.get("outcome")):
        errors.append("outcome must be null or a typed observed result with evidence")

    verdict = receipt.get("verdict")
    if verdict == "PENDING":
        errors.append("final receipt cannot remain PENDING")
    elif verdict not in FINAL_VERDICTS:
        errors.append(f"verdict must be one of {sorted(FINAL_VERDICTS)}")
    if (
        actual == "J3"
        and verdict == "PASS"
        and not _approval_is_valid(receipt.get("owner_approval"))
    ):
        errors.append("a passing J3 action requires typed positive owner approval")
    failure_code = receipt.get("failure_code")
    if failure_code is not None and failure_code not in FAILURE_CODES:
        errors.append(f"unknown failure_code {failure_code!r}")
    if failure_code is not None and verdict == "PASS":
        errors.append(f"{failure_code} cannot PASS; use ABSTAIN")
    if receipt.get("disagreement") and verdict not in {"HOLD", "ABSTAIN"}:
        errors.append("judge disagreement requires HOLD or ABSTAIN")
    if verdict in FINAL_VERDICTS:
        expected = gate_verdict(receipt)
        if verdict != expected:
            errors.append(f"verdict must equal deterministic gate result {expected}")
    if receipt.get("audit") is not None and not audit_is_complete(receipt):
        errors.append("audit does not satisfy the policy-versioned audit schema")
    try:
        expected_sampling = sampling_record(receipt)
        if receipt.get("sampling") != expected_sampling:
            errors.append(
                "sampling must match the versioned deterministic policy record"
            )
    except (FileNotFoundError, KeyError, ValueError) as exc:
        errors.append(f"sampling policy unavailable or invalid: {exc}")
    return errors


def audit_is_complete(receipt: Mapping[str, Any]) -> bool:
    audit = receipt.get("audit")
    if not isinstance(audit, dict):
        return False
    version = str(receipt.get("policy_version", ""))
    try:
        policy = load_policy(version=version)
    except (FileNotFoundError, KeyError, ValueError):
        return False
    required = {"auditor_id", "routing_correct", "execution_correct", "completed_at"}
    if "audit_schema" in policy:
        required |= {
            "audit_session_id",
            "independent_context",
            "rubric_version",
            "evidence_refs",
            "finding",
            "reason",
        }
    if not required.issubset(audit):
        return False
    if not isinstance(audit.get("auditor_id"), str) or not audit["auditor_id"].strip():
        return False
    if not isinstance(audit.get("routing_correct"), bool) or not isinstance(
        audit.get("execution_correct"), bool
    ):
        return False
    completed_at = audit.get("completed_at")
    if not isinstance(completed_at, str) or not completed_at.strip():
        return False
    try:
        datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    judge_ids = {
        judge.get("judge_id")
        for judge in receipt.get("judges", [])
        if isinstance(judge, dict)
    }
    if audit["auditor_id"] in judge_ids:
        return False
    if "audit_schema" not in policy:
        return True
    if not _valid_uuid(audit.get("audit_session_id")):
        return False
    if audit.get("independent_context") is not True:
        return False
    if (
        not isinstance(audit.get("rubric_version"), str)
        or not audit["rubric_version"].strip()
    ):
        return False
    evidence_refs = audit.get("evidence_refs")
    if (
        not isinstance(evidence_refs, list)
        or not evidence_refs
        or not all(isinstance(ref, str) and ref.strip() for ref in evidence_refs)
    ):
        return False
    finding = audit.get("finding")
    if finding not in set(policy["audit_schema"]["findings"]):
        return False
    if finding == "none" and (
        not audit["routing_correct"] or not audit["execution_correct"]
    ):
        return False
    if finding == "routing_miss" and audit["routing_correct"]:
        return False
    if finding == "execution_miss" and audit["execution_correct"]:
        return False
    if not isinstance(audit.get("reason"), str) or not audit["reason"].strip():
        return False
    return True


def _read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    receipts: list[dict[str, Any]] = []
    for line_number, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"ledger line {line_number} is invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError(f"ledger line {line_number} must be an object")
        receipts.append(value)
    return receipts


def _issuance_failures(
    receipts: list[Mapping[str, Any]], issuance_path: Path = ISSUANCE_PATH
) -> int:
    governed: list[Mapping[str, Any]] = []
    for receipt in receipts:
        try:
            policy = load_policy(version=str(receipt.get("policy_version", "")))
        except (FileNotFoundError, KeyError, ValueError):
            continue
        if "routing" in policy:
            governed.append(receipt)
    if not governed:
        return 0
    try:
        events = _read_ledger(issuance_path)
    except ValueError:
        return len(governed)
    issued: dict[str, Mapping[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for event in events:
        if event.get("event_type") != "issued":
            continue
        episode_id = event.get("episode_id")
        if not isinstance(episode_id, str):
            continue
        if episode_id in issued:
            duplicate_ids.add(episode_id)
        issued[episode_id] = event
    immutable_fields = (
        "schema_version",
        "policy_version",
        "episode_id",
        "root_episode_id",
        "attempt",
        "repository_id",
        "work_anchor",
        "issued_at",
        "task_id",
        "task_class",
        "signals",
        "routing_profile",
        "recommended_tier",
        "actual_tier",
    )
    failures = 0
    for receipt in governed:
        episode_id = str(receipt.get("episode_id", ""))
        event = issued.get(episode_id)
        if event is None or episode_id in duplicate_ids:
            failures += 1
            continue
        if any(event.get(field) != receipt.get(field) for field in immutable_fields):
            failures += 1
            continue
        issued_sampling = event.get("sampling")
        terminal_sampling = receipt.get("sampling")
        if not isinstance(issued_sampling, dict) or not isinstance(
            terminal_sampling, dict
        ):
            failures += 1
            continue
        for field in ("sampling_unit", "policy_version", "policy_hash"):
            if issued_sampling.get(field) != terminal_sampling.get(field):
                failures += 1
                break
    return failures


def _issuance_state(
    receipts: list[Mapping[str, Any]],
    issuance_path: Path = ISSUANCE_PATH,
    repository_id: str | None = None,
) -> dict[str, int]:
    try:
        events = _read_ledger(issuance_path)
    except ValueError:
        return {
            "issuance_failures": max(1, len(receipts)),
            "pending_issuances": 0,
            "issuance_anchor_conflicts": 0,
        }
    issued = [
        event
        for event in events
        if event.get("event_type") == "issued"
        and (repository_id is None or event.get("repository_id") == repository_id)
    ]
    terminal_ids = {
        str(receipt.get("episode_id"))
        for receipt in receipts
        if _valid_uuid(receipt.get("episode_id"))
    }
    pending = sum(str(event.get("episode_id")) not in terminal_ids for event in issued)
    anchor_roots: dict[tuple[str, str], set[str]] = {}
    for event in issued:
        key = (
            str(event.get("repository_id", "")),
            str(event.get("work_anchor", "")),
        )
        anchor_roots.setdefault(key, set()).add(str(event.get("root_episode_id", "")))
    conflicts = sum(len(roots) > 1 for roots in anchor_roots.values())
    return {
        "issuance_failures": _issuance_failures(receipts, issuance_path),
        "pending_issuances": pending,
        "issuance_anchor_conflicts": conflicts,
    }


def _outcome_state(
    outcome_path: Path = OUTCOME_PATH,
    issuance_path: Path = ISSUANCE_PATH,
    repository_id: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    try:
        events = _read_ledger(outcome_path)
        issuance = _read_ledger(issuance_path)
    except ValueError:
        return [], 1
    issued_roots = {
        str(item.get("root_episode_id"))
        for item in issuance
        if item.get("event_type") == "issued"
        and (repository_id is None or item.get("repository_id") == repository_id)
    }
    valid: list[dict[str, Any]] = []
    failures = 0
    event_ids: set[str] = set()
    for event in events:
        if (
            repository_id is not None
            and str(event.get("root_episode_id")) not in issued_roots
        ):
            continue
        event_id = event.get("event_id")
        payload = {
            "status": event.get("status"),
            "observed_at": event.get("observed_at"),
            "evidence_refs": event.get("evidence_refs"),
        }
        if (
            event.get("event_type") != "outcome"
            or not _valid_uuid(event_id)
            or event_id in event_ids
            or str(event.get("root_episode_id")) not in issued_roots
            or not _outcome_is_valid(payload)
        ):
            failures += 1
            continue
        event_ids.add(str(event_id))
        valid.append(event)
    return valid, failures


def review_policy_change(
    *,
    ledger_path: Path,
    current_tier: str,
    signals: Mapping[str, bool],
    issuance_path: Path = ISSUANCE_PATH,
    outcome_path: Path = OUTCOME_PATH,
) -> dict[str, Any]:
    """Derive a review recommendation from the ledger; never mutate policy."""
    if current_tier not in TIERS:
        raise ValueError("current_tier must be J0-J3")
    policy = load_policy()
    minimum_tier = route_tier(signals, version=str(policy["policy_version"]))
    if TIERS.index(current_tier) < TIERS.index(minimum_tier):
        raise ValueError("current_tier cannot be below the router minimum")
    policy_receipts = [
        receipt
        for receipt in _read_ledger(ledger_path)
        if receipt.get("policy_version") == policy["policy_version"]
    ]
    terminal = _terminal_receipts(policy_receipts)
    invalid_receipts = [receipt for receipt in terminal if validate_receipt(receipt)]
    lineage_failures = _ledger_lineage_failures(policy_receipts)
    issuance_state = _issuance_state(policy_receipts, issuance_path)
    outcome_events, outcome_failures = _outcome_state(outcome_path, issuance_path)
    if (
        invalid_receipts
        or lineage_failures
        or any(issuance_state.values())
        or outcome_failures
    ):
        return {
            "action": "hold",
            "recommended_tier": current_tier,
            "reason": "invalid_ledger_evidence",
            "automatic_change": False,
            "evidence": {
                "receipts": len(policy_receipts),
                "invalid_receipts": len(invalid_receipts),
                "lineage_failures": lineage_failures,
                "outcome_failures": outcome_failures,
                **issuance_state,
            },
        }
    receipts = [
        receipt
        for receipt in terminal
        if not validate_receipt(receipt)
        if receipt.get("actual_tier") == current_tier
    ]
    audited = [receipt for receipt in receipts if audit_is_complete(receipt)]
    findings = [str(receipt["audit"]["finding"]) for receipt in audited]
    critical_misses = findings.count("critical_miss")
    material_misses = findings.count("material_miss")
    routing_misses = findings.count("routing_miss")
    execution_misses = findings.count("execution_miss")
    outcome_material_misses = sum(
        isinstance(receipt.get("outcome"), dict)
        and receipt["outcome"].get("status") == "material_miss"
        for receipt in receipts
    )
    outcome_critical_misses = sum(
        isinstance(receipt.get("outcome"), dict)
        and receipt["outcome"].get("status") == "critical_miss"
        for receipt in receipts
    )
    current_roots = {_sampling_unit(receipt) for receipt in receipts}
    outcome_material_misses += sum(
        event.get("root_episode_id") in current_roots
        and event.get("status") == "material_miss"
        for event in outcome_events
    )
    outcome_critical_misses += sum(
        event.get("root_episode_id") in current_roots
        and event.get("status") == "critical_miss"
        for event in outcome_events
    )
    owner_overturns = sum(
        receipt.get("owner_override") is not None for receipt in receipts
    )
    evidence = {
        "receipts": len(receipts),
        "audited_receipts": len(audited),
        "critical_misses": critical_misses,
        "material_misses": material_misses,
        "routing_misses": routing_misses,
        "execution_misses": execution_misses,
        "outcome_material_misses": outcome_material_misses,
        "outcome_critical_misses": outcome_critical_misses,
        "owner_overturns": owner_overturns,
        "invalid_receipts": len(invalid_receipts),
        "task_classes": {
            task_class: sum(
                receipt.get("task_class") == task_class for receipt in audited
            )
            for task_class in sorted(TASK_CLASSES)
        },
    }
    if (
        critical_misses
        or material_misses
        or routing_misses
        or execution_misses
        or outcome_material_misses
        or outcome_critical_misses
        or owner_overturns
    ):
        target_index = min(TIERS.index(current_tier) + 1, TIERS.index("J3"))
        return {
            "action": "owner_review",
            "recommended_tier": TIERS[target_index],
            "reason": "ledger_observed_miss_or_overturn",
            "automatic_change": False,
            "evidence": evidence,
        }
    targets = {
        task_class: _statistical_target(policy, current_tier, task_class)
        for task_class in sorted(TASK_CLASSES)
    }
    selected_by_class: dict[str, list[str]] = {}
    audited_by_class: dict[str, int] = {}
    populations: dict[str, int] = {}
    for task_class in sorted(TASK_CLASSES):
        target = targets[task_class]
        ordinary = [
            receipt
            for receipt in _ordinary_terminal_receipts(policy_receipts)
            if receipt.get("task_class") == task_class
            and receipt.get("actual_tier") == current_tier
            and not validate_receipt(receipt)
            and not _is_mandatory_control(receipt)
        ]
        populations[task_class] = len({_sampling_unit(item) for item in ordinary})
        if target is None or current_tier == "J3":
            selected_by_class[task_class] = []
            audited_by_class[task_class] = 0
            continue
        selected = plan_ordinary_audits(
            ordinary,
            tier=current_tier,
            task_class=task_class,
            policy=policy,
        )
        selected_by_class[task_class] = selected
        latest = {_sampling_unit(item): item for item in ordinary}
        audited_by_class[task_class] = sum(
            audit_is_complete(latest[unit]) for unit in selected
        )
    evidence["ordinary_populations"] = populations
    evidence["ordinary_audited"] = audited_by_class
    targets_met = all(
        target is not None
        and populations[task_class] >= target
        and audited_by_class[task_class] >= target
        for task_class, target in targets.items()
    )
    if not targets_met:
        return {
            "action": "hold",
            "recommended_tier": current_tier,
            "reason": "insufficient_evidence",
            "automatic_change": False,
            "required_sample_counts": targets,
            "evidence": evidence,
        }
    target_index = max(TIERS.index(current_tier) - 1, TIERS.index(minimum_tier))
    if target_index == TIERS.index(current_tier):
        return {
            "action": "hold",
            "recommended_tier": current_tier,
            "reason": "router_floor",
            "automatic_change": False,
            "evidence": evidence,
        }
    return {
        "action": "owner_review",
        "recommended_tier": TIERS[target_index],
        "reason": "zero_failure_targets_met",
        "automatic_change": False,
        "evidence": evidence,
    }


def rollout_status(scratch: Path, config_path: Path = ROLLOUT_PATH) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    configured = config.get("repositories", {})
    default = config.get(
        "unlisted_repository",
        {"disposition": "defer", "mode": "reminder", "reminder": True},
    )
    rows: dict[str, Any] = {}
    for project in sorted(scratch.iterdir()):
        if not project.is_dir() or project.name.startswith("."):
            continue
        row = dict(configured.get(project.name, default))
        row.setdefault("reminder", row.get("mode") == "reminder")
        if row.get("mode") == "active":
            blockers = _activation_blockers()
            if blockers:
                row["effective_mode"] = "blocked"
                row["activation_blockers"] = blockers
            else:
                row["effective_mode"] = "active"
        rows[project.name] = row
    return rows


def _activation_blockers() -> list[str]:
    policy = load_policy()
    blockers: list[str] = []
    if policy.get("enforcement_mode") != "active":
        blockers.append("policy_not_active")
    sampling = policy.get("statistical_sampling", {})
    if sampling.get("status") != "ratified":
        blockers.append("statistical_targets_not_ratified")
    else:
        confidence = sampling.get("confidence")
        try:
            for tier in ("J0", "J1", "J2"):
                for task_class in sorted(TASK_CLASSES):
                    if _statistical_target(policy, tier, task_class) is None:
                        raise ValueError("missing target")
            if not isinstance(confidence, (int, float)):
                raise ValueError("missing confidence")
        except (KeyError, TypeError, ValueError):
            blockers.append("statistical_contract_invalid")
    coverage = policy.get("invocation_coverage", {})
    if coverage.get("active_blocking_allowed") is not True:
        blockers.append("independent_task_population_frame_missing")
    elif not _activation_artifact_valid(coverage):
        blockers.append("task_population_frame_artifact_invalid")
    evidence = policy.get("evidence_verification", {})
    if evidence.get("active_blocking_allowed") is not True:
        blockers.append("verifier_backed_evidence_records_missing")
    elif not _activation_artifact_valid(evidence):
        blockers.append("evidence_verifier_artifact_invalid")
    requirements = policy.get("judge_requirements", {})
    registry_version = requirements.get("registry_version")
    try:
        registry = load_judge_registry(str(registry_version))
    except (FileNotFoundError, KeyError, ValueError):
        blockers.append("judge_registry_unavailable")
        return blockers
    purposes = registry.get("purposes", {})
    if not purposes or any(
        purpose.get("calibration_status") != "calibrated"
        for purpose in purposes.values()
        if isinstance(purpose, dict)
    ):
        blockers.append("judge_purposes_not_calibrated")
    return blockers


def _activation_artifact_valid(config: Mapping[str, Any]) -> bool:
    artifact_path = config.get("artifact_path")
    expected_hash = config.get("artifact_sha256")
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        return False
    if not isinstance(expected_hash, str) or not expected_hash.startswith("sha256:"):
        return False
    path = (ROOT / artifact_path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    if not path.is_file():
        return False
    actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return actual == expected_hash


def activation_check(repository_id: str, config_path: Path = ROLLOUT_PATH) -> list[str]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    row = config.get("repositories", {}).get(repository_id)
    if not isinstance(row, dict) or row.get("mode") != "active":
        return []
    return _activation_blockers()


def _ledger_lineage_failures(receipts: list[Mapping[str, Any]]) -> int:
    governed = [
        receipt
        for receipt in receipts
        if _valid_uuid(receipt.get("episode_id"))
        and _valid_uuid(receipt.get("root_episode_id"))
    ]
    episode_ids = [str(receipt["episode_id"]) for receipt in governed]
    failures = len(episode_ids) - len(set(episode_ids))
    roots: dict[str, list[Mapping[str, Any]]] = {}
    for receipt in governed:
        roots.setdefault(str(receipt["root_episode_id"]), []).append(receipt)
    for root_id, attempts in roots.items():
        attempt_numbers = [receipt.get("attempt") for receipt in attempts]
        if not all(
            isinstance(attempt, int) and not isinstance(attempt, bool) and attempt >= 1
            for attempt in attempt_numbers
        ):
            failures += 1
            continue
        numeric_attempts = [int(attempt) for attempt in attempt_numbers]
        if len(numeric_attempts) != len(set(numeric_attempts)):
            failures += 1
        expected = list(range(1, max(numeric_attempts) + 1))
        if sorted(set(numeric_attempts)) != expected:
            failures += 1
        first = [receipt for receipt in attempts if receipt.get("attempt") == 1]
        if len(first) != 1 or first[0].get("episode_id") != root_id:
            failures += 1
        if len({receipt.get("task_class") for receipt in attempts}) != 1:
            failures += 1
        if len({receipt.get("policy_version") for receipt in attempts}) != 1:
            failures += 1
    return failures


def audit_ledger(
    path: Path,
    issuance_path: Path = ISSUANCE_PATH,
    outcome_path: Path = OUTCOME_PATH,
    repository_id: str | None = None,
) -> dict[str, Any]:
    report = {
        "receipts": 0,
        "routing_failures": 0,
        "execution_failures": 0,
        "sampled_audits_due": 0,
        "parse_failures": 0,
        "lineage_failures": 0,
        "issuance_failures": 0,
        "pending_issuances": 0,
        "issuance_anchor_conflicts": 0,
        "outcome_failures": 0,
        "ledger_missing": 0,
        "empty_ledger": 0,
    }
    if not path.exists():
        report["ledger_missing"] = 1
        report.update(_issuance_state([], issuance_path, repository_id))
        return report
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    if not lines:
        report["empty_ledger"] = 1
        report.update(_issuance_state([], issuance_path, repository_id))
        return report
    receipts: list[dict[str, Any]] = []
    for raw in lines:
        try:
            receipt = json.loads(raw)
        except json.JSONDecodeError:
            report["parse_failures"] += 1
            continue
        if not isinstance(receipt, dict):
            report["parse_failures"] += 1
            continue
        if repository_id is not None:
            receipt_repository = receipt.get("repository_id")
            if receipt_repository is None and repository_id != ".gemini":
                continue
            if receipt_repository is not None and receipt_repository != repository_id:
                continue
        report["receipts"] += 1
        receipts.append(receipt)
        errors = validate_receipt(receipt)
        routing_errors = [
            error
            for error in errors
            if error.startswith(
                ("recommended_tier", "actual_tier cannot", "unknown signal")
            )
        ]
        report["routing_failures"] += int(bool(routing_errors))
        report["execution_failures"] += int(
            bool([error for error in errors if error not in routing_errors])
        )
        try:
            selected = bool(sampling_record(receipt)["selected"])
        except (FileNotFoundError, KeyError, ValueError):
            selected = True
        if selected:
            if not audit_is_complete(receipt):
                report["sampled_audits_due"] += 1
            else:
                audit = receipt["audit"]
                report["routing_failures"] += int(not audit["routing_correct"])
                report["execution_failures"] += int(not audit["execution_correct"])
    report["lineage_failures"] = _ledger_lineage_failures(receipts)
    report.update(_issuance_state(receipts, issuance_path, repository_id))
    _outcome_events, report["outcome_failures"] = _outcome_state(
        outcome_path, issuance_path, repository_id
    )
    versions = sorted(
        {
            str(receipt.get("policy_version"))
            for receipt in receipts
            if receipt.get("policy_version")
        }
    )
    for version in versions:
        try:
            policy = load_policy(version=version)
        except (FileNotFoundError, KeyError, ValueError):
            continue
        if not isinstance(policy.get("statistical_sampling"), dict):
            continue
        version_receipts = _ordinary_terminal_receipts(
            [
                receipt
                for receipt in receipts
                if receipt.get("policy_version") == version
            ]
        )
        version_receipts = [
            receipt
            for receipt in version_receipts
            if not _is_mandatory_control(receipt)
        ]
        for tier in ("J0", "J1", "J2"):
            for task_class in sorted(TASK_CLASSES):
                if _statistical_target(policy, tier, task_class) is None:
                    continue
                selected = plan_ordinary_audits(
                    version_receipts,
                    tier=tier,
                    task_class=task_class,
                    policy=policy,
                )
                latest = {
                    _sampling_unit(receipt): receipt
                    for receipt in version_receipts
                    if receipt.get("actual_tier") == tier
                    and receipt.get("task_class") == task_class
                }
                for unit in selected:
                    receipt = latest[unit]
                    if not audit_is_complete(receipt):
                        report["sampled_audits_due"] += 1
                        continue
                    audit = receipt["audit"]
                    report["routing_failures"] += int(not audit["routing_correct"])
                    report["execution_failures"] += int(not audit["execution_correct"])
    return report


def _parse_signals(raw: str) -> dict[str, bool]:
    signals = {name.strip(): True for name in raw.split(",") if name.strip()}
    _validate_signals(signals, policy=load_policy())
    return signals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    route = sub.add_parser("route")
    route.add_argument("--task-id", required=True)
    route.add_argument("--task-class", choices=sorted(TASK_CLASSES), required=True)
    route.add_argument("--signals", default="")
    route.add_argument("--actual-tier", choices=TIERS)
    begin = sub.add_parser("begin")
    begin.add_argument("--task-id", required=True)
    begin.add_argument("--task-class", choices=sorted(TASK_CLASSES), required=True)
    begin.add_argument("--signals", default="")
    begin.add_argument("--actual-tier", choices=TIERS)
    begin.add_argument("--repository-id", required=True)
    begin.add_argument("--work-anchor", required=True)
    begin.add_argument("--retry-of", type=Path)
    begin.add_argument("--issuance", type=Path, default=ISSUANCE_PATH)
    complete = sub.add_parser("complete")
    complete.add_argument("receipt", type=Path)
    complete.add_argument(
        "--ledger", type=Path, default=ROOT / "governance" / "judge_ledger.jsonl"
    )
    complete.add_argument("--issuance", type=Path, default=ISSUANCE_PATH)
    outcome = sub.add_parser("record-outcome")
    outcome.add_argument("--root-episode-id", required=True)
    outcome.add_argument("--status", choices=sorted(OUTCOME_STATUSES), required=True)
    outcome.add_argument("--evidence-ref", action="append", required=True)
    outcome.add_argument("--observed-at")
    outcome.add_argument("--outcomes", type=Path, default=OUTCOME_PATH)
    outcome.add_argument("--issuance", type=Path, default=ISSUANCE_PATH)
    validate = sub.add_parser("validate")
    validate.add_argument("receipt", type=Path)
    rollout = sub.add_parser("rollout-status")
    rollout.add_argument(
        "--scratch", type=Path, default=ROOT / "antigravity" / "scratch"
    )
    reminders = sub.add_parser("rollout-reminders")
    reminders.add_argument(
        "--scratch", type=Path, default=ROOT / "antigravity" / "scratch"
    )
    activation = sub.add_parser("activation-check")
    activation.add_argument("--repository-id", required=True)
    activation.add_argument("--config", type=Path, default=ROLLOUT_PATH)
    audit = sub.add_parser("audit-ledger")
    audit.add_argument("ledger", type=Path)
    audit.add_argument("--issuance", type=Path, default=ISSUANCE_PATH)
    audit.add_argument("--outcomes", type=Path, default=OUTCOME_PATH)
    audit.add_argument("--repository-id")
    plan = sub.add_parser("plan-audits")
    plan.add_argument("ledger", type=Path)
    plan.add_argument("--tier", choices=("J0", "J1", "J2"), required=True)
    plan.add_argument("--task-class", choices=sorted(TASK_CLASSES), required=True)
    review = sub.add_parser("review-policy")
    review.add_argument("ledger", type=Path)
    review.add_argument("--current-tier", choices=TIERS, required=True)
    review.add_argument("--signals", default="")
    review.add_argument("--issuance", type=Path, default=ISSUANCE_PATH)
    review.add_argument("--outcomes", type=Path, default=OUTCOME_PATH)
    args = parser.parse_args()

    if args.command == "route":
        print(
            json.dumps(
                new_receipt(
                    task_id=args.task_id,
                    task_class=args.task_class,
                    signals=_parse_signals(args.signals),
                    actual_tier=args.actual_tier,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "begin":
        retry_of = (
            json.loads(args.retry_of.read_text(encoding="utf-8"))
            if args.retry_of
            else None
        )
        receipt = new_receipt(
            task_id=args.task_id,
            task_class=args.task_class,
            signals=_parse_signals(args.signals),
            actual_tier=args.actual_tier,
            repository_id=args.repository_id,
            work_anchor=args.work_anchor,
            retry_of=retry_of,
        )
        issue_receipt(receipt, args.issuance)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return
    if args.command == "complete":
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        complete_receipt(receipt, ledger_path=args.ledger, issuance_path=args.issuance)
        print("terminal receipt appended")
        return
    if args.command == "record-outcome":
        event = record_outcome(
            root_episode_id=args.root_episode_id,
            status=args.status,
            evidence_refs=args.evidence_ref,
            observed_at=args.observed_at,
            outcome_path=args.outcomes,
            issuance_path=args.issuance,
        )
        print(json.dumps(event, indent=2, sort_keys=True))
        return
    if args.command == "validate":
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        errors = validate_receipt(receipt)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            raise SystemExit(1)
        print("receipt valid")
        return
    if args.command == "audit-ledger":
        report = audit_ledger(
            args.ledger, args.issuance, args.outcomes, args.repository_id
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        blocking = (
            report["routing_failures"]
            or report["execution_failures"]
            or report["parse_failures"]
            or report["lineage_failures"]
            or report["issuance_failures"]
            or report["pending_issuances"]
            or report["issuance_anchor_conflicts"]
            or report["outcome_failures"]
            or report["ledger_missing"]
            or report["empty_ledger"]
            or report["sampled_audits_due"]
        )
        if blocking:
            raise SystemExit(1)
        return
    if args.command == "plan-audits":
        print(
            json.dumps(
                plan_ordinary_audits(
                    _read_ledger(args.ledger),
                    tier=args.tier,
                    task_class=args.task_class,
                ),
                indent=2,
            )
        )
        return
    if args.command == "review-policy":
        print(
            json.dumps(
                review_policy_change(
                    ledger_path=args.ledger,
                    current_tier=args.current_tier,
                    signals=_parse_signals(args.signals),
                    issuance_path=args.issuance,
                    outcome_path=args.outcomes,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.command == "rollout-reminders":
        rows = rollout_status(args.scratch)
        due = [name for name, row in rows.items() if row.get("reminder")]
        print(
            "judge rollout decision due: " + ", ".join(due)
            if due
            else "no judge rollout decisions due"
        )
        return
    if args.command == "activation-check":
        blockers = activation_check(args.repository_id, args.config)
        if blockers:
            print("activation blocked: " + ", ".join(blockers))
            raise SystemExit(1)
        print("activation check passed")
        return
    print(json.dumps(rollout_status(args.scratch), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
