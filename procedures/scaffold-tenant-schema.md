---
name: scaffold-tenant-schema
description: Establish tenant boundaries only after the product profile explicitly requires multiple isolated customer tenants. Use for tenant isolation, tenant context, RLS, or multi-tenant schema design; not for generic database setup.
---

# Scaffold Tenant Boundaries

Do not add `tenant_id`, row-level security, pooled infrastructure, or tenant-aware abstractions to a personal, single-customer, or ordinary multi-user product. Start only after `multi_tenant` is an explicit profile requirement.

## Choose the isolation model

Inspect the current database, identity boundary, jobs, caches, blobs, search, analytics, LLM context, operational skill, and regulatory/risk needs. Select pool, bridge, silo, or a documented hybrid based on actual isolation and operating constraints. Prefer database-enforced isolation when the selected store supports it reliably; application filters alone are not proof.

## Required contract

- One immutable tenant context established from trusted identity/provider mapping at every request, job, webhook, import, and administrative boundary.
- Tenant scope propagated to database, cache, object storage, queues, search, analytics, logs, exports, backups, billing, and model/tool context as applicable.
- Default-deny reads and writes, scoped uniqueness/idempotency, and no tenant identity accepted from an unverified payload.
- Administrative cross-tenant actions explicit, authorized, audited, and rare.
- Lifecycle rules for creation, suspension, export, deletion/offboarding, legal holds, and retained financial/audit records; do not use universal cascades.
- Reversible, data-preserving migration and backfill plan with reconciliation evidence. `run_id` is lineage, not a universal business key.
- Negative tests proving tenant A cannot read, mutate, infer, search, export, prompt-leak, or bill tenant B, including privileged and background paths.

Keep vendor-specific RLS/policy examples in optional dated references selected after stack inspection. Finish with `tenant-boundaries`, `sec-authz`, and the applicable data/operations gates before admitting a second tenant.
