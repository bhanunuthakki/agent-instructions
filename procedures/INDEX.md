# Procedure routing and composition

This catalog selects workflows when native skill discovery is unavailable. `GLOBAL.md` owns shared invariants; this index owns selection and composition; each procedure owns its decision flow. Read the selected body completely, then only applicable references.

Compose workflows semantically, not by concatenating every instruction from every matching skill:

- Choose one primary owner for the requested deliverable. Additional skills contribute only the boundary, domain, or execution mechanics unique to them; they do not restart discovery, expand scope, duplicate evidence, or impose a second handoff.
- When one routing skill deliberately calls another, the caller keeps authority over why and when the callee runs. The callee supplies only the requested mechanics and may not reopen the selected route or broaden the deliverable.
- The most specific artifact or runtime owner governs its execution interface. The product or domain owner governs intended behavior and meaning. The closest project rulebook governs local commands and gates. `GLOBAL.md` governs communication, authority, and completion.
- Resolve incompatible defaults through that ownership order instead of trying to satisfy both. Preserve explicit user and template requirements. If two candidate owners still claim the same decision, stop loading more skills and resolve the routing ambiguity first.
- Modifiers such as Chisle can compress work across a code chat but never become a second deliverable owner. Formal specialist names such as `sec-authz` or `ux-design` are hardening rubrics, not ordinary skills; invoke them through `harden --audit <specialist>` only when a proportional audit is actually required.

## Select the requested deliverable

| Deliverable | Primary owner |
|---|---|
| Implement, fix, refactor, or review code | [code-change](code-change.md) |
| Define a material product behavior before implementation | [product-feature](product-feature.md) |
| Design or review a rendered interface | [frontend-quality](frontend-quality.md); [mockup-review](mockup-review.md) for a mockup-only deliverable |
| Assess or rewrite instructions, skills, or context ownership | [context-engineering](context-engineering.md) |
| Explain a substantial agent-written change | [explain-change](explain-change.md) |
| Explicit interview or unresolved consequential product choice | [grill-me](grill-me.md) |
| Compare a consequential vendor or build/buy choice | [tool-selector](tool-selector.md) |
| Verify a drift-sensitive external fact or design choice | [external-practice](external-practice.md) |
| Work through a strategic-finance, FP&A, BizOps, or operating case study in deliberate phases | [finance-case-study](finance-case-study.md) |
| Explicit Judge/Critic/Evaluation Suite or required semantic review | [judging](judging.md) |
| Maturity-gated audit or approved remediation | [harden](harden.md), with only the applicable specialist rubrics |
| Run the delegation check for any substantive task, delegate work, coordinate resources, schedule LLM work, or assess task closure | [agent-operations](agent-operations.md) |
| Synchronize Linear from an exact issue's branch/PR state | [linear-pr-sync](linear-pr-sync.md) |
| Reconcile Linear backlog, duplicates, dependencies, or stale pipeline states | [linear-pipeline-hygiene](linear-pipeline-hygiene.md) |
| Synchronize canonical instructions and runtime artifacts | [source-command-sync-agent-stubs](source-command-sync-agent-stubs.md) |

Ordinary answers and research need no artificial engineering workflow. Use applicable evidence, domain, and machine boundaries. Native artifact skills own documents, spreadsheets, presentations, and other runtime-supported deliverables.

## Add only the controls for boundaries actually touched

| Changed or uncertain boundary | Additional owner |
|---|---|
| Delegation assessment required by GLOBAL; bounded workers, coordination, or scheduling | [agent-operations](agent-operations.md) owns dispatch, capability, write ownership, and resource closure |
| Material user behavior in a build task | [product-feature](product-feature.md) owns outcome/acceptance; code-change owns implementation |
| Durable state, identity, migration, lineage, or recovery | [data-foundation](data-foundation.md) |
| Visible code change or isolated mockup | [frontend-quality](frontend-quality.md) owns interaction and rendered evidence, including when mockup-review owns the deliverable |
| New UI foundation | [scaffold-design-system](scaffold-design-system.md), after the task and hierarchy are understood |
| External capability consumed by the product | [external-integration](external-integration.md); tool-selector only if provider choice is unresolved |
| Application LLM purpose, prompt, schema, fallback, or budget | [llm-ops](llm-ops.md); instruction-system prose stays with context-engineering |
| Model selection, economics, or qualification needs a current comparison | [model-frontier](model-frontier.md); [source-command-refresh-frontier](source-command-refresh-frontier.md) for a requested registry refresh |
| New or changed network call, webhook, LLM transport, or network diagnostics | [log-redaction](log-redaction.md) owns credential-safe logs and exceptions, alongside the capability owner |
| Credential configuration or leak prevention | [scaffold-secrets](scaffold-secrets.md); add log-redaction when network diagnostics are affected |
| Product now needs identity, tenancy, or deployment | [scaffold-auth](scaffold-auth.md), [scaffold-tenant-schema](scaffold-tenant-schema.md), or [scaffold-deploy](scaffold-deploy.md), respectively |
| Durable domain meaning, public/persisted name, or vocabulary collision | [definitions](definitions.md); ordinary local identifiers do not trigger ratification |
| Deliberate temporary compromise of a normal implementation requirement | [iteration-shortcut](iteration-shortcut.md); ordinary isolated experiments are not automatically shortcuts |
| OpenRouter, Linear, configured credential source, or cross-machine operation | [machine-operations](machine-operations.md), before execution |

## Apply the selected route

GLOBAL owns the shared task understanding, collaboration, authority, and completion. The primary owner supplies the deliverable; additional owners contribute only their applicable constraints and evidence. Do not restart discovery or create separate handoffs. Load references or specialists for actual decisions or risks: reuse a qualified LLM route without a new comparison, skip product discovery for a small fix, and resolve semantics for a new persisted identity. Project restrictions remain binding until changed through their named authority.
