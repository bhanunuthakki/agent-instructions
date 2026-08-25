---
name: product-feature
description: Define or review a material product feature before implementation: user outcome, smallest coherent behavior, state and authority, non-goals, acceptance evidence, and kill criteria.
---

# Product Feature

Use this for a material new capability or behavior change. Keep it lightweight for small personal tools: the output is a decision contract, not a project-management ceremony.

## Feature contract

Establish from repository evidence and the request:

- **User and job:** who encounters the problem, what recurring task or decision is improved, and the current workaround.
- **Outcome:** the observable user-visible result. Name the primary path and the smallest coherent vertical slice.
- **Boundaries:** non-goals, permissions, destructive or external actions, and what remains unchanged.
- **Truth and state:** the canonical owner of every read and write; distinguish source-of-truth state from derived views, caches, drafts, and evidence. Reuse an existing authority unless a seam census proves it cannot represent the requirement.
- **Behavior:** entry point, state transitions, empty/loading/error/recovery behavior, cancellation or rollback, and effects on existing operations or surfaces.
- **Evidence:** acceptance checks tied to the outcome. Use rendered evidence for visible work, deterministic checks for rules and data, and representative evals for probabilistic behavior.
- **Learning:** the cheapest signal that the feature is useful, plus a falsifiable condition to simplify, remove, or stop it.

Load the effective definition chain at the start. Discovery and mockup language may remain provisional, but route a term through `definitions` before it becomes a durable code symbol, schema/API field, persisted state, canonical UI label, or governing directive concept.

Prefer a derived projection over new persistence, one behavior path over parallel implementations, and a reversible local change over speculative platform work. Route a deliberate temporary compromise through `iteration-shortcut` rather than hiding it in the feature contract.

## Ownership

- Product feature owns user outcome, behavior boundary, non-goals, action authority, and acceptance contract.
- `frontend-quality` owns task hierarchy, composition, and rendered UX evidence.
- `architecture-reviewer` owns system/module structure; `data-foundation` owns durable truth and lifecycle; `code-change` owns implementation; QA owns test sufficiency.

## Handoff

State the outcome, smallest slice, authorities reused, new state or side effects, acceptance evidence, and open owner decisions. Ask only when a missing product choice would materially alter the result; otherwise choose the smallest reversible default and continue.
