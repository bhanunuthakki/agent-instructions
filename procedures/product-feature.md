---
name: product-feature
description: Define or review a material product feature before implementation: user outcome, smallest coherent behavior, state and authority, non-goals, acceptance evidence, and kill criteria.
---

# Product Feature

Use this for a material new capability or behavior change. Extend the existing task understanding with the behavior and acceptance decisions below. Keep it as working reasoning unless a written specification is requested or helps coordinate consequential work; it is not a questionnaire or a required separate artifact.

## Feature contract

Establish from repository evidence and the request:

- **User and job:** who encounters the problem, what recurring task or decision is improved, and the current workaround.
- **Outcome:** the observable user-visible result. Name the primary path and the smallest coherent vertical slice.
- **Boundaries:** non-goals and affected permissions or external/destructive effects, applying the global authorization contract.
- **Truth and state:** the canonical owner of every read and write; distinguish source-of-truth state from derived views, caches, drafts, and evidence. Reuse a sound existing authority; replace or extend it when observed limitations justify the change, retaining explicit migration and ownership.
- **Behavior:** entry point, state transitions, empty/loading/error/recovery behavior, cancellation or rollback, and effects on existing operations or surfaces.
- **Evidence:** acceptance checks tied to the outcome. Use rendered evidence for visible work, deterministic checks for rules and data, and representative evals for probabilistic behavior.
- **Learning:** when usefulness is uncertain, the cheapest signal and a condition to simplify, remove, or stop the experiment. Established behavior and straightforward fixes need no invented experiment.

Resolve the affected domain terms from their closest owner. Discovery and mockup language may remain provisional. Use `definitions` for durable semantic changes, public/persisted names, or collisions; ordinary internal naming does not need ratification.

Prefer a derived projection over unnecessary persistence and a coherent behavior path over redundant implementations. Choose a larger replacement when evidence shows that it improves the requested outcome more effectively than incremental patches. Evaluate usefulness, clarity, reliability, and effort; small diff size is not the product objective. Route a deliberate temporary compromise through `iteration-shortcut` rather than hiding it in the feature contract.

## Ownership

- Product feature owns the feature outcome, behavior boundary, non-goals, and acceptance contract. Identify affected action authorities; do not redefine their approval rules.
- `frontend-quality` owns task hierarchy, composition, and rendered UX evidence.
- `architecture-reviewer` owns system/module structure; `data-foundation` owns durable truth and lifecycle; `code-change` owns implementation; QA owns test sufficiency.

Carry these decisions into implementation through the shared task record. Additional procedures contribute their constraints and evidence; the global collaboration and completion contracts govern questions and delivery.
