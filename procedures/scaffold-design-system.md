---
name: scaffold-design-system
description: Generate a secure-by-default, accessible design system for a new web UI — design tokens, a small Radix-based component set, and empty/loading/error stubs. Use when the user says "set up a design system", "design tokens", "component library", "starter components", "scaffold the UI", "build the UI from scratch", or "make it look good" / "make it consistent". This is the generative counterpart to the `ux-design` hardening audit; bake its WCAG-AA criteria in up front instead of getting graded after.
---

# Scaffold: Design System

Generate the design language a new UI will be graded on, so the `ux-design` audit (and the Frontend Correctness rules in AGENTS.md) passes on the first run. The deliverable is **tokens → a few deep, accessible components → state stubs → locale helpers**, with accessibility defaults already baked in, not bolted on.

This skill covers *generation*. It does not restate the always-on Frontend Correctness rules — those live in AGENTS.md and are assumed. It adds the concrete files and the acceptance mapping.

## Default stack

**Next.js (App Router) + TypeScript + Radix UI primitives + Tailwind.** Radix gives keyboard/focus behavior for free (never hand-roll it); Tailwind carries the tokens as theme values + CSS variables. Alternative in one line: if the team wants zero setup, **shadcn/ui** (which *is* Radix + Tailwind, pre-wired) is a faster path to the same primitives — install it and skip step 2's hand-written components.

## Workflow

1. **Lay down tokens first (step A).** Everything else references them. No raw hex/px in components.
2. **Build the component set on Radix (step B).** Button, Dialog, labelled Input — each deep enough to hide a11y wiring behind a plain prop API.
3. **Generate the three state stubs (step C).** Empty / loading / error are first-class, not afterthoughts — this is an explicit `ux-design` line item.
4. **Add the Intl helpers (step D).** Locale-aware dates/numbers, one entry point each.
5. **Verify against the checklist** at the bottom before handing off.

---

## A. Design tokens

One source of truth: CSS variables in `globals.css`, surfaced to Tailwind via `theme.extend`. **Document the AA-contrast pairing** for every foreground/background combo (the audit checks contrast explicitly — WCAG AA = 4.5:1 for body text, 3:1 for large text and UI borders).

`app/globals.css`:

```css
@import "tailwindcss";

:root {
  /* Color — each fg/bg pairing below is annotated with its measured contrast ratio.
     Pairings marked AA pass 4.5:1 (text) or 3:1 (large text / UI). */
  --color-bg:            #ffffff;
  --color-surface:       #f6f7f9;
  --color-fg:            #18181b; /* on --color-bg: 16.1:1  AA/AAA */
  --color-fg-muted:      #52525b; /* on --color-bg:  7.4:1  AA    */
  --color-border:        #d4d4d8; /* on --color-bg:  1.5:1  — UI line only, not text */
  --color-primary:       #1d4ed8;
  --color-primary-fg:    #ffffff; /* on --color-primary: 6.4:1 AA */
  --color-danger:        #b91c1c;
  --color-danger-fg:     #ffffff; /* on --color-danger:  6.5:1 AA */
  --color-ring:          #2563eb; /* focus ring; on --color-bg: 4.6:1 (visible) */

  /* Type scale — 1.250 (major third), rem-based. */
  --text-xs:   0.75rem;  /* 12px */
  --text-sm:   0.875rem; /* 14px */
  --text-base: 1rem;     /* 16px — body; also the mobile input floor */
  --text-lg:   1.25rem;
  --text-xl:   1.563rem;
  --text-2xl:  1.953rem;

  /* Spacing scale — 4px base. */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* Minimum interactive size — keep every hit target at or above this. */
  --hit-min: 44px; /* mobile floor; desktop a11y floor is 24px */
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg:        #0a0a0b;
    --color-surface:   #18181b;
    --color-fg:        #fafafa; /* on --color-bg: 18.9:1 AA/AAA */
    --color-fg-muted:  #a1a1aa; /* on --color-bg:  7.0:1 AA    */
    --color-border:    #3f3f46;
    --color-primary:   #3b82f6;
    --color-primary-fg:#0a0a0b; /* on --color-primary: 6.0:1 AA */
    --color-ring:      #60a5fa;
  }
}
```

`tailwind.config.ts` (maps tokens so components use semantic class names, never raw values):

```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        fg: "var(--color-fg)",
        "fg-muted": "var(--color-fg-muted)",
        border: "var(--color-border)",
        primary: "var(--color-primary)",
        "primary-fg": "var(--color-primary-fg)",
        danger: "var(--color-danger)",
        "danger-fg": "var(--color-danger-fg)",
        ring: "var(--color-ring)",
      },
      borderRadius: { sm: "var(--radius-sm)", md: "var(--radius-md)", lg: "var(--radius-lg)" },
    },
  },
  plugins: [],
};

export default config;
```

---

## B. Component set (on Radix)

Three components that cover most early UI. Each is *deep*: a small prop surface hiding the a11y wiring. Focus rings via `:focus-visible`, never `outline: none` without a replacement.

`components/button.tsx` — the icon-only path forces an `aria-label` at the type level:

```tsx
import { forwardRef } from "react";
import { Slot } from "@radix-ui/react-slot";

type Variant = "primary" | "secondary" | "danger";

const base =
  "inline-flex items-center justify-center gap-2 rounded-md text-base font-medium " +
  "min-h-[44px] min-w-[44px] px-4 " + // hit target >= 44px (mobile floor)
  "transition-[background-color,opacity] duration-150 motion-reduce:transition-none " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 " +
  "disabled:opacity-50 disabled:pointer-events-none";

const variants: Record<Variant, string> = {
  primary: "bg-primary text-primary-fg hover:opacity-90",
  secondary: "bg-surface text-fg border border-border hover:bg-border/40",
  danger: "bg-danger text-danger-fg hover:opacity-90",
};

// Icon-only buttons MUST carry an accessible name. Either show text children,
// or pass `iconOnly` + `aria-label`. The union makes the unsafe case a type error.
type Common = { variant?: Variant; asChild?: boolean } & React.ButtonHTMLAttributes<HTMLButtonElement>;
type ButtonProps =
  | (Common & { iconOnly?: false })
  | (Common & { iconOnly: true; "aria-label": string });

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", asChild = false, className = "", iconOnly, ...props },
  ref,
) {
  const Comp = asChild ? Slot : "button";
  const shape = iconOnly ? "aspect-square px-0" : "";
  return (
    <Comp
      ref={ref}
      className={`${base} ${variants[variant]} ${shape} ${className}`}
      {...props}
    />
  );
});
```

`components/text-field.tsx` — label is always associated; errors are announced and focus moves to the field:

```tsx
import { forwardRef, useId } from "react";

type TextFieldProps = {
  label: string;
  error?: string;
  hint?: string;
} & React.InputHTMLAttributes<HTMLInputElement>;

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(function TextField(
  { label, error, hint, id, className = "", ...props },
  ref,
) {
  const autoId = useId();
  const inputId = id ?? autoId;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={inputId} className="text-sm font-medium text-fg">
        {label}
      </label>
      <input
        ref={ref}
        id={inputId}
        // text-base = 16px: prevents iOS zoom-on-focus. Never set inputs below this on mobile.
        className={
          "min-h-[44px] rounded-md border border-border bg-bg px-3 text-base text-fg " +
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring " +
          (error ? "border-danger " : "") +
          className
        }
        aria-invalid={error ? true : undefined}
        aria-describedby={[hintId, errorId].filter(Boolean).join(" ") || undefined}
        {...props}
      />
      {hint && !error && (
        <p id={hintId} className="text-sm text-fg-muted">{hint}</p>
      )}
      {error && (
        <p id={errorId} role="alert" className="text-sm text-danger">{error}</p>
      )}
    </div>
  );
});
```

`components/dialog.tsx` — Radix handles focus trap, `Esc`, scroll lock, `aria-modal`; you just style it:

```tsx
"use client";

import * as RadixDialog from "@radix-ui/react-dialog";

export const Dialog = RadixDialog.Root;
export const DialogTrigger = RadixDialog.Trigger;

export function DialogContent({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <RadixDialog.Portal>
      <RadixDialog.Overlay
        className="fixed inset-0 bg-black/50 motion-safe:data-[state=open]:animate-[fade_150ms_ease]"
      />
      <RadixDialog.Content
        className="fixed left-1/2 top-1/2 w-[min(90vw,32rem)] -translate-x-1/2 -translate-y-1/2 " +
        "rounded-lg bg-bg p-6 shadow-xl focus-visible:outline-none"
      >
        <RadixDialog.Title className="text-lg font-semibold text-fg">{title}</RadixDialog.Title>
        {description && (
          <RadixDialog.Description className="mt-1 text-sm text-fg-muted">
            {description}
          </RadixDialog.Description>
        )}
        <div className="mt-4">{children}</div>
        <RadixDialog.Close
          aria-label="Close dialog"
          className="absolute right-4 top-4 grid h-11 w-11 place-items-center rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          ✕
        </RadixDialog.Close>
      </RadixDialog.Content>
    </RadixDialog.Portal>
  );
}
```

---

## C. State stubs (empty / loading / error)

These are required components, not optional polish. Generate them so every data view has all three states wired from the start.

`components/states.tsx`:

```tsx
import { Button } from "./button";

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <div className="flex flex-col items-center gap-3 p-8 text-center">
      <h2 className="text-lg font-semibold text-fg">{title}</h2>
      {description && <p className="max-w-sm text-sm text-fg-muted">{description}</p>}
      {action && <Button onClick={action.onClick}>{action.label}</Button>}
    </div>
  );
}

export function LoadingState({ label = "Loading" }: { label?: string }) {
  // Animation is opacity-only and disabled under reduced-motion; role=status announces to AT.
  return (
    <div role="status" aria-live="polite" className="flex items-center justify-center gap-3 p-8">
      <span
        aria-hidden
        className="h-5 w-5 rounded-full border-2 border-border border-t-primary motion-safe:animate-spin"
      />
      <span className="text-sm text-fg-muted">{label}</span>
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description,
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="flex flex-col items-center gap-3 p-8 text-center">
      <h2 className="text-lg font-semibold text-fg">{title}</h2>
      {description && <p className="max-w-sm text-sm text-fg-muted">{description}</p>}
      {onRetry && <Button variant="secondary" onClick={onRetry}>Try again</Button>}
    </div>
  );
}
```

---

## D. Locale-aware formatting helpers

Dates and numbers go through `Intl.*` — never hand-formatted, never hardcoded locale. One entry point each so a locale change is a one-line edit.

`lib/format.ts`:

```ts
// Resolve once on the client; pass an explicit locale server-side to avoid hydration drift.
const defaultLocale =
  typeof navigator !== "undefined" ? navigator.language : "en-US";

export function formatDate(
  value: Date | string | number,
  locale: string = defaultLocale,
  options: Intl.DateTimeFormatOptions = { dateStyle: "medium" },
): string {
  return new Intl.DateTimeFormat(locale, options).format(new Date(value));
}

export function formatNumber(
  value: number,
  locale: string = defaultLocale,
  options: Intl.NumberFormatOptions = {},
): string {
  return new Intl.NumberFormat(locale, options).format(value);
}

export function formatCurrency(
  value: number,
  currency: string,
  locale: string = defaultLocale,
): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency }).format(value);
}
```

---

## Defaults & anti-patterns

- **Default:** ship dark mode via `prefers-color-scheme` (already in the tokens) rather than a manual toggle — the toggle is more state to manage and the OS preference is usually right. Add the toggle only if asked.
- **Never** put raw hex or px in a component — reference a token. A magic color in a component is the first thing the audit flags.
- **Never** `outline: none` without a `:focus-visible` replacement ring.
- **Never** animate layout props or use `transition: all`; animate `transform`/`opacity` only, gate on `motion-safe:` / `motion-reduce:`.
- **Never** drop an input below 16px (`text-base`) on mobile — it triggers iOS zoom-on-focus.
- **Don't** hand-roll a modal, dropdown, tabs, or tooltip — reach for the Radix primitive; the keyboard and focus behavior is the hard part and it's already correct there.

## Verify with: `/harden --audit ux-design`

Acceptance = the `ux-design` agent's checklist + AGENTS.md Frontend Correctness. Map:

- **Design language** → tokens exist as one source of truth (step A); type/spacing/color/radius scales documented; components reference tokens, not raw values.
- **Contrast (WCAG AA)** → every fg/bg pairing in step A is annotated with its ratio; body text ≥4.5:1, large text/UI ≥3:1.
- **Keyboard + focus** → Radix primitives (step B) for focus behavior; visible `:focus-visible` ring on every interactive element; no bare `outline: none`.
- **Semantics / ARIA** → native `button`/`label`/`input` first; icon-only `Button` requires `aria-label` at the type level; `aria-invalid` + `aria-describedby` wired on `TextField`.
- **Hit targets** → `min-h-[44px] min-w-[44px]` on Button, inputs, and the Dialog close.
- **Empty / loading / error** → all three present as real components (step C), with `role="status"`/`role="alert"` and live regions.
- **prefers-reduced-motion** → all motion gated `motion-safe:`/`motion-reduce:`.
- **Forms UX** → label association + `aria-describedby` error wiring; paste not blocked (no input handlers that intercept it); validate-after-typing and focus-first-error are the consuming form's job — note this to the caller.
- **Responsive / locale** → mobile-first Tailwind; `Intl.*` helpers (step D) for all dates/numbers/currency.

### Test it (structural properties only — never assert on copy)

- `Button` with `iconOnly` and no `aria-label` is a TypeScript error (compile-time check).
- Every rendered interactive element has a computed `min-height` ≥ 44px.
- `TextField` with an `error` renders an element with `role="alert"` whose `id` is referenced by the input's `aria-describedby`.
- `LoadingState` exposes `role="status"`; `ErrorState` exposes `role="alert"`.
- No component file contains a raw hex color or px value outside the token files (grep assertion).
