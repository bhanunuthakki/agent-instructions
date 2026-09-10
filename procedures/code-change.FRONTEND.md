# Frontend engineering reference

Use `frontend-quality` for the user-task hypothesis, compositional restraint, reduction pass, and rendered evidence. Use the project’s existing design system and accessible primitives; for a new UI foundation, use `scaffold-design-system` after the hierarchy is known. This reference owns implementation mechanics only.

- Use native semantics before ARIA. Icon-only controls need accessible names; decorative elements are hidden from assistive technology.
- Preserve visible `:focus-visible` treatment and use established keyboard/focus primitives rather than hand-rolled logic.
- Use the project’s accessible target-size and spacing contract. For a new interface, 24px pointer and 44px touch targets are starting defaults, not universal project geometry. Validate usability, focus, and the applicable accessibility requirements; local geometry cannot waive those. Mobile input text should avoid unintended zoom (16px is a common web default).
- Forms allow paste, validate after input rather than during it, focus the first submitted error, preserve password-manager and 2FA behavior, and warn on unsaved changes.
- Use dynamic viewport units and safe-area insets for fixed mobile layouts.
- Prefer `transform` and `opacity` for inexpensive animation; other properties require relevant performance evidence. Keep repeated feedback responsive and respect reduced-motion preferences.
- Give images dimensions, use locale-aware date/number formatting, handle empty/loading/error states, and verify controlled inputs.
- Measure before virtualizing. Verify the affected states and responsive sizes as required by `frontend-quality`; do not claim browser proof when rendering is unavailable.
