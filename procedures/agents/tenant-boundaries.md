---
name: tenant-boundaries
description: Audit multi-tenant context propagation and prove isolation across every tenant-owned storage and compute path.
---

# Tenant Boundaries

Apply only when the profile is genuinely multi-tenant. Own both the tenancy model and proof of separation; do not require `tenant_id` or RLS in a personal/single-user product.

## Evaluate

- The tenancy model and isolation boundary are explicit; tenant-owned resources are inventoried across database rows, files, object storage, caches, search/vector stores, queues, jobs, exports, logs, and model context.
- A typed immutable tenant context is established from trusted identity/provider mapping at each request, job, webhook, and administrative entry point. No fallback/default tenant exists.
- Storage enforcement is default-deny at the strongest practical boundary. Shared Postgres normally uses RLS with a non-bypass role; silo/bridge designs prove equivalent routing and administrative isolation.
- Every read, write, fetch-by-ID, cache key, file path, queue payload, background task, and retrieval query is scoped by construction.
- Negative tests create at least two tenants and prove cross-tenant read, write, update, delete, export, cache, search, job, and model-context attempts fail.
- Migration, backup/restore, retention/deletion, offboarding, support access, and break-glass paths preserve the same boundary and audit exceptional access.
- Privileged roles, maintenance functions, connection pools, async context, and provider webhooks cannot bypass or leak scope.

## Blocking standard

Any plausible cross-tenant access, unscoped entry point, trusted client tenant identifier, privileged-role bypass, or missing negative proof on a material store is `BLOCK`.

## Coordinate

`sec-authz` owns who the principal is and what they may do. `data-foundation` owns schema/migrations/lineage. `qa-test-strategy` owns fixture strategy; this rubric owns isolation assertions.
