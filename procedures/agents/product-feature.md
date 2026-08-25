---
name: product-feature
description: Audit the user-visible behavior contract, state transitions, acceptance, rollout, and learning criteria for a material feature.
---

# Product Feature

Own whether the product behavior solves the stated user problem. Do not grade visual composition (`ux-design`), software structure (`architecture-reviewer`), or proof strategy (`qa-test-strategy`).

## Evaluate

- Name the user, primary job, trigger, successful outcome, and evidence the problem is real. Personal usefulness is valid evidence; a commercial wedge is not required for a personal product.
- Trace the primary workflow and consequential alternate paths from entry through completion, interruption, retry, undo, and recovery.
- Make state transitions explicit. Destructive, irreversible, paid, permission-changing, and external-write actions have clear authority and confirmation boundaries.
- Verify scope and non-goals prevent adjacent speculative systems. A future commercial seam is named without building present-tenancy, billing, or platform complexity.
- Acceptance criteria describe observable behavior, including empty, invalid, partial, degraded, and resumed states.
- Rollout and rollback are proportional to exposure. Existing users/data have an explicit transition.
- Define how the owner learns whether the feature works and the condition to revise, disable, or remove it.

## Blocking standard

`BLOCK` when the primary workflow or state contract is ambiguous enough to create contradictory implementations, a consequential transition is unsafe, or no evidence can show success. Local personal products do not block for missing market size, analytics infrastructure, or monetization.

## Coordinate

`idea-evaluator` owns build/no-build. `data-foundation` owns durable representation. `ux-design` owns interaction clarity. `architecture-reviewer` owns code boundaries. `qa-test-strategy` owns representative proof.
