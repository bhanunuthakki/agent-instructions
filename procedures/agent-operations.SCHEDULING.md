# Agent scheduling and quota reference

Use this reference only for multi-agent bursts or recurring jobs that consume a shared model quota.

## Shared capacity

- Treat interactive sessions, application calls, scheduled jobs, and delegated workers that use the same account or transport as one capacity pool until measured otherwise.
- Record provider, transport, purpose, model identifier, and measured usage separately. A subscription changes billing mechanics, not exhaustion risk.
- The machine or project schedule registry is authoritative for protected windows. This shared reference does not own project-specific times.

## Before a burst or new recurring job

1. Inspect the machine schedule and the relevant project registry for jobs using the same capacity pool.
2. Identify protected windows, deadlines, concurrency limits, and the interactive reserve from current evidence.
3. Estimate the burst by capability role and cap concurrency or stagger work only as much as the measured pool requires.
4. Assign one writer to each mutable state, cursor, ledger, or output artifact.
5. If schedule or quota state cannot be inspected, state that uncertainty and avoid creating a collision-prone recurring job.

## Recurring-job failure behavior

- Treat a transient subscription CLI failure as `defer this item and continue`; record the deferred count and retry on the next run.
- Fail loudly on setup, schema, authorization, or hard budget errors.
- Do not let one quota-starved item abort an otherwise independent batch.
- Emit enough structured state to distinguish completed, deferred, failed, and never-attempted items.
