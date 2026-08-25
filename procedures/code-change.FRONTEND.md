# Frontend engineering reference

Use `frontend-quality` for the user-task hypothesis, compositional restraint, reduction pass, and rendered evidence. Use the project’s existing design system and accessible primitives; for a new UI foundation, use `scaffold-design-system` after the hierarchy is known. This reference owns implementation mechanics only.

- Use native semantics before ARIA. Icon-only controls need accessible names; decorative elements are hidden from assistive technology.
- Preserve visible `:focus-visible` treatment and use established keyboard/focus primitives rather than hand-rolled logic.
- Keep interactive targets at least 24px, or 44px on mobile. Mobile inputs use at least 16px text.
- Forms allow paste, validate after input rather than during it, focus the first submitted error, preserve password-manager and 2FA behavior, and warn on unsaved changes.
- Use dynamic viewport units and safe-area insets for fixed mobile layouts.
- Animate only `transform` and `opacity`, keep feedback brief, and respect reduced-motion preferences.
- Give images dimensions, use locale-aware date/number formatting, handle empty/loading/error states, and verify controlled inputs.
- Measure before virtualizing. Verify the affected states and responsive sizes as required by `frontend-quality`; do not claim browser proof when rendering is unavailable.
