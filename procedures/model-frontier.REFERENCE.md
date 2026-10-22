# Model Cost/Performance Frontier

**Last refreshed: 2026-10-21 for GPT-6 Luna, GPT-6.1 Sol, GPT-6 Astra, Claude Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1, and Gemini 4 Argon. Other rows retain their historical verification dates and require re-verification before a current selection. Next review: 2026-10-28.** Cross-provider blended cost-per-MTok, ordered cheapest → most expensive. Read this before answering model-cost questions; see `SKILL.md` for the formula and cheapest-at-parity procedure.

Blended sort key: `(6 * input + 1 * output) / 7` (input weighted 6:1 over output). Prices are public list API prices in USD per million tokens (per-MTok), the lowest prompt-length tier where a model charges a long-context premium (Haiku 5.5: ≤100K; OpenAI GPT-6 rows: ≤272K; historical Gemini Pro: ≤200K). Claimed strengths are discovery hints only. A model is qualified for a role only by a current representative evaluation receipt; no row below is permission to issue a blocking verdict.

| Model id in code | Provider | Input $/MTok | Output $/MTok | Blended $/MTok | Context | Claimed strengths | Price/spec verified | Source |
|---|---|---:|---:|---:|---:|---|---|---|
| `deepseek/deepseek-v4-flash` | OpenRouter | 0.04 | 0.08 | 0.05 | 1M | Ultra-cheap / classify · filter · high-volume mechanical | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gpt-6-luna` | OpenAI | 0.10 | 0.50 | 0.16 | 1.05M | Efficient candidate / focused high-volume tasks | 2026-10-21 | [Luna specifications](https://developers.openai.com/api/docs/models/gpt-6-luna) |
| `claude-haiku-5-5` | Anthropic | 0.10 | 0.50 | 0.16 | 1M | Low-latency candidate / classify · extract · route; ≤100K prompt price | 2026-10-21 | [Haiku specifications](https://platform.claude.com/docs/en/models/haiku-5-5/overview) |
| `gpt-5.6-luna` | OpenAI | 0.20 | 1.20 | 0.34 | 1.05M | Efficient / classify · extract · high-volume | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-luna) |
| `qwen/qwen-2.5-72b-instruct` | OpenRouter | 0.35 | 0.40 | 0.36 | 128K | Open-weight workhorse / structured extract · translation | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `deepseek/deepseek-chat` | OpenRouter | 0.26 | 1.03 | 0.37 | 128K | Open-weight value / general reasoning · coding · synthesis | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gemini-3.1-flash-lite` | Google | 0.25 | 1.50 | 0.43 | 1M | Cheap Google / classify · routing · short tasks | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.5-flash-lite` | Google | 0.30 | 2.50 | 0.61 | 1M | Cheapest Google / classify · structured-extract · high-volume | 2026-08-25 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `deepseek/deepseek-r1` | OpenRouter | 0.70 | 2.50 | 0.96 | 128K | Open-weight reasoning / math · logic · hard classification | 2026-08-24 | [openrouter.ai/models](https://openrouter.ai/models) |
| `gemini-3.7-flash` | Google | 0.75 | 3.75 | 1.18 | 1M | Fast flagship (intro price) / agentic · multimodal · code | 2026-09-02 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-haiku-4-5` | Anthropic | 1.00 | 5.00 | 1.57 | 200K | Mechanical worker / extract · inventory · parallel pre-scan | 2026-09-02 | [platform.claude.com/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| `gemini-3.5-flash` | Google | 1.50 | 9.00 | 2.57 | 1M | Fast-premium / agentic · reasoning-light | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `claude-sonnet-5-5` | Anthropic | 2.00 | 10.00 | 3.14 | 1M | Workhorse candidate / implementation · multistep tool use | 2026-10-21 | [Sonnet specifications](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) |
| `gpt-6.1-sol` | OpenAI | 2.00 | 10.00 | 3.14 | 1.05M | Complex coding · computer use · professional work candidate | 2026-10-21 | [Sol specifications](https://developers.openai.com/api/docs/models/gpt-6.1-sol) |
| `gemini-4-argon` | Google | 2.00 | 10.00 | 3.14 | 1,048,576 shared input/output | Flagship candidate / reasoning · coding · agents; introductory price | 2026-10-21 | [Argon specifications](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon), [pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.1-pro-preview` | Google | 2.00 | 12.00 | 3.43 | 1M | High (current-gen Pro) / reasoning · agentic · vision | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gpt-5.6-terra` | OpenAI | 2.00 | 12.00 | 3.43 | 1.05M | Balanced workhorse / spec'd impl · prose · reasoning | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-terra) |
| `gpt-5.6-sol` | OpenAI | 4.00 | 20.00 | 6.29 | 1.05M | Architecture · complex agents · hard judgment | 2026-09-02 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol) |
| `claude-opus-5-5` | Anthropic | 4.00 | 20.00 | 6.29 | 1M | Long-running coding · knowledge work candidate | 2026-10-21 | [Opus specifications](https://platform.claude.com/docs/en/models/opus-5-5/overview) |
| `claude-fable-5-1` | Anthropic | 10.00 | 50.00 | 15.71 | 1M | Frontier orchestrator / demanding reasoning · long-horizon agentic work · judgment | 2026-10-21 | [Anthropic model overview](https://platform.claude.com/docs/en/models/fable-5-1/overview) |
| `gpt-6-astra` | OpenAI | 10.00 | 50.00 | 15.71 | 1.05M | Frontier orchestrator / hardest end-to-end reasoning · coding · research · computer use | 2026-10-21 | [OpenAI model page](https://developers.openai.com/api/docs/models/gpt-6-astra) |

**Notes on the rows above:**
- Gemini Pro tiers (`gemini-3.1-pro-preview`) charge a long-context premium above 200K tokens (roughly 2× input, ~1.5× output). The blended figure here uses the ≤200K rate; re-blend at the premium rate for purposes that routinely exceed 200K input.
- Gemini 3.7 Flash lists an introductory rate ($0.75/$3.75) through 2026-12-31; reverts to standard $1.50/$7.50 on 2027-01-01.
- Haiku 5.5 costs $0.10/$0.50 for prompts up to 100,000 tokens, and $0.50/$2.50 above that threshold (blended $0.79). Prompt length includes cache reads/writes; the higher tier applies to the request. Its newer tokenizer can use approximately 30% more tokens than Haiku 4.5 for the same text, so compare measured request cost.
- Argon costs $2/$10 through 2026-11-30 (blended $3.14), then $4/$20 from 2026-12-01 (blended $6.29). Output prices include thinking. Implicit cache reads cost $0.10, then $0.20; explicit caching is unsupported. Batch/Flex are half Standard; Priority is 1.8× Standard.
- Sonnet 5.5 remains $2/$10, Opus 5.5 $4/$20, and Fable 5.1 $10/$50. Their full 1M context is standard-priced. Existing pins and qualification history remain unchanged.
- Historical OpenRouter rows recorded pass-through pricing and an approximately 5% credit deposit fee; neither rates nor fees were re-verified in this pass.
- Named models remain candidates until their intended role has a dated representative receipt. Prompt guidance is version- and effort-specific; see `context-engineering.REFERENCE.md`. New intelligence claims do not remove local authority or evidence controls.
- Historical GPT-5.6 Luna, Terra, and Sol rows also recorded a >272K full-request premium of 2× input and 1.5× output. These older rates and limits were not re-verified in this refresh; verify them before a current cost comparison.
- GPT-6 Luna, GPT-6.1 Sol, and GPT-6 Astra charge a long-context premium above 272K input tokens (2× input and 1.5× output for the full request). Their blended figures use the standard-context rate. Subscription-backed Codex calls still record these public API-equivalent prices so cross-provider comparisons remain meaningful; they do not represent an incremental membership bill.

## Frontier orchestration and Judge tier — 2026-10-21

Formal blocking judgment names the provider-neutral `frontier-synthesizer` role. The dated frontier candidates here are `gpt-6-astra` and `claude-fable-5-1`; exact eligibility still requires a current receipt for the purpose. An unqualified candidate can provide clearly advisory evidence, never a blocking verdict. Routine work may retain its capable available root. The exact OpenAI subscription advisory default is owned by `config/judge_route.json`, not this candidate table; it does not confer frontier qualification. Explicit user model selection remains valid for advisory work.

## Targeted instruction applicability — 2026-10-21

The approved review covers GPT-6 Astra, Claude Opus 5.5, and Gemini 4 Argon (`gemini-4-argon`). [Google's Argon model page](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon), checked 2026-10-21, establishes its identity; the user confirmed Argon as the intended model. This is a candidate identity and prompting update, not a refresh of old price rows, account access, or local capability receipts. See `context-engineering.REFERENCE.md` for task-specific prompting guidance. No cross-model parity or blocking-Judge qualification is claimed.

## Requested refresh — 2026-10-21

This pass checks the eight named candidates above against current primary documentation. Older rows, introductory-rate notes for older Gemini models, and open-weight economics remain historical. No account access test, native model call, parity evaluation, or blocking-Judge qualification was run.

- **Anthropic availability and integration:** The [current lineup](https://platform.claude.com/docs/en/models/overview) lists Fable 5.1, Opus 5.5, Sonnet 5.5, and Haiku 5.5. Each accepts text/images, produces text, and lists 1M context and 128K standard maximum output. Opus/Haiku default to `medium` effort; Fable/Sonnet to `high`. Opus/Fable thinking is always on. All list Claude API and cloud distribution; account access remains `(verify)`. Fable 5.5 remains unverified; do not substitute an invented alias. [Opus](https://platform.claude.com/docs/en/models/opus-5-5/overview), [Sonnet](https://platform.claude.com/docs/en/models/sonnet-5-5/overview), [Fable](https://platform.claude.com/docs/en/models/fable-5-1/overview), [Haiku](https://platform.claude.com/docs/en/models/haiku-5-5/overview).
- **Anthropic economics and migration:** Cache reads per MTok: Sonnet $0.10, Opus $0.20, Fable $0.25; Haiku $0.01 up to 100K prompt tokens and $0.05 above. Sonnet's earlier $0.20 cache figure was incorrect. Batch halves token prices. Opus Fast is $8/$40; regional processing can add 10%. Verify model-switch thinking compatibility, forced-tool constraints, computer-use versions, and progress-display handling before migration. [Pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- **OpenAI Sol/Astra:** Both list 1,050,000 context, 128,000 maximum output, text/image input, text output, structured outputs, and streaming. API efforts: `low`, `medium`, `high`, `xhigh`, `max`; Sol defaults to `medium`. Use Responses for tool calling. Current pages list paid Build/Launch/Grow tiers, not the older numbered tiers. Account access remains `(verify)`. Sol input/cache-read/cache-write/output is $2/$0.10/$2.50/$10; Astra is $10/$1/$12.50/$50 per MTok. Above 272K input, full-request input/cache doubles and output rises 1.5×: blends $5.57 and $27.86. Batch/Flex halve Standard; Fast doubles it. Sol Ultrafast is 6× Standard. [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
- **OpenAI Luna:** `gpt-6-luna` lists 1,050,000 context, 128,000 maximum output, text/image input and text output. Default effort is `medium`; `none` is also supported. Responses supports tools; Chat Completions function calling requires `none`. Standard input/cache-read/cache-write/output is $0.10/$0.01/$0.125/$0.50 per MTok. The >272K full-request premium is 2× input/cache and 1.5× output (blended $0.28). Batch/Flex halve Standard and Fast doubles it; regional processing can add 10%. Availability in this account remains `(verify)`. [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).
- **Google Argon:** Stable `gemini-4-argon` accepts text, images, audio, video, and PDFs, and produces text. Its 1,048,576-token window is shared by input, thinking, and output. Default synchronous maximum output is 65,536; long decode can extend to remaining context through background execution or explicit continuation. Default thinking is `medium`, with `low` and `high` available. Function calling, structured outputs, code execution, and preview computer use are documented. Gemini API/AI Studio availability is documented; no Free tier, and account access remains `(verify)`. Price dates are recorded above. [Model](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon), [migration](https://ai.google.dev/gemini-api/docs/latest-model), [pricing](https://ai.google.dev/gemini-api/docs/pricing).

### Purposes challenged for evaluation

These are evaluation candidates, not observed parity or dominance findings. Inspect each project's actual purpose registry before repinning; no fleet-wide purpose inventory was run.

- Haiku 5.5 and Luna 6 challenge older Haiku/Luna classification, extraction, routing, inventory, and mechanical-worker purposes; include tokenizer differences, prompt thresholds, retries, and measured token use.
- Sonnet 5.5 and Sol 6.1 challenge older implementation, tool-use, and complex-work incumbents; Opus 5.5 challenges long-running coding and knowledge-work purposes. Compare task cost against frontier-tier use where quality permits.
- Argon challenges older Gemini Pro/Flash reasoning, multimodal, and agent purposes; compare all three thinking levels and include the December price increase, shared output budget, and continuation/storage behavior.
- Astra and Fable remain frontier candidates for demanding orchestration, synthesis, and separately registered `specialist`/`risk` Judge purposes. Preserve existing role mappings until purpose-specific evidence supports a change. The advisory Judge route is unchanged.

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
