# Incident, performance, forensics, and hillclimb reference

Use for a recurring service/job failure, an application performance issue (`perf-issue`), live runtime or captured trace forensics (`runtime-forensics` / `trace-forensics`), or a benchmark/hillclimb task (`/benchmark-checklist` / `hillclimb`). `code-change` retains implementation ownership.

## Recurring-job and service failures

Treat a repeated failure as an unresolved reliability defect, even if a restart or retry restores service. Separate **mitigated**, **cause established**, **fix validated**, and **live recurrence verification pending**; do not close the incident from one healthy probe or a successful manual run.

- Reconstruct the failing run from its actual host, scheduler identity, effective configuration, dependency readiness, and preserved attempt/exit evidence. Establish the cause with a relevant reproduction or direct causal evidence; label hypotheses explicitly. Preserve failed evidence when a later attempt succeeds.
- Correct the failure mechanism and the recovery gap together. Add a regression that fails before the correction, plus relevant cases for repeated failure, recovery, overlap/duplicate effects, and unavailable dependencies. Never obtain green status by suppressing errors, discarding obligations, weakening data validation, or indiscriminately increasing retries/timeouts.
- Distinguish process liveness from data readiness. Stale or incomplete data must remain visible; it is not by itself a reason to kill an otherwise responsive service. Verify exact ownership before recovery, bound retry/backoff behavior, and preserve diagnostic evidence when automatic recovery is exhausted.
- Verify the deployed version through the real entrypoint and consumer, not only a port or process check. Exercise the triggering condition safely and confirm the intended outcome without duplicate writes/sends. Require the next relevant genuine scheduled execution and a recurrence window justified by the observed pattern before declaring recurrence resolved. If that evidence lies in the future, leave an explicit verification owner and follow-up; do not replay consequential jobs merely to manufacture proof.

## Application performance and the 7 performance mantras (`perf-issue`)

Tie every performance fix to a baseline and post-fix measurement vetted by `/benchmark-checklist` below; never claim a ceiling or speedup from source inspection alone. Trace the affected user request through its real dependencies (queueing, network, query/computation, serialization, client rendering), ground with `/how`, and apply the **7 performance mantras in cheapest-first order**, stopping as soon as an earlier mantra meets the target:

1. **Don't do it:** delete work whose result nothing uses rather than optimizing it.
2. **Do it, but don't do it again:** memoize or cache expensive results only with explicit keys, bounded retention, invalidation, freshness, and privacy rules; preserve provenance and never cache failed/empty fallbacks as valid data.
3. **Do it less:** batch, coalesce duplicate in-flight requests with bounded waits, throttle, or reduce frequency.
4. **Do it later:** defer non-critical work off the boot or request-critical path.
5. **Do it when they're not looking:** precompute or move work to bounded background queues.
6. **Do it concurrently:** parallelize independent reads within dependency and resource limits while keeping write and checkpoint ownership explicit.
7. **Do it cheaper:** optimize the algorithm, query plan, index, or data structure.

Maintain end-to-end request budgets with compatible client and dependency deadlines. Cancel obsolete reads on navigation or superseding input (consult [MDN AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) for browser cancellation; verify actual server lifecycle since client abort does not prove remote work stopped). Pair regression coverage with measured user-path evidence from `frontend-quality` for visible applications.

## Runtime forensics vs. trace forensics

When the deliverable is a cited diagnosis of a leak, CPU spin, lock contention, or glitch (hand back the diagnosis without a fix unless asked):

- **Runtime forensics (live process):** capture a live signal on the matching surface (CPU profile for a spin, heap snapshot for a leak, CDP trace for a visual glitch). Reduce bulk artifacts in a worker or scratch SQLite table (`guard-the-context-window`), prove the mechanism via live instrumentation or hotfix injection without reloading before believing the hypothesis, and map the finding to exact `file:symbol:line`.
- **Trace forensics (captured artifact):** load the fixed `.cpuprofile`, `.json.gz`, `.heapsnapshot`, or spindump into a local scratch SQLite database (one row per sample, frame, or heap node) before querying. Walk the hot call tree or GC-root retainer chain, resolve source symbols through the artifact's symbol map (never claim a diagnosis from unmapped frames), and diff paired before/after captures when available.

## Benchmark checklist and hillclimb (`/benchmark-checklist` / `hillclimb`)

Before reporting or acting on any measured number (`explain-the-number`), verify these five checks from run evidence:

1. **Limiter:** profile in a separate non-reported run (`py-spy`, `perf`, `--cpu-prof`, I/O wait, syscall counts) so profiler overhead does not skew the reported number, and confirm the load generator itself did not saturate first.
2. **Production tuning parity:** run baseline and candidate with release flags, production batching/transaction/pool settings, matching warm/cold cache state, and identical datasets. Tune default-config bottlenecks (debug flags, per-row commits, missing indexes) before comparing implementations.
3. **Error and work accounting:** make the harness print both error count and completed work units alongside timing so fast failures or dropped work never look like speedups.
4. **Noise and repeat discipline:** check host load (`uptime`); interleave baseline and candidate runs when background noise cannot be stopped; report medians and spread across multiple runs rather than a single sample (unless explicitly requested and labeled as a single-run ballpark).
5. **End-to-end relevance:** verify that a micro-benchmark improvement moves the real user or service path.

For sustained iterative optimization against a target metric (**hillclimb**):

1. Ground the architecture with `/how`, select a realistic workload that reproduces the bottleneck, and set a checkable stop predicate that pairs a target delta with a minimum iteration floor or contrasting-workload check.
2. Build and **freeze a sensitive measurement harness** (`build-the-lever`) vetted by `/benchmark-checklist`, paired with a deterministic regression test gate.
3. Open a task-owned scratch decision log (`decision.tsv` with columns `ts, phase, decision, why, evidence, result`, governed by `storage-lifecycle` and gitignored unless an auditable trail is requested in the repository).
4. Test one mechanism-grounded hypothesis per iteration: measure before and after on the frozen harness, run the regression gate, commit one atomic change per win that clears noise (`git add <files>`, never `git add -A`), keep a code simplification that holds the number (`laziness-protocol`), and revert in full any attempt that fails the gate, regresses, or stays within noise.
