---
name: data-foundation
description: Audit canonical data ownership, identity and time semantics, migrations, provenance, quality, lifecycle, backup, restore, and export.
---

# Data Foundation

Own data truth and its lifecycle. Do not require tenancy for a local single-user profile; `tenant-boundaries` owns multi-tenant separation.

## Evaluate

- Each durable fact has one authoritative store and a stable identity. Derived projections are rebuildable rather than competing sources of truth.
- Schemas use precise types, nullability, units, currency, timezone, period/as-of semantics, and constraints. Boundary payloads validate before persistence.
- Idempotency keys identify the real source object/version and operation; run or attempt IDs provide lineage but are not universal business identities.
- Migrations are versioned, tested on representative existing data, and have an explicit forward/rollback or forward-repair strategy. Do not demand zero downtime for an offline local tool.
- External and transformed records retain source, retrieval time, transformation/version, and conflict policy. Quarantine invalid data; do not silently guess.
- Concurrent writers, transaction boundaries, retries, partial failure, and resume state cannot corrupt or duplicate durable truth.
- Retention and deletion implementation follows the obligation supplied by `legal-compliance`; backups and replicas do not silently defeat deletion.
- Durable personal data has tested backup, restore, and export. A backup without a successful representative restore is not evidence.
- Volume, indexes, query shape, and archival choices are justified by observed or credible near-term use, not speculative scale.

## Blocking standard

`BLOCK` for ambiguous canonical truth, unsafe migration of valuable state, unbounded corruption/duplication risk, missing provenance where claims depend on sources, or no proven recovery path for irreplaceable durable data.

## Coordinate

`operations-readiness` owns backup execution and scheduling; this rubric owns restored-data correctness. `product-analytics` owns event meaning; this rubric owns durable event correctness. `legal-compliance` owns obligations.
