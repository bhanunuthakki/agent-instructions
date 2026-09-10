from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "procedures"


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_global_contract_and_local_guide_have_distinct_owners() -> None:
    global_rules = _text("GLOBAL.md")
    local = _text("AGENTS.md")
    routes = _text("procedures/INDEX.md")
    machine = _text("procedures/machine-operations.md")
    assert "## Outcome and initiative" in global_rules
    assert "Approved product intent governs required behavior" in global_rules
    assert "do not switch branches" in global_rules
    assert "never" in global_rules.lower() and "credentials" in global_rules
    assert "procedures/INDEX.md" in global_rules
    assert "procedures/machine-operations.md" in global_rules
    assert "## Orchestration and delegation" in global_rules
    assert "At task start, after material user input" in global_rules
    assert "Do not wait for the user to request delegation explicitly" in global_rules
    assert "For every substantive task, load agent operations" in global_rules
    assert "highest-capability available agent at the root" in global_rules
    assert "source" in local and "sync_agent_stubs.py" in local
    assert "## Outcome and initiative" not in local
    assert "OPENROUTER_API_KEY" not in global_rules
    assert "LINEAR_API_KEY" not in global_rules
    assert "without searching for other credentials" in machine
    assert "Load only that variable at runtime" in machine
    assert "before execution" in routes
    assert "owns the delegation check even when the result is serial execution" in routes
    assert "a primary deliverable owner" in global_rules
    assert "proposed, implemented, validated, committed, merged, deployed" in global_rules


def test_operations_owns_resource_handoff_and_truthful_closure() -> None:
    operations = _text("procedures/agent-operations.md")
    assert "Reassess delegation at task start, after material user input" in operations
    assert "Delegate by default" in operations
    assert "one to three parallel workers" in operations
    assert "Workers do not recursively fan out by default" in operations
    assert "makes the final acceptance judgment" in operations
    assert "auto-reconnecting browser or remote-control session" in operations
    assert "After two equivalent failures" in operations
    assert "cancel temporary task-owned monitors" in operations
    assert "Preserve a user-requested persistent monitor" in operations
    assert "applies the global completion contract" in operations


def test_code_change_calibrates_tests_and_release_gates() -> None:
    code_change = _text("procedures/code-change.md")
    assert "For a bug or new behavior" in code_change
    assert "mechanical refactor or documentation-only change" in code_change
    assert "At the push or release boundary" in code_change


def test_clarification_and_shortcut_have_one_detailed_owner() -> None:
    grill = _text("procedures/grill-me.md")
    shortcut = _text("procedures/iteration-shortcut.md")
    operations = _text("procedures/agent-operations.md")
    assert "Lightweight clarification" in grill and "Deep interview" in grill
    assert "explicitly invokes `/grill-me`" in grill
    assert "irreplaceable data integrity" in shortcut
    assert "expiry or cleanup trigger" in shortcut
    assert "not a universal receipt or another rigor tier" in operations


def test_frontend_route_preserves_project_family_and_prototype_boundary() -> None:
    frontend = _text("procedures/frontend-quality.md")
    mockup = _text("procedures/mockup-review.md")
    assert "nearest shipped sibling and registered family" in frontend
    assert "typed rationale and an adversarial continuity test" in frontend
    assert "when the project contract requires" in frontend
    assert "item count alone never mandates controls" in frontend
    assert "useful richness" in frontend
    assert "Exact tokens, recipes, exceptions" in frontend
    assert "recompose the approved direction through the production project's registered masters" in mockup
    assert "Approval never promotes prototype code into production" in mockup


def test_evidence_maturity_and_effort_axes_do_not_collapse() -> None:
    judging = _text("procedures/judging.md")
    harden = _text("procedures/harden.md")
    grill = _text("procedures/grill-me.md")
    assert "Review tiers describe rigor" in judging
    assert "Maturity is one axis" in harden
    assert "Lightweight clarification" in grill
    assert "quick reversible iteration" not in "\n".join((judging, harden, grill))


def test_llm_eval_depth_and_open_weight_economics_are_stage_aware() -> None:
    evals = _text("procedures/llm-ops.EVALS.md")
    frontier = _text("procedures/model-frontier.md")
    assert all(label in evals for label in ("Exploration", "Recurring personal use", "External, commercial"))
    assert "cannot promote a production model" in evals
    assert "runtime/model/quantization/hardware tuple" in evals
    assert "amortized hardware" in frontier


def test_representative_route_matrix_is_complete() -> None:
    # These are decision trajectories, not prose snapshots. Each expected owner must
    # exist, and every trajectory has exactly one primary workflow owner.
    cases = {
        "clear-small-feature": "code-change",
        "underspecified-product-goal": "grill-me",
        "short-answer-prevents-fanout": "agent-operations",
        "answer-recoverable-from-code": "code-change",
        "reversible-mechanism-choice": "code-change",
        "product-performance-tradeoff": "grill-me",
        "isolated-ui-mockup": "mockup-review",
        "canonical-data-shortcut": "iteration-shortcut",
        "new-established-page": "frontend-quality",
        "no-fitting-family": "frontend-quality",
        "material-ui-change": "frontend-quality",
        "undefined-durable-term": "definitions",
        "experimental-personal-llm": "llm-ops",
        "cheaper-model-promotion": "model-frontier",
        "independent-task-judgment": "judging",
        "personal-l1-hardening": "harden",
        "paid-single-user-l3": "harden",
        "missing-rubric-package": "harden",
        "exposed-secret": "harden",
        "routine-handoff": "explain-change",
        "release-shortcut": "iteration-shortcut",
        "historical-contract-conflict": "context-engineering",
    }
    assert len(cases) == 22
    for owner in set(cases.values()):
        assert (PROCEDURES / f"{owner}.md").is_file(), owner


def test_active_procedures_name_owners_instead_of_stale_global_rules() -> None:
    active = [PROCEDURES / "log-redaction.md"]
    active.extend(
        path
        for path in (PROCEDURES / "agents").glob("*.md")
        if path.name != "RETIRED.md"
    )
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in active)
    for stale_reference in (
        "Universal Safety Rule",
        "per global standards",
        "per global TDD rules",
        "per Testing Discipline",
    ):
        assert stale_reference not in corpus


def test_interaction_outcome_corpus_covers_observed_failure_modes() -> None:
    path = ROOT / "evals" / "agent_system" / "interaction_outcome_cases.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    ids = {case["case_id"] for case in cases}
    assert {
        "decision-first-advice",
        "cross-task-objective-preservation",
        "huntdesk-crm-sync-scope",
        "huntdesk-company-axes",
        "crd-resource-handoff",
        "truthful-archive-readiness",
        "explore-dcf-boundary",
        "matched-alpha-precision",
    } <= ids
    assert {
        "archive-ready-positive",
        "huntdesk-broad-inbox-authorized",
        "distributed-adoption-positive",
        "crd-release-positive",
        "alpha-reconciled-positive",
        "angel-approved-publication",
        "blog-live-edit-authorized",
        "resume-unsupported-claim",
        "dcf-edit-positive",
        "reading-simulator-boundary",
        "company-tracked-inactive",
        "maintenance-preview-authority",
        "cross-task-relevant-dependency",
        "wealthplan-private-scenario",
    } <= ids
    for case in cases:
        assert case["context"] and case["request"]
        assert case["instruction_paths"]
        assert case["must_include"] and case["must_avoid"]


def test_instruction_quality_cases_cover_initiative_and_its_boundaries() -> None:
    cases = [json.loads(line) for line in _text("evals/agent_system/interaction_outcome_cases.jsonl").splitlines() if line]
    ids = {case["case_id"] for case in cases}
    assert {
        "internal-rename-positive", "layout-replacement-positive", "six-citations-no-facets",
        "changed-golden-expectation", "unexplained-golden-drift", "bounded-prototype-positive",
        "intent-over-bug", "adjacent-scope-boundary", "ambiguous-cleanup-clarification",
        "proactive-parallel-discovery", "phase-transition-redelegation",
        "trivial-work-stays-rooted", "worker-result-needs-root-judgment",
        "decomposition-decision-before-fanout", "substantive-fanout-negative-economics",
        "overlapping-writes-serialize", "cheapest-qualified-worker",
    } <= ids
    for case in cases:
        assert "agent-instructions/GLOBAL.md" in case["instruction_paths"]
        assert "agent-instructions/AGENTS.md" not in case["instruction_paths"]


def test_instruction_quality_rubric_is_complete_and_gated() -> None:
    rubric = json.loads(_text("evals/agent_system/instruction_quality_rubric.json"))
    assert sum(item["points"] for item in rubric["dimensions"]) == 100
    assert len({item["id"] for item in rubric["dimensions"]}) == len(rubric["dimensions"])
    assert "regardless of total score" in rubric["blocking_rule"]
    assert "never rerun unchanged work" in rubric["iteration_rule"]
