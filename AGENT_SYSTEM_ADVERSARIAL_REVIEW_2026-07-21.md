# Agent System Adversarial Review — 2026-07-21

## Executive verdict

The system is now fit for Fable/Sol-led orchestration: the primary session owns
requirements, architecture, synthesis, and review; Sonnet/Terra is the normal
execution tier; Haiku/Luna is restricted to bounded mechanical work. Default
delegation is depth one with one to three workers, read-heavy parallelism, and
exclusive ownership for concurrent writes.

Before this pass, the instruction graph was directionally strong but internally
inconsistent. The largest risks were fixed-model pins, Claude-only dispatch
assumptions, fixed eight-agent fan-out, generated-file direction drift, audit
agents that simultaneously forbade and required writing, and app-hardening
gates applied without checking project type.

## What changed

- `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` now define runtime-native Fable/Sol
  orchestration and current workhorse/mechanical roles without forcing agents
  onto tiny cohesive tasks.
- The hardening fleet uses workhorse models for verdict-bearing audits, caps
  concurrency, checks applicability before dispatch, and assigns ownership for
  overlapping security/data/LLM findings.
- All 25 canonical hardening-agent files now permit only their audit report in
  AUDIT mode and no longer pin the frontier model for routine audit execution.
- Canonical direction is enforced as `procedures/ -> generated Claude/Codex
  artifacts`. The sync command now discovers unwired projects and works from a
  sandboxed runtime without Git dubious-ownership failures.
- Model-frontier guidance now covers Anthropic, OpenAI, and Google and separates
  dated evidence from durable routing policy.
- `angel-research` replaced a fixed four-researcher plus four-skeptic topology
  with adaptive zero-to-three research workers and one targeted skeptic only
  when a load-bearing claim remains uncertain.
- Missing rulebooks and wrappers were added for MyClaw, Wealthplan,
  repo-maintenance, and the XR glasses guide.

## Project fit

| Project | Fit after pass | Important project-specific boundary |
|---|---|---|
| angel-memos | Strong | High-stakes research uses source provenance, hostile-content handling, adaptive delegation, schema validation, and explicit user confirmation. |
| date-suggester | Good | Routine tests stay offline; real Calendar/Gmail/LLM/weather access is an explicitly authorized smoke test and email remains off by default. |
| earnings-summary | Strong | Fable/Sol retains pipeline judgment, workers have bounded ownership, directives need separate edit/commit authority, and mutable runs require one writer. |
| huntdesk | Good | ATS/job/company content is untrusted data; role and funding claims retain source/freshness metadata. |
| portfolio-tracker | Good with high-stakes caution | Metrics expose source/staleness; live DB migration/backfill needs backup, scope preview, and confirmation; LLM coaching cannot invent financial facts. |
| reading-companion-app | Appropriate for design stage | Manual capture, visible consent, minimal retention, deletion, citations, and physical-device privacy/performance checks precede passive capture. |
| myclaw | Good for experimental memory | Frontier-led curation, serialized state writers, and model/procedure/corpus provenance make experiments comparable. |
| wealthplan | Good with high-stakes caution | Household facts and tax constants require source/year/unit clarity and confirmation; sibling financial databases remain read-only. |
| repo-maintenance | Strong for operational scripts | Dry-run and explicit targets precede destructive work; backups require integrity and restore checks; live database files are handled as live state. |
| xr-glasses-dev-guide | Strong for a research repository | Official-source preference, freshness dates, platform distinctions, privacy, device constraints, and terminology/link checks replace irrelevant app scaffolding. |

## Adversarial findings resolved

1. **Frontier-model overuse:** every hardening expert previously ran on an
   expensive class. Experts now default to workhorse execution; only the root
   orchestrator performs judgment-heavy synthesis and blocking-verdict review.
2. **Ritual parallelism:** fixed fan-out spent quota even when one coherent
   pass was better. Delegation now depends on independent uncertainty and has a
   hard depth/concurrency ceiling.
3. **Split-brain source of truth:** source-command guidance implied generated
   skills could update procedures. Both command guidance and tests now enforce
   procedures as canonical.
4. **Impossible audit permissions:** agents said “never write” and then required
   a report. AUDIT mode now makes the report path the sole permitted write.
5. **Capability lag:** Codex was described as lacking subagents and preview
   tools were treated as universal. Dispatch is runtime-native, and visual
   agents use available browser/render tools while reporting verification gaps.
6. **Unsafe evidence ingestion:** investment, jobs, and XR/reading research did
   not consistently state that retrieved text is data, not instructions. The
   relevant project rules now do.
7. **High-stakes overwrite ambiguity:** angel decisions and personal-finance
   mutations now require validation, change summaries, conflict checks, atomic
   replacement, and user confirmation.
8. **Over-broad global absolutes:** numeric function-size and list-size gates,
   blanket inline-import bans, and blanket exact-text-test bans were converted
   to intent-based rules that modern models can apply with judgment.

## Residual risks and recommended next work

### Priority 1 — application model migrations

Several applications still contain evaluated or historical exact pins such as
older Sonnet/Opus IDs. Do not mechanically replace them. For each named LLM
purpose, run the existing blind eval and cost/latency gate, then promote the
new model through the central picker. Instruction routing and application
routing are deliberately separate.

### Priority 2 — skill modularity

`scaffold-design-system`, `scaffold-tenant-schema`, and `scaffold-deploy` are
useful but large and framework-specific. Split durable policy from
framework/provider recipes if maintenance starts producing divergent variants.
Keep the current files until there is a second real implementation target;
premature splitting would increase interface surface without proven value.

`llm-ops` also mixes durable governance with this machine's subscription
transport paths. A later cleanup should move machine paths and provider CLI
details into a local reference file while keeping the skill's core contract
portable.

### Priority 3 — ongoing evidence freshness

The Anthropic and OpenAI frontier rows were refreshed on 2026-07-21. The Google
rows remain older and should be restamped from official Google sources before a
Google routing decision. Treat the frontier table as dated evidence, never a
permanent roster.

### Priority 4 — behavioral eval coverage

Add small trigger/negative-trigger eval sets when a frequently used skill
starts misfiring. The two angel skills were forward-tested in this pass, but
most scaffold and hardening skills currently have schema/drift tests rather
than scenario-level behavioral evals.

## Verification performed

- 31 sync/generation/wrapper/model-default regression tests passed.
- All 15 personally authored and project-local skills checked in this pass
  passed the official skill frontmatter/schema validator.
- Both modified angel skills were forward-tested by fresh Terra workhorse
  agents against normal and adversarial scenarios; the discovered edge cases
  were incorporated.
- `sync_agent_stubs.py --check` reports no wrapper, generated-artifact, hook, or
  documentation drift.
- Existing unrelated working-tree changes, financial workbooks, databases,
  backups, and logs were not modified.

## Current-source basis

- OpenAI GPT-5.6 model guidance:
  https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6
- Anthropic Fable 5:
  https://www.anthropic.com/claude/fable
- Anthropic Sonnet 5:
  https://www.anthropic.com/news/claude-sonnet-5
- Anthropic Haiku:
  https://www.anthropic.com/claude/haiku
