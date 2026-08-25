from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCEDURES = ROOT / "procedures"


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_root_is_invariant_and_routing_only() -> None:
    root = _text("AGENTS.md")
    assert "quick reversible iteration" not in root
    assert "## Effort calibration" not in root
    assert "short answer is likely to prevent materially greater rework" in root
    assert root.count("procedures/iteration-shortcut.md") == 1


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
