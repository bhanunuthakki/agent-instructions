# Gemini Agent Instructions

@./AGENTS.md

---

The block above (`AGENTS.md`) is the canonical, tool-agnostic rulebook and governs everything. The section below is **Gemini-only**: it substitutes for the native skills/commands/hooks that Claude Code has and Gemini CLI does not. Claude never loads this file (it reads `CLAUDE.md`), so there is no duplication across tools.

## Skill-mimic — read the procedure on trigger

Gemini has no skill auto-loader, so when one of these triggers fires, **read the named procedure file first, then act on it.** These are the same self-contained, tool-neutral procedures any runtime uses (see `AGENTS.md` → "How any runtime consumes this system").

<!-- BEGIN:triggers -->
| Trigger (say the name, or its frontmatter 'use when') | Read this first, then act on it |
|---|---|
| **definitions** — Build, refresh, or enforce the project's ubiquitous-language vocabulary file (DEFINITIONS.md). | `procedures/definitions.md` |
| **explain-change** — After an LLM writes or edits code, explain the change in plain language for a non-expert reviewer — what changed, what could break, and how to confir… | `procedures/explain-change.md` |
| **grill-me** — Force the Grill-Me requirements-gathering protocol on the current task. | `procedures/grill-me.md` |
| **llm-ops** — Govern an LLM-backed feature so no call is a black box — one entry point, a purpose-keyed model picker, schema-validated output, per-call cost/latenc… | `procedures/llm-ops.md` |
| **log-redaction** — Design guidance for keeping secrets out of logs and exception output (AGENTS.md Universal Safety Rule 4). | `procedures/log-redaction.md` |
| **model-frontier** — Pick an LLM against the dated cross-provider cost/performance frontier instead of from memory. | `procedures/model-frontier.md` (+ `model-frontier.REFERENCE.md`) |
| **scaffold-auth** — Generate secure-by-default authentication for a web app — the generative counterpart to the sec-authz audit gate. | `procedures/scaffold-auth.md` |
| **scaffold-deploy** — Take a working localhost app to a live, secure deployment — container + managed platform + CI + backups. | `procedures/scaffold-deploy.md` |
| **scaffold-design-system** — Generate a secure-by-default, accessible design system for a new web UI — design tokens, a small Radix-based component set, and empty/loading/error s… | `procedures/scaffold-design-system.md` |
| **scaffold-secrets** — Set up secrets/env handling so credentials never enter the repo and load typed at startup. | `procedures/scaffold-secrets.md` |
| **scaffold-tenant-schema** — Generate secure-by-default multi-tenant database schema, Postgres Row-Level Security policies, a tenant-context object, and reversible Alembic migrat… | `procedures/scaffold-tenant-schema.md` |
| **harden** — Run the maturity-gated hardening fleet (L0→L3) — audit a project with domain-expert subagents and gate advancement. | `procedures/harden.md` (+ `procedures/agents/`) |
<!-- END:triggers -->

`procedures/` is the **canonical source**; the Claude skills are generated *from* it. This table is regenerated from the procedures' frontmatter by `snippets/sync_agent_stubs.py` — re-run it (or `/sync-agent-stubs`) after adding a procedure so Gemini stays in sync. Each row's procedure is self-contained; the hardening fleet's per-expert criteria live in `procedures/agents/`.

## Gemini-specific notes

- **Enforcement (hooks):** the credential-scan and pre-push gates are **git hooks** in a shared `githooks/` dir wired per-repo via `core.hooksPath`, so they fire for Gemini sessions too — they are not Claude-only. The stub generator runs `git config core.hooksPath <…/githooks>` for each repo.
- **Dispatch:** use Gemini's native subagent surface when the active runtime exposes one; otherwise run the same `procedures/harden.md` criteria sequentially. Do not claim dispatch is Claude-only.
- **Model tiers:** Fable/Sol are the preferred orchestrators in their native runtimes. When Gemini is launched explicitly, fill judgment with the current Pro-class model, execution with Pro or Flash as warranted, and mechanical work with Flash/Flash-Lite; verify the current lineup rather than pinning a remembered ID.
