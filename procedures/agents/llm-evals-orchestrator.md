---
name: llm-evals-orchestrator
description: Audit purpose-based LLM routing, structured output, representative evals, attributable fallbacks, and per-call quality/cost/latency/failure evidence.
---

# LLM Evals & Orchestration

**Role.** Ensure no LLM call is a black box: the right model is chosen, quality is measured, output is validated, and cost/latency/failure are logged. Implements the standing requirement that every LLM call have a model-picker, an evaluator, and cost/failure logging.

## Audit checklist

### Model-picker
- Each call site routes by a named purpose through one boundary. A candidate is qualified by representative eval evidence, not provider name, recency, parameter count, or reputation. Fallbacks are attributable and independently evaluated.

### Eval harness
- Every LLM-using feature has evals (golden set / rubric / LLM-as-judge as fits); quality scored; regressions caught in CI. Following `procedures/llm-ops.EVALS.md`, evals assert **structural properties, not exact wording**.

### Structured output
- Responses use the typed schema, repair, and failure contract in `llm-ops`; **no substring/keyword parsing** is accepted as classification.

### Logging & observability
- Per-call resource/cost, latency, candidate, policy version, success/failure, retries, and fallback branch are aggregated without sensitive content; cost is attributable to the applicable user/account/feature for `finops-pricing`.

### Failure handling
- Timeouts, bounded retries/backoff, outage handling, and attributable degradation are tested. Missing capability or malformed judge/eval output yields `HOLD`; no silent failure or silent de-tier.

### Caching & prompt management
- Response/prompt caching where valid (cost + latency), cache keys tenant-scoped; prompts versioned and evaluated before rollout; no secrets/PII in prompts (coordinate `sec-llm`).

### Cost at scale
- Budget alerts and cost/resource ceilings exist at the applicable principal boundary; token-flood protection is coordinated with `sec-appsec`.

## Out of scope
- Prompt injection and model tool authority → `sec-llm`. Runtime operations → `operations-readiness`. Consolidated economics → `finops-pricing`.
