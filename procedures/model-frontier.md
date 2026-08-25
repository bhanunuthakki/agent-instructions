---
name: model-frontier
description: Pick a hosted or open-weight LLM/runtime candidate against a dated cost and capability frontier instead of from memory. Use for model cost comparisons, cheapest-at-parity routing, annual cost estimates, per-purpose model selection, or /refresh-frontier.
---

# Model Frontier

`REFERENCE.md` is the dated candidate table across the providers and runtimes actually evaluated. Read it before answering a price or routing question. A stale row is evidence to refresh, not authority.

This procedure owns candidate economics. Shared call governance lives in `llm-ops`; evaluation depth lives in `llm-ops.EVALS.md`; independent task judging lives in `judging`. Do not use one purpose's receipt as evidence for another.

## Candidate records

Hosted rows record the exact model identifier, provider/runtime, input and output prices, declared context, availability, verification date, and primary source. Open-weight rows bind model, runtime, quantization, hardware, throughput, tail latency, energy or hosting cost, amortized hardware assumptions where material, availability, failure behavior, verification date, and sources.

Application code owns its routing field names. This shared procedure never assumes a project registry such as `LLM_MODELS` or `model_pin_overrides`.

## Search-order economics

The dated reference may publish a clearly labeled input/output weighting for rough hosted-model search ordering:

```text
blended_usd_per_mtok =
  (input_weight * input_usd_per_mtok + output_weight * output_usd_per_mtok)
  / (input_weight + output_weight)
```

That heuristic is not a billing estimate or a universal workload model. For a real purpose, use its measured input/output split and attempt rate. For open-weight candidates, use total runtime economics rather than inventing a token price.

## Cheapest-at-parity selection

1. Identify the incumbent runtime/model tuple for the named purpose and its measured workload, quality contract, latency, failures, and cost basis.
2. Order candidates with a credible lower total cost for that purpose. Hosted blended cost is only a search heuristic; open-weight cost includes runtime and hardware economics.
3. Evaluate candidates cheapest-first against the same representative purpose corpus, schema, failure contract, and owner-ratified threshold. Keep model/provider identities hidden from semantic graders when feasible.
4. Promote only when quality and failure behavior hold at parity and the economic improvement survives real token/runtime usage. Keep the incumbent on insufficient or conflicting evidence.
5. Store a promotion as reversible routing data and continue monitoring. A later regression clears or rolls back the override through the owning LLM procedure.

Exploration smoke tests can justify more exploration; they cannot authorize production promotion or qualify a blocking Judge.

## Sources and refresh

- Hosted candidate: current official provider model, capability, availability, and pricing documentation.
- Open-weight candidate: publisher's canonical model card and license plus the selected runtime's official documentation; measure the actual runtime/model/quantization/hardware tuple locally when economics or performance matters.
- Secondary benchmarks may identify candidates but never replace current primary documentation or representative local evaluation.

Refresh on the documented cadence and when a relevant provider, model, runtime, price, license, or hardware assumption changes. `/refresh-frontier` re-verifies only candidates actually under consideration and restamps only rows checked in that pass.

## Anti-patterns

- Selecting from memory or provider reputation.
- Treating a context window, parameter count, or model launch date as capability evidence.
- Recommending a downgrade without purpose-specific parity evidence.
- Comparing open-weight and hosted candidates on token price alone.
- Hiding runtime, quantization, hardware, latency, or failure differences.
- Hardcoding a model at call sites rather than routing a named purpose.
