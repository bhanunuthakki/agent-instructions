---
name: agent-operations
description: Dispatch bounded workers or coordinate shared worktrees, resources, capability roles, and scheduled LLM work. Load for actual orchestration when its benefit exceeds coordination cost.
---

# Agent Operations

The root agent owns user intent, decomposition, architecture, synthesis, authority decisions, and final verification. Use a capable available root; resolve a consequential model selection through `model-frontier`, without requiring a model switch for routine work. Delegate bounded workstreams whose outputs can be checked independently to the least expensive evaluated capability that fits; delegation changes execution ownership, not decision ownership. Formal Judge or Critic seats remain separately briefed, frontier-class, and governed by `judging`, including its purpose-qualification and independence requirements.

## Delegation check

For coordinated work, reconsider delegation when new evidence, user input, or a phase transition changes which streams are independent or economical. Dispatch useful independent work early; do not add a delegation ceremony to a serial task.

- Delegate when a bounded evidence, implementation, or verification stream benefits from independent work while the root can make useful progress. Use one to three parallel workers when their benefit exceeds setup and reconciliation.
- Good worker streams include repository or source inventories, independent primary-source checks, test or failure triage, isolated file or module changes with an exact acceptance check, rendered-behavior inspection, and adversarial review.
- Keep work at the root when it is a trivial single action, tightly coupled to the root's next decision, blocked on a user answer that would materially change the decomposition, or likely to cost more in coordination than it saves.
- Never parallelize overlapping writes or shared mutable resources. Give concurrent workers exclusive file, module, state, or resource ownership; serialize the rest.
- Keep the root active on decomposition, synthesis, integration, or an independent workstream while workers run. Consume completed results promptly and reassess the remaining work instead of waiting for every worker when one result changes the plan.

## Capability roles

- **mechanical-worker** — inventory, extraction, formatting, deterministic comparison, or other work with an exact acceptance check.
- **implementation-worker** — a specified code or document change inside an owned boundary with repository tests.
- **blocking-specialist** — narrow expertise required to resolve a material risk, failure, or unknown.
- **frontier-synthesizer** — ambiguous architecture, cross-domain synthesis, or consequential review where weaker reasoning would dominate the outcome.

Use the least expensive currently evaluated model for each bounded worker role. Cost optimization applies to execution workers, not the root, acceptance, or formal Judge seats. For recurring, scheduled, high-risk, or evaluation-governed routing, record a capability receipt with the material evidence. A provider label, model name, context window, or advertised tier alone is not evidence of fitness; insufficient evidence for a consequential route yields `HOLD`, not silent down-tiering.

## Dispatch

- Before a nontrivial fan-out, check whether one short user answer is likely to change the result enough to avoid materially greater elapsed time, worker count, token/model spend, rework, or debt. When it is, use the lightweight `grill-me` route first. Otherwise proceed with the smallest reversible default or narrow the fan-out. Record this decision only when the delegation is material; it is not a universal receipt or another rigor tier.
- Cross-task messages may update a dependency or resource handoff, but they do not replace the current task's user objective unless the user explicitly accepts the expanded scope. Apply relevant coordination to the original deliverable, then validate and report that deliverable; queue or acknowledge irrelevant coordination without making it the task's reported outcome.
- Cross-service or cross-session coordination without GUI automation uses headless CLI transports (such as `snippets/codex_cli.py` or `snippets/claude_cli.py`). An active session in one runtime can pass task handoffs, audit findings, or verification summaries to another service's headless agent via non-interactive CLI execution (`codex exec`, `claude exec`).
- Give each worker one outcome, explicit scope or file ownership, relevant constraints, required evidence, and a stopping condition.
- Use one to three concurrent workers at depth one unless the runtime or task proves a different limit useful. Workers do not recursively fan out by default.
- Do not leak the intended answer into an audit or skill evaluation. Give the worker the raw artifact and acceptance criteria.
- A worker returns findings, changed paths, and validation evidence. The root reconciles conflicts and verifies the integrated result.
- Improve a weak brief or split the task before escalating capability. Resume an interrupted worker when its context is still valid.
- Treat an auto-reconnecting browser or remote-control session as an owned mutable resource even when it appears idle. A handoff names the current owner, in-flight action, last proof, resources held or released, and receiving owner. The current owner releases the session through the applicable browser or remote-control workflow and verifies release. The receiving owner takes control only after that verified release.

## Shared checkout

- Treat unexplained changes as intentional. Check status before editing and do not revert unrelated work.
- Concurrent writers need exclusive file or module ownership. If an existing change overlaps and cannot be preserved mechanically, stop at that file and ask.
- Stage or commit only an explicit allowlist. Verify staged names and whitespace before committing.

## Failure recovery

During delegated or coordinated work: After two equivalent failures from the same tool or mechanism, change the approach or surface the blocker. Do not repeat an unchanged attempt.

## Scheduling and quota

For multi-agent bursts sharing a quota or recurring LLM jobs, read [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) before dispatch or registration. An ordinary single call does not require a scheduling review.

## Completion

For delegated or coordinated work, synthesize worker activity into the user-visible outcome rather than returning an activity log. During a long operation, also provide a concise periodic update when the user would otherwise lack current status.

When delegated work finishes, propagate the result promptly, cancel temporary task-owned monitors that are no longer part of the requested outcome, and release held resources. Preserve a user-requested persistent monitor until its own stop condition or explicit cancellation. The root checks worker results against repository state and success criteria, resolves conflicts with direct evidence, makes the final acceptance judgment, then applies the global completion contract.
