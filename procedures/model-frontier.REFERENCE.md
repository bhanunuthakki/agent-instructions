# Model Cost/Performance Frontier

**Last refreshed: 2026-10-24 for the OpenRouter open-weight candidates and endpoint economics below. Other rows retain their recorded verification dates and require re-verification before a current selection. Next review: 2026-10-31.** Cross-provider blended cost-per-MTok, ordered cheapest → most expensive. Read this before answering model-cost questions; see `SKILL.md` for the formula and cheapest-at-parity procedure.

Blended sort key: `(6 * input + 1 * output) / 7` (input weighted 6:1 over output). Prices are public list API prices in USD per million tokens (per-MTok), standard context tier (≤200K) where a model charges a long-context premium. OpenRouter rows use the cheapest sampled standard endpoint with reported 30-minute uptime ≥99%, ordered by the same 6:1 cost; exact endpoint slugs appear in the Provider column. These are provisional quotes before purpose-specific capability, privacy, and quantization checks, not production route selections. Claimed strengths are discovery hints only. A model is qualified for a role only by a current representative evaluation receipt; no row below is permission to issue a blocking verdict.

| Model id in code | Provider | Input $/MTok | Output $/MTok | Blended $/MTok | Context | Claimed strengths | Price/spec verified | Source |
|---|---|---:|---:|---:|---:|---|---|---|
| `z-ai/glm-5.3-flash` | OpenRouter (`open-inference/fp4`) | 0.018402 | 0.1062 | 0.03 | 1,048,576 | Value candidate / general reasoning · tools | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flash/endpoints), [model card](https://huggingface.co/zai-org/GLM-5.3-Flash) |
| `openai/gpt-oss-120b` | OpenRouter (`near-ai/fp4`) | 0.03 | 0.15 | 0.05 | 131,072 | Throughput alternative / evaluate task quality | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/openai/gpt-oss-120b/endpoints), [model card](https://huggingface.co/openai/gpt-oss-120b) |
| `deepseek/deepseek-v4-flash-0731` | OpenRouter (`baidu/fp8`) | 0.04444 | 0.13332 | 0.06 | 1,048,576 | Low-cost alternative / reasoning · coding | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4-flash-0731/endpoints), [model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) |
| `deepseek/deepseek-v4.1-flash` | OpenRouter (`baidu/fp8`) | 0.0537 | 0.2148 | 0.08 | 1,048,576 | Distinct checkpoint / do not inherit 1017 scores | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash/endpoints), [model card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) |
| `deepseek/deepseek-v4.1-flash-1017` | OpenRouter (`sail-research/fp4/us`) | 0.101 | 0.15 | 0.11 | 1,048,576 | Recent checkpoint / reasoning · coding | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/deepseek/deepseek-v4.1-flash-1017/endpoints), [model card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |
| `xiaomi/mimo-v2.6-flash` | OpenRouter (`io-net/fp8`) | 0.1 | 0.28 | 0.13 | 1,048,320 | Efficient candidate / extraction · tool tasks | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/xiaomi/mimo-v2.6-flash/endpoints), [model card](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL) |
| `z-ai/glm-5.3` | OpenRouter (`wafer/us`) | 0.079 | 1.4 | 0.27 | 1,048,576 | Stronger reasoning candidate / endpoint is FP4 | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/z-ai/glm-5.3/endpoints), [model card](https://huggingface.co/zai-org/GLM-5.3) |
| `gpt-5.6-luna` | OpenAI | 0.20 | 1.20 | 0.34 | 1.05M | Efficient / classify · extract · high-volume | 2026-09-02 | [developers.openai.com](https://developers.openai.com/api/docs/models/gpt-5.6-luna) |
| `gemini-3.1-flash-lite` | Google | 0.25 | 1.50 | 0.43 | 1M | Cheap Google / classify · routing · short tasks | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `xiaomi/mimo-v2.6-pro` | OpenRouter (`deepinfra/fp8`) | 0.387 | 0.783 | 0.44 | 1,048,576 | Higher-capability candidate / long tasks | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/xiaomi/mimo-v2.6-pro/endpoints), [model card](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Pro-RL) |
| `gemini-3.5-flash-lite` | Google | 0.30 | 2.50 | 0.61 | 1M | Cheapest Google / classify · structured-extract · high-volume | 2026-08-25 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-3.7-flash` | Google | 0.75 | 3.75 | 1.18 | 1M | Fast flagship (intro price) / agentic · multimodal · code | 2026-09-02 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `moonshotai/kimi-k3` | OpenRouter (`relace/fp4`) | 0.19 | 8.94 | 1.44 | 1,048,576 | Coding alternative / output-heavy cost | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/moonshotai/kimi-k3/endpoints), [model card](https://huggingface.co/moonshotai/Kimi-K3) |
| `claude-haiku-4-5` | Anthropic | 1.00 | 5.00 | 1.57 | 200K | Mechanical worker / extract · inventory · parallel pre-scan | 2026-09-02 | [platform.claude.com/pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| `gemini-3.5-flash` | Google | 1.50 | 9.00 | 2.57 | 1M | Fast-premium / agentic · reasoning-light | 2026-08-24 | [ai.google.dev/pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `qwen/qwen3.8-2.4t-a95b` | OpenRouter (`novita`) | 2 | 6 | 2.57 | 1,000,000 | Large open-weight alternative / quantization unknown | 2026-10-24 | [Endpoints](https://openrouter.ai/api/v1/models/qwen/qwen3.8-2.4t-a95b/endpoints), [model card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) |
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
- OpenRouter charges a credit-purchase fee: Standard 5.5%, Business 8%, separate from inference quotes. Apply the actual plan fee, transaction minimum, and taxes when estimating cash cost. [OpenRouter pricing](https://openrouter.ai/pricing), checked 2026-10-24.
- Named models remain candidates until their intended role has a dated representative receipt. Prompt guidance is version- and effort-specific; see `context-engineering.REFERENCE.md`. New intelligence claims do not remove local authority or evidence controls.
- Historical GPT-5.6 Luna, Terra, and Sol rows also recorded a >272K full-request premium of 2× input and 1.5× output. These older rates and limits were not re-verified in this refresh; verify them before a current cost comparison.
- GPT-6.1 Sol and GPT-6 Astra charge a long-context premium above 272K input tokens (2× input and 1.5× output for the full request). Their blended figures use the standard-context rate. Subscription-backed Codex calls still record these public API-equivalent prices so cross-provider comparisons remain meaningful; they do not represent an incremental membership bill.

## OpenRouter open-weight screening frontier — 2026-10-24

This is a bounded candidate list, not the full OpenRouter catalog or a deployment inventory. All ten sampled endpoints above reported 100% uptime in the last 30 minutes at inspection. Refresh their quotes and health before use. Short-window uptime is not a long-term service guarantee. Endpoint latency and throughput were not measured here. Hardware, exact served checkpoint, and parity with the publisher weights remain `(verify)`; quantization is endpoint-reported. No paid inference or local quality evaluation was run.

**Preliminary Pareto set:** minimize the unrounded 6:1 endpoint cost and maximize the OpenRouter-reported Artificial Analysis Intelligence Index within these ten candidates. A candidate is dominated only if another has no higher cost and no lower score, with at least one strict improvement. This is a screening proxy, not measured task parity or a claim about every workload.

| Candidate | Reported intelligence | Reported coding | Screening result |
|---|---:|---:|---|
| GLM 5.3 Flash | 41.8 | 71.5 | Frontier: $0.030945/MTok; first value candidate to evaluate |
| GLM 5.3 | 44.8 | 74.8 | Frontier: $0.267714/MTok; evaluate when Flash misses quality |
| MiMo V2.6 Pro | 46.3 | unavailable | Frontier: $0.443571/MTok; evaluate harder tasks |
| DeepSeek V4 Flash 0731 | 34.3 | 69.1 | Dominated on these axes; possible FP8 alternative |
| DeepSeek V4.1 Flash | 24.7 | unavailable | Dominated; distinct from the 1017 checkpoint |
| DeepSeek V4.1 Flash 1017 | 39.5 | unavailable | Dominated; preserve exact version and effort in evaluations |
| MiMo V2.6 Flash | 37.9 | unavailable | Dominated; possible FP8 alternative |
| Kimi K3 | 43.6 | 76.2 | Dominated on intelligence/cost; stays on the coding/cost frontier |
| Qwen3.8 2.4T A95B | 39.9 | 71.9 | Dominated on these axes; retain only for a measured task advantage |
| gpt-oss-120b | 11.6 | 30.4 | Dominated on these axes; throughput is a separate evaluation |

Coding scores are a separate axis. Among rows with a reported coding score, the coding/cost frontier is GLM 5.3 Flash → GLM 5.3 → Kimi K3. Missing scores do not mean zero. FP4 and FP8 serving can differ in quality; do not transfer these model-level scores to the quoted endpoints. The cost/intelligence result is conditional on that unresolved parity. Actual reasoning tokens, cache use, latency, failures, and privacy restrictions can change the best choice.

**Evidence and scope:** OpenRouter's public [models API](https://openrouter.ai/api/v1/models) supplies identifiers and the benchmark fields above; each row links its official endpoint quotes and publisher model card. These benchmark numbers are attributed screening data, not independently reverified scores or local receipts. The [benchmark publisher's GLM 5.3 page](https://artificialanalysis.ai/models/glm-5-3) identifies its evaluated effort as Max; the exact effort/version mapping for the other API scores remains `(verify)`. Publisher cards establish released weights: DeepSeek, MiMo, GLM Flash, and gpt-oss use MIT/Apache licenses; GLM 5.3, Kimi K3, and Qwen3.8 use named custom licenses. Use “open-weight” for this mixed set; do not assume a common open-source license. All sources accessed 2026-10-24; provider pages are mutable.

**Watchlist and retired discovery rows:** `moonshotai/kimi-k3.1-pro` is available on OpenRouter at $2/$10 (blend $3.14), 1,048,576 context, and reported intelligence 55.1. Publisher weight/license verification is unresolved, so it is excluded from the released open-weight Pareto set. [OpenRouter model page](https://openrouter.ai/moonshotai/kimi-k3.1-pro). The old `deepseek/deepseek-r1` ID was absent from this catalog snapshot; do not silently substitute a dated checkpoint. `deepseek/deepseek-v4-flash` remains listed with canonical slug `deepseek/deepseek-v4-flash-20260423`; it is not the 0731 or V4.1 checkpoint. That older row and legacy `qwen/qwen-2.5-72b-instruct` / `deepseek/deepseek-chat` no longer represent the discovery shortlist. Existing pins and receipts are unchanged.

**Provider decision:** follow the OpenRouter provider selection section in the `model-frontier` procedure. Official [routing documentation](https://openrouter.ai/docs/guides/routing/provider-selection) and the [endpoint API contract](https://openrouter.ai/docs/api/api-reference/endpoints/list-all-endpoints-for-a-model), checked 2026-10-24, support filtering endpoints then sorting by price. Default load balancing is price-weighted; explicit price sorting disables it. The 99% floor is our initial rule, not an OpenRouter parameter or guarantee. No route implementation or production policy changed in this refresh.

**Purposes challenged:** classification, extraction, filtering, routing, inventory, and mechanical-worker purposes should evaluate GLM Flash first; reasoning, synthesis, implementation, and tool-use purposes should compare GLM Flash, GLM 5.3, and MiMo Pro. Include Kimi K3 for coding-specific comparisons. These are evaluation targets, not promotions. No project purpose registry or complete fleet call inventory was inspected; existing transport, budget, and Judge authorities remain in force.

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
