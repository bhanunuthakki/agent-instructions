---
name: llm-ops
description: Govern an LLM-backed feature so no call is a black box — one entry point, a purpose-keyed model picker, schema-validated output, per-call cost/latency logging, and evals. Use when building an LLM-backed feature, when the user says "set up evals", "which model should I use", "add a model picker", "is my LLM call governed", "route my LLM calls", "score my prompt", or when adding the first LLM call to a project that has none.
---

# LLM-Ops Discipline

Make every LLM call **measured, routed, validated, and logged** — never a scattered SDK call with a hardcoded model and a `json.loads` in a `try/except pass`. This skill turns the always-on rules in AGENTS.md ("LLM-Native Engineering") into a build checklist. Don't restate those rules — this is the *how*.

Reference implementation: **earnings-summary `directives/`** (`llm_calls.md`, `cheapest_model_routing.md`, `model_eval_loop.md`, `llm_evals_plan.md`). When in doubt about a design decision, read the corresponding directive — it's a battle-tested instance of every item below.

For **which concrete model** to pick at each tier against today's cross-provider prices, defer to the `model-frontier` reference — never pick from memory; prices and IDs move.

## Build checklist (do these in order)

### 1. One `call_llm` entry point

Every call routes through a single function. Direct provider SDK imports (`import anthropic`, `import google.generativeai`, `from openai import OpenAI`) are forbidden anywhere except inside that one module. This is what makes model-swap, timeout, billing, fallback, and logging changes happen in one place.

```python
# src/llm_client.py  — the ONLY module that imports a provider SDK
from llm_client import call_llm
raw = call_llm(prompt, purpose="bear_case")   # every call site looks like this
```

`call_llm(prompt, *, purpose: str, model: str | None = None, timeout_seconds: int | None = None) -> str`. The `model=` arg is an escape hatch for debugging only — call sites pass `purpose`, never an ad-hoc model.

### 2. Purpose-keyed model picker (cheapest-sufficient default + fallback)

Selection lives in one table keyed by a `snake_case` *purpose*, never hardcoded per call. Default to the cheapest model that holds parity; register a one-line rationale per entry. On operational failure (timeout / non-zero exit / empty output), fall back to a second model automatically — wired once, inside `call_llm`, not per call site.

```python
from enum import StrEnum

class Purpose(StrEnum):           # closed set — adding a call site adds a member
    BEAR_CASE = "bear_case"
    QA_TOPICS = "qa_topics"
    TRANSCRIPT_METADATA = "transcript_metadata"

# purpose -> provider-qualified model id. Comment = why this tier. See `model-frontier` for current IDs.
LLM_MODELS: dict[Purpose, str] = {
    Purpose.BEAR_CASE:           "gpt-5.6-sol",         # frontier judgment; do not downgrade
    Purpose.QA_TOPICS:           "gpt-5.6-terra",       # balanced execution; downgrade-candidate
    Purpose.TRANSCRIPT_METADATA: "gpt-5.6-luna",        # short closed-enum extraction
}
DEFAULT_MODEL = "gpt-5.6-terra"   # unknown purpose -> default + WARN log (not silenced)
```

An unknown purpose logs a warning and uses the default — that warning means "register a new purpose", not "suppress the log".

### 2a. Provider dispatch on this machine — three-tier fallback: Claude → Codex → OpenRouter

Resolve the model first, then dispatch from its family in the single `call_llm` module. Fallback is a fixed, ordered chain per purpose, not a free choice per call site:

1. **Claude subscription** (default tier-1 for most purposes) — `claude-*` → `C:\Users\Bhanu\.gemini\snippets\claude_cli.py` → Claude Pro/Max subscription.
2. **Codex subscription** (tier-2, tried only on tier-1's operational failure) — `gpt-*` → `C:\Users\Bhanu\.gemini\snippets\codex_cli.py` → ChatGPT/Codex membership.
3. **OpenRouter** (tier-3, last resort only — tried only after both subscriptions fail) — metered, API-key-billed. See the exception below before wiring this tier.
4. Anything else → fail loudly until a governed backend is registered.

Tiers 1 and 2 are both subscription-backed and carry no per-call billing risk — that's what makes them the default path and each other's fallback. The OpenAI transport uses a dedicated `CODEX_HOME` with a minimal config (Windows-keyring credentials, history persistence off, goals and memories off), requires `codex login` through **Sign in with ChatGPT**, and refuses to start when `OPENAI_API_KEY` or `CODEX_API_KEY` is present. It runs `codex exec` in an empty temporary directory with an ephemeral session, read-only sandbox, project rules ignored, and shell, apps, hooks, multi-agent, plugins, and web search disabled. Prompts travel over stdin; responses come from schema-validated JSONL events. This is an answer-only LLM transport, not an autonomous repository agent.

OpenAI purpose defaults are `gpt-5.6-luna` for mechanical/extraction work, `gpt-5.6-terra` for normal execution, and `gpt-5.6-sol` only for judgment-heavy work. These are starting tiers, not permanent pins: every purpose still earns its model through the eval and downgrade loop below.

**The OpenRouter exception to "never fall back to API billing."** The general rule stands: don't fall back to an SDK or API-key path, because unexpected API billing is an operational failure, not graceful degradation. OpenRouter is a narrow, deliberate carve-out to that rule for purposes that opt in — a *third* tier only, never tier-1 or tier-2, and only reachable after both subscription transports have already failed for that call:

- **Opt-in per purpose, not global.** A purpose without an OpenRouter entry simply fails loud when both subscriptions are down — that's correct for anything that shouldn't incur surprise spend.
- **Hard budget cap, `on_exceed='block'` — never `'warn'` or `'skip'`.** A soft cap on a metered tier defeats the point of gating it behind two free tiers.
- **Alert on every use, not just threshold breaches.** Reaching tier-3 at all means both subscriptions are unhealthy — that's an operational signal independent of spend, and it should page/notify immediately.
- **Dispatch through a dedicated wrapper analogous to `claude_cli.py`/`codex_cli.py`** (e.g. `snippets\openrouter_cli.py`, not yet built as of this writing) so the metered call is isolated to one auditable module — never an inline `requests`/SDK call at a call site.
- **Ledger it distinctly**: `provider="openrouter"`, `transport="metered_api"` (§4) — this is what makes tier-3 usage searchable and alertable after the fact, separate from the two free tiers.

### 3. Schema-validated structured output — never substring-parse

Any call that returns structured data is validated against a Pydantic (Python) or Zod (TS) schema. On mismatch, **retry once with the parse error fed back to the model** ("your previous response was not valid JSON: <err>"). On final failure, raise loudly — never return `{}` / `[]` / `None`, which is indistinguishable from a real "nothing found" (the silent-empty pathology). Never branch logic on `if "yes" in response.lower()`.

```python
from pydantic import BaseModel

class QaTopic(BaseModel):
    topic: str
    sentiment: Literal["positive", "neutral", "negative"]

def call_llm_structured(prompt: str, *, purpose: Purpose, schema: type[BaseModel]) -> BaseModel:
    raw = call_llm(prompt, purpose=purpose)
    try:
        return schema.model_validate_json(_strip_json_fence(raw))
    except ValidationError as err:
        repaired = call_llm(f"{prompt}\n\nYour previous reply was invalid:\n{err}\nReturn only valid JSON.",
                            purpose=purpose)
        return schema.model_validate_json(_strip_json_fence(repaired))  # raises StructuredParseError if still bad
```

### 4. Per-call ledger: model, tokens, cost, latency, success

Every call — success **and** failure — writes one row. This is the substrate for cost reporting, eval cost-joins, and downgrade decisions. Cost basis is **public list API price** (output-weighted), even on a flat-rate subscription — a subscription makes every model look free, useless for ranking. `codex_cli.py` exposes the measured input, cached-input, output, and reasoning-output counts emitted by `codex exec --json`; the central ledger, not the wrapper, converts those counts to the public-list estimate.

```python
class LlmCall(BaseModel):
    run_id: str          # correlates a call to its eval/feature run
    purpose: str
    model: str
    provider: Literal["anthropic", "openai", "google", "openrouter"]
    transport: Literal["subscription_cli", "metered_api"]  # makes billing path auditable
    input_tokens: int
    output_tokens: int
    cost_estimate_usd: float    # input*in_price + output*out_price, from a priced model ladder
    elapsed_ms: int
    success: bool
    error: str | None
    fallback_used: str | None   # which model the fallback degraded to, if any
```

Store the prompt/response as `sha256` in production (they embed sensitive content); store full text only in the eval store (§5), where volume is tiny and replayability matters.

### 5. Eval mode per purpose (the harness)

One harness, three modes, all converging on the same `(purpose, prompt_version)` key so prompt changes become measurable regressions, not vibes:

- **Golden set (mode A)** — for classifiers / extractors with deterministic ground truth (enum labels, valid JSON, exact spec). Checked-in `golden/<purpose>.json` of input→expected; graded by code; spend a judge only on ambiguous divergence. Add **injection canaries** here (cases with adversarial instructions embedded in the input; assert they're ignored).
- **Rubric / LLM-as-judge (mode B)** — for prose & judgment purposes (summaries, analyses, memos). A versioned markdown rubric; a cheap judge scores facet-by-facet with a structured verdict.
- **Outcome calibration (mode C)** — grade against reality later (did the prediction come true). Optional; only where reality eventually arbitrates.

Bump `prompt_versions[purpose]` whenever you materially rewrite a prompt, then run the eval and gate on `--min-score` before merge. Evals assert **structural properties, not exact wording** (per Testing Discipline) — for prose, score via rubric, never string-match the copy.

### 6. The brand-blind pairwise self-judge

A single primitive serves both jobs: it scores **"Response A" vs "Response B"** and never learns which model (or which prompt version) produced which. As a *quality* eval it compares candidate vs reference output; as a *model-downgrade* evaluator it puts the incumbent in slot A and a cheaper candidate in slot B. Run it in **both slot orders** and require position-consistency to neutralize position bias.

```python
class PairwiseVerdict(BaseModel):
    winner: Literal["A", "B", "tie"]
    margin: float            # 0..1 confidence
    rationale: str

# downgrade reuse: A = incumbent response, B = cheaper-candidate response.
# winner=="A" => incumbent held; winner=="B" => candidate at-or-better.
```

### 7. Conservative switch gate (parity + cross-judge + min sample; auto-demote)

A downgrade ships only when a cheaper model *clearly* holds up — a bad silent downgrade costs more than the saving. Default rule:

- `INSUFFICIENT_DATA` below `min_n` (default **4**; use **≥10** for high-stakes purposes).
- `SWITCH_DOWN` only if **every** judge has the candidate at parity-or-better on ≥ `parity_threshold` (default **0.8**) of cases **AND** cross-judge agreement ≥ **0.6**.
- `KEEP_INCUMBENT` if any judge has the incumbent winning a majority.
- `HOLD` otherwise (mixed / judges disagree).

A candidate that errors/times out counts as an incumbent win. On a SWITCH_DOWN, write the choice to a **reversible override** (data, not code) and **auto-demote** (clear the override) if a later sweep regresses below the bar. Token efficiency (candidate vs incumbent output tokens) is a *secondary* signal surfaced in the verdict, never a hard gate — a model that's slightly more verbose but 10× cheaper per token still wins.

### 8. The judge is itself a governed purpose

The judge is not exempt — it's a first-class purpose: cheap model pin (a narrow schema-bound verdict task → cheapest tier), its own budget row, ledger attribution, and a `prompt_versions` bump when its rubric changes. It **fails closed**: an unparseable verdict scores the case 0 / failed and persists the raw verdict text — never silently passes. **Spot-check** a sample of judge verdicts against human judgment periodically and record the agreement rate; escalate the judge to a stronger model for a purpose if agreement comes back weak.

### 9. Per-purpose budgets + cost alerts

Each purpose gets a monthly cap with `on_exceed ∈ {warn, block, skip}`, enforced pre-call. A budget block is a hard-stop that propagates (it's configuration, not a quality failure — don't let fallback swallow it). Seed the judge's own budget conservatively (`on_exceed='warn'`). Alert when a purpose's cost, error rate, or fallback rate crosses a threshold. The OpenRouter tier (§2a) is the one exception to the `warn`-by-default posture: it always gets `on_exceed='block'`, and every reach into that tier alerts regardless of spend, since it signals both subscription transports are down.

## Acceptance criteria (passes the `llm-evals-orchestrator` audit)

The feature is done when it would clear `~/.claude/agents/llm-evals-orchestrator.md` at L1 (`B`, blocking):

- **Model-picker** — every call site selects by purpose via the central picker; cheapest-sufficient default; fallback on failure. No hardcoded-per-call models.
- **Eval harness** — every LLM-using purpose has an eval (golden / rubric / judge as fits); regressions caught; assertions are structural, not exact-wording.
- **Structured output** — schema-validated; retry/repair on mismatch; zero substring/keyword classification.
- **Logging** — per call: model, tokens in/out, cost, latency, success/failure, retries — written on success and failure.
- **Transport attribution** — every row records provider and transport/auth class, so subscription routing can be audited independently of the model ID.
- **Failure handling** — timeouts, ordered fallback (Claude → Codex → OpenRouter), no silent failure (no `{}`/`[]`/`None` masquerading as "nothing found").
- **Billing (this machine)** — subscription-backed Python calls route through `claude_cli.py` for Claude or `codex_cli.py` for OpenAI. Metered `anthropic`, `claude_agent_sdk`, and `openai` SDK paths are forbidden when subscription billing was intended. A purpose that opts into the OpenRouter tier-3 fallback (§2a) is the sole sanctioned exception, and only through a dedicated wrapper with `on_exceed='block'` and per-use alerting.

## Defaults (one named choice each)

- **Backend dispatch:** model-first — resolve the model from the purpose, then pick the backend from the model's family. A cross-provider model ID in the picker is enough to route there; no separate allowlist. Tradeoff: a single mechanism, but the picker must carry full provider-qualified IDs and unknown families fail loud.
- **Fallback order:** Claude subscription → Codex subscription → OpenRouter, fixed and in that order for every purpose that opts into a fallback chain (§2a). Tradeoff: no per-purpose reordering, but a single predictable chain is what makes the OpenRouter carve-out auditable — a purpose either opts into the full three-tier chain or stops at two free tiers.
- **Sampling for the downgrade loop:** scheduled batch over a random sample of (purpose, input) pairs, **not** a probabilistic tap on the live `call_llm` path. Tradeoff: eval signal lags live traffic slightly, but live latency and live billing are never touched by eval traffic.
- **Judge model:** cheapest tier that passes spot-checks. Tradeoff: cents-per-eval cost, but escalate per-purpose if agreement is weak (expected for high-judgment purposes).

## Anti-patterns

- Provider SDK imported outside the one `call_llm` module; an ad-hoc `model="..."` at a call site instead of a registered purpose.
- `if "yes" in response.lower()` / substring matching to classify — use a schema + enum.
- Returning `{}` / `[]` / `None` on parse failure (silent-empty) instead of raising.
- Pinning a model from memory of last year's prices — consult `model-frontier`.
- A judge that "best-effort" passes unparseable verdicts, or a downgrade that flips production with `n=1` and one judge.
- Cost basis of `$0` because it's a flat-rate subscription — rank on public list prices.
- Invoking the OpenAI SDK, inheriting `OPENAI_API_KEY` / `CODEX_API_KEY`, or reusing an API-key-authenticated Codex home for a call intended to use ChatGPT membership.
- Running subscription-backed `codex exec` in a project checkout or with agent tools/config enabled; the transport must stay isolated and answer-only.
- Putting OpenRouter in tier-1 or tier-2, calling it directly from a call site, or giving its purpose budget anything but `on_exceed='block'` — it's a last-resort tier-3 exception, not a peer of the two subscription transports.
- Reordering the fallback chain per purpose (e.g. Codex before Claude, or OpenRouter before Codex) instead of the fixed Claude → Codex → OpenRouter order.
- Asserting on exact prompt/copy wording in eval tests — score structure (per Testing Discipline).

## Scope note

This is an **on-demand** skill — load it when building or auditing an LLM-backed feature. Do not make it always-loaded; the cheap always-on summary already lives in AGENTS.md → "LLM-Native Engineering".
