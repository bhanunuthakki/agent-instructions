# Model Cost/Performance Frontier

**Last refreshed: 2026-09-05 for OpenAI GPT-6 Astra; other rows retain their row-level verification dates. Next review: 2026-09-09.** Cross-provider blended cost-per-MTok, ordered cheapest → most expensive. Read this before answering model-cost questions; see `SKILL.md` for the formula and cheapest-at-parity procedure.

Blended sort key: `(6 * input + 1 * output) / 7` (input weighted 6:1 over output). Prices are public list API prices in USD per million tokens (per-MTok), standard context tier (≤200K) where a model charges a long-context premium. Claimed strengths are discovery hints only. A model is qualified for a role only by a current representative evaluation receipt; no row below is permission to issue a blocking verdict.

| Model id in code | Provider | Input $/MTok | Output $/MTok | Blended $/MTok | Context | Claimed strengths | Price/spec verified | Source |
|---|---|---:|---:|---:|---:|---|---|---|
| `deepseek/deepseek-v4-flash` | OpenRouter | 0.04 | 0.08 | 0.05 | 1M | Ultra-cheap / classify · filter · high-volume mechanical | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gpt-5.6-luna` | OpenAI | 0.20 | 1.20 | 0.34 | 1.05M | Efficient / classify · extract · high-volume | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-luna) |
| `qwen/qwen-2.5-72b-instruct` | OpenRouter | 0.35 | 0.40 | 0.36 | 128K | Open-weight workhorse / structured extract · translation | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `deepseek/deepseek-chat` | OpenRouter | 0.26 | 1.03 | 0.37 | 128K | Open-weight value / general reasoning · coding · synthesis | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gemini-3.1-flash-lite` | Google | 0.25 | 1.50 | 0.43 | 1M | Cheap Google / classify · routing · short tasks | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.5-flash-lite` | Google | 0.30 | 2.50 | 0.61 | 1M | Cheapest Google / classify · structured-extract · high-volume | 2026-08-25 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `deepseek/deepseek-r1` | OpenRouter | 0.70 | 2.50 | 0.96 | 128K | Open-weight reasoning / math · logic · hard classification | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gemini-3.7-flash` | Google | 0.75 | 3.75 | 1.18 | 1M | Fast flagship (intro price) / agentic · multimodal · code | 2026-09-02 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-haiku-4-5` | Anthropic | 1.00 | 5.00 | 1.57 | 200K | Mechanical worker / extract · inventory · parallel pre-scan | 2026-09-02 | [platform.claude.com/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| `gemini-3.5-flash` | Google | 1.50 | 9.00 | 2.57 | 1M | Fast-premium / agentic · reasoning-light | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-sonnet-5` | Anthropic | 2.00 | 10.00 | 3.14 | 1M | Workhorse / spec'd implementation · audits · agentic execution | 2026-09-02 | [platform.claude.com/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| `gemini-3.1-pro-preview` | Google | 2.00 | 12.00 | 3.43 | 1M | High (current-gen Pro) / reasoning · agentic · vision | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gpt-5.6-terra` | OpenAI | 2.00 | 12.00 | 3.43 | 1.05M | Balanced workhorse / spec'd impl · prose · reasoning | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-terra) |
| `gpt-5.6-sol` | OpenAI | 4.00 | 20.00 | 6.29 | 1.05M | Architecture · complex agents · hard judgment | 2026-09-02 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| `claude-opus-5` | Anthropic | 5.00 | 25.00 | 7.86 | 1M | Complex reasoning · verification · long-horizon work | 2026-09-02 | [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview) |
| `claude-fable-5` | Anthropic | 10.00 | 50.00 | 15.71 | 1M | Frontier orchestrator / long-horizon judgment · synthesis · review | 2026-09-02 | [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview) |
| `gpt-6-astra` | OpenAI | 10.00 | 50.00 | 15.71 | 1.05M | Frontier candidate / complex reasoning · coding · computer use · research · documents | 2026-09-05 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-6-astra) |

**Notes on the rows above:**
- Gemini Pro tiers (`gemini-3.1-pro-preview`) charge a long-context premium above 200K tokens (roughly 2× input, ~1.5× output). The blended figure here uses the ≤200K rate; re-blend at the premium rate for purposes that routinely exceed 200K input.
- Gemini 3.7 Flash lists an introductory rate ($0.75/$3.75) through 2026-12-31; reverts to standard $1.50/$7.50 on 2027-01-01.
- Sonnet 5's introductory $2/$10 rate became its standard price; Anthropic states the previously scheduled 2026-09-01 increase will not occur.
- OpenRouter rates reflect pass-through provider pricing. OpenRouter adds a standard ~5% credit deposit fee.
- Named models remain candidates until their intended role has a dated representative receipt. Opus 5's proactive verification means prompts should remove redundant verification/subagent mandates when the task does not independently require them; Fable 5 guidance likewise favors lean context, explicit interfaces, and progressive disclosure over repeated rules.
- GPT-5.6 Luna, Terra, and Sol charge a long-context premium above 272K input tokens (2× input and 1.5× output for the full request). Their blended figures use the standard-context rate. Subscription-backed Codex calls still record these public API-equivalent prices so cross-provider comparisons remain meaningful; they do not represent an incremental membership bill.

## GPT-6 Astra refresh — 2026-09-05

- **Availability and limits:** OpenAI lists `gpt-6-astra` for paid API tiers 1–5 (Free unsupported); account access remains `(verify)` before use. It accepts text/image input and produces text, with 128K maximum output tokens. Structured outputs, streaming, and function calling are supported. [Model specifications](https://developers.openai.com/api/docs/models/gpt-6-astra).
- **Economics:** Standard uncached blend is `(6 × 10 + 50) / 7 = $15.71/MTok`. Above 272K input tokens, full-request input/cache rates double and output rises 1.5×: $20/$75, blended $27.86. Standard cached reads cost $1/MTok and cache writes $12.50/MTok; Batch/Flex cost half Standard and Fast costs twice the applicable rates. [Pricing and limits](https://developers.openai.com/api/docs/models/gpt-6-astra).
- **Integration constraints:** API reasoning efforts are `low`, `medium`, `high`, `xhigh`, and `max`; runtime-specific effort labels are not API guarantees. Tool calling requires Responses. Check unsupported parameters and Fast-mode residency restrictions before migration. Async tools and mid-turn steering require application support. [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra).
- **Evaluation targets:** Astra challenges the frontier-synthesizer candidate set for architecture, complex agent execution, research/document synthesis, and consequential review. Include registered `specialist` and `risk` review purposes when considering Astra for those roles, preserving independence requirements. Existing project incumbents require inspection through their own purpose registries before proposing changes; this refresh does not establish a fleet-wide purpose inventory.
- **Qualification:** Astra ties the recorded Fable 5 token-price blend and costs 2.5× the recorded Sol rates. OpenAI reports lower task cost in some evaluations through fewer output tokens; that is a reason to measure complete-task quality, attempts, latency, and cost locally, not evidence of local parity or dominance. Astra remains `candidate_only`; no routing pins or Judge qualifications change. [Provider claim](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra).

## Evaluation receipt registry

For each production or audit purpose, record: `purpose`, `capability_role`, `model_id`, `dataset/version`, `quality threshold`, `result`, `evaluated_at`, and `expires_at`. Price verification and capability qualification are separate receipts. Open-weight models use the same bar as hosted models. Expired or missing receipts make a model `candidate_only` for blocking or frontier work.

## Annualized-cost framing

Blended $/MTok ranks models; it does not estimate a bill. To project a purpose's yearly cost, use its **measured** input/output token split, not the blended figure:

```
cost_per_call   = (avg_input_tokens  / 1e6) * input_usd_per_mtok
                + (avg_output_tokens / 1e6) * output_usd_per_mtok
annual_usd      = cost_per_call * calls_per_month * 12
```

The output-heavy a model is, the more its blended rank understates its real cost — and vice versa. A purpose that writes long answers (high output share) is cheaper to move down-tier than the blended column suggests; a near-pure-classification purpose (tiny output) tracks the input price. Always compute against the real split before recommending a switch, and pair the projection with a parity eval (`SKILL.md` → cheapest-at-parity).
