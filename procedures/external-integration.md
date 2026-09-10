---
name: external-integration
description: Add or audit an inbound external API, webhook, SDK, or MCP capability through a typed, least-privilege, observable adapter.
---

# External Integration

Own the contract for a capability the product consumes. A product-exposed contract belongs to the `api-surface-designer` hardening rubric when a formal review is required; invoke it through `harden --audit api-surface-designer`, not as a sibling skill.

1. Name the product job and minimum capability. Use `tool-selector` first when provider/build choice is unresolved.
2. Verify current primary documentation for authentication, scopes, endpoints/tools, schemas, pagination, rate limits, retries, idempotency, webhooks, data use/retention, terms, pricing, and deprecation/version behavior.
3. Put the provider behind one typed adapter. Validate external payloads before domain use; retain raw evidence only under an explicit sensitive-data lifecycle.
4. Use least-privilege credentials from typed secret configuration. Keep them out of URLs, arguments, logs, exceptions, fixtures, and model context.
5. Define timeout, retry/backoff, rate budget, cursor/checkpoint, cache/TTL, idempotency, partial failure, and attributable degradation. Do not silently coerce schema drift.
6. For webhooks, verify signatures and provider-account mapping before resolving local identity/tenant context; handle duplicates, replay, delay, and reordering.
7. Test success plus auth failure, rate limit, timeout, malformed/schema-drift payload, duplicate, partial page, and recovery/resume. Record provenance for consequential imported facts.
8. Document replacement/export seams and the exact current source evidence. Provider or capability failure is visible; no fabricated fallback data.

Use `data-foundation` for durable data. When the task's risk or release boundary requires a formal specialist review, route generic vulnerabilities, runtime behavior, and LLM-mediated content/tool risks through `harden --audit sec-appsec`, `harden --audit operations-readiness`, and `harden --audit sec-llm`, respectively. Do not load those rubric names as ordinary skills.
