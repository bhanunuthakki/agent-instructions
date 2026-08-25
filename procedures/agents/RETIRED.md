# Hardening rubric migrations

These former rubric names are not active gates. Use the owning replacement so findings are filed once:

| Former rubric | Replacement |
|---|---|
| `data-engineer` | `data-foundation` |
| `backend-multitenancy`, `sec-tenant-isolation` | `tenant-boundaries` |
| `infra-devops`, `infra-sre` | `operations-readiness` |
| `product-analytics-growth` | `product-analytics` |
| `customer-support`, `docs-devex` | `docs-support-readiness` |
| `notifications-email` | `sec-authz`, `payments`, `legal-compliance`, or `operations-readiness`, according to the finding |
| `content-marketing` | product work outside the hardening gate; in-product clarity remains with `ux-design` |
| `tool-selector` | standalone `procedures/tool-selector.md` |
| `api-mcp-ingestor` | standalone `procedures/external-integration.md` |

Generated runtime adapters must exclude former rubric names. Historical reports may retain them as provenance but may not satisfy a current gate.
