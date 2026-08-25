---
name: agent-operations
description: Coordinate subagents, shared worktrees, capability roles, or scheduled LLM work. Use when delegating implementation or audits, running parallel agent work, creating or changing recurring LLM jobs, or deciding which worker capability should own a task.
---

# Agent Operations

Keep the root agent responsible for intent, architecture, synthesis, and final verification. Delegate only a bounded workstream whose output can be checked independently.

## Capability roles

- **mechanical-worker** — inventory, extraction, formatting, deterministic comparison, or other work with an exact acceptance check.
- **implementation-worker** — a specified code or document change inside an owned boundary with repository tests.
- **blocking-specialist** — narrow expertise required to resolve a material risk, failure, or unknown.
- **frontier-synthesizer** — ambiguous architecture, cross-domain synthesis, or consequential review where weaker reasoning would dominate the outcome.

Choose the least expensive currently evaluated model that meets the role. A provider label, model name, context-window size, or advertised tier is not evidence of fitness. Record a capability receipt when routing matters: role, purpose, runtime, model identifier, effort, relevant evaluation, evaluation date, and known limit. If no current evidence qualifies a candidate, use a stronger evaluated candidate or return `HOLD`; do not silently lower the role.

## Dispatch

- Before a nontrivial fan-out, check whether one short user answer is likely to change the result enough to avoid materially greater elapsed time, worker count, token/model spend, rework, or debt. When it is, use the lightweight `grill-me` route first. Otherwise proceed with the smallest reversible default or narrow the fan-out. Record this decision only when the delegation is material; it is not a universal receipt or another rigor tier.
- Give each worker one outcome, explicit scope or file ownership, relevant constraints, required evidence, and a stopping condition.
- Use one to three concurrent workers at depth one unless the runtime or task proves a different limit useful. Parallelize independent reads; serialize overlapping writes.
- Do not leak the intended answer into an audit or skill evaluation. Give the worker the raw artifact and acceptance criteria.
- A worker returns findings, changed paths, and validation evidence. The root reconciles conflicts and verifies the integrated result.
- Improve a weak brief or split the task before escalating capability. Resume an interrupted worker when its context is still valid.

## Shared checkout

- Treat unexplained changes as intentional. Check status before editing and do not revert unrelated work.
- Concurrent writers need exclusive file or module ownership. If an existing change overlaps and cannot be preserved mechanically, stop at that file and ask.
- Stage or commit only an explicit allowlist. Verify staged names and whitespace before committing.

## Scheduling and quota

When work uses subscription-backed agents or recurring LLM calls, read [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) before dispatch or registration.

## Completion

The root finishes only after checking the worker result against the repository state and the task’s success criteria. Delegation changes who executes; it does not transfer decision ownership.
