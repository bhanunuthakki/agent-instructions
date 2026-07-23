---
description: Run the maturity-gated hardening fleet (L0→L3) — audit a project with domain-expert subagents and gate advancement. Usage: /harden [rung] [--deep] [--audit <expert>] [--status] [--full]
---

# Hardening Orchestrator

You are the **conductor** of a maturity-gated fleet of domain-expert **audit/fix subagents** whose criteria are canonical in `procedures/agents/<expert>.md`, taking a project from ideation to limited commercial release. The expertise lives in those agent files; this command is the dispatch logic, matrix, and gate rules.

Parse `$ARGUMENTS` into the mode below. With no arguments, default to **quick upgrade to `current_rung + 1`**.

## Runtimes

The expert **criteria** are tool-neutral files in `procedures/agents/<expert>.md` — every runtime audits against the same criteria; only the dispatch differs.

- **Claude:** Fable 5 orchestrates and dispatches generated expert agents through the Agent tool. Expert files under `~/.claude/agents/` are generated from `procedures/agents/`; edit the procedure, not the copy.
- **Codex:** Sol orchestrates and dispatches the corresponding expert role through its native collaboration tools, normally overriding workers to Terra. Use Luna only for bounded inventories/extraction, not verdicts.
- **Other runtimes:** use their native dispatch surface when available. A runtime that genuinely lacks it reads the same expert criteria and runs a sequential guided pass. Worktree-isolated FIX mode may degrade to approved in-place work only when the runtime cannot isolate changes.

## Modes (explicit — no fuzzy phrase-matching)

| Invocation | Action |
|---|---|
| `/harden` | **Quick upgrade** to `current_rung + 1`: the target rung's gates + cheap re-verify (`↻`) of prior blocking gates |
| `/harden <rung>` (e.g. `/harden l2`) | Quick upgrade straight to a named rung |
| `/harden --deep` · `/harden --deep <rung>` | **Robust re-run** — full re-audit of every gate `L0..target`, ignoring cached state |
| `/harden --audit <expert>` | Run a single expert against current state |
| `/harden --status` | Read `.harden/state.json`, run cheap checks only, report blockers — **no fixes** |
| `/harden --full` | Override the personal-project L1 cap (see below) and allow L2/L3 multi-tenant/commercial gates |

## Personal-project default (L1 cap)

Most of this user's projects are personal/single-user local tools (earnings-summary, huntdesk, portfolio-tracker). **Unless `--full` is passed or the project clearly targets multi-tenant/commercial release, cap the target at L1** and skip the L2/L3 gates (tenant isolation, payments, dunning, marketing, support). When you cap, say so in one line and note `--full` unlocks the rest. L2+ assumes a real multi-tenant SaaS.

## Rungs

- **L0 Ideation** — decide if/what to build.
- **L1 MVP / Prototype** — works end-to-end for one tenant.
- **L2 Multi-tenant Beta** — safe to admit multiple real tenants.
- **L3 Limited Commercial Release** — sellable, supportable, legal, monetized.

## Matrix

`B` blocking · `A` advisory · `↻` re-verify · `—` n/a. Each expert first appears at its *cheapest useful* rung (shift-left).

| Expert | L0 | L1 | L2 | L3 |
|---|:--:|:--:|:--:|:--:|
| idea-evaluator | B | — | — | — |
| finops-pricing | A | — | — | B |
| architecture-reviewer | A | B | ↻ | ↻ |
| legal-compliance | A | — | B | B |
| data-engineer | — | B | ↻ | — |
| llm-evals-orchestrator | — | B | ↻ | ↻ |
| qa-test-strategy | — | B | ↻ | ↻ |
| sec-appsec | — | A | B | ↻ |
| sec-llm | — | A | B | — |
| backend-multitenancy | — | A | B | — |
| infra-devops | — | A | B | — |
| infra-sre | — | A | B | ↻ |
| ux-design | — | A | — | B |
| frontend-web | — | A | — | B |
| api-surface-designer | — | A | ↻ | B |
| sec-tenant-isolation | — | — | B | — |
| sec-authz | — | — | B | — |
| product-analytics-growth | — | — | A | B |
| customer-support | — | — | A | B |
| notifications-email | — | — | A | B |
| docs-devex | — | — | A | B |
| payments | — | — | — | B |
| content-marketing | — | — | — | A |

**On-demand (not rung-gated):** `tool-selector`, `api-mcp-ingestor` — invoke whenever a build/buy or external-integration decision arises, at any rung.

**Solo-builder note:** `infra-devops` (deploy mechanics) and `infra-sre` (observability/SLO/DR) are adjacent — for a one-person project run them as a single "infra" pass (dispatch both, treat their findings as one operational report). Keep prompt-secret hygiene owned by `sec-llm`; `llm-evals-orchestrator` cross-references it rather than re-auditing it.

### Overlap ownership

Assign one owner to each finding and cross-reference supporting reports rather
than filing duplicates:

- `sec-appsec` owns general application vulnerabilities, secret hygiene,
  dependency risk, injection, and abuse controls.
- `sec-authz` owns identity, sessions, authorization policy, IDOR, and key
  lifecycle; `sec-tenant-isolation` owns proof that tenant boundaries hold
  across every storage and compute path.
- `sec-llm` owns prompt injection, untrusted model output, tool agency, and LLM
  data exfiltration. `llm-evals-orchestrator` owns response quality, structured
  contracts, cost/latency telemetry, routing evals, and regression detection.
- `data-engineer` owns data quality, provenance, lineage, and lifecycle;
  `backend-multitenancy` owns tenant-context propagation and tenant-ready
  schema shape.

### Applicability before dispatch

Record a one-line rationale for every selected or skipped expert. The matrix gives the earliest useful rung; it does not make an irrelevant gate mandatory.

- No LLM calls → skip `llm-evals-orchestrator` and `sec-llm`.
- No persistent or externally sourced data → skip `data-engineer`.
- No deployed service or scheduled production workload → skip `infra-devops` and `infra-sre`.
- No external users or public API → skip customer, growth, notification, payments, and public API gates.
- Documentation/research repositories use source quality, freshness, licensing, and consistency checks; do not force application scaffolds onto them.
- Native/mobile/XR work uses platform accessibility, permissions, privacy, device performance, and simulator-versus-device evidence; web-only checks are n/a unless a web client exists.

**Model tiers:** Fable (Claude) or Sol (Codex) is the orchestrator and final reviewer. Fleet agents default to the workhorse tier (Sonnet/Terra). Mechanical pre-scans may use Haiku/Luna, but a blocking verdict requires workhorse review. Improve a failed brief before escalating model tier.

## Generative scaffolds (build-it-right-first, not just grade-it-after)

Before auditing a gate on a greenfield project, prefer to **generate** the secure baseline, then audit it:
- auth → `scaffold-auth` skill (verified by `sec-authz`)
- tenant schema / RLS / migrations → `scaffold-tenant-schema` skill (verified by `sec-tenant-isolation`, `backend-multitenancy`, `data-engineer`)
- design system → `scaffold-design-system` skill (verified by `ux-design`)
- LLM governance → `llm-ops` skill (verified by `llm-evals-orchestrator`)

## Dispatch protocol

1. Read `.harden/state.json` (create at `L0` if absent, conforming to the schema below). Resolve the target rung and its gate set from the matrix, applying the L1 cap unless `--full`.
2. Apply the applicability rules, then dispatch independent experts through the runtime's native subagent tool. Default to depth 1 and no more than three concurrent workers. Honor `Depends on`; hard-ordered: `data-engineer → backend-multitenancy`; `sec-authz` + `backend-multitenancy → sec-tenant-isolation`; `legal-compliance → payments`.
3. Each expert runs **AUDIT mode**: product code and state are read-only; `docs/hardening/<rung>/<expert>.md` is the sole permitted write. It returns the same report and verdict to the orchestrator.
4. **Gate logic:** at a `B` cell, any open `critical`/`high` finding ⇒ rung **BLOCKED**. `A`/`↻` cells log findings, never block. Advancing requires every `B` gate at the target rung = `PASS`.
5. The Fable/Sol orchestrator checks applicability, deduplicates overlapping findings, reviews every blocking verdict, and presents the consolidated result. **Wait for explicit approval before any product change.**
6. On approval: create a git **worktree**, dispatch the relevant experts in **FIX mode** to apply approved fixes there, then re-audit to confirm green. Never fix on the working branch. (On this machine, remove worktrees with PowerShell `Remove-Item -Force`, not `git worktree remove` — Drive sync breaks it.)
7. Update `.harden/state.json`.

## Output contract

- **Report** (`docs/hardening/<rung>/<expert>.md`): verdict, findings table (`severity | location | finding | fix`), checklist results, out-of-scope notes. Severity ∈ {critical, high, medium, low, info}. Stamp with today's date.
- **State** (`.harden/state.json`) — conform to this schema:

```json
{
  "$schema": "internal://harden-state/v1",
  "current_rung": "L0|L1|L2|L3",
  "is_multitenant_target": false,
  "gates": {
    "<rung>": {
      "<expert>": {
        "verdict": "PASS|BLOCK|ADVISORY",
        "open_findings": 0,
        "last_run": "YYYY-MM-DD"
      }
    }
  }
}
```

Validate the file against this shape on read; if malformed, halt and report rather than guessing. Quick runs skip already-passed checks (idempotent); `--deep` ignores the cache.
