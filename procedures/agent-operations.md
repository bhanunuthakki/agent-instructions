---
name: agent-operations
description: Coordinate subagents, shared worktrees, model tiers, or scheduled LLM work. Use when delegating implementation or audits, running parallel agent work, creating or changing recurring LLM jobs, or deciding which agent tier should own a task.
---

# Agent Operations

Keep the root agent responsible for intent, architecture, synthesis, and final verification. Delegate only a bounded workstream whose output can be checked independently.

## Dispatch

- Give each worker one outcome, explicit scope or file ownership, relevant constraints, and required evidence.
- Use one to three concurrent workers at depth one. Parallelize independent reads freely; serialize overlapping writes.
- Choose the cheapest tier that can own the judgment: mechanical extraction at the fast tier, specified execution at the workhorse tier, and ambiguous or high-impact synthesis at the frontier tier.
- Do not leak the intended answer into an audit or skill evaluation. Give the worker the raw artifact and acceptance criteria.
- A worker returns findings, changed paths, and validation evidence. The root reconciles conflicts and verifies the integrated result.
- Improve a weak brief or split the task before escalating model tier. Resume an interrupted worker when its context is still valid.

## Shared checkout

- Treat unexplained changes as intentional. Check status before editing and do not revert unrelated work.
- Concurrent writers need exclusive file or module ownership. If an existing change overlaps and cannot be preserved mechanically, stop at that file and ask.
- Stage or commit only an explicit allowlist. Verify staged names and whitespace before committing.

## Scheduling and quota

When work uses subscription-backed agents or recurring LLM calls, read [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) before dispatch or registration.

## Completion

The root finishes only after checking the worker result against the repository state and the task’s success criteria. Delegation changes who executes; it does not transfer decision ownership.
