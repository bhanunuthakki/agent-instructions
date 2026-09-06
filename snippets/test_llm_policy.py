from __future__ import annotations

import json
from pathlib import Path

import pytest

import llm_policy


def test_application_route_is_codex_then_claude() -> None:
    assert llm_policy.subscription_route(environ={}) == (
        llm_policy.SubscriptionBackend.CODEX,
        llm_policy.SubscriptionBackend.CLAUDE,
    )


def test_canonical_primary_override_is_reversible() -> None:
    assert llm_policy.subscription_route(
        environ={"LLM_PRIMARY_SUBSCRIPTION_BACKEND": "claude"}
    ) == (
        llm_policy.SubscriptionBackend.CLAUDE,
        llm_policy.SubscriptionBackend.CODEX,
    )


def test_canonical_fallback_switch_truncates_route() -> None:
    assert llm_policy.subscription_route(
        environ={"LLM_SUBSCRIPTION_FALLBACK_DISABLED": "true"}
    ) == (llm_policy.SubscriptionBackend.CODEX,)


def test_judge_route_must_be_explicit() -> None:
    with pytest.raises(llm_policy.RoutingPolicyError, match="explicit registered"):
        llm_policy.subscription_route(llm_policy.WorkloadClass.JUDGE, environ={})

    assert llm_policy.subscription_route(
        llm_policy.WorkloadClass.JUDGE,
        explicit_judge_route=("claude", "codex"),
        environ={
            "LLM_PRIMARY_SUBSCRIPTION_BACKEND": "codex",
            "LLM_SUBSCRIPTION_FALLBACK_DISABLED": "true",
        },
    ) == (
        llm_policy.SubscriptionBackend.CLAUDE,
        llm_policy.SubscriptionBackend.CODEX,
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
        "harness",
        "huntdesk",
        "repo-maintenance",
        "wealthplan",
    }
    earnings = next(entry for entry in index["projects"] if entry["project"] == "earnings-summary")
    assert earnings["judge_route_authority"]
    harness = next(entry for entry in index["projects"] if entry["project"] == "harness")
    assert harness["workload_classes"] == ["judge"]
    assert harness["application_route"] is None
    assert harness["judge_route_state"] == "project_explicit"
    assert harness["judge_independence_authority"]
