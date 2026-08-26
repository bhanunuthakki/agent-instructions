---
name: frontend-quality
description: Design, modify, review, or scaffold a rendered interface around the user's task, with compositional restraint and proportional browser or renderer evidence. Use for frontend creation, visible UI changes, redesigns, mockups, or frontend reviews.
---

# Frontend Quality

Build the smallest coherent interface that makes the user's primary task easier. This procedure owns first-principles UX reasoning, compositional restraint, the rendered implementation loop, and the evidence record. It composes with `code-change`, `mockup-review`, `scaffold-design-system`, project design contracts, and hardening; it does not replace their engineering, product-behavior, or accessibility owners.

## Applicability and posture

A **material frontend change** adds, removes, rearranges, or materially restyles a visible region, control, hierarchy, navigation path, state, or responsive behavior. Typo-only copy corrections, nonvisual handler changes, and mechanically regenerated mirrors with no rendered delta are not material.

For a material change to a runnable existing interface, rendered evidence is part of implementation. For an unrunnable or non-web interface, use the closest renderer, simulator, or device evidence available and report the gap precisely. Never claim visual, hierarchy, responsive, or interaction verification that could not be observed.

## Start with the task, not the component

Before choosing cards, grids, accents, or variants, record a concise implementation hypothesis from the request, current workflow, product data, and active contracts:

- primary user and the task or decision being made;
- the one action or outcome the surface makes easiest;
- minimum information and intended reading/interaction order;
- what is primary, supporting, or progressively disclosed;
- observed friction and the smallest visible change expected to improve it.

This is working reasoning, not a mandatory questionnaire. Inspect available evidence and make reversible product judgments. Use `grill-me` only when an unresolved product choice would materially change the result; use a mockup when recognition is more useful than prose. Prototype approval never authorizes production changes.

Before composing an established project interface, resolve the closest `AGENTS.md` `## Interface` block in this order:

1. Read its `Profile`, `Contract`, `Executable authority`, `Render`, and `Gate` fields.
2. Load the project-owned contract and every executable authority it names before proposing or editing visual code.
3. Render the current page plus its nearest shipped sibling and registered family at the declared primary viewport.
4. Treat a missing field, missing file, repository-escaping reference, or unrunnable recipe as an authority gap. Repair it when the request authorizes project changes; otherwise report it instead of silently borrowing another project's language.

The standard declarations and profile seeds are defined in `frontend-quality.PROFILES.md`; profiles seed new contracts but never override an established local authority. If a repository has no rendered interface, it declares profile `none` and every other field `none`.

Preserve the registered family's shell, navigation, semantic text roles, controls, density, responsive grammar, and state anatomy. Introduce a new family only when the user task cannot be expressed by an existing family, with a typed rationale and an adversarial continuity test. Exact tokens, recipes, exceptions, and verification commands remain project-owned and must not be copied into this shared procedure.

## Observe–reason–change–reobserve

For a material change to an existing runnable surface:

1. Render and inspect the affected baseline before editing. Exercise the primary task and identify the current friction.
2. Compose the fewest existing roles, primitives, and registered recipes that address the hypothesis. Add or extend styling only for a remaining named semantic or interaction need.
3. After each material composition change, re-render and exercise the affected path. Inspect applicable populated, loading, empty, error, focus, and overflow states plus project-supported viewports; check hierarchy, clipping, density, feedback, console errors, and failed requests.
4. Compare the final surface to the hypothesis, then perform the reduction pass below. Do not replace this loop with source inspection or one final screenshot.

The scope is proportional: inspect affected states and viewports, not an unrelated matrix. `frontend-web` owns implementation fidelity and browser/console mechanics; `ux-design` owns task clarity and whole-page composition.

## Compositional restraint

- **Typography economy:** use one primary family and only established semantic text roles. Another face, including mono, needs a named semantic role. Give one page or region the largest heading; a subtitle must add information, not repeat it. Do not stack size, weight, color, case, and indentation when one cue communicates hierarchy.
- **Container economy:** begin with ordinary flow. A box, rail, divider, background, shadow, or panel needs a named semantic, state, interaction, or ownership boundary. Prefer whitespace, alignment, and proximity; nested boxes need a distinct boundary at every level. Flatten any container whose removal preserves comprehension and operation.
- **Layout consistency:** use one dominant layout grammar per surface or registered family. Equivalent sections use equivalent recipes; do not vary adjacent layouts merely for visual novelty. Responsive behavior preserves hierarchy rather than inventing a second visual language.
- **Semantic differentiation:** accent communicates interaction, selection, focus, or unread state. Status communicates status and keeps a non-color cue. Decorative accent rails, arbitrary tinted panels, gradients, ornamental icons, oversized numerals, and floating shapes require a concrete product purpose and approved recipe.
- **Structural formatting:** indentation represents a parent-child relationship and bullets represent parallel items. Do not turn isolated facts, labels, or prose into indentation or bullets for texture.

### Reduction pass

Inspect the whole affected surface before completion. Remove non-semantic decoration; flatten redundant containers; normalize equivalent text and controls; remove redundant titles, subtitles, helper text, badges, dividers, and icons; and reject locally attractive components that create another page-level grammar. When in doubt, choose the plainer treatment unless the richer one has a named semantic or interaction purpose.

## Route product behavior to its owner

This procedure does not decide navigation or destinations, overlays and dismissal behavior, control mutation semantics, provenance meaning, or operational truth. Follow the active project owners for those concerns. When an operation, operational observation, or operator action changes, complete that project’s operations-governance disposition. Project design contracts may narrow this procedure with exact roles, recipes, and sanctioned exceptions; they must not duplicate this rubric.

## Evidence and handoff

For a material frontend change, record compact dual proof:

| Field | Record |
|---|---|
| Task and outcome | surface/route, primary task exercised, and observed user-visible result |
| Rendered evidence | browser/renderer used, affected viewports and states, baseline/final observation |
| Deterministic proof | applicable design, accessibility, frontend, and repository checks |
| Reduction | what was removed or flattened, or why nothing qualified |
| Gaps | unavailable rendering, states, widths, or interactions; do not imply they passed |

For reviews and hardening, ask: What boundary does each container express? Why does each indentation exist? What does each text treatment or accent communicate? Why is an equivalent section visually different? What becomes harder if this element is removed? An unclear answer is a finding, not permission to keep it.

Shadow fixtures and task trajectories may calibrate this procedure. They do not prove that it was invoked on every task; invocation coverage needs an independent task population frame under `judging`.
