---
name: llm-ops
description: Govern an LLM-backed feature with one entry point, purpose-based model selection, schema-validated output, attributable fallbacks, per-call cost and latency logging, and representative evals. Use when adding or changing an LLM call, model router, prompt, judge, eval, fallback, or budget.
---

# LLM Ops

An LLM call is complete only when its selection, contract, cost, failures, and quality can be inspected independently of the model’s prose.

## Start at the seam

1. Inventory active provider calls, model strings and aliases, prompts, tools, parsers, fallbacks, budgets, and evals.
2. Identify the user-visible purpose and whether the output is deterministic data, classification, prose judgment, or an action proposal.
3. Run `external-practice` for current model, endpoint, tool, caching, and provider behavior. Use `model-frontier` for current price and performance; do not select from memory.
4. Preserve existing behavior and effective reasoning as the baseline before changing model, prompt, or transport.

## Build order

1. Route every call through one typed entry point.
2. Select a provider-qualified model by a closed, named purpose.
3. Validate structured output with Pydantic, Zod, or an equivalent schema. Retry a malformed response once with the validation failure, then raise a domain error.
4. Record every attempt and fallback with model, provider, transport, token counts, public-list cost estimate, latency, retries, result, and safe error classification.
5. Attach a representative eval to each purpose before trusting it.
6. Enforce a purpose-specific budget before the call and keep operational fallback distinct from budget or configuration failure.

Read only the reference needed for the task:

- Core API, schemas, ledger, budgets, and completion contract: [llm-ops.CONTRACTS.md](llm-ops.CONTRACTS.md)
- Golden sets, rubric judges, downgrade gates, and judge governance: [llm-ops.EVALS.md](llm-ops.EVALS.md)
- This machine’s subscription wrappers, isolation, fallback order, and metered exception: [llm-ops.TRANSPORTS.md](llm-ops.TRANSPORTS.md)

## Decision rules

- Use deterministic code for calculations, eligibility, thresholds, state transitions, and authorization. Use the model for synthesis or judgment inside that deterministic envelope.
- A deliberate fallback announces the branch and reason in structured telemetry. If it returns a value, stamp the value with the producing path when downstream logic depends on provenance.
- Do not classify with keyword or substring matching when a schema enum expresses the result.
- Do not return `{}`, `[]`, `None`, or a guessed value after parse or provider failure; these are indistinguishable from legitimate empty results.
- Keep prompts outcome-focused: purpose, relevant evidence, hard constraints, output schema, success criteria, authority boundary, and stop condition. Remove repeated rules and examples unless an eval shows they correct a real gap.
- Treat prompt changes, model changes, reasoning changes, and optional provider features as separate treatments so regressions remain attributable.

## Completion

For every affected purpose report the entry point, target model role, effective reasoning, schema, fallback chain, budget, eval, and validation evidence. State unchanged or ambiguous call sites explicitly. A model-string edit alone is not a migration.
