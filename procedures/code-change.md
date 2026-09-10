---
name: code-change
description: Implement, fix, refactor, or review code with the repository’s tests and conventions. Use for behavior-changing code edits, bug fixes, frontend work, architectural refactors, or pre-push verification.
---

# Code Change

Implement the authorized outcome. Use the surrounding code for conventions and current behavior, while approved intent and domain contracts define what should happen. Preserve unrelated public behavior; replace an inadequate implementation when evidence shows that a larger coherent change better serves the task.

## Work loop

1. Inspect the affected interface, nearby tests, repository commands, and current diff.
2. Resolve the next behavior from the shared task understanding; expose an unresolved consequential choice through the global collaboration contract.
3. For a bug or new behavior, add the smallest regression or behavior test that should fail without the change and confirm the failure is relevant. For a mechanical refactor or documentation-only change, use adequate existing coverage unless inspection reveals a real gap.
4. Implement the coherent solution, including adjacent improvements that directly remove the task’s friction or risk. Refactor where it improves information hiding, removes genuine duplication, or replaces an obsolete mechanism; keep unrelated improvements as proposals.
5. Run targeted validation after each behavior. At the push or release boundary, finish with the repository’s applicable format, lint, typecheck, tests, and build checks in that order.

Do not weaken or disable a test merely to make it pass. When requested behavior changes or evidence shows the oracle is wrong, revise the affected expectation and preserve tests for the underlying invariant and nearby failure paths. Compare against existing expectations before regenerating goldens; review intended changes, then run comparison mode. Exact prose assertions are appropriate only when wording is the contract; prefer structural and semantic checks.

## Recurring-job and service failures

Treat a repeated failure as an unresolved reliability defect, even if a restart or retry restores service. Separate **mitigated**, **cause established**, **fix validated**, and **live recurrence verification pending**; do not close the incident from one healthy probe or a successful manual run.

- Reconstruct the failing run from its actual host, scheduler identity, effective configuration, dependency readiness, and preserved attempt/exit evidence. Establish the cause with a relevant reproduction or direct causal evidence; label hypotheses explicitly. Preserve failed evidence when a later attempt succeeds.
- Correct the failure mechanism and the recovery gap together. Add a regression that fails before the correction, plus relevant cases for repeated failure, recovery, overlap/duplicate effects, and unavailable dependencies. Never obtain green status by suppressing errors, discarding obligations, weakening data validation, or indiscriminately increasing retries/timeouts.
- Distinguish process liveness from data readiness. Stale or incomplete data must remain visible; it is not by itself a reason to kill an otherwise responsive service. Verify exact ownership before recovery, bound retry/backoff behavior, and preserve diagnostic evidence when automatic recovery is exhausted.
- Verify the deployed version through the real entrypoint and consumer, not only a port or process check. Exercise the triggering condition safely and confirm the intended outcome without duplicate writes/sends. Require the next relevant genuine scheduled execution and a recurrence window justified by the observed pattern before declaring recurrence resolved. If that evidence lies in the future, leave an explicit verification owner and follow-up; do not replay consequential jobs merely to manufacture proof.

## Design contract

- Use the strongest practical types and validate untrusted payloads into precise schemas at boundaries.
- Fail with clear errors. A deliberate compatibility or degradation path must emit a structured event naming the branch and reason; returned values also record their provenance when downstream logic depends on it.
- Prefer direct, cohesive modules that hide decisions behind a small interface. Avoid pass-through layers, namespace-only service classes, configuration objects without behavior, and helpers extracted only to shorten one caller.
- Keep imports at module scope unless lazy loading, an optional dependency, or a documented cycle requires otherwise.
- Treat LLM output, network payloads, files, and user input as untrusted. Do not classify with substring heuristics when an enum or validated schema expresses the contract.
- Match local comment density, naming, and idiom. Add explanation where the code cannot make a consequential invariant obvious.

For architecture or review work, read [code-change.REVIEW.md](code-change.REVIEW.md). For browser or UI work, read [code-change.FRONTEND.md](code-change.FRONTEND.md) and `frontend-quality`. `frontend-quality` owns task reasoning, composition, reduction, and rendered evidence; this procedure keeps the engineering loop.

## Network and sensitive surfaces

Keep secrets in headers or typed secret configuration, never query strings or logs. Sanitize exceptions before logging, replace credential-bearing HTTP failures with a safe public exception, and ensure telemetry also redacts retained exception context. Use `procedures/log-redaction.md` for implementation details.

Use the matching scaffold or hardening expert when an affected sensitive boundary presents a material risk. Carry that risk and its evidence into the shared task record.

## Handoff

Use the global completion contract. `frontend-quality` supplies rendered evidence for visible changes; `explain-change` supplies deeper owner comprehension when a substantial change needs it. Combine their relevant findings into one explanation.
