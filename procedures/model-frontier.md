---
name: model-frontier
description: Pick an LLM against the dated cross-provider cost/performance frontier instead of from memory. Use for model cost comparisons, cheapest-at-parity routing, annual cost estimates, per-purpose model selection, or /refresh-frontier. Covers current Anthropic Claude, OpenAI GPT/Codex, and Google Gemini tiers.
---

# Model Frontier

`REFERENCE.md` is the dated, blended cost-per-MTok table across Anthropic, OpenAI, and Google, ordered cheapest → most expensive. Read it before answering a price/routing question. A stale row is evidence to refresh, not authority.

This skill is the procedure; `REFERENCE.md` is the data. Shared call governance lives in `llm-ops`; review rigor and brand-blind judging live in `judging`. Do not restate those contracts here.

## How to read the reference

Each row is `{model id in code, provider, input $/MTok, output $/MTok, blended $/MTok, context, tier bucket, last-verified, source}`. Sort key is **blended $/MTok**. The `model id in code` column is the exact string you put in `LLM_MODELS` / `model_pin_overrides` / a `model=` arg — copy it verbatim, don't reconstruct it.

## Blended-cost formula (the sort key)

Output tokens cost more per token but a typical call reads far more than it writes, so weight input 6:1 over output (matches earnings-summary `model_ladder.blended_usd_per_mtok` and reproduces its Haiku anchor):

```
blended_usd_per_mtok = (6 * input_usd_per_mtok + 1 * output_usd_per_mtok) / 7
```

This is a ranking heuristic, not a billing estimate. For an actual cost projection of one purpose, use its real measured input/output token split (see the annualized example in `REFERENCE.md`), not the blended figure.

## Cheapest-at-parity selection procedure

1. Identify the **incumbent** model for the purpose (what it routes to today) and find its blended row.
2. Take every row **strictly cheaper** than the incumbent, in ascending blended order — that's the search order.
3. For each candidate cheapest-first: run the purpose's eval (golden set for classifiers/structured output; rubric or pairwise LLM-judge for prose/judgment). Stop at the first candidate that holds parity.
4. Switch only on parity + cross-judge agreement + a minimum sample, and auto-demote on regression (per `AGENTS.md`). A cheaper model that fails parity is not a candidate — keep the incumbent.
5. Token efficiency is a secondary signal: flag a candidate that uses >1.5× the incumbent's output tokens as a cost headwind even when quality holds; note <0.8× as extra savings. Never gate the switch on it alone — per-token price usually dominates.

**Default when you cannot run an eval:** recommend the incumbent, not the cheaper model. Cost-driven downgrades without a parity check are how silent quality regressions ship.

## Authoritative sources at refresh time

- Claude: current official Anthropic model and pricing pages.
- OpenAI: current official model guidance/model pages on `developers.openai.com`.
- Gemini: Google's official pricing page at `https://ai.google.dev/gemini-api/docs/pricing`.
- A runtime-native provider skill may help retrieve those sources, but no installed skill name is assumed. Verify every changed row directly; mark unconfirmed fields `(verify)`.

## Refresh cadence

Monthly, **and** on any model launch from either provider (a new tier reorders the frontier). `/refresh-frontier` re-runs the two sources above, recomputes blended values, re-sorts, and restamps `REFERENCE.md` with today's date. Bump the `last-verified` date only on rows you actually re-confirmed this pass.

## Anti-patterns

- Answering "which model is cheapest" from training memory instead of reading `REFERENCE.md`.
- Recommending a downgrade with no parity eval ("Gemini Flash is 8× cheaper, switch to it") — cheapest-at-*parity*, not cheapest.
- Inventing a price to one-cent precision when the source was ambiguous — mark `(verify)`.
- Hardcoding a model per call site instead of routing a *purpose* through the central picker.
- Treating an unavailable provider skill or a stale local cache as more authoritative than current official documentation.
- Comparing on input price or output price alone instead of the blended sort key.
