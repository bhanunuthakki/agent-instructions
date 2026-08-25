---
name: context-engineering
description: Audit or rewrite AGENTS.md, CLAUDE.md, GEMINI.md, system prompts, skills, agent rubrics, tool descriptions, or memory placement for advanced models. Use for instruction hierarchy changes, prompt simplification, context bloat, conflicting rules, or progressive-disclosure migrations.
---

# Context Engineering

Design the assembled context for each task, not each file in isolation. Advanced models need the outcome, true invariants, relevant evidence, and stopping conditions; they do not benefit from several layers restating the same process.

Read [context-engineering.REFERENCE.md](context-engineering.REFERENCE.md) when provider-specific applicability or source provenance matters.

## Audit

1. Inventory every layer that can reach the model: system/developer prompt, global and nested rulebooks, runtime wrappers, skills, agent rubrics, tool schemas, memory, and the user request.
2. Sample the contexts assembled for representative tasks. Look for duplicate rules, contradictions, irrelevant tools, stale model facts, examples that narrow exploration, and instructions recoverable from the repository.
3. Give every instruction a disposition: **keep**, **move**, **merge**, **replace**, or **delete**. Record its current owner and intended owner so deletion does not silently remove a safety or authority boundary.
4. Classify each surviving item:
   - invariant: safety, authority, data, or business boundary;
   - local gotcha: repository fact the model cannot infer cheaply;
   - workflow: reusable task procedure;
   - reference: detailed rubric, schema, template, or example;
   - interface: tool parameters, return fields, and error behavior.

## Placement

- Put product identity and true cross-task invariants in the always-loaded root.
- Put repo purpose, exact commands, state ownership, data boundaries, and codebase-specific traps in the closest project or subtree rulebook.
- Keep runtime wrappers to imports and runtime-only mechanics.
- Put reusable workflows in skills. Keep the skill body to its decision flow and load detailed references only when needed.
- Put tool usage in the tool schema. Prefer expressive enums and return types to prose examples.
- Put historical facts and user preferences in memory, not durable project rules.
- Use source code, tests, schemas, mockups, and rubrics as high-fidelity references when they express the requirement better than prose.

## Rewrite

- State the user-visible outcome, success criteria, hard constraints, evidence needs, authority boundaries, and stop rules.
- Use absolute language only for genuine invariants. Express judgment calls as decision rules.
- State each instruction once at the narrowest scope that reliably applies.
- Merge overlapping routes around one owner and make adjacent owners name their handoff. A routing table should be collectively exhaustive for supported work without making every task load every procedure.
- Remove scaffolding for behavior the target model and tool interface already perform reliably.
- Do not add repeated verification prompts for a model that already verifies proactively. Keep explicit checks only where they define required evidence, a risk control, or a completion gate.
- Preserve provider-specific differences; cross-provider similarity is a hypothesis to validate, not permission to erase documented guidance.
- For long-running work, allow conservative adaptation when implementation reveals a load-bearing unknown, and surface the deviation with evidence.

## Validate

Change one instruction group at a time when practical. Validate only representative routes affected by the change during iteration; at a release boundary or after cross-route authority changes, broaden to the applicable matrix: a simple change, material feature, frontend change, and high-risk operation. Before expanding a focused instruction edit into a fleet-wide rewrite or expensive multi-model evaluation, confirm that broader outcome with the user unless they already requested it. Compare correctness, authority, and required evidence before token savings, then remove context that adds cost without decision value. Retain a rollback diff, verify generated artifacts, and check that every relative reference is reachable in each generated runtime layout.
