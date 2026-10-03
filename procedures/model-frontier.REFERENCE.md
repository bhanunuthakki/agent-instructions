# Model Cost/Performance Frontier

**Last refreshed: 2026-10-02 for Claude Opus 5.5, Sonnet 5.5, Fable 5.1, GPT-6.1 Sol, and GPT-6 Astra. Other rows retain their historical verification dates and require re-verification before a current selection. Next review: 2026-10-09.** Cross-provider blended cost-per-MTok, ordered cheapest → most expensive. Read this before answering model-cost questions; see `SKILL.md` for the formula and cheapest-at-parity procedure.

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
| `claude-sonnet-5-5` | Anthropic | 2.00 | 10.00 | 3.14 | 1M | Workhorse candidate / implementation · multistep tool use | 2026-10-02 | [Sonnet specifications](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) |
| `gpt-6.1-sol` | OpenAI | 2.00 | 10.00 | 3.14 | 1.05M | Complex coding · computer use · professional work candidate | 2026-10-02 | [Sol specifications](https://developers.openai.com/api/docs/models/gpt-6.1-sol) |
| `gemini-3.1-pro-preview` | Google | 2.00 | 12.00 | 3.43 | 1M | High (current-gen Pro) / reasoning · agentic · vision | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gpt-5.6-terra` | OpenAI | 2.00 | 12.00 | 3.43 | 1.05M | Balanced workhorse / spec'd impl · prose · reasoning | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-terra) |
| `gpt-5.6-sol` | OpenAI | 4.00 | 20.00 | 6.29 | 1.05M | Architecture · complex agents · hard judgment | 2026-09-02 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| `claude-opus-5-5` | Anthropic | 4.00 | 20.00 | 6.29 | 1M | Long-running coding · knowledge work candidate | 2026-10-02 | [Opus specifications](https://platform.claude.com/docs/en/models/opus-5-5/overview) |
| `claude-fable-5-1` | Anthropic | 10.00 | 50.00 | 15.71 | 1M | Frontier orchestrator / demanding reasoning · long-horizon agentic work · judgment | 2026-10-02 | [Anthropic model overview](https://platform.claude.com/docs/en/models/fable-5-1/overview) |
| `gpt-6-astra` | OpenAI | 10.00 | 50.00 | 15.71 | 1.05M | Frontier orchestrator / hardest end-to-end reasoning · coding · research · computer use | 2026-10-02 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-6-astra) |

**Notes on the rows above:**
- Gemini Pro tiers (`gemini-3.1-pro-preview`) charge a long-context premium above 200K tokens (roughly 2× input, ~1.5× output). The blended figure here uses the ≤200K rate; re-blend at the premium rate for purposes that routinely exceed 200K input.
- Gemini 3.7 Flash lists an introductory rate ($0.75/$3.75) through 2026-12-31; reverts to standard $1.50/$7.50 on 2027-01-01.
- The current Sonnet 5.5 rate is $2/$10. Earlier Sonnet 5 and Opus 5 rows were replaced in this discovery table; existing pins and their qualification history remain unchanged.
- OpenRouter rates reflect pass-through provider pricing. OpenRouter adds a standard ~5% credit deposit fee.
- Named models remain candidates until their intended role has a dated representative receipt. Prompt guidance is version- and effort-specific; see `context-engineering.REFERENCE.md`. New intelligence claims do not remove local authority or evidence controls.
- Historical GPT-5.6 Luna, Terra, and Sol rows also recorded a >272K full-request premium of 2× input and 1.5× output. These older rates and limits were not re-verified in this refresh; verify them before a current cost comparison.
- GPT-6.1 Sol and GPT-6 Astra charge a long-context premium above 272K input tokens (2× input and 1.5× output for the full request). Their blended figures use the standard-context rate. Subscription-backed Codex calls still record these public API-equivalent prices so cross-provider comparisons remain meaningful; they do not represent an incremental membership bill.

## Frontier orchestration and Judge tier — 2026-10-02

Shared orchestration and judging rules name the provider-neutral `frontier-synthesizer` role. Its current model candidates are `gpt-6-astra` and `claude-fable-5-1`: keep one at the root for orchestration and final acceptance, and use a separately briefed one for each formal Judge seat. Exact selection depends on host availability and a current receipt for the purpose; an unqualified candidate may provide advisory evidence but cannot issue a blocking verdict. Delegate bounded execution to the cheapest evaluated worker that meets that worker role, preserving escalation back to the root. This mapping is the single owner for current model names; do not copy them into shared skills or project prose.

## Requested refresh — 2026-10-02

- **Identity and availability:** Anthropic's current lineup lists `claude-opus-5-5`, `claude-sonnet-5-5`, and `claude-fable-5-1` as active. No official Fable 5.5 entry was found in the current overview or targeted official-source search; its identifier, price, and availability remain `(verify)`. Do not invent an alias or treat Fable 5.1 as Fable 5.5. All three listed Claude models accept text/images, produce text, and have 128K standard maximum output. Account access remains `(verify)`. [Current lineup](https://platform.claude.com/docs/en/models/overview).
- **Claude integration:** Opus 5.5 defaults to `medium` effort with thinking always on; Sonnet 5.5 defaults to `high` with adaptive thinking; Fable 5.1 defaults to `high` with thinking always on. Their overviews name Claude API, Bedrock, Google Cloud, Foundry, and Claude Platform on AWS. Cache-read rates are $0.20, $0.20, and $0.25/MTok respectively. Check model-switch thinking compatibility, forced-tool constraints, computer-use versions, and progress-display handling before migration. [Opus](https://platform.claude.com/docs/en/models/opus-5-5/overview), [Sonnet](https://platform.claude.com/docs/en/models/sonnet-5-5/overview), [Fable](https://platform.claude.com/docs/en/models/fable-5-1/overview).
- **OpenAI integration:** Sol 6.1 and Astra list 1,050,000 context and 128,000 maximum output tokens, text/image input, text output, structured outputs, and streaming. API effort levels are `low`, `medium`, `high`, `xhigh`, and `max`; Sol defaults to `medium`. Use Responses for tool calling. Runtime-only effort labels do not establish API support. Both list paid tiers 1–5; account access remains `(verify)`. [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
- **Economics:** Sonnet 5.5 and Sol 6.1 each blend to `(6 × 2 + 10) / 7 = $3.14/MTok`; Opus 5.5 to `(6 × 4 + 20) / 7 = $6.29`; Fable 5.1 and Astra to `(6 × 10 + 50) / 7 = $15.71`. Sol/Astra prompts above 272K input use full-request 2× input/cache and 1.5× output: Sol $4/$15, blended $5.57; Astra $20/$75, blended $27.86. Sol cache reads are $0.10 and writes $2.50; Astra reads $1 and writes $12.50. Batch/Flex halve Standard; Fast doubles applicable rates. Other service tiers and regional premiums require their own workload calculation. [Sol pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Astra pricing](https://developers.openai.com/api/docs/models/gpt-6-astra).
- **Evaluation targets:** Sonnet 5.5 challenges Sonnet 5 implementation and audit purposes; Opus 5.5 challenges Opus 5 long-running coding/knowledge purposes and the cost of Fable-class work; Sol 6.1 challenges older Sol/Terra complex-work purposes and Astra's task cost. Preserve the Astra/Fable frontier role mapping until purpose-specific evidence supports a change. Include architecture, research/document synthesis, agent execution, and separately registered `specialist`/`risk` Judge purposes where applicable. These are candidate challenges, not parity or dominance findings. Inspect each project's actual purpose registry before repinning; this refresh is not a complete fleet purpose inventory.
- **Qualification:** No new local parity evaluation or blocking-Judge qualification was run. Provider performance claims do not transfer incumbent qualification. Production routing policy, usage registries, and evaluation-harness defaults are unchanged.

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
