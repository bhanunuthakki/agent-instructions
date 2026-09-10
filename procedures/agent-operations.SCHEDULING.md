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

## Portable scheduled-job boundary

- Keep the scheduler thin: it owns identity, cadence, wake conditions, overlap policy, and the path to a checked-in entrypoint. It does not own prompts, provider commands, business rules, or mutable-state semantics.
- Make the checked-in job core callable with explicit inputs outside the scheduler. Put provider SDKs, subscription CLIs, model identifiers, and authentication setup behind one narrow adapter selected by machine or job configuration.
- Give each model call a stable purpose and capability role. Require a typed or schema-validated result, then let deterministic code validate targets and perform writes, sends, or deletions. A provider process does not receive broader mutation authority merely because the run is unattended.
- Record provider, transport, physical model, purpose, attempt identity, latency, measured usage when available, fallback path, and a redacted failure class. Never record prompts, responses, credentials, or personal source content merely to debug the schedule.
- Keep fallback explicit. A migration is incomplete while an old provider can still run silently; disable that fallback for the migrated schedule or declare it in the authoritative registry with a tested rollback reason.
- Keep source paths and provider choice configurable at one seam. Preserve legacy defaults only when they are the current durable-state location, and name the migration variable that moves them.

## Scheduler migration proof

1. Inventory native schedulers and embedded provider invocations separately; an empty hosted scheduler does not prove that OS tasks stopped invoking its CLI.
2. Map each live trigger to one checked-in job identity, entrypoint, mutable-state writer, provider policy, and durable output.
3. Validate the portable core deterministically, then preview or shadow-run only with the authority required by that job's side effects.
4. Switch the provider at the adapter/config seam, disable the old silent fallback, and verify the next run's ledger names the intended provider.
5. Disable the superseded trigger only after proving the destination trigger is installed and exactly one writer remains. Preserve the old trigger definition long enough for a reversible rollback.
