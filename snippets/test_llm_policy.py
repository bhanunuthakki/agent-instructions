from __future__ import annotations

import json
from pathlib import Path

import pytest

import llm_policy


def test_advisory_judge_binding_does_not_claim_blocking_qualification(tmp_path):
    route = llm_policy.load_advisory_judge_route()
    assert route.backend is llm_policy.SubscriptionBackend.CLAUDE
    assert route.model.startswith("claude-")
    path = tmp_path / "judge.json"
    raw = json.loads(llm_policy.JUDGE_ROUTE_PATH.read_text())
    raw["status"] = "qualified"
    path.write_text(json.dumps(raw))
    with pytest.raises(llm_policy.RoutingPolicyError):
        llm_policy.load_advisory_judge_route(path)


def test_application_route_disables_codex_and_prefers_gemini_then_claude() -> None:
    policy = llm_policy.load_policy()
    assert llm_policy.preferred_provider_order(policy) == ("gemini", "claude")
    assert "codex" in policy.disabled_backends
    assert llm_policy.subscription_route(environ={}) == (
        llm_policy.SubscriptionBackend.CLAUDE,
    )


def test_disabled_codex_override_fails_closed() -> None:
    with pytest.raises(llm_policy.RoutingPolicyError):
        llm_policy.subscription_route(
            environ={"LLM_PRIMARY_SUBSCRIPTION_BACKEND": "codex"}
        )


def test_canonical_fallback_switch_truncates_route() -> None:
    assert llm_policy.is_subscription_fallback_disabled(environ={}) is False
    assert (
        llm_policy.is_subscription_fallback_disabled(
            environ={"LLM_SUBSCRIPTION_FALLBACK_DISABLED": "true"}
        )
        is True
    )
    assert llm_policy.subscription_route(
        environ={"LLM_SUBSCRIPTION_FALLBACK_DISABLED": "true"}
    ) == (llm_policy.SubscriptionBackend.CLAUDE,)


def test_judge_route_must_be_explicit() -> None:
    with pytest.raises(llm_policy.RoutingPolicyError, match="explicit registered"):
        llm_policy.subscription_route(llm_policy.WorkloadClass.JUDGE, environ={})

    assert llm_policy.subscription_route(
        llm_policy.WorkloadClass.JUDGE,
        explicit_judge_route=("claude",),
        environ={
            "LLM_SUBSCRIPTION_FALLBACK_DISABLED": "true",
        },
    ) == (llm_policy.SubscriptionBackend.CLAUDE,)

    with pytest.raises(llm_policy.RoutingPolicyError):
        llm_policy.subscription_route(
            llm_policy.WorkloadClass.JUDGE,
            explicit_judge_route=("claude", "codex"),
            environ={},
        )


def test_usage_index_names_every_known_application_llm_project() -> None:
    root = Path(__file__).resolve().parents[1]
    index = json.loads((root / "config" / "llm_usage_index.json").read_text(encoding="utf-8"))
    projects = {entry["project"] for entry in index["projects"]}

    assert projects == {
        "angel-memos",
        "agent-instructions",
        "date-suggester",
        "earnings-summary",
        "huntdesk",
        "repo-maintenance",
        "wealthplan",
    }
    earnings = next(entry for entry in index["projects"] if entry["project"] == "earnings-summary")
    assert earnings["judge_route_authority"]
    instructions = next(
        entry for entry in index["projects"] if entry["project"] == "agent-instructions"
    )
    assert instructions["workload_classes"] == ["judge"]
    assert instructions["application_route"] is None
    assert instructions["judge_route_state"] == "project_explicit"
    assert instructions["judge_independence_authority"]
