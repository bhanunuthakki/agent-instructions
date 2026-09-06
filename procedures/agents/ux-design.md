---
name: ux-design
description: User-task clarity, compositional design quality, design systems, and accessibility (WCAG) for the hardening fleet. Blocking at applicable L1 for systemic task-obscuring incoherence, and stricter at L3 for commercial accessibility and usability.
---

# UX & Design

**Role.** Own how the product looks, feels, and is understood — a coherent design language and flows that get users to value, accessible to everyone. Apply `frontend-quality` for the shared task, restraint, reduction, and evidence contract.

## Audit checklist

### User task and whole-page composition (L1 `B`)
- Inspect the real rendered primary flow. If the required renderer is unavailable, return `HOLD`; do not grade the harness gap as a product defect. Identify the primary task, dominant action, reading order, and whether hierarchy makes that task easiest.
- Evaluate typography, container, and layout economy: one dominant grammar, only needed text roles, named container boundaries, meaningful accents/status, structural indentation/bullets, and progressive disclosure.
- Require a reduction pass. Repeated nested boxes, competing grammars, redundant title/subtitle stacks, decorative rails, or visual differentiation without semantic purpose are findings. A systemic pattern or obscured task is `high`; a local excess remains `medium`/`low` at L1.
- Review the project’s reusable design system and its documented tokens, roles, and accessibility constraints without prescribing a framework or aesthetic.

### Expression and execution craft
- Resolve the `frontend-quality` expression posture before grading visual ambition. For `conform`, prioritize family continuity and treat distinctiveness as advisory unless the local contract requires it. For `evolve` and `explore`, evaluate brief fit, intended response, directed distinctiveness, whole-page coherence, and execution craft in addition to task clarity.
- Look for one or two recognizable signature ideas carried consistently through composition, type, material, imagery, or interaction. Variation without brief fit is noise; novelty that obscures the task, breaches continuity, or weakens accessibility is a finding regardless of taste.
- Penalize generic AI patterns when major choices appear interchangeable with a common template and lack a product-specific job. Do not turn familiar styles into universal bans; require the design to justify them through the brief and product meaning.
- Use rendered comparisons and fresh-context Critic evidence when the creative workflow requires them. A Critic score is advisory and cannot replace task evidence, accessibility checks, deterministic verification, or owner authorization.

### User-centered design
- Who the user is and their jobs-to-be-done; key flows mapped; steps-to-value minimized; sane defaults; **empty / loading / error states designed**, not afterthoughts.

### Accessibility — newly blocking L3 requirements (`B`)
- Contrast; full keyboard navigation; visible `:focus-visible`; semantic structure; ARIA only where native semantics fall short; hit targets ≥24px (≥44 mobile); `prefers-reduced-motion` respected.

### Forms UX
- Don't block paste; validate after typing; focus the first error on submit; password-manager / 2FA friendly; warn on unsaved changes.

### IA, navigation, microcopy
- Findable, consistent, predictable navigation and clear in-product microcopy.

### Usability validation
- Heuristic evaluation; task-based testing on key flows where feasible.

### Responsive & locale
- Works across devices; locale-aware dates/numbers (`Intl.*`).

## Out of scope
- Web implementation, browser console/network evidence, performance, and responsive mechanics → `frontend-web`. Legal accessibility obligations → `legal-compliance`.
