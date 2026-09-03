# Your agent system — human guide

A one-page map of what you have and when it fires. **This file is for you, not the agents** — no tool loads it into context (only `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` auto-load).

The **inventory tables** below (skills · commands · agents · procedures · projects) are **auto-generated** from the filesystem by `/sync-agent-stubs` and live between `<!-- BEGIN:… -->` / `<!-- END:… -->` markers — so the counts can never silently drift again. The pre-push hook runs `--check` and fails if they fall out of date. Everything *outside* the markers is hand-written prose; edit it freely.

## The mental model

- **`AGENTS.md`** (in the tracked `agent-instructions` repository) = the always-on rulebook every tool reads. Slim on purpose.
- **`CLAUDE.md`** / **`GEMINI.md`** = thin wrappers that import `AGENTS.md` and add tool-specific bits.
- **`procedures/`** = the heavy "how-to" guides (auth, deploy, evals…), as plain markdown any tool can read. **The canonical source** — the Claude skills, the `/harden` command, and the agent fleet (`procedures/agents/`) are generated *from* these.
- **Skills / commands / hooks** = how Claude (and git) make the above automatic. Other tools (Gemini, Codex, a local model) read `AGENTS.md` → `procedures/` and get the same thing.

You rarely touch any of this. It just shapes how the agent behaves.

## Evidence governance

- **Shared language:** root `DEFINITIONS.md` defines only cross-project control-plane terms. Projects may add terms but never override them.
- **Review rigor:** J0 is deterministic; J1 uses one Judge; J2 uses one specialist plus a conditional independent second Judge; J3 is reserved for actual irreversible or external actions and requires owner approval only to PASS.
- **Reliability loop:** an exclusive writer seals task identity before work and typed receipts separate routing from execution. Mandatory J3/exception controls are censused; ordinary prevalence estimates use sealed episodes and owner-ratified, per-stratum Statistical Sample Targets.
- **Activation boundary:** Judge purposes, ordinary sampling, evidence authenticity, and invocation coverage remain shadow-only until calibration, tolerances/confidence, verifier-backed evidence, and an independent Task Population Frame are ratified. Receipt audits cannot detect omitted work by themselves.
- **Adaptation:** the ledger may recommend promotion or demotion, but changes require owner ratification. Missing statistical targets or sample volume reports `INSUFFICIENT_EVIDENCE`; budget never manufactures confidence.

## Skills — say the trigger, the agent does the thing

<!-- BEGIN:skills -->
**25 shared skills** — say the trigger, the agent runs the procedure. Codex also exposes `harden` as a native skill; Claude exposes the same procedure as `/harden`.

| Skill | What it does |
|---|---|
| **agent-operations** | Coordinate subagents, shared worktrees, capability roles, or scheduled LLM work. |
| **code-change** | Implement, fix, refactor, or review code with the repository’s tests and conventions. |
| **context-engineering** | Audit or rewrite AGENTS.md, CLAUDE.md, GEMINI.md, system prompts, skills, agent rubrics, tool descriptions, or memory placement for advanced models. |
| **data-foundation** | Design or change durable application state, schemas, data pipelines, or sources of truth with local-first simplicity, explicit lifecycle, recovery, a… |
| **definitions** | Build, refresh, or enforce the project’s canonical domain vocabulary in DEFINITIONS.md. |
| **explain-change** | After an LLM writes or edits code, explain the outcome, impact, risk, and proof in plain language at a depth proportional to the change. |
| **external-integration** | Add or audit an inbound external API, webhook, SDK, or MCP capability through a typed, least-privilege, observable adapter. |
| **external-practice** | Verify a consequential, drift-sensitive implementation or design choice against current primary sources. |
| **frontend-quality** | Design, modify, review, or scaffold a rendered interface around the user's task, with compositional restraint and proportional browser or renderer ev… |
| **grill-me** | Resolve load-bearing product unknowns before a feature, design, plan, or consequential decision. |
| **iteration-shortcut** | Bound a deliberate temporary shortcut that accelerates learning without silently weakening retained truth, safety, or recovery. |
| **judging** | Govern explicit Judge, Critic, evaluation-suite, or consequential incomplete-oracle review work through proportional evidence tiers, independence rul… |
| **linear-pipeline-hygiene** | Audit and conservatively reconcile Linear pipelines across projects. |
| **linear-pr-sync** | Synchronize an existing Linear issue with branch and pull-request progress. |
| **llm-ops** | Govern an LLM-backed feature with one entry point, purpose-based model selection, schema-validated output, attributable fallbacks, per-call cost and… |
| **log-redaction** | Keep secrets out of logs, exception output, and network diagnostics. |
| **mockup-review** | Redesign or review an existing application page through an observed mockup, task hypothesis, and proportional implementation notes. |
| **model-frontier** | Pick a hosted or open-weight LLM/runtime candidate against a dated cost and capability frontier instead of from memory. |
| **product-feature** | Define or review a material product feature before implementation: user outcome, smallest coherent behavior, state and authority, non-goals, acceptan… |
| **scaffold-auth** | Establish stack-appropriate authentication and authorization after the product profile requires external identity or multiple users. |
| **scaffold-deploy** | Establish a reproducible, secure release and operation baseline for the selected local, private, hosted, or distributed profile. |
| **scaffold-design-system** | Establish a small, accessible, stack-appropriate UI foundation after the user task and hierarchy are understood. |
| **scaffold-secrets** | Establish narrow, typed secret configuration and leak prevention for the repository's actual stack. |
| **scaffold-tenant-schema** | Establish tenant boundaries only after the product profile explicitly requires multiple isolated customer tenants. |
| **tool-selector** | Compare a consequential library, service, vendor, or build/buy choice against current evidence and the product's real constraints. |
<!-- END:skills -->

## Commands — type these

<!-- BEGIN:commands -->
**3 commands** — type these.

| Command | What it does |
|---|---|
| `/harden` | Run profile-aware, evidence-backed product hardening |
| `/refresh-frontier` | Re-verify and restamp the canonical model cost and capability frontier from current primary sources and measurements, then flag purposes for evaluati… |
| `/sync-agent-stubs` | Audit and synchronize canonical procedures, generated runtime artifacts, rulebook wrappers, semantic references, and composable shared hooks. |
<!-- END:commands -->

## What happens automatically (no action needed)

- **On `git commit`** → the pre-commit hook blocks credential files and suspected hardcoded secrets without printing their values. If it flags a false positive, repair the rule with a regression test; do not bypass the safety gate.
- **On `git push`** → the effective pre-push hook runs the project gate, then verifies the global instruction system, generated artifacts, human guide, and tests. The tracked instruction repository and every wired project use the shared hook path; an optional project `.githooks/pre-push` is composed, not substituted. Resolve a failing prerequisite or check before pushing.
- Hooks live in the tracked `githooks/` directory and are wired into each repo by `/sync-agent-stubs`. They apply across Claude, Codex, Gemini, and plain `git`.
- Live Judge ledgers, hardening policy ratification, and capability evidence live in the ignored private state root, not this public repository. The default is `.private-state/`; `AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT` may name another absolute location. The tracked evaluation policy is an unratified template.

## The hardening fleet (advanced, opt-in)

Domain-expert auditors grade the product from decision (L0) through limited commercial release (L3). Maturity is separate from deployment, identity, commerce, data, and interface profile, so a personal tool receives the local reliability checks it needs without speculative SaaS machinery. Invoke them via `/harden`.

<!-- BEGIN:agents -->
**19 audit agents** — criteria canonical in `procedures/agents/`, generated into `~/.claude/agents/` for Claude's `/harden` dispatch. Profile and capability applicability keep personal tools local-first without weakening commercial gates.

| Agent | Audits |
|---|---|
| `api-surface-designer` | Audit product-owned API, MCP, webhook, or plugin contracts for schemas, errors, idempotency, limits, compatibility, and documentation. |
| `architecture-reviewer` | Audit system coherence, module depth, dependency direction, state ownership, failure design, and profile-driven scalability. |
| `data-foundation` | Audit canonical data ownership, identity and time semantics, migrations, provenance, quality, lifecycle, backup, restore, and export. |
| `docs-support-readiness` | Audit setup, health, backup/recovery, user/API documentation, support intake, escalation, and feedback routing proportional to product reach. |
| `finops-pricing` | Audit operating cost, unit economics, price, packaging, margin, and cost ceilings for the selected personal, free, or paid profile. |
| `frontend-web` | Audit web implementation correctness, responsiveness, accessibility mechanics, performance, state handling, and rendered evidence. |
| `idea-evaluator` | Decide if and what to build for the hardening fleet — time commitment, commercial viability, market wedge, competitive landscape, data-rights feasibi… |
| `legal-compliance` | Audit applicable data rights, licensing, privacy, distribution, accessibility, payment, and commercial obligations; not a substitute for counsel. |
| `llm-evals-orchestrator` | Audit purpose-based LLM routing, structured output, representative evals, attributable fallbacks, and per-call quality/cost/latency/failure evidence. |
| `operations-readiness` | Audit release, distribution, runtime health, scheduled work, backup/restore execution, rollback, incidents, and proportional cost/availability teleme… |
| `payments` | Audit the selected payment, billing, licensing, metering, reconciliation, refund/dispute, tax, and entitlement lifecycle. |
| `product-analytics` | Audit the learning system for external beta and commercial products: questions, event meaning, activation, retention, and privacy-proportional eviden… |
| `product-feature` | Audit the user-visible behavior contract, state transitions, acceptance, rollout, and learning criteria for a material feature. |
| `qa-test-strategy` | Audit the representative unit, integration, end-to-end, regression, failure, and profile-specific performance test strategy. |
| `sec-appsec` | Audit application vulnerabilities, credential hygiene, dependencies, untrusted inputs, sensitive data, abuse ceilings, disclosure, and threat boundar… |
| `sec-authz` | Audit identity and access control whenever authentication exists or a non-local web/API product surface requires an explicit access decision. |
| `sec-llm` | Audit prompt injection, untrusted model output, tool authority, model-mediated exfiltration, retrieval poisoning, and resource abuse. |
| `tenant-boundaries` | Audit multi-tenant context propagation and prove isolation across every tenant-owned storage and compute path. |
| `ux-design` | User-task clarity, compositional design quality, design systems, and accessibility (WCAG) for the hardening fleet. |
<!-- END:agents -->

## Procedures — the tool-neutral export

<!-- BEGIN:procedures -->
**39 files** in `procedures/` (+ **19 fleet criteria** in `procedures/agents/`) — the **canonical, tool-neutral source**. `sync_agent_stubs.py` generates 25 shared Claude and Codex skills, Codex's `harden` skill, Claude's `/harden` command, and the agent fleet FROM these, so every runtime reads the same markdown Claude runs:

`agent-operations.SCHEDULING.md`, `agent-operations.md`, `code-change.FRONTEND.md`, `code-change.REVIEW.md`, `code-change.md`, `context-engineering.REFERENCE.md`, `context-engineering.md`, `data-foundation.md`, `definitions.md`, `explain-change.md`, `external-integration.md`, `external-practice.md`, `frontend-quality.PROFILES.md`, `frontend-quality.md`, `grill-me.md`, `harden.md`, `iteration-shortcut.md`, `judging.EVALS.md`, `judging.REFERENCE.md`, `judging.md`, `linear-pipeline-hygiene.md`, `linear-pr-sync.md`, `llm-ops.CONTRACTS.md`, `llm-ops.EVALS.md`, `llm-ops.TRANSPORTS.md`, `llm-ops.md`, `log-redaction.md`, `mockup-review.md`, `model-frontier.REFERENCE.md`, `model-frontier.md`, `product-feature.md`, `scaffold-auth.md`, `scaffold-deploy.md`, `scaffold-design-system.md`, `scaffold-secrets.md`, `scaffold-tenant-schema.md`, `source-command-refresh-frontier.md`, `source-command-sync-agent-stubs.md`, `tool-selector.md`
<!-- END:procedures -->

## Projects under the rulebook

<!-- BEGIN:projects -->
**13 projects** carry the rulebook — each layers its own `AGENTS.md` on the global core, with thin `CLAUDE.md`/`GEMINI.md` wrappers:

| Project | Rulebook files present |
|---|---|
| agent-instructions | AGENTS.md, CLAUDE.md, GEMINI.md |
| angel-memos | AGENTS.md, CLAUDE.md, GEMINI.md |
| bhanu-resume-system | AGENTS.md, CLAUDE.md, GEMINI.md |
| blog-engine | AGENTS.md, CLAUDE.md, GEMINI.md |
| date-suggester | AGENTS.md, CLAUDE.md, GEMINI.md |
| earnings-summary | AGENTS.md, CLAUDE.md, GEMINI.md |
| harness | AGENTS.md, CLAUDE.md, GEMINI.md |
| huntdesk | AGENTS.md, CLAUDE.md, GEMINI.md |
| portfolio-tracker | AGENTS.md, CLAUDE.md, GEMINI.md |
| reading-companion-app | AGENTS.md, CLAUDE.md, GEMINI.md |
| repo-maintenance | AGENTS.md, CLAUDE.md, GEMINI.md |
| wealthplan | AGENTS.md, CLAUDE.md, GEMINI.md |
| xr-glasses-dev-guide | AGENTS.md, CLAUDE.md, GEMINI.md |
<!-- END:projects -->

## Adding a new project

1. Drop an `AGENTS.md` in the repo (or ask the agent to write one).
2. If it has a rendered interface, add the standard `## Interface` block or seed one with `python snippets/project_agent_contract.py init --repo <path> --profile <profile>`, then replace every `TODO` with the project-owned contract, executable paths, render recipe, and gate. Nonvisual repositories use profile `none`.
3. Run `python snippets/project_agent_contract.py check --repo <path>` and `/sync-agent-stubs` — the checker verifies local UI authority; sync adds the `CLAUDE.md`/`GEMINI.md` wrappers, wires the git hooks, re-lists the project, and reports non-blocking migration warnings for any other project without an Interface declaration.

## If you switch off Claude

Everything still works: `AGENTS.md` + `procedures/` (including the hardening fleet's per-expert criteria in `procedures/agents/`) are plain markdown that another capable runtime or local model can read directly. Procedures remain canonical; runtime skills are replaceable adapters. A candidate model earns blocking work through the same representative role evaluation and typed receipt rather than its provider or parameter count. The git hooks remain runtime-independent.
