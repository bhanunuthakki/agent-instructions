# Agent scheduling and quota reference

Use this reference only for multi-agent bursts or recurring jobs that call Claude or Codex.

## Shared subscription pools

- `claude_cli.py` and interactive Claude sessions share the Claude Pro/Max window.
- `codex_cli.py` and interactive Codex sessions share ChatGPT/Codex membership usage and credits.
- Record provider and transport separately in usage ledgers. A subscription avoids per-call API billing but not quota exhaustion.

## Before a burst or new recurring job

1. Inspect the machine’s scheduled tasks and relevant repo `cron/` directories for LLM-calling jobs.
2. Keep 03:00–05:00 America/Los_Angeles clear. The earnings-summary morning pipeline runs at 04:00 and its monthly scenario-prior refresh runs at 03:00.
3. Run one bounded agent wave per quota window and space waves by at least 6–7 hours.
4. If the task list cannot be inspected, say so and avoid scheduling into the protected window.

## Recurring-job failure behavior

- Treat a transient subscription CLI failure as `defer this item and continue`; record the deferred count and retry on the next run.
- Fail loudly on setup, schema, authorization, or hard budget errors.
- Do not let one quota-starved item abort an otherwise independent batch.

Reference implementation: earnings-summary `directives/llm_quota_scheduling.md` and the `attach_conditions` per-item degradation pattern.
