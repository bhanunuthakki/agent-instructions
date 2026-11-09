---
name: context-engineering
description: Audit or rewrite AGENTS.md, CLAUDE.md, GEMINI.md, system prompts, skills, agent rubrics, tool descriptions, or memory placement for advanced models. Use for instruction hierarchy changes, prompt simplification, context bloat, conflicting rules, progressive-disclosure migrations, /correct recurring-mistake elimination, or /reflect transcript learning.
---

# Context Engineering

Design the assembled context for each task, not each file in isolation. Advanced models need the outcome, true invariants, relevant evidence, and stopping conditions; they do not benefit from several layers restating the same process.

Read [context-engineering.REFERENCE.md](context-engineering.REFERENCE.md) when provider-specific applicability, authored-documentation style (`technical-writing` / `unslop`), or source provenance matters.

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

- Put cross-task invariants and bounded initiative in the always-loaded global contract. Put product identity and improvement priorities in the local project rulebook; keep this repository’s global source (`GLOBAL.md`) separate from its own `AGENTS.md`.
- Put repo purpose, exact commands, state ownership, data boundaries, and codebase-specific traps in the closest project or subtree rulebook.
- Keep runtime wrappers to imports and runtime-only mechanics.
- Put reusable workflows in skills. Keep the skill body to its decision flow and load detailed references only when needed.
- Put tool usage in the tool schema. Prefer expressive enums and return types to prose examples.
- Put historical facts and user preferences in memory, not durable project rules.
- Keep memory selective: stable preferences, durable decisions and rationale, hard-to-rederive constraints, and unresolved obligations. Keep task progress in its owning task record and repository facts in canonical sources. Update or supersede existing entries rather than appending repeated summaries. At closure, preserve useful evidence references and unique history under their owning policy; retire transient tool output, temporary paths, and completed-session detail. Keep the memory index short and load detail on demand. Disk retention and model-context retention are separate decisions.
- When an incident pattern or agent mistake class recurs (`>= 2` occurrences across commits, reverts, reviews, or user corrections, or an explicit `/correct` pass), fix it at the highest enforcement tier that works before adding prose:
  1. **Architecture:** give each piece of state one owner and each task one supported path; hide internals so wrong imports fail; delete dead or legacy patterns that an agent inspecting one file would copy.
  2. **Types:** encode the invariant so the invalid state cannot be constructed.
  3. **Lint or CI check:** add a deterministic check whose error message names the replacement symbol, file, or command, and prove it fails on a real past mistake.
  4. **Behavior test:** add or repair a test that fails when observable behavior breaks.
  5. **Instruction or policy prose last:** maintain one current lesson at its narrowest owning instruction or application policy only for judgment calls that code cannot enforce, paired with its enforcement check or evidence pointer. Supersede stale guidance rather than appending another incident transcript or competing memory entry, and drop a prose rule once structural enforcement prevents the mistake.
- Use source code, tests, schemas, mockups, and rubrics as high-fidelity references when they express the requirement better than prose.
- For `/reflect` after a non-trivial task, inspect only the active workspace's session transcript (never glob across unrelated projects), extract recurring process or domain lessons, and route them to concrete proposals or requested edits on the owning canonical procedure. For an explicit pause or session pickup (`pause-safely` / `session-pickup`), stop at a safe atomic boundary without unapproved external writes, record intent, verified state, and the exact resume action in the task record or a compact off-context note (never copy raw transcripts into durable memory), and on pickup reconstruct state from that trail and Git history without redoing completed work while still verifying inherited claims against the real artifact before closure.

## Rewrite

- State the user-visible outcome, success criteria, hard constraints, evidence needs, authority boundaries, and stop rules.
- Use absolute language only for genuine invariants. Express judgment calls as decision rules.
- State each instruction once at the narrowest scope that reliably applies.
- Merge overlapping routes around one owner and make adjacent owners name their handoff. The routing catalog should be collectively exhaustive for supported work without making every task load every procedure: one primary deliverable owner plus controls for actual changed boundaries, sharing one outcome and evidence record.
- Remove scaffolding for behavior the target model and tool interface already perform reliably.
- Do not add repeated verification prompts for a model that already verifies proactively. Keep explicit checks only where they define required evidence, a risk control, or a completion gate.
- Keep the same outcome, authority, and evidence standard across models. Preserve provider-specific differences in thin runtime adjustments only when current documentation or observed failures justify them; identify the model/runtime version and a recheck condition. A new model is not a reason to copy its full prompting guide into the global contract. Cross-provider similarity remains a hypothesis to validate.
- For long-running work, allow conservative adaptation when implementation reveals a load-bearing unknown, and surface the deviation with evidence.

## Validate

Include owner enablement when auditing collaboration instructions: routine decisions proceed without unnecessary homework; consequential decisions carry recommendations and practical tradeoffs; references or prototypes resolve vague preferences; useful challenges preserve user authority; delivery is inspectable and honest about evidence. Review assembled contexts, including the host's existing instructions, so a local improvement does not compound an inherited rule.


Change one instruction group at a time when practical. Validate only representative routes affected by the change during iteration; at a release boundary or after cross-route authority changes, broaden to the applicable matrix: a simple change, material feature, frontend change, and high-risk operation. Before expanding a focused instruction edit into a fleet-wide rewrite or expensive multi-model evaluation, confirm that broader outcome with the user unless they already requested it. Compare correctness, authority, and required evidence before token savings, then remove context that adds cost without decision value. Retain a rollback diff, verify generated artifacts, and check that every relative reference is reachable in each generated runtime layout.
