# Incident and request lifecycle reference

Use only for a recurring service/job failure or a changed application performance path. `code-change` retains implementation ownership.

## Recurring-job and service failures

Treat a repeated failure as an unresolved reliability defect, even if a restart or retry restores service. Separate **mitigated**, **cause established**, **fix validated**, and **live recurrence verification pending**; do not close the incident from one healthy probe or a successful manual run.

- Reconstruct the failing run from its actual host, scheduler identity, effective configuration, dependency readiness, and preserved attempt/exit evidence. Establish the cause with a relevant reproduction or direct causal evidence; label hypotheses explicitly. Preserve failed evidence when a later attempt succeeds.
- Correct the failure mechanism and the recovery gap together. Add a regression that fails before the correction, plus relevant cases for repeated failure, recovery, overlap/duplicate effects, and unavailable dependencies. Never obtain green status by suppressing errors, discarding obligations, weakening data validation, or indiscriminately increasing retries/timeouts.
- Distinguish process liveness from data readiness. Stale or incomplete data must remain visible; it is not by itself a reason to kill an otherwise responsive service. Verify exact ownership before recovery, bound retry/backoff behavior, and preserve diagnostic evidence when automatic recovery is exhausted.
- Verify the deployed version through the real entrypoint and consumer, not only a port or process check. Exercise the triggering condition safely and confirm the intended outcome without duplicate writes/sends. Require the next relevant genuine scheduled execution and a recurrence window justified by the observed pattern before declaring recurrence resolved. If that evidence lies in the future, leave an explicit verification owner and follow-up; do not replay consequential jobs merely to manufacture proof.

## Application performance and request lifecycle

For application performance work, trace the affected user request through its real dependencies before optimizing. Measure queueing, network, query/computation, serialization, and client work as relevant. Remove unnecessary critical-path work before adding caches, concurrency, or infrastructure. Inventory shared request helpers and service consumers so a common defect is fixed consistently without changing unrelated contracts.

- Use end-to-end request budgets with compatible client and dependency deadlines. Bound queues, concurrent work, duplicate-request waits, retries, and backoff. A timed-out client must not create unlimited background work; cancel when supported, and otherwise bound and account for remaining work. Avoid increasing timeouts as the sole correction for a slow path.
- Parallelize independent reads only within dependency and resource limits. Preserve explicit ownership for writes and checkpoints. Isolate optional failures from required results and preserve required validation and truthful partial states.
- Cancel obsolete reads on navigation or superseding input where supported. Prevent late responses from overwriting newer state. Distinguish cancellation from failure and do not automatically retry consequential mutations without an established safe replay contract.
- Reuse or cache expensive results only with explicit keys, bounded retention, invalidation, freshness, and privacy rules. Preserve provenance and semantic admission. Coalesce duplicate work with bounded waits and a defined failure/recovery path; never convert missing or failed results into a successful empty value.
- Leave proportionate timing and failure evidence at service boundaries without exposing credentials or private payloads. Verify representative cold/warm behavior, slow/unavailable dependencies, concurrent reads, recovery, and resource cleanup as relevant. Pair regression coverage with measured user-path evidence from `frontend-quality` for visible applications.

For browser request implementation, consult current platform support and [MDN AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) for cancellation and deadline composition. Client abort does not establish that remote computation stopped; verify the actual service lifecycle.

