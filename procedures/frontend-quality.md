---
name: frontend-quality
description: Design, modify, review, or scaffold a rendered interface around the user's task, with compositional restraint and proportional browser or renderer evidence. Use for frontend creation, visible UI changes, redesigns, mockups, or frontend reviews.
---

# Frontend Quality

Improve the user's task and give expressive work a deliberate identity. This procedure owns interaction hierarchy, expression posture, and rendered evidence. Product/domain contracts own behavior, state, and mutation meaning; `code-change` owns implementation; project UI contracts own exact visual language and control geometry. Share one task hypothesis and evidence record across those owners.

## Applicability and task hypothesis

A material frontend change alters a visible region, hierarchy, interaction, state, or responsive behavior. Typo-only corrections, nonvisual handlers, and generated mirrors with no rendered delta do not require a full visual cycle.

For material work, inspect the request, affected workflow, authentic product data, and current surface. Identify the primary user, desired outcome, information/interaction order, observed friction, and expected improvement. Keep this concise working reasoning rather than a questionnaire. Use `grill-me` only for an unresolved choice that would materially change the solution.

Never invent financial or operational metrics and present them as product truth. Isolated mockups and tests may use clearly labeled synthetic fixtures that fit supported domain shapes and protect private inputs. Distinguish proposed capability from implemented capability.

## Expression and improvement latitude

- **`conform`:** repair or extend an established language when it serves the task. Reuse its semantics and sound recipes; do not manufacture alternatives.
- **`evolve`:** improve hierarchy, interaction, composition, or identity while preserving recognizable context and domain meaning. Change the shell, density, navigation arrangement, or recipe when observed friction justifies it and the task authorizes that boundary.
- **`explore`:** establish or replace a visual direction when the task calls for it or the existing family cannot express the outcome. Compare meaningful directions when the choice is genuinely open; a clear supplied direction does not require artificial alternatives.

Infer posture from the task and local contract. For expressive work, name the intended response, identity constraints, references or inspiration, and anti-goals. Read [frontend-quality.CREATIVE.md](frontend-quality.CREATIVE.md) for `explore` or consequential expressive `evolve`. Do not silently reduce expressive work to a generic utility treatment.

Mockup approval concerns the shown direction and revision. Production edits require task authorization, which may already be present in a build request; do not ask again for an authorized implementation. An isolated prototype never acquires live state or publication authority from its appearance.

## Resolve project authority

Before a material change to an established interface:

1. Read the closest `AGENTS.md` Interface fields: Profile, Contract, Executable authority, Render, and Gate. Profiles are initial hypotheses from [frontend-quality.PROFILES.md](frontend-quality.PROFILES.md), not continuing visual authority.
2. Read the affected contract and primitive catalog, then inspect the executable owners needed for the changed task. Do not load every listed implementation file when only one component is relevant.
3. Inspect the affected baseline and nearest shipped sibling and registered family when continuity matters.
4. Repair a missing field, file, or unusable recipe within an authorized project change; otherwise report the specific gap. Never borrow a sibling project's rules as a silent substitute.

Extend registered masters for legitimate new needs; do not create a competing page-local styling system. A consequential family departure needs a typed rationale and an adversarial continuity test when the project contract requires those controls. Preserve the tested extension path rather than treating current design choices as immutable. Exact tokens, recipes, exceptions, and geometry remain project-owned.

Read [frontend-quality.PRIMITIVES.md](frontend-quality.PRIMITIVES.md) when defining or changing reusable primitives, catalogs, drift gates, or automated repair. It supplies semantic questions; the project supplies answers and mutation boundaries.

## Observe, change, and verify

For a material change to a runnable surface:

1. Render the baseline and exercise the affected task before editing. For an unavailable renderer, use the closest artifact, simulator, or device evidence and name its limits.
2. Choose the solution against the task and expression posture. Implement through the project's owners and primitives, extending them when justified.
3. Re-render after material composition changes. Exercise affected populated, empty, loading, error, stale, focus, overflow, and recovery states where applicable, at supported widths. Inspect console errors and failed requests for browser work.
4. Compare the result with the task hypothesis and perform the reduction pass below. Source inspection and a single final screenshot do not substitute for observed interaction evidence.

Scope observation to affected states and surfaces. Unavailable hardware or rendering bounds the verification claim; it does not prevent useful independent work already authorized. Never claim a surface passed without its evidence.

## Composition as decision rules

- **Hierarchy:** let the task and reading order determine emphasis. A secondary label, subtitle, or explanation must add information. Distinct typography can carry a semantic role or the chosen identity; an arbitrary font-count rule does not define quality.
- **Grouping:** use proximity, alignment, whitespace, rules, panels, or cards according to actual relationships and interaction boundaries. Remove nested containers that add no task or identity value.
- **Consistency:** equivalent meanings should remain recognizable across the product. Different tasks may need different layouts; intentional variation belongs in the owning design contract.
- **Color and state:** keep status and controls understandable without color alone. Accent, imagery, texture, and decoration may carry an intentional identity as well as interaction; verify readability and priority rather than banning visual richness.
- **Lists and navigation:** add search, sorting, or facets when record volume and retrieval tasks justify them. A short sequence or bibliography may need none; item count alone never mandates controls.
- **Motion:** use motion for useful feedback, continuity, comprehension, or an authorized expressive purpose. Preserve reduced-motion behavior and input responsiveness; do not disrupt reading or ongoing actions. Prefer inexpensive properties and verify performance of richer effects.
- **Density:** optimize access and comprehension for the project task. Empty space may aid reading or expression; dense operational tools may need immediate controls. Neither is a universal aesthetic.

Project-selected defaults can change through their owner when evidence and task authority justify it. Accessibility, truthful state, data/privacy boundaries, and control semantics remain requirements.

## Evidence and handoff

Use one compact record: task/outcome; expression posture and selected direction when relevant; baseline/final rendered observations; affected states/widths; deterministic checks; and unverified surfaces or interactions. A reduction pass removes redundant content, containers, controls, or effects whose removal improves the task without losing the chosen identity; retain useful richness and explain material tradeoffs, not every styling decision.

For reviews, assess task success, clarity, product fit, distinctiveness where requested, interaction correctness, accessibility, and evidence. Do not equate prose compliance, visual novelty, or a plain layout with quality. Representative rendered comparisons can evaluate this procedure; they do not establish invocation coverage across all agent work.
