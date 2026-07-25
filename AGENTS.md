# Agent Instructions (tool-agnostic core)

The canonical, always-loaded rulebook — shared by **every** agent runtime: Claude Code, Gemini CLI/Antigravity, OpenAI Codex, Cursor, Aider, and any local-model harness. `AGENTS.md` is the de-facto cross-tool standard filename; this is the single source of truth. Project-specific guidance lives in each repo's own `AGENTS.md` and merges on top.

Heavy procedures (Grill-Me, Definitions, Hardening, LLM-ops, secure-app scaffolding, log-redaction) are **not** spelled out here — each is a self-contained file under `procedures/`, so this file stays cheap to load every turn and the procedures work on any tool. Each is referenced below as `procedures/<name>.md`.

## How any runtime consumes this system

- **Universal path (works everywhere):** the tool reads `AGENTS.md` (this file); when a procedure is referenced, it reads `procedures/<name>.md` — plain, self-contained markdown with no tool-specific machinery. That alone runs the whole system on Codex, Cursor, Aider, or a local model.
- **Claude Code and Codex** additionally get generated native skills and subagent dispatch. Claude loads this file via `CLAUDE.md`; Codex loads `AGENTS.md` directly. Both use the same canonical procedures and runtime-native model bindings.
- **Gemini CLI** loads this file via `@./AGENTS.md` in `GEMINI.md` and uses a trigger→`procedures/` table (it has no skill auto-loader).
- **Enforcement is tool-agnostic:** the credential-scan + pre-push gates are **git hooks** (a shared `githooks/` dir wired per-repo via `core.hooksPath`), so they fire regardless of which agent — or a human — makes the commit.
- **`procedures/` is the canonical source.** `snippets/sync_agent_stubs.py` generates the Claude skills, the `/harden` command, and the agent fleet (`procedures/agents/`) *from* it — an identity copy, so the procedures are not downstream of Claude. Drop Claude and the whole system, fleet included, still runs as plain markdown.

## Universal Safety Rules

1. **Never log, read aloud, or output credential file contents** (`.env`, `credentials.json`, `token.json`, `*.pem`, anything matching `*secret*` or `*key*`).
2. **No destructive operations without confirmation** — `rm -rf`, `DROP TABLE`, `git push --force`, mass file deletes, schema migrations on prod. State the operation, wait for explicit go-ahead.
3. **Never commit credentials.** If a file matching credential patterns appears in a staged diff, halt. *(Enforced deterministically by the pre-commit git hook — this rule is the rationale, the hook is the guarantee.)*
4. **Never log a URL or exception that may embed credentials.** HTTP libraries stringify the full request URL (query string intact) into exception messages — `raise_for_status`, timeouts, connection errors. When writing networked code: redact before logging, prefer secrets in headers (`Authorization`, `x-api-key`) over query params, and re-raise propagated HTTP exceptions as new exceptions with `from None` to drop the credentialed traceback. *(Full redactor pattern + the env-var-to-call-site audit procedure → `procedures/log-redaction.md`; the canonical implementation lives in earnings-summary `src/log_redact.py`.)*

## Requirement Gathering — Grill-Me

For a new feature or consequential design decision, inspect the repository first and resolve only ambiguities that would materially change the solution. Propose defaults with the tradeoff named; do not ask preferences recoverable from code or context. Pause deliverables until shared understanding is verified when a wrong choice would be expensive to unwind. Well-scoped work and reversible implementation details do not require an interview.

- **Trigger** (`/grill-me` or "grill me / interview me") forces the full protocol even on an otherwise-exempt request, or restarts it.
- **Full procedure** → `procedures/grill-me.md` (Claude auto-loads it as the `grill-me` skill).

## Vocabulary Standardization — Definitions

Maintain a `DEFINITIONS.md` at each repo root fixing canonical domain terms; use them verbatim in code, comments, commits, PRs, and conversation. **Never coin a new synonym** — if a concept has no defined term, propose adding it before using it. Flag overlapping/ambiguous terms when you spot them.

- **Trigger** (`/definitions`) forces a full vocabulary scan + canonicalization proposal.
- **Full procedure** → `procedures/definitions.md` (Claude auto-loads it as the `definitions` skill).

## Execution Pace — Strict TDD

Applies to changes that **add or modify behavior**. Bugfixes need a regression test, not the full cycle. Throwaway/exploratory scripts are exempt.

**Cycle:** (1) Define the behavior in one sentence. (2) Write the failing test against the smallest interface; confirm it fails for the right reason. (3) Write the minimum implementation to pass. (4) Refactor for design (Deep Modules); tests stay green. (5) Repeat.

**Guardrails (always on, even mid-task):**
- One behavior per cycle. If a test needs ≥2 assertions on distinct concerns, split it.
- Don't write code outside the cycle — no "while I'm here" changes; start a new cycle.
- A hard-to-write test is a design signal (shallow/leaky interface). Fix the design first.
- Never disable, comment out, or weaken a failing test to make progress. Fix the code or revert.
- Don't generate massive monolithic blocks. Outrunning your headlights produces code that compiles but encodes the wrong behavior.

## Backend / General Code Standards

Apply to Python, TypeScript, Go, etc.

### NEVER
- Unexplained inline imports. Keep imports at module scope unless lazy loading, optional dependencies, or a documented cycle requires otherwise.
- Untyped catch-alls in domain interfaces. At external boundaries, accept `unknown`/raw data only long enough to schema-validate it into a precise type.
- Type-error suppression (`# noqa`, `@ts-ignore`) — fix the annotations. Narrow exception: a single `cast(...)` at a validated JSON / external-data boundary (right after an `isinstance`/schema check). Never `# type: ignore`.
- `try/except pass` or any error silencing.
- Permissive `getattr` defaults or fallbacks that hide bugs.
- Substring/keyword matching to classify responses, detect intent, or branch logic — use enums or structured outputs.
- Magic strings/constants sprinkled through code.
- Silent fallbacks on unexpected input — let it raise.

### ALWAYS
- Strong typing enforced by the strictest typechecker available.
- Schema-validated models (Pydantic, Zod, etc.) for structured data, payloads, and config.
- Function length is a design signal, not a numeric gate. Extract only genuinely separable complexity, reuse, or a helper whose name is more informative than its body; a cohesive long function can be deeper than several pass-through helpers.
- DRY **genuine** duplication only. Two pieces that look alike but represent different domain concepts will diverge; premature DRY couples them. When in doubt, wait for the third occurrence.
- Fail loudly with clear exceptions.
- **A deliberate degradation path must announce itself.** The NEVER list bans fallbacks that *hide bugs*; this is the obligation on the ones that are *supposed* to exist — a schema-compatibility shim, a degrade-don't-crash exit, a "provider didn't send it" branch. Each must be distinguishable at runtime from the happy path: a structured log event naming which branch was taken and why, plus — when a value is returned — a field on that value recording which path produced it. Without that, the fallback becomes an unobservable default and a real defect inside the primary path is absorbed by it: an `except OperationalError` written for an older schema will equally swallow a malformed query in the new one, and the write then *succeeds* while silently dropping data. The failure mode is not a crash but a plausible wrong answer, which is why review misses it and only measurement finds it. Note this is not satisfied by "we have structured logging" — the branch itself must be attributable. *(Empirical: 2026-07-24/25, earnings-summary shipped seven instances of this shape in one program — a discriminator field that measured constant across every input, two `"unknown"` values comparing equal and licensing a false delta, a placeholder/column mismatch absorbed by a compat branch so every write silently lost provenance, a stale test fixture doing the same, an unsurfaced `None` branch, an omitted test double that reached the live network, and a file write that reported success with corrupted content. Review caught none; measurement caught all seven.)*
- Direct attribute access over defensive fallbacks.

## Architectural Constraints — Deep Modules

**Principle.** Depth = functionality ÷ interface complexity. Prefer few large modules whose interface is dramatically simpler than their implementation. Reject classitis. (Ousterhout, *A Philosophy of Software Design*.)

### NEVER
- Pass-through methods (`return other.method(args)` with the same/near signature) — inline or relocate the real logic.
- Pass-through variables threaded through ≥3 layers where only the bottom uses it — use a context object or restructure.
- "Configuration classes" with no behavior — use a typed dataclass / Pydantic model.
- Adjacent layers that share vocabulary — layer N providing no abstraction lift over N+1 → collapse.
- Helpers called from exactly one site, extracted only to shorten the parent — inline if clearer.
- Splitting a class for "too many methods" without checking whether the split increases total interface surface or causes information leakage.

### ALWAYS
- Before extracting, check the depth ratio. Interface size ≈ implementation size in concepts → shallow → leave inlined.
- Prefer one general-purpose API over N special-purpose ones, unless it inflates the argument list past usability.
- If two modules consistently change together, that's information leakage — merge them or move the shared knowledge into one encapsulating module.
- Each layer's interface must speak a different abstraction than the layer below.

### Smells to flag in review
- Class whose public API can be paraphrased from its private state. Docstring that just restates the signature. `*Service`/`*Manager`/`*Helper`/`*Utils` class that's a namespace for free functions. Five-line helper called once. Abstraction added "for testability" with no information hiding. Two adjacent layers passing the same structures with the same field names.

## Frontend Correctness (when working on UI)

- Accessible primitives (Base UI, React Aria, Radix) for anything with keyboard/focus behavior. Never hand-roll keyboard/focus logic.
- Visible focus rings (`:focus-visible`); never `outline: none` without replacement.
- Icon-only buttons need `aria-label`; decorative elements `aria-hidden`. Native semantics first (`button`, `a`, `label`) before ARIA. Never `<div onClick>` for navigation.
- Hit targets ≥24px (≥44px mobile). Mobile `<input>` font-size ≥16px.
- Forms: don't block paste; validate after typing not during; focus first error on submit; warn on unsaved changes; allow password-manager + 2FA paste.
- Use `h-dvh`, not `h-screen`. Respect `safe-area-inset` for fixed elements.
- Animate `transform`/`opacity` only — never layout props, never `transition: all`; ≤200ms for feedback; respect `prefers-reduced-motion`. Don't add animation unless asked.
- Virtualize lists when measured render volume or interaction cost warrants it; explicit image dimensions prevent CLS; `useEffect` is not a substitute for render logic.
- Inputs with `value` need `onChange` (or `defaultValue`). Locale-aware dates/numbers (`Intl.*`). Flex children need `min-w-0` for truncation; handle empty states.
- **Starting a UI from scratch?** Use the design-system scaffold rather than hand-rolling tokens/components — see *Building Secure Apps* below.

## LLM-Native Engineering (when building LLM-backed features)

Every LLM call must be governed, not a black box. Always-on rules:
- **One entry point.** All calls route through a single `call_llm`-style function — never scattered SDK calls.
- **Model-picker per purpose.** Each call site selects a model by a named *purpose* via a central picker (cheapest-sufficient default, easy override, fallback model on failure) — never a hardcoded model per call.
- **Structured output.** Schema-validate every response (Pydantic/Zod); retry/repair on mismatch. Never substring-parse to classify (see Code Standards).
- **Log every call:** model, tokens in/out, cost, latency, success/failure, retries.
- **Eval before trust.** New prose/judgment purposes get a rubric or LLM-as-judge eval; classifiers get a golden set. Evals assert structural properties, not exact wording (see Testing Discipline).
- **Self-judging is brand-blind.** Any model-vs-model decision uses a pairwise judge that never learns which model produced which output; switch conservatively (parity + cross-judge agreement + min sample), auto-demote on regression.
- **Cost/perf is a moving frontier.** Pick models against the dated cross-provider frontier reference, not memory.
- **Subscription transports on this machine.** Route Claude models through `C:\Users\Bhanu\.gemini\snippets\claude_cli.py` and OpenAI models through `C:\Users\Bhanu\.gemini\snippets\codex_cli.py`. Both are CLI subprocess transports backed by the user's monthly memberships. Never substitute a metered provider SDK or API-key-authenticated CLI session; OpenAI membership calls must use the wrapper's dedicated `CODEX_HOME` and answer-only isolation.
- **Fallback order: Claude → Codex → OpenRouter.** Per-purpose fallback is this fixed three-tier chain, tried in order on operational failure. The first two tiers are subscription-backed and billing-safe by default. OpenRouter is a narrow, opt-in, last-resort exception to "never fall back to metered billing" — tier-3 only, hard budget block (`on_exceed='block'`, never `warn`), alert on every use. Full carve-out conditions → `procedures/llm-ops.md` §2a.
- **Full method** → `procedures/llm-ops.md` + the dated cost table `procedures/model-frontier.REFERENCE.md` (Claude auto-loads these as the `llm-ops` + `model-frontier` skills). Reference implementation: earnings-summary `directives/` (`llm_calls`, `cheapest_model_routing`, `model_eval_loop`, `llm_evals_plan`).

## Building Secure Apps (multi-user / web)

When building a complex app with auth, a database, or multi-tenancy, **generate secure-by-default scaffolding first, then let the hardening fleet audit it** — don't hand-roll auth/RLS and get graded on it after. Defaults: auth uses slow-hash (argon2id) + HttpOnly/Secure/SameSite cookies (or short-lived JWT + rotating refresh) + default-deny route guards; every tenant-owned table carries `tenant_id` with an *unbypassable* scope (Postgres RLS or an enforced base query) from day one; migrations are versioned and reversible.

- **Scaffolds** → `procedures/`: `scaffold-secrets.md` (env/secret hygiene), `scaffold-auth.md`, `scaffold-tenant-schema.md`, `scaffold-design-system.md`, `scaffold-deploy.md` (localhost → live: container + managed platform + CI + backups). Claude auto-loads each as a skill.
- **Audit/harden** → see *Hardening Fleet* below.

## Reviewing LLM-written code

When code is largely LLM-written, the owner often can't tell when it's subtly wrong. After a **substantial** change, before relying on it: produce a plain-language review — what changed, what could break (flag any secret/DB/auth/money/deletion surface), and the exact way to confirm it works. → `procedures/explain-change.md` (Claude: `explain-change` skill). This is comprehension + risk for a non-expert owner — distinct from a bug-hunt (`code-review`) and the security gates (`/harden`).

## Testing Discipline

Prefer structural and semantic assertions over exact generated wording, prompt text, logs, or incidental errors. Exact text assertions are appropriate only when the text is itself a stable user-visible or protocol contract. Never weaken an assertion merely because it is inconvenient.

## Pre-Push Checklist

Always in this order; never push red. *(Enforced by the pre-push git hook; this is the rationale.)*

1. Sync dependencies if changed → 2. Format → 3. Lint → 4. Typecheck (run all available) → 5. Tests → 6. Build (if applicable).

## PR Conventions

**Title:** imperative mood ("Add webhook retry"), focused on WHAT not HOW. **Body:** `## Why` (problem/motivation) · `## Changes` (high-level bullets) · `## Test Plan` (how verified). No line-by-line diff narration.

## Operating Principles

- **Branching:** don't switch branches unless explicitly told to.
- **Multi-agent coordination:** others may be working in the same repo. Don't touch unrelated changes; if they conflict with yours, ask before resolving.
- **Respect existing edits:** assume unexplained changes in the tree were intentional.
- **Tool prioritization:** check for existing scripts/utilities in the repo before writing new code.
- **Engineering bar:** approach every change as a senior principal engineer would. The architecture should be obvious to a first-time reader. Every abstraction must earn its existence (see Deep Modules).

## Session & Agent Model Selection (Token Discipline)

The interactive root is the orchestrator: **Claude Fable 5** in Claude Code and **GPT-5.6 Sol** in Codex. It owns requirements, ambiguous decisions, architecture, delegation briefs, synthesis, and final review. Gemini remains supported when launched explicitly but is not the preferred orchestration runtime.

| Role | Claude | Codex | Use |
|---|---|---|---|
| Frontier orchestrator | Fable 5 | Sol | Ambiguity, architecture, high-impact judgment, synthesis, final review |
| Workhorse executor | Sonnet 5 | Terra | Specified implementation, audits, refactors, tests, research slices |
| Mechanical worker | Haiku 4.5 | Luna | Extraction, formatting, inventories, deterministic sweeps |

Delegation contract:

- **Delegation is the default for execution-shaped work.** Once the approach is settled, a spec'd implementation, tests against defined behavior, a bounded refactor or audit, or a research sweep goes to a workhorse (deterministic sweeps to the mechanical tier). State the worker's model and a one-line reason with every spawn.
- **Inline execution by the orchestrator is the named exception, not the quiet default.** Legitimate exemptions: (a) the task is small/single-step enough that writing the brief costs more than the diff; (b) the execution is inseparable from judgment still being formed; (c) the user is iterating interactively on the output. When starting execution-shaped work without spawning, state which exemption applies in one line — if you can't name one, spawn. An unstated exemption is the rule being missed, not an implicit waiver.
- Default to depth 1 and 1–3 concurrent workers. Parallelize independent read-heavy work freely; concurrent writers require exclusive file/module ownership.
- A worker returns a concise result and evidence. The orchestrator verifies integration and never treats delegation as abdication.
- On a weak result, improve the brief or split the task once before escalating the worker's model. Escalate only when the lower tier demonstrably fails.
- App-internal LLM routing is separate and remains purpose-keyed and eval-gated under LLM-Native Engineering.

## Scheduling & Quota Discipline (agent bursts + recurring LLM runs)

Interactive agent sessions and this machine's resident apps/cron jobs draw on the **same LLM quota** — every project whose in-app transport is the subscription `claude` CLI shares one Pro/Max session window with all interactive Claude Code sessions. A multi-agent build burst can therefore starve a scheduled job's own LLM calls hours later; the failure surfaces as `claude` CLI **exit 1 at cron time**, not as anything obviously quota-shaped. (Empirical: 2026-07-02/03, two all-night agent waves broke earnings-summary's 04:00 pipeline two mornings running.)

- **Segment bursts.** Run multi-agent/parallel-session waves as bounded bursts spaced **≥6–7h apart** (owner directive 2026-07-03), each sized to finish within the current window. One wave per window; don't chain waves back-to-back.
- **Track subscription pools separately.** `claude_cli.py` consumes the Claude Pro/Max window; `codex_cli.py` consumes ChatGPT/Codex membership usage and credits. Both are finite even though neither produces a per-call API bill. Tag the provider/transport in the ledger and apply the same defer-this-item behavior when either CLI reports a transient limit.
- **Protect cron windows.** Before launching a wave — or registering a NEW recurring job that makes LLM calls — check the machine's scheduled-task fleet (`schtasks /query`, per-repo `cron/` dirs) for LLM-calling jobs and keep their windows clear. Canonical protected window: **03:00–05:00 America/Los_Angeles** (earnings-summary 04:00 morning pipeline; its monthly 03:00 scenario-prior refresh). New recurring jobs pick slots that don't collide with existing LLM jobs or likely burst hours.
- **Recurring jobs degrade per-item.** Any scheduled job making LLM calls must treat a transient CLI failure (often = exhausted quota) as *defer-this-item-and-continue* with an explicit deferred tally and retry on the next run — never let one starved call kill the whole run. Hard setup/budget errors still fail loud. (Reference implementation: earnings-summary `attach_conditions`, PR #814; repo detail: earnings-summary `directives/llm_quota_scheduling.md`.)
- **Resume, don't respawn.** An agent killed mid-flight by a quota limit keeps its context — message it to resume after the reset instead of restarting the work.

## Hardening Fleet

A maturity-gated fleet of domain-expert **audit/fix subagents** takes a project from ideation (L0) → MVP (L1) → multi-tenant beta (L2) → limited commercial release (L3). The expert criteria are canonical in `procedures/agents/`. Fable or Sol orchestrates; workhorse subagents run applicable audits; the orchestrator consolidates and reviews all blocking findings. A runtime that genuinely lacks subagent dispatch runs the same criteria sequentially.

- **Run it** → `/harden` (`/harden <rung>`, `/harden --deep`, `/harden --audit <expert>`, `/harden --status`). Personal/single-user projects cap at L1 unless opted into L2+. Codex and Claude dispatch runtime-native subagents; other runtimes follow `procedures/harden.md` using their available dispatch surface or a sequential pass.
- Expertise lives in the `procedures/agents/` criteria files; the matrix, rungs, and dispatch protocol live in `procedures/harden.md` (and the `/harden` command), not here.
