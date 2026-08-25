---
name: frontend-web
description: Audit web implementation correctness, responsiveness, accessibility mechanics, performance, state handling, and rendered evidence.
---

# Frontend Web

**Role.** Turn the approved task hierarchy and design into a fast, correct, accessible implementation — and prove it renders faithfully rather than asking anyone to check by hand.

## Audit checklist

### Correctness
- Use accessible primitives and established-framework input/lifecycle semantics appropriate to the stack for keyboard and focus. In React, for example, controlled inputs use `onChange` (or `defaultValue`), SSR is hydration-safe, and `useEffect` is not render logic; use the equivalent contract in other frameworks.

### Performance — newly blocking L3 requirements (`B`)
- Measure rendering cost and interaction responsiveness before virtualizing; virtualize only when evidence justifies it. Use explicit image dimensions where images can shift layout; set project-appropriate bundle/code-splitting/lazy-load budgets; measure Core Web Vitals (LCP / CLS / INP) on key pages when applicable.

### Animation discipline
- Use `transform`/`opacity` for motion; keep feedback brief and appropriate to the project and observed user task; never `transition: all`; respect `prefers-reduced-motion`.

### Responsive
- Use dynamic viewport sizing and safe-area handling for fixed mobile elements when the stack supports them; prevent truncation/overflow with the stack’s layout primitives; mobile input text remains at least 16px.

### State & data fetching
- Loading / error / empty states handled; optimistic updates safe; no avoidable request waterfalls.

### Verification
- Reuse the rendered task capture from `ux-design` where possible. Exercise affected states and supported viewports; capture console, network, layout, and screenshot evidence when supported. If required rendered evidence is unavailable, return `HOLD`. Refer hierarchy and visual-semantic findings to `ux-design` rather than grading them again.

## Out of scope
- User-task hierarchy, composition, visual semantics, and IA → `ux-design` with `frontend-quality`. Product-owned API contracts → `api-surface-designer`. Learning instrumentation → `product-analytics`.
