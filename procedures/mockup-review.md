---
name: mockup-review
description: Redesign or review an existing application page through an observed mockup, task hypothesis, and proportional implementation notes. Use for mockups, redesigns, visual revisions, or design review before production implementation.
---

# Mockup Review

Keep mockup approval separate from production implementation. A prototype may be interactive, but it must not silently become a live route, writer, or source of truth. The normal posture for a personal/local tool is an observed mockup, a clear user-task hypothesis, and compact implementation notes—not a program-management exercise.

## Default review loop

1. Inspect the current diff, existing rendered page, active design contract, executable guards, and production import path. Determine whether a mockup is isolated or production-derived.
2. For a material runnable surface, capture the baseline and exercise the primary task. State the primary user, dominant action, information order, observable friction, and smallest expected improvement under `frontend-quality`.
3. Preserve truth: identify visible data as live, derived, owner-ratified, draft, stale, unavailable, illustrative, or proposed. For retained or added controls, note user intent, read-only versus mutating behavior, and unresolved behavior.
4. Compose the fewest existing roles and primitives. Perform the whole-page reduction pass: remove decorative variation, redundant containers, repeated titles/subtitles, and secondary grammars before adding styling.
5. Verify the mockup at affected widths and states, including applicable keyboard/focus, overflow, console, and network evidence. Record browser/renderer evidence and explicit gaps.

Use focused structural tests where the repository supports them. Do not modify APIs, persistence, migrations, jobs, or live routes during a mockup-only request.

## Compact handoff

For normal personal/local work, hand off:

- approved artifact/revision and user-visible outcome;
- task exercised, widths/states observed, deterministic checks, and verification gaps;
- data-truth and interaction notes for changed visible values/controls;
- a short Keep / Change / Unknown implementation note with exact seams.

Approval covers only the revision shown. A later material revision reopens visual approval; production implementation still needs separate authorization.

## Escalate only when the handoff is consequential

Use the expanded discovery and implementation package only when the user explicitly requests a **production implementation handoff**, the redesign is consequential and multi-surface, or the work is a commercial transition. Then, proportionate to risk:

- run bounded existing-page, backend-capability, and implementation-delta discovery (three read-only workers only when delegation is available and useful);
- maintain complete data-truth and interaction registers for every affected visible value/control, including typed payloads, freshness, degradation, authorization, idempotency, and error states;
- produce a durable requirements artifact with an exhaustive boundary census, acceptance trace, delivery decomposition, and release/rollback matrix; and
- reconcile an approved delivery roadmap or Linear only when tracking exists and the user authorized those writes. Read back every external write.

Unknowns remain visible; illustrative fixtures never become a claim of backend capability. Route operational changes through the project’s operations-governance owner. The expanded package is an implementation handoff, not a prerequisite for an ordinary mockup review.
