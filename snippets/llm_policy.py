"""Typed fleet policy for subscription-backed application LLM routing.

Projects own purposes, prompts, schemas, budgets, and evals. This module owns
the ordinary provider order and the environment variables that may alter it.
Judge routes are never inferred from the ordinary application default.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "llm_routing_policy.json"


class RoutingPolicyError(RuntimeError):
    """The fleet routing policy or requested override is invalid."""


class WorkloadClass(StrEnum):
    APPLICATION = "application"
    JUDGE = "judge"


class SubscriptionBackend(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"


@dataclass(frozen=True)
class RoutingPolicy:
    default_application_route: tuple[SubscriptionBackend, ...]
    allowed_subscription_backends: frozenset[SubscriptionBackend]
    instructions_home_env: str
    primary_backend_env: str
    fallback_disabled_env: str


def _backend(value: object, *, field: str) -> SubscriptionBackend:
    if not isinstance(value, str):
        raise RoutingPolicyError(f"{field} must contain backend names.")
    try:
        return SubscriptionBackend(value)
    except ValueError:
        raise RoutingPolicyError(f"{field} contains unsupported backend {value!r}.") from None


def load_policy(path: Path = POLICY_PATH) -> RoutingPolicy:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutingPolicyError("The fleet LLM routing policy is unavailable or invalid.") from exc
    if not isinstance(raw, dict) or raw.get("$schema") != "internal://llm-routing-policy/v1":
        raise RoutingPolicyError("The fleet LLM routing policy has an unsupported schema.")

    raw_allowed = raw.get("allowed_subscription_backends")
    raw_route = raw.get("default_application_route")
    raw_env = raw.get("canonical_environment")
    raw_classes = raw.get("workload_classes")
    if not isinstance(raw_allowed, list) or not isinstance(raw_route, list):
        raise RoutingPolicyError("The fleet LLM routing policy must define backend lists.")
    if not isinstance(raw_env, dict) or not isinstance(raw_classes, dict):
        raise RoutingPolicyError("The fleet LLM routing policy is missing its authority maps.")

    allowed = frozenset(_backend(item, field="allowed_subscription_backends") for item in raw_allowed)
    route = tuple(_backend(item, field="default_application_route") for item in raw_route)
    if not route or len(route) != len(set(route)) or not set(route) <= allowed:
        raise RoutingPolicyError("The default application route must be non-empty, unique, and allowed.")
    if raw_classes != {
        WorkloadClass.APPLICATION.value: "fleet_default",
        WorkloadClass.JUDGE.value: "explicit_registration_required",
    }:
        raise RoutingPolicyError("The workload-class policy is incomplete or unsupported.")

    env_values = (
        raw_env.get("instructions_home"),
        raw_env.get("primary_subscription_backend"),
        raw_env.get("subscription_fallback_disabled"),
    )
    if not all(isinstance(value, str) and value for value in env_values):
        raise RoutingPolicyError("Canonical environment variable names must be non-empty strings.")
    return RoutingPolicy(
        default_application_route=route,
        allowed_subscription_backends=allowed,
        instructions_home_env=str(env_values[0]),
        primary_backend_env=str(env_values[1]),
        fallback_disabled_env=str(env_values[2]),
    )


def _enabled(value: str | None, *, variable: str) -> bool:
    normalized = (value or "").strip().lower()
    if normalized in {"", "0", "false", "no", "off"}:
        return False
    if normalized in {"1", "true", "yes", "on"}:
        return True
    raise RoutingPolicyError(f"{variable} must be a boolean value.")


def subscription_route(
    workload_class: WorkloadClass = WorkloadClass.APPLICATION,
    *,
    explicit_judge_route: Sequence[str | SubscriptionBackend] | None = None,
    environ: Mapping[str, str] | None = None,
    policy: RoutingPolicy | None = None,
) -> tuple[SubscriptionBackend, ...]:
    """Resolve the governed subscription order for one workload class."""
    active_policy = policy or load_policy()
    active_env = os.environ if environ is None else environ

    if workload_class is WorkloadClass.JUDGE:
        if explicit_judge_route is None:
            raise RoutingPolicyError("Judge routing requires an explicit registered route.")
        route = tuple(_backend(str(item), field="explicit_judge_route") for item in explicit_judge_route)
        if not route or len(route) != len(set(route)) or not set(route) <= active_policy.allowed_subscription_backends:
            raise RoutingPolicyError("The explicit Judge route must be non-empty, unique, and allowed.")
        return route
    elif workload_class is WorkloadClass.APPLICATION:
        if explicit_judge_route is not None:
            raise RoutingPolicyError("Ordinary application routing cannot supply a Judge route.")
        route = active_policy.default_application_route
        primary_raw = active_env.get(active_policy.primary_backend_env, route[0].value).strip().lower()
        primary = _backend(primary_raw, field=active_policy.primary_backend_env)
        if primary not in route:
            raise RoutingPolicyError(
                f"{active_policy.primary_backend_env} selects a backend outside the application route."
            )
        route = (primary, *(backend for backend in route if backend is not primary))
    else:
        raise RoutingPolicyError(f"Unsupported workload class {workload_class!r}.")

    if _enabled(
        active_env.get(active_policy.fallback_disabled_env),
        variable=active_policy.fallback_disabled_env,
    ):
        return route[:1]
    return route
