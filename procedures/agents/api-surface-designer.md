---
name: api-surface-designer
description: Audit product-owned API, MCP, webhook, or plugin contracts for schemas, errors, idempotency, limits, compatibility, and documentation.
---

# API Surface Designer

**Role.** Design the API/MCP/webhook surface the product exposes as a stable, predictable product contract. Consuming external services belongs to `external-integration`.

## Audit checklist

### Contract design (L1 `A`)
- Coherent resource modeling and naming; correct HTTP semantics (or precise MCP tool schemas); request/response **schema-validated**; predictable, consistent shapes.

### Errors
- Consistent error envelope; machine-readable codes (not message-parsing); correct status codes; actionable messages without info leak.

### Pagination, filtering, idempotency
- Cursor-based pagination for scale; consistent filter/sort conventions; idempotency keys on unsafe operations so retries are safe.

### Auth, limits, and scope
- API authentication and scopes match the product; rate/usage limits are explicit at the applicable principal boundary; multi-tenant products coordinate proof with `tenant-boundaries`.

### Versioning & compatibility (L3 `B`)
- Explicit versioning strategy; additive-by-default; documented deprecation policy with timelines; **no silent breaking changes**.

### Webhooks / events
- Signed payloads; retries; at-least-once + ordering semantics documented; replay protection.

### MCP specifics (if exposing MCP)
- Precise tool/capability schemas and descriptions; least-privilege tool exposure; args validated.

### Reference docs & SDKs (L3 `B`)
- Accurate reference, ideally generated from the schema, with runnable examples and a changelog (coordinate `docs-support-readiness`).

## Out of scope
- Consuming external APIs/MCP → `external-integration`. Internal architecture → `architecture-reviewer`. User/support documentation → `docs-support-readiness`.
