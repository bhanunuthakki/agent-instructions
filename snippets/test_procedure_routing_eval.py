from __future__ import annotations

import json
from pathlib import Path

import pytest

import procedure_routing_eval as routing


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "agent_system" / "procedure_routing_cases.jsonl"


def _case() -> routing.RouteCase:
    return routing.RouteCase(
        case_id="change-state",
        request="Add a durable local setting and implement it.",
        required_procedures=("code-change", "data-foundation"),
        allowed_procedures=("product-feature",),
        forbidden_procedures=("frontend-quality",),
        allowed_effects=("mutate_local",),
        should_clarify=False,
    )


def _decision(**overrides: object) -> routing.RouteDecision:
    values: dict[str, object] = {
        "case_id": "change-state",
        "selected_procedures": ["code-change", "data-foundation"],
        "effect": "mutate_local",
        "should_clarify": False,
    }
    values.update(overrides)
    return routing.RouteDecision.from_mapping(values)


def test_corpus_is_valid_and_uses_known_procedures() -> None:
    catalog = routing.load_procedure_catalog(ROOT)
    cases = routing.load_cases(CASES_PATH, known_procedures=set(catalog))

    assert len(cases) == 39
    assert len({case.case_id for case in cases}) == len(cases)
    assert any(not case.required_procedures for case in cases)
    assert any(case.should_clarify for case in cases)
    required = {name for case in cases for name in case.required_procedures}
    assert {"agent-operations", "scaffold-secrets"} <= required


def test_chisle_routes_automatically_persists_and_honors_boundaries() -> None:
    catalog = routing.load_procedure_catalog(ROOT)
    cases = routing.load_cases(CASES_PATH, known_procedures=set(catalog))
    by_id = {case.case_id: case for case in cases}

    assert "chisle" in by_id["code-chat-auto-chisle"].required_procedures
    assert "chisle" in by_id["code-chat-chisle-persists"].required_procedures
    assert "chisle" in by_id["code-chat-chisle-opt-out"].forbidden_procedures
    assert "chisle" in by_id["non-code-excludes-chisle"].forbidden_procedures


def test_frontier_routing_default_is_astra() -> None:
    assert routing.DEFAULT_MODEL == "gpt-6-astra"
    assert routing._parse_args([]).model == routing.DEFAULT_MODEL


def test_substantive_routes_allow_proactive_delegation_and_tiny_work_does_not() -> None:
    catalog = routing.load_procedure_catalog(ROOT)
    cases = routing.load_cases(CASES_PATH, known_procedures=set(catalog))
    by_id = {case.case_id: case for case in cases}
    for case_id in (
        "explain-llm-change",
        "fix-bounded-bug",
        "shorten-agent-rules",
        "add-application-llm-call",
        "choose-observability-vendor",
        "explicit-deep-interview",
        "material-frontend-change",
        "scaffold-authentication",
        "add-external-api",
        "confirm-external-publication",
        "configure-api-secret",
        "reuse-qualified-llm-route",
        "publication-unreviewed-candidate",
        "publication-exact-approval",
    ):
        case = by_id[case_id]
        assert "agent-operations" in case.required_procedures + case.allowed_procedures
    assert "agent-operations" in by_id["clear-small-change"].forbidden_procedures


def test_coverage_summary_separates_required_boundaries_untested_and_deferred() -> None:
    catalog = {
        "code-change": "change code",
        "frontend-quality": "change interfaces",
        "harden": "audit maturity",
        "linear-pr-sync": "sync a PR",
        "source-command-sync-agent-stubs": "generated source command",
    }
    case = routing.RouteCase(
        case_id="coverage",
        request="Change the interface.",
        required_procedures=("code-change", "frontend-quality"),
        allowed_procedures=("harden",),
        forbidden_procedures=(),
        allowed_effects=("mutate_local",),
        should_clarify=False,
    )

    coverage = routing.summarize_coverage(catalog, [case])

    assert coverage.required == ("code-change", "frontend-quality")
    assert coverage.boundary_only == ("harden",)
    assert coverage.untested == ("linear-pr-sync",)
    assert coverage.deferred == ("source-command-sync-agent-stubs",)


def test_perfect_score() -> None:
    score = routing.score_decisions([_case()], [_decision()])

    assert score.required_route_recall == 1.0
    assert score.forbidden_activation_rate == 0.0
    assert score.unnecessary_route_count == 0
    assert score.authority_accuracy == 1.0
    assert score.clarification_accuracy == 1.0
    assert score.case_failures == ()


def test_score_surfaces_missed_forbidden_excess_and_authority_errors() -> None:
    decision = _decision(
        selected_procedures=["code-change", "frontend-quality", "harden"],
        effect="inspect",
        should_clarify=True,
    )

    score = routing.score_decisions([_case()], [decision])

    assert score.required_route_recall == 0.5
    assert score.forbidden_activation_rate == 1.0
    assert score.unnecessary_route_count == 2
    assert score.authority_accuracy == 0.0
    assert score.clarification_accuracy == 0.0
    assert score.case_failures == (
        routing.CaseFailure(
            case_id="change-state",
            missing_required=("data-foundation",),
            forbidden_selected=("frontend-quality",),
            unnecessary_selected=("frontend-quality", "harden"),
            authority_correct=False,
            clarification_correct=False,
        ),
    )


@pytest.mark.parametrize(
    "payload,match",
    [
        ({"case_id": "x"}, "selected_procedures"),
        (
            {
                "case_id": "x",
                "selected_procedures": ["code-change", "code-change"],
                "effect": "inspect",
                "should_clarify": False,
            },
            "duplicate",
        ),
        (
            {
                "case_id": "x",
                "selected_procedures": [],
                "effect": "delete_everything",
                "should_clarify": False,
            },
            "effect",
        ),
    ],
)
def test_malformed_model_decision_is_rejected(
    payload: dict[str, object], match: str
) -> None:
    with pytest.raises(routing.RoutingEvalError, match=match):
        routing.RouteDecision.from_mapping(payload)


def test_response_must_cover_each_case_exactly_once() -> None:
    raw = json.dumps(
        [
            {
                "case_id": "change-state",
                "selected_procedures": ["code-change", "data-foundation"],
                "effect": "mutate_local",
                "should_clarify": False,
            }
        ]
    )

    with pytest.raises(routing.RoutingEvalError, match="exactly"):
        routing.parse_decisions(
            raw,
            expected_case_ids=("change-state", "second-case"),
            known_procedures={"code-change", "data-foundation"},
        )


def test_routing_context_uses_global_contract_and_fallback_without_local_guide(tmp_path) -> None:
    (tmp_path / "procedures").mkdir()
    (tmp_path / "GLOBAL.md").write_text("SHARED RULES")
    (tmp_path / "AGENTS.md").write_text("LOCAL REPOSITORY RULES")
    fallback = tmp_path / "procedures/INDEX.md"
    fallback.write_text("ROUTE OWNERS")
    first = routing.assemble_context(tmp_path, {"code-change": "Implementation"})
    assert "SHARED RULES" in first
    assert "ROUTE OWNERS" in first
    assert "LOCAL REPOSITORY RULES" not in first
    fallback.write_text("CHANGED ROUTE OWNERS")
    second = routing.assemble_context(tmp_path, {"code-change": "Implementation"})
    assert routing._sha256(first.encode()) != routing._sha256(second.encode())
