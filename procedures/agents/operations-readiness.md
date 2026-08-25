---
name: operations-readiness
description: Audit release, distribution, runtime health, scheduled work, backup/restore execution, rollback, incidents, and proportional cost/availability telemetry.
---

# Operations Readiness

Own the product's ability to keep working and recover in its actual deployment profile. A localhost scheduler and a hosted service both have operations; they need different evidence.

## Evaluate

- There is one documented build, verification, release, and rollback path; automation runs the repository's own commands and preserves mandatory safety checks.
- Dependencies and artifacts are reproducible enough for the selected distribution. Desktop/native releases address signing, permissions, update channel, downgrade limits, and data compatibility when applicable.
- Health signals distinguish configured, live, ready, degraded, and failed. Logs are actionable and secret-safe; scheduled work exposes last success, next run, lag, failure, and retry state.
- Timeouts, retries, backoff, idempotency, concurrency limits, resource ceilings, and graceful degradation match the failure modes.
- Durable state is backed up on an explicit schedule, retained appropriately, and restored in a representative drill. Local products also provide export and recovery instructions.
- Hosting or distributed releases have environment separation proportional to risk, migration ordering, TLS, secret injection, rollback evidence, and an incident path. Do not require a specific cloud, IaC tool, or three environments.
- Availability, latency, capacity, and cost telemetry are defined only where the product promise needs them. Alert ownership is explicit and actionable.

## Blocking standard

`BLOCK` when the target release cannot be reproduced, valuable state cannot be restored, likely failures are invisible, updates can strand data/users, or rollback/recovery for a consequential release is unproven.

## Coordinate

`qa-test-strategy` owns test sufficiency; this rubric owns pipeline and release mechanics. `data-foundation` owns restored-data semantics. `sec-appsec` owns security finding interpretation. `finops-pricing` owns economic synthesis.
