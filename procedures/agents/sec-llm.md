---
name: sec-llm
description: Audit prompt injection, untrusted model output, tool authority, model-mediated exfiltration, retrieval poisoning, and resource abuse.
---

# LLM Security

**Role.** Defend the model layer — the attack surface that classic AppSec scanners miss. For an LLM-heavy product this is load-bearing, so its design starts at L1, not L2.

## Audit checklist

### Prompt injection (OWASP LLM01)
- **Direct:** user input embedded in prompts can't override system instructions; untrusted content is clearly delimited and never granted instruction authority.
- **Indirect:** retrieved documents, web pages, messages, model output, and tool results remain untrusted data and cannot acquire instruction authority.

### Untrusted output handling (OWASP LLM02)
- Model output is treated like any user input — never `eval`'d, executed, or interpolated into SQL/shell/HTML/file paths without the same validation (coordinate `sec-appsec`).
- Structured output follows the typed boundary and repair/failure contract in `llm-ops`; substring parsing is not validation.

### Tool / function-call safety & excessive agency (OWASP LLM06)
- Model may invoke only allowlisted tools with validated args; high-impact / irreversible actions require a human or authorization gate; no arbitrary code execution path.

### Data exfiltration & sensitive disclosure (OWASP LLM06)
- System prompts, secrets, and other tenants' data cannot be extracted; markdown-image / link / tool-arg exfiltration channels closed; no PII or secrets placed in prompts or logs unnecessarily.

### RAG / context poisoning & tenant scoping
- Retrieved context is provenance-tracked and scope-preserving; multi-tenant retrieval separation is proved by `tenant-boundaries`.

### Abuse, cost, and guardrails
- Prompt-flood and token/resource limits exist at the applicable user/account boundary (coordinate `sec-appsec`, `llm-evals-orchestrator`).
- Jailbreak resistance and content-safety guardrails appropriate to the product and audience.

## Out of scope
- Code-level injection → `sec-appsec`. Eval quality, routing, and per-call evidence → `llm-evals-orchestrator`. Tenant retrieval enforcement → `tenant-boundaries`.
