---
name: scaffold-design-system
description: Establish a small, accessible, stack-appropriate UI foundation after the user task and hierarchy are understood. Use when a project needs design tokens, reusable primitives, starter UI states, or a new web UI foundation.
---

# Scaffold: Design System

Create the smallest durable foundation for the product at hand. This is a generation workflow, not a generic aesthetic or framework recipe. `frontend-quality` owns the user-task hypothesis, composition, reduction pass, and rendered proof; `ux-design` later audits the resulting experience.

## Establish the fit first

1. Inspect the repository, existing design system, framework, component primitives, accessibility utilities, tests, and current rendered surfaces. Preserve a chosen stack and its conventions.
2. For a genuine greenfield project with no selected stack, present a neutral, small foundation that fits the deployment and team constraints. Do not presume Next.js, Tailwind, Radix, shadcn, or a specific font/aesthetic. Propose a library only when it materially removes a real accessibility or maintenance burden.
3. Follow `frontend-quality` before styling: define the primary task, information hierarchy, reading order, and minimum content. Start with ordinary document flow and one neutral page frame, then compose the fewest roles and primitives needed.

## Foundation contract

Create or complete the closest `AGENTS.md` `## Interface` declaration before styling:

- `Profile`: one seed from `frontend-quality.PROFILES.md` (`dense-desktop`, `editorial-reading`, `touch-first`, or `none`);
- `Contract`: a repository-relative project design contract, normally `docs/UI_CONTRACT.md`;
- `Executable authority`: repository-relative token, primitive, or stylesheet paths that implement the contract;
- `Render`: the runnable command and primary viewport or renderer;
- `Gate`: the deterministic command that checks the local contract.

The profile is scaffolding input only. Write the task-specific density, typography, spacing, interaction, responsive, state, exception, and rendered-evidence decisions into the local contract, then make the executable authority and gate enforce them. Do not leave another project's paths or design values in the scaffold.

Use the existing stack’s equivalent mechanisms, not copied framework samples. The foundation should have one source of truth for:

- semantic color, typography, spacing, sizing, shape, depth, motion, and breakpoint tokens; document foreground/background contrast pairings to WCAG AA where text or controls use them;
- a small semantic text-role set and one primary type family; another family is allowed only for a named semantic role;
- accessible primitives for the actual early controls (normally buttons, fields, overlays, navigation, and feedback), using native semantics first and mature focus/keyboard primitives where available;
- neutral empty, loading, and error states with clear meaning and recovery action when one exists; they do not need card treatment by default;
- locale-aware date, number, and currency formatting at a shared boundary.

Avoid raw visual literals outside the foundation, open-ended style APIs, hand-rolled focus traps or widgets when maintained primitives are available, `outline: none` without a visible focus replacement, layout-property animation, and `transition: all`.

## Accessibility and responsive baseline

- Preserve visible focus, keyboard operation, semantic labels, and non-color state cues.
- Keep targets at least 24px (44px on touch-first mobile contexts); mobile text inputs remain at least 16px.
- Respect reduced motion; animate only `transform` and `opacity` for brief feedback.
- Design empty, loading, error, overflow, and controlled-input states deliberately. Allow paste, validate after input, move focus to submitted errors, and preserve password-manager/2FA behavior.
- Use responsive layout primitives appropriate to the stack, dynamic viewport sizing and safe-area handling for fixed mobile surfaces, and locale-aware formatting.

## Finish

Add focused structural tests for the foundation’s actual contracts. Render the scaffold at applicable widths and states, then complete the `frontend-quality` reduction pass: remove decorative variants, redundant containers, unused tokens, and components that create a second grammar. Handoff identifies the task the starter surface supports, the primitives/tokens established, rendered proof, deterministic checks, and any verification gap.

Framework-specific examples belong in optional repository templates or references after stack selection, not in this universal procedure.
