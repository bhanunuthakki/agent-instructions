# Model Cost/Performance Frontier

**Last refreshed: 2026-07-21 for Anthropic and OpenAI rows; 2026-06-18 for Google rows. Next review: 2026-08-31.** Cross-provider blended cost-per-MTok, ordered cheapest → most expensive. Read this before answering model-cost questions; see `SKILL.md` for the formula and cheapest-at-parity procedure.

Blended sort key: `(6 * input + 1 * output) / 7` (input weighted 6:1 over output). Prices are public list API prices in USD per million tokens (per-MTok), standard context tier (≤200K) where a model charges a long-context premium. Capability bucket is a coarse routing hint, not a benchmark.

| Model id in code | Provider | Input $/MTok | Output $/MTok | Blended $/MTok | Context | Tier / capability bucket | Last-verified | Source |
|---|---|---:|---:|---:|---:|---|---|---|
| `gemini-2.5-flash-lite` | Google | 0.10 | 0.40 | 0.14 | 1M | Cheapest / classify · structured-extract · high-volume | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.1-flash-lite` | Google | 0.25 | 1.50 | 0.43 | 1M | Cheap / classify · routing · short tasks | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.5-flash` | Google | 0.30 | 2.50 | 0.61 | 1M | Fast / structured-extract · summarize · classify | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3-flash-preview` | Google | 0.50 | 3.00 | 0.86 | 1M | Fast (current-gen) / summarize · extract · agentic-light | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-haiku-4-5` | Anthropic | 1.00 | 5.00 | 1.57 | 200K | Mechanical worker / extract · inventory · parallel pre-scan | 2026-07-21 | [anthropic.com/claude/haiku](https://www.anthropic.com/claude/haiku) |
| `gpt-5.6-luna` | OpenAI | 1.00 | 6.00 | 1.71 | 1.05M | Efficient / classify · extract · high-volume | 2026-07-21 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-luna) |
| `gemini-2.5-pro` | Google | 1.25 | 10.00 | 2.50 | 1M | Mid / reasoning · long-context · analysis | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.5-flash` | Google | 1.50 | 9.00 | 2.57 | 1M | Fast-premium / agentic · reasoning-light | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-sonnet-5` | Anthropic | 2.00 | 10.00 | 3.14 | 1M (verify) | Workhorse / spec'd implementation · audits · agentic execution | 2026-07-21 | [Anthropic launch pricing](https://www.anthropic.com/news/claude-sonnet-5) |
| `gemini-3.1-pro-preview` | Google | 2.00 | 12.00 | 3.43 | 1M | High (current-gen Pro) / reasoning · agentic · vision | 2026-06-18 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gpt-5.6-terra` | OpenAI | 2.50 | 15.00 | 4.29 | 1.05M | Balanced workhorse / spec'd impl · prose · reasoning | 2026-07-21 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-terra) |
| `claude-opus-4-8` | Anthropic | 5.00 | 25.00 | 7.86 | 1M | Heavy general reasoning / fallback for safeguarded Fable domains | 2026-07-21 | [anthropic.com/claude/opus](https://www.anthropic.com/claude/opus) |
| `gpt-5.6-sol` | OpenAI | 5.00 | 30.00 | 8.57 | 1.05M | Frontier / architecture · complex agents · hard judgment | 2026-07-21 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| `claude-fable-5` | Anthropic | 10.00 | 50.00 | 15.71 | 1M (verify) | Frontier orchestrator / long-horizon judgment · synthesis · review | 2026-07-21 | [anthropic.com/claude/fable](https://www.anthropic.com/claude/fable) |

**Notes on the rows above:**
- Gemini Pro tiers (`gemini-2.5-pro`, `gemini-3.1-pro-preview`) charge a long-context premium above 200K tokens (roughly 2× input, ~1.5× output). The blended figure here uses the ≤200K rate; re-blend at the premium rate for purposes that routinely exceed 200K input.
- Sonnet 5's $2/$10 launch pricing runs through 2026-08-31, then moves to $3/$15; refresh the row at that date. Its and Fable's context figures still need direct documentation confirmation.
- `gemini-3.1-pro-preview` / `gemini-3-flash-preview` are preview-channel IDs — confirm the GA string before pinning a production purpose to them.
- Fable is intentionally present despite being the most expensive row because it is the primary Claude orchestration tier; that policy role is not a cheapest-at-parity claim.
- GPT-5.6 Luna, Terra, and Sol charge a long-context premium above 272K input tokens (2× input and 1.5× output for the full request). Their blended figures use the standard-context rate. Subscription-backed Codex calls still record these public API-equivalent prices so cross-provider comparisons remain meaningful; they do not represent an incremental membership bill.

## Annualized-cost framing (the number that actually matters)

Blended $/MTok ranks models; it does not estimate a bill. To project a purpose's yearly cost, use its **measured** input/output token split, not the blended figure:

```
cost_per_call   = (avg_input_tokens  / 1e6) * input_usd_per_mtok
                + (avg_output_tokens / 1e6) * output_usd_per_mtok
annual_usd      = cost_per_call * calls_per_month * 12
```

**Worked example — a `qa_topics`-style extraction purpose, ~400 calls/month, ~8K input + ~600 output tokens per call:**

| Model | per-call | × 400/mo | × 12 = annual | vs Sonnet |
|---|---:|---:|---:|---:|
| `claude-sonnet-5` ($2 / $10 launch price) | $0.0220 | $8.80/mo | **$106/yr** | incumbent |
| `gemini-2.5-pro` ($1.25 / $10) | $0.0160 | $6.40/mo | **$77/yr** | −51% |
| `gemini-2.5-flash` ($0.30 / $2.50) | $0.0039 | $1.56/mo | **$19/yr** | −88% |

The output-heavy a model is, the more its blended rank understates its real cost — and vice versa. A purpose that writes long answers (high output share) is cheaper to move down-tier than the blended column suggests; a near-pure-classification purpose (tiny output) tracks the input price. Always compute against the real split before recommending a switch, and pair the projection with a parity eval (`SKILL.md` → cheapest-at-parity).
