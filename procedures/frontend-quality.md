---
name: frontend-quality
description: Design, modify, review, or scaffold a rendered interface around the user's task, with compositional restraint and proportional browser or renderer evidence. Use for frontend creation, visible UI changes, redesigns, mockups, or frontend reviews.
---

# Frontend Quality

Build the smallest coherent interface that makes the user's primary task easier and gives expressive work a deliberate identity. This procedure owns first-principles UX reasoning, expression-posture routing, compositional restraint, the rendered implementation loop, and the evidence record. It composes with `code-change`, `mockup-review`, `scaffold-design-system`, project design contracts, and hardening; it does not replace their engineering, product-behavior, or accessibility owners.

## Applicability and posture

A **material frontend change** adds, removes, rearranges, or materially restyles a visible region, control, hierarchy, navigation path, state, or responsive behavior. Typo-only copy corrections, nonvisual handler changes, and mechanically regenerated mirrors with no rendered delta are not material.

For a material change to a runnable existing interface, rendered evidence is part of implementation. For an unrunnable or non-web interface, use the closest renderer, simulator, or device evidence available and report the gap precisely. Never claim visual, hierarchy, responsive, or interaction verification that could not be observed.

## Start with the task, not the component

Before choosing cards, grids, accents, or variants, record a concise implementation hypothesis from the request, current workflow, product data, and active contracts:

- primary user and the task or decision being made;
- the one action or outcome the surface makes easiest;
- minimum information and intended reading/interaction order;
- what is primary, supporting, or progressively disclosed;
- observed friction and the smallest visible change expected to improve it;
- **grounded domain data:** never invent or simulate metrics, percentages, margins, burn rates, or KPIs not supported by the project’s data models or verified primary sources. In private-company, financial, and operational tools, surface authentic state attributes (stage, round, lead investor, census, ATS status, verified citations) rather than generic venture-dashboard proxies.

This is working reasoning, not a mandatory questionnaire. Inspect available evidence and make reversible product judgments. Use `grill-me` only when an unresolved product choice would materially change the result; use a mockup when recognition is more useful than prose. Prototype approval never authorizes production changes.

## Choose the expression posture

Expression posture is orthogonal to the interface profile and describes how much visual continuity or exploration the task needs:

- **`conform`:** preserve an established family, supplied template, or familiar platform convention. Use for routine additions, repairs, and utility-first greenfield work unless the request or contract calls for a distinct identity. Do not manufacture alternatives by default.
- **`evolve`:** preserve the shell, semantic roles, control behavior, state anatomy, and product truth while materially improving hierarchy, composition, or identity. Use when the current language should remain recognizable but the requested outcome cannot be reached by a local adjustment.
- **`explore`:** create or replace a distinctive visual direction. Use for explicitly expressive, memorable, brand-led, immersive, or greenfield identity work, and for an authorized departure from an established family. Bounded divergence is required before selecting a direction.

Infer the posture from the user request, current product, and local contract; record it when the change is material. For `evolve` and `explore`, extend the hypothesis with the intended response, identity constraints, one candidate signature idea, supplied references or inspiration, and anti-goals. If a missing taste choice would materially change the result, ask once or create an isolated mockup comparison; do not silently collapse expressive work into the safest default.

Read [frontend-quality.CREATIVE.md](frontend-quality.CREATIVE.md) completely for `explore` and for consequential expressive `evolve` work. Keep it out of routine `conform` tasks.

Read [frontend-quality.PRIMITIVES.md](frontend-quality.PRIMITIVES.md) completely when creating,
changing, auditing, or automating a reusable primitive, component family, design-system catalog, or
drift gate. Keep project names, visual recipes, and product mutation semantics in the project-owned
contract and executable authority.

Before composing an established project interface, resolve the closest `AGENTS.md` `## Interface` block in this order:

1. Read its `Profile`, `Contract`, `Executable authority`, `Render`, and `Gate` fields.
2. Load the project-owned contract, any primitive catalog it links, and every executable authority it names before proposing or editing visual code.
3. Render the current page plus its nearest shipped sibling and registered family at the declared primary viewport.
4. Treat a missing field, missing file, repository-escaping reference, or unrunnable recipe as an authority gap. Repair it when the request authorizes project changes; otherwise report it instead of silently borrowing another project's language.

The standard declarations and profile seeds are defined in `frontend-quality.PROFILES.md`; profiles seed new contracts but never override an established local authority. If a repository has no rendered interface, its entire declaration is `## Interface` with `Profile: none`.

For `conform` and `evolve`, preserve the registered family's shell, navigation, semantic text roles, controls, density, responsive grammar, and state anatomy. Introduce a new family only under `explore`, when the user task cannot be expressed by an existing family or the owner authorizes a new identity, with a typed rationale and an adversarial continuity test. Exact tokens, recipes, exceptions, and verification commands remain project-owned and must not be copied into this shared procedure.

## Observe–reason–change–reobserve

For a material change to an existing runnable surface:

1. Render and inspect the affected baseline before editing. Exercise the primary task and identify the current friction.
2. When `explore` or consequential `evolve` applies, select a direction through the creative workflow before editing production code. Then compose the fewest roles, primitives, and registered recipes that realize the selected direction. Add or extend styling only for a remaining named semantic, identity, or interaction need.
3. After each material composition change, re-render and exercise the affected path. Inspect applicable populated, loading, empty, error, focus, and overflow states plus project-supported viewports; check hierarchy, clipping, density, feedback, console errors, and failed requests.
4. Compare the final surface to the hypothesis, then perform the reduction pass below. Do not replace this loop with source inspection or one final screenshot.

The scope is proportional: inspect affected states and viewports, not an unrelated matrix. `frontend-web` owns implementation fidelity and browser/console mechanics; `ux-design` owns task clarity and whole-page composition.

## Compositional restraint

- **Typography economy:** use one primary family and only established semantic text roles. Another face, including mono, needs a named semantic role. Give one page or region the largest heading; a subtitle must add information, not repeat it. Do not stack size, weight, color, case, and indentation when one cue communicates hierarchy.
- **Container economy:** begin with ordinary flow. A box, rail, divider, background, shadow, or panel needs a named semantic, state, interaction, or ownership boundary. Prefer whitespace, alignment, and proximity; nested boxes need a distinct boundary at every level. Flatten any container whose removal preserves comprehension and operation.
- **Layout consistency:** use one dominant layout grammar per surface or registered family. Equivalent sections use equivalent recipes; do not vary adjacent layouts merely for visual novelty. Responsive behavior preserves hierarchy rather than inventing a second visual language.
- **Semantic differentiation:** accent communicates interaction, selection, focus, or unread state. Status communicates status and keeps a non-color cue. Decorative accent rails, arbitrary tinted panels, gradients, ornamental icons, oversized numerals, and floating shapes require a concrete product purpose and approved recipe.
- **Structural formatting:** indentation represents a parent-child relationship and bullets represent parallel items. Do not turn isolated facts, labels, or prose into indentation or bullets for texture.
- **Operating bands over empty space:** prioritize immediate access to working tasks over decorative titles or inactive whitespace. Headings must not push working surfaces below the viewport. Any list, register, or table tracking more than 5 items must include a compact operating band containing instant search and single-select facet filters.

### Motion economy

When motion is introduced or changed, name its user-serving purpose: feedback, state legibility, spatial continuity, or prevention of a jarring change. If none applies, keep the transition instant. Reduce motion intensity as interaction frequency rises; keyboard-led and repeatedly invoked flows default to immediate response. Do not move information the user is reading or acting on for decoration. Exact timing, easing, geometry, and sanctioned exceptions remain project-owned.

### Reduction pass

Inspect the whole affected surface before completion. Remove non-semantic decoration; flatten redundant containers; normalize equivalent text and controls; remove decorative titles, ungrounded proxy KPIs, and empty whitespace that delays user action; remove redundant subtitles, helper text, badges, dividers, and icons; and reject locally attractive components that create another page-level grammar. When in doubt, choose the plainer treatment unless the richer one has a named semantic or interaction purpose.

## Route product behavior to its owner

This procedure does not decide navigation or destinations, overlays and dismissal behavior, control mutation semantics, provenance meaning, or operational truth. The portable primitive reference defines the distinction questions, not a project's answers. Follow the active project owners for those concerns. When an operation, operational observation, or operator action changes, complete that project’s operations-governance disposition. Project design contracts may narrow this procedure with exact roles, recipes, and sanctioned exceptions; they must not duplicate this rubric.

## Evidence and handoff

For a material frontend change, record compact dual proof:

| Field | Record |
|---|---|
| Task and outcome | surface/route, primary task exercised, and observed user-visible result |
| Expression | posture and, when applicable, selected direction and intended response |
| Rendered evidence | browser/renderer used, affected viewports and states, baseline/final observation |
| Deterministic proof | applicable design, accessibility, frontend, and repository checks |
| Reduction | what was removed or flattened, or why nothing qualified |
| Gaps | unavailable rendering, states, widths, or interactions; do not imply they passed |

For reviews and hardening, ask: Does the result fit the selected posture and intended response? What recognizable idea carries its identity? What boundary does each container express? Why does each indentation exist? What does each text treatment or accent communicate? Why is an equivalent section visually different? What becomes harder if this element is removed? An unclear answer is a finding, not permission to keep it.

Shadow fixtures and task trajectories may calibrate this procedure. They do not prove that it was invoked on every task; invocation coverage needs an independent task population frame under `judging`.
