---
name: data-foundation
description: Design or change durable application state, schemas, data pipelines, or sources of truth with local-first simplicity, explicit lifecycle, recovery, and a deliberate commercial transition seam.
---

# Data Foundation

Build the smallest trustworthy data layer for the current product profile. Personal tools default to local, single-user storage; multi-user or tenant isolation is a separate explicit transition.

## Data contract

Before adding or changing persistence, identify:

- **Authority:** one canonical writer and source of truth for each concept. Label derived views, caches, indexes, snapshots, drafts, and external evidence as such.
- **Identity and time:** stable business keys, attempt/run identity, timezone and period semantics, point-in-time or as-of behavior, revisions, and ordering.
- **Boundaries:** validate untrusted input into typed schemas; make units, currency, locale, nullability, and enums explicit where applicable.
- **Writes:** transaction boundary, idempotency, concurrency owner, deduplication rule, and behavior on partial failure or retry.
- **Lineage:** source, capture time, transformation/version, and enough provenance to reproduce or explain consequential records.
- **Lifecycle:** creation, correction, supersession, retention, deletion, export, backup, restore, and cleanup ownership.
- **Evolution:** forward migration and backfill strategy, compatibility window when needed, rollback or recovery plan, and deterministic verification.
- **Use:** actual query and volume evidence for indexes, caches, partitions, or a database change. Do not scale from imagination.

Do not add a second persisted representation when a query or projection suffices. Do not use an execution attempt ID as a logical idempotency key. Do not claim a backup without a restore check.

## Product profiles

- **Local single-user:** choose the simplest durable store that meets integrity, query, backup, and recovery needs. No `tenant_id` requirement.
- **Hosted single-customer or distributed client:** add deployment, sync, identity, and recovery controls that the actual topology requires.
- **Multi-user or multi-tenant:** invoke `scaffold-tenant-schema` and the tenant-boundary hardening gate before admitting another trust domain.

## Handoff

Report the source of truth, read/write owners, schema or contract changes, migration/backfill and recovery evidence, retained data risks, and the explicit trigger that would require the next product profile.
