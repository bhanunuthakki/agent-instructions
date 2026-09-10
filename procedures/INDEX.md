# Procedure routing and composition

This catalog is the fallback when native skill discovery is unavailable. `GLOBAL.md` owns cross-project invariants; this index owns workflow selection, and each linked procedure owns its decision flow. Read the selected body completely, then only its applicable references. A task may need several owners; one decision must not have competing owners.

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
| Any substantive task, at its start and each discovery, implementation, verification, or recovery transition | [agent-operations](agent-operations.md) owns the delegation check even when the result is serial execution; the root retains synthesis and final judgment |
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

## Share one contract and evidence record

The primary owner carries the requested outcome and authorized actions. This record may remain implicit for straightforward work; it does not require a file or user-facing form. Additional owners contribute their boundary constraints and acceptance evidence to that same contract. The global contract owns collaboration, questions, and completion; procedures do not restart discovery or generate separate handoffs. Load a reference or specialist only when an actual decision or risk needs it. A qualified existing LLM route does not require a fresh model comparison; a small fix does not require product discovery; a new persisted identity does require data semantics. A documented project restriction remains binding until changed through its named authority.
