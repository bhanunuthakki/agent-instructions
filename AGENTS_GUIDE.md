# Your agent system — human guide

A one-page map of what you have and when it fires. **This file is for you, not the agents** — no tool loads it into context (only `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` auto-load).

The **inventory tables** below (skills · commands · agents · procedures · projects) are **auto-generated** from the filesystem by `/sync-agent-stubs` and live between `<!-- BEGIN:… -->` / `<!-- END:… -->` markers — so the counts can never silently drift again. The pre-push hook runs `--check` and fails if they fall out of date. Everything *outside* the markers is hand-written prose; edit it freely.

## The mental model

- **`AGENTS.md`** (at `C:\Users\bhanu\.gemini\`) = the always-on rulebook every tool reads. Slim on purpose.
- **`CLAUDE.md`** / **`GEMINI.md`** = thin wrappers that import `AGENTS.md` and add tool-specific bits.
- **`procedures/`** = the heavy "how-to" guides (auth, deploy, evals…), as plain markdown any tool can read. **The canonical source** — the Claude skills, the `/harden` command, and the agent fleet (`procedures/agents/`) are generated *from* these.
- **Skills / commands / hooks** = how Claude (and git) make the above automatic. Other tools (Gemini, Codex, a local model) read `AGENTS.md` → `procedures/` and get the same thing.

You rarely touch any of this. It just shapes how the agent behaves.

## Skills — say the trigger, the agent does the thing

<!-- BEGIN:skills -->
**15 shared skills** — say the trigger, the agent runs the procedure. Codex also exposes `harden` as a native skill; Claude exposes the same procedure as `/harden`.

| Skill | What it does |
|---|---|
| **agent-operations** | Coordinate subagents, shared worktrees, model tiers, or scheduled LLM work. |
| **code-change** | Implement, fix, refactor, or review code with the repository’s tests and conventions. |
| **context-engineering** | Audit or rewrite AGENTS.md, CLAUDE.md, GEMINI.md, system prompts, skills, agent rubrics, tool descriptions, or memory placement for advanced models. |
| **definitions** | Build, refresh, or enforce the project’s canonical domain vocabulary in DEFINITIONS.md. |
| **explain-change** | After an LLM writes or edits code, explain the outcome, impact, risk, and proof in plain language at a depth proportional to the change. |
| **external-practice** | Verify a consequential, drift-sensitive implementation or design choice against current primary sources. |
| **grill-me** | Interview the user to uncover load-bearing unknowns before a feature, design, plan, or consequential decision. |
| **llm-ops** | Govern an LLM-backed feature with one entry point, purpose-based model selection, schema-validated output, attributable fallbacks, per-call cost and… |
| **log-redaction** | Design guidance for keeping secrets out of logs and exception output (AGENTS.md Universal Safety Rule 4). |
| **model-frontier** | Pick an LLM against the dated cross-provider cost/performance frontier instead of from memory. |
| **scaffold-auth** | Generate secure-by-default authentication for a web app — the generative counterpart to the sec-authz audit gate. |
| **scaffold-deploy** | Take a working localhost app to a live, secure deployment — container + managed platform + CI + backups. |
| **scaffold-design-system** | Generate a secure-by-default, accessible design system for a new web UI — design tokens, a small Radix-based component set, and empty/loading/error s… |
| **scaffold-secrets** | Set up secrets/env handling so credentials never enter the repo and load typed at startup. |
| **scaffold-tenant-schema** | Generate secure-by-default multi-tenant database schema, Postgres Row-Level Security policies, a tenant-context object, and reversible Alembic migrat… |
<!-- END:skills -->

## Commands — type these

<!-- BEGIN:commands -->
**3 commands** — type these.

| Command | What it does |
|---|---|
| `/harden` | Run the maturity-gated hardening fleet (L0→L3) — audit a project with domain-expert subagents and gate advancement. |
| `/refresh-frontier` | Re-verify and restamp the model cost/performance frontier reference with today's prices. |
| `/sync-agent-stubs` | Ensure every scratch project has CLAUDE.md/GEMINI.md wrappers importing its rulebook, and wire the shared git hooks. |
<!-- END:commands -->

## What happens automatically (no action needed)

- **On `git commit`** → the pre-commit hook blocks credential files and hardcoded secrets. Bypass a false positive with `git commit --no-verify`.
- **On `git push`** → the pre-push hook runs the full toolchain gate in order (sync deps → format → lint → typecheck → tests → build), **then verifies the global instruction system is in sync** (`sync_agent_stubs.py --check` + its tests) — so a stale or hand-edited Claude artifact, GEMINI trigger table, or guide table blocks the push from *any* wired repo (the meta-repo isn't itself under git, so this cross-repo gate is what enforces it). Never pushes red. Bypass with `git push --no-verify`.
- Hooks live in `C:\Users\bhanu\.gemini\githooks\` and are wired into each repo by `/sync-agent-stubs`. They work in **both** Claude and Gemini sessions (and plain `git`).

## The hardening fleet (advanced, opt-in)

Domain-expert "auditors" that grade a project from idea (L0) to commercial release (L3) — security, architecture, data, infra, legal, payments, etc. You invoke them via `/harden`. **Most are SaaS-grade and won't fire on personal tools** (that's the L1 cap). Use them when a project is genuinely heading to paying users.

<!-- BEGIN:agents -->
**25 audit agents** — criteria canonical in `procedures/agents/`, generated into `~/.claude/agents/` for Claude's `/harden` dispatch (most are SaaS-grade and won't fire on personal tools — that's the L1 cap).

| Agent | Audits |
|---|---|
| `api-mcp-ingestor` | On-demand ingestion of an external API or MCP server's docs/capabilities into a usable capability map plus a typed client/contract, for the hardening… |
| `api-surface-designer` | The outbound API/MCP surface the product EXPOSES to customers and developers — contract design, versioning, idempotency, pagination, errors, webhooks… |
| `architecture-reviewer` | System-design coherence and Deep-Module review for the hardening fleet. |
| `backend-multitenancy` | Multi-tenant data model and tenant-context propagation for the hardening fleet. |
| `content-marketing` | Positioning, messaging, and content strategy for the hardening fleet — value proposition, landing page, and acquisition content. |
| `customer-support` | Support and helpdesk for the hardening fleet — channels, ticketing, knowledge base, SLAs, escalation, incident comms, and the feedback loop to produc… |
| `data-engineer` | Traceable, auditable, robust data for the hardening fleet — schema design, pipeline robustness, lineage/provenance, data-quality audits, and retentio… |
| `docs-devex` | User documentation, API reference, onboarding, and developer experience for the hardening fleet. |
| `finops-pricing` | Unit economics and pricing for the hardening fleet — cost-of-goods modeling (compute, LLM tokens, data licenses, support), margin per tenant, and the… |
| `frontend-web` | Frontend implementation quality for the hardening fleet — correctness, performance, responsiveness, and rendered-UI verification. |
| `idea-evaluator` | Decide if and what to build for the hardening fleet — time commitment, commercial viability, market wedge, competitive landscape, data-rights feasibi… |
| `infra-devops` | CI/CD, infrastructure-as-code, environments, deployment, and release safety for the hardening fleet. |
| `infra-sre` | Reliability and operability for the hardening fleet — observability (logs/metrics/traces), SLOs and alerting, resilience patterns, backups/DR with te… |
| `legal-compliance` | Legal and regulatory posture for the hardening fleet — data-rights and licensing feasibility (L0), privacy (GDPR/CCPA) and data handling once real PI… |
| `llm-evals-orchestrator` | LLM call governance for the hardening fleet — every LLM call must have a model-picker, an eval harness scoring response quality, structured schema-va… |
| `notifications-email` | Transactional notifications and email deliverability for the hardening fleet — provider setup, templates, SPF/DKIM/DMARC, bounce/complaint handling,… |
| `payments` | Billing and payments for the hardening fleet — provider integration, subscriptions/metering, invoicing, dunning, tax, refunds/chargebacks, with PCI s… |
| `product-analytics-growth` | Product analytics instrumentation, funnel/activation/retention measurement, SEO, and onboarding-flow optimization for the hardening fleet. |
| `qa-test-strategy` | Test strategy beyond per-change TDD for the hardening fleet — E2E/integration/regression suites, test data, CI gates, and (L3) load/performance testi… |
| `sec-appsec` | Application-security audit for the hardening fleet — secrets hygiene, PII handling, dependency/supply-chain (SCA/SBOM), injection (SQLi/XSS/SSRF/comm… |
| `sec-authz` | Authentication and authorization for the hardening fleet — identity (SSO/OAuth/OIDC/passwords/MFA), session and token lifecycle, RBAC/ABAC, broken-ac… |
| `sec-llm` | LLM-specific security for the hardening fleet — prompt injection (direct and indirect), the OWASP LLM Top 10, untrusted output handling, tool-call sa… |
| `sec-tenant-isolation` | Tenant isolation for the hardening fleet — guarantee no tenant can read or write another tenant's data, cache, storage, jobs, or compute. |
| `tool-selector` | On-demand build/buy decisions for the hardening fleet — evaluate tools, libraries, services, and vendors by cost, functional fit, lock-in, and operat… |
| `ux-design` | Design language, design system, user-centered design, and accessibility (WCAG) for the hardening fleet. |
<!-- END:agents -->

## Procedures — the tool-neutral export

<!-- BEGIN:procedures -->
**24 files** in `procedures/` (+ **25 fleet criteria** in `procedures/agents/`) — the **canonical, tool-neutral source**. `sync_agent_stubs.py` generates 15 shared Claude and Codex skills, Codex's `harden` skill, Claude's `/harden` command, and the agent fleet FROM these, so every runtime reads the same markdown Claude runs:

`agent-operations.SCHEDULING.md`, `agent-operations.md`, `code-change.FRONTEND.md`, `code-change.REVIEW.md`, `code-change.md`, `context-engineering.REFERENCE.md`, `context-engineering.md`, `definitions.md`, `explain-change.md`, `external-practice.md`, `grill-me.md`, `harden.md`, `llm-ops.CONTRACTS.md`, `llm-ops.EVALS.md`, `llm-ops.TRANSPORTS.md`, `llm-ops.md`, `log-redaction.md`, `model-frontier.REFERENCE.md`, `model-frontier.md`, `scaffold-auth.md`, `scaffold-deploy.md`, `scaffold-design-system.md`, `scaffold-secrets.md`, `scaffold-tenant-schema.md`
<!-- END:procedures -->

## Projects under the rulebook

<!-- BEGIN:projects -->
**11 projects** carry the rulebook — each layers its own `AGENTS.md` on the global core, with thin `CLAUDE.md`/`GEMINI.md` wrappers:

| Project | Rulebook files present |
|---|---|
| angel-memos | AGENTS.md, CLAUDE.md, GEMINI.md |
| blog-engine | AGENTS.md, CLAUDE.md, GEMINI.md |
| date-suggester | AGENTS.md, CLAUDE.md, GEMINI.md |
| earnings-summary | AGENTS.md, CLAUDE.md, GEMINI.md |
| huntdesk | AGENTS.md, CLAUDE.md, GEMINI.md |
| myclaw | AGENTS.md, CLAUDE.md, GEMINI.md |
| portfolio-tracker | AGENTS.md, CLAUDE.md, GEMINI.md |
| reading-companion-app | AGENTS.md, CLAUDE.md, GEMINI.md |
| repo-maintenance | AGENTS.md, CLAUDE.md, GEMINI.md |
| wealthplan | AGENTS.md, CLAUDE.md, GEMINI.md |
| xr-glasses-dev-guide | AGENTS.md, CLAUDE.md, GEMINI.md |
<!-- END:projects -->

## Adding a new project

1. Drop an `AGENTS.md` in the repo (or ask the agent to write one).
2. Run `/sync-agent-stubs` — it adds the `CLAUDE.md`/`GEMINI.md` wrappers, wires the git hooks, and re-lists the project in the table above.

## If you switch off Claude

Everything still works: `AGENTS.md` + `procedures/` (including the hardening fleet's per-expert criteria in `procedures/agents/`) are plain markdown that Codex/Cursor/Aider/a local model read directly — the procedures are the canonical source, not a Claude export, so nothing is lost. You lose only the auto-triggering + parallel-subagent convenience (you'd point the tool at the relevant `procedures/<name>.md` and run the fleet matrix sequentially). The git hooks keep working regardless.
