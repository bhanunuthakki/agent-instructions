# Fleet LLM routing and usage index

Use this reference when adding an LLM-bearing service, changing provider order, migrating a legacy call path, or registering explicit Judge routing.

## Authority split

- `config/llm_routing_policy.json` owns ordinary membership-provider order and canonical environment-variable names.
- `snippets/llm_policy.py` is the typed resolver consumed by application entry points.
- `config/llm_usage_index.json` is the fleet inventory and points to delegated project authorities.
- The closest project `AGENTS.md` and indexed source paths own purposes, prompts, schemas, qualified models, budgets, ledgers, evals, and domain-specific data boundaries.
- `procedures/judging.md`, the central Judge policy registry, and each indexed `judge_route_authority` plus `judge_independence_authority` own explicit Judge selection and independence. A Judge never inherits ordinary application routing.

This split keeps provider priority centralized without moving product semantics into a global file.

## Ordinary application route

The default membership route is:

1. Codex
2. Claude

Application code imports `snippets/llm_policy.py`, calls `subscription_route()`, and maps the returned closed backend enum to transports qualified for its local purpose. Do not duplicate this tuple in service code or project instructions.

Only these fleet variables alter ordinary subscription routing:

- `AGENT_INSTRUCTIONS_HOME`: path to the canonical agent-instructions clone when the machine default cannot be used.
- `LLM_PRIMARY_SUBSCRIPTION_BACKEND=codex|claude`: reversible primary-provider override.
- `LLM_SUBSCRIPTION_FALLBACK_DISABLED=true|false`: truncate the resolved route after the primary.

Do not add a global model-ID override. Model and reasoning choices remain purpose-qualified, evaluation-backed project data. Do not add project-specific aliases for provider priority or fallback state.

## Judge route

Call `subscription_route(WorkloadClass.JUDGE, explicit_judge_route=...)` only with a route read from the indexed project authority. The route must be non-empty, use allowed backends, preserve the Judge procedure's independence requirements, and remain distinct from application fallback policy. A missing or invalid Judge route fails closed.

Provider-neutral Judge systems may register only the `judge` workload class and leave `application_route` null. Mixed services register both classes and name both authorities. `project_explicit` identifies a project-owned router plus a separately named independence gate; `shared_subscription` additionally requires `WorkloadClass.JUDGE` and an `explicit_judge_route` at the indexed route authority. `migration_hold` and `migration_required` remain visible, non-compliant debt with a concrete Judge migration note.

## Usage-index entry

Every canonical Git repository containing an active LLM call has exactly one entry with:

- project and delegated instruction section;
- typed entry point and purpose registry;
- ledger, budget, and eval authorities, using null only when the project truly has no such boundary yet;
- one or both workload classes;
- application migration state when applicable;
- explicit Judge route state, routing authority, and independence authority when applicable;
- a concrete migration note for `migration_hold` or `migration_required`.

`fleet_default` means the application entry point consumes the shared resolver, not merely that its hard-coded order happens to match. `migration_hold` names overlapping in-flight work that must not be overwritten. `migration_required` names a known incompatible route or variable contract. Neither state is treated as compliant.

Run `python snippets/check_llm_usage_index.py` after changes. Fleet discovery intentionally inspects canonical checkouts, not linked worktrees. `snippets/sync_agent_stubs.py --check` also enforces this index.
