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

Use the runtime's normal assignment for ordinary bounded delegation. For recurring, scheduled, high-risk, or evaluation-governed routing, choose the least expensive currently evaluated model that meets the role and record a capability receipt with the material evidence. A provider label, model name, context window, or advertised tier alone is not evidence of fitness; insufficient evidence for a consequential route yields `HOLD`, not silent down-tiering.

## Dispatch

- Before a nontrivial fan-out, check whether one short user answer is likely to change the result enough to avoid materially greater elapsed time, worker count, token/model spend, rework, or debt. When it is, use the lightweight `grill-me` route first. Otherwise proceed with the smallest reversible default or narrow the fan-out. Record this decision only when the delegation is material; it is not a universal receipt or another rigor tier.
- Cross-task messages may update a dependency or resource handoff, but they do not replace the current task's user objective unless the user explicitly accepts the expanded scope. Apply relevant coordination to the original deliverable, then validate and report that deliverable; queue or acknowledge irrelevant coordination without making it the task's reported outcome.
- Give each worker one outcome, explicit scope or file ownership, relevant constraints, required evidence, and a stopping condition.
- Use one to three concurrent workers at depth one unless the runtime or task proves a different limit useful. Parallelize independent reads; serialize overlapping writes.
- Do not leak the intended answer into an audit or skill evaluation. Give the worker the raw artifact and acceptance criteria.
- A worker returns findings, changed paths, and validation evidence. The root reconciles conflicts and verifies the integrated result.
- Improve a weak brief or split the task before escalating capability. Resume an interrupted worker when its context is still valid.
- Treat an auto-reconnecting browser or remote-control session as an owned mutable resource even when it appears idle. A handoff names the current owner, in-flight action, last proof, resources held or released, and receiving owner; the applicable browser or remote-control workflow owns release mechanics.

## Shared checkout

- Treat unexplained changes as intentional. Check status before editing and do not revert unrelated work.
- Concurrent writers need exclusive file or module ownership. If an existing change overlaps and cannot be preserved mechanically, stop at that file and ask.
- Stage or commit only an explicit allowlist. Verify staged names and whitespace before committing.

## Failure recovery

During delegated or coordinated work: After two equivalent failures from the same tool or mechanism, change the approach or surface the blocker. Do not repeat an unchanged attempt.

## Scheduling and quota

When work uses subscription-backed agents or recurring LLM calls, read [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) before dispatch or registration.

## Completion

For delegated or coordinated work, synthesize worker activity into the user-visible outcome rather than returning an activity log. During a long operation, also provide a concise periodic update when the user would otherwise lack current status.

When delegated work finishes, propagate the result promptly, cancel temporary task-owned monitors that are no longer part of the requested outcome, and release held resources. Preserve a user-requested persistent monitor until its own stop condition or explicit cancellation. The root checks worker results against repository state and success criteria, then applies the global completion contract. Delegation changes who executes; it does not transfer decision ownership.
