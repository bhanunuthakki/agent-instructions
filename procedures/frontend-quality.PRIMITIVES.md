# Portable UI primitive contract

Use this reference when a task creates, changes, audits, or automates a reusable UI primitive or
design-system gate. It defines portable semantic boundaries; it does not impose a component library,
framework, CSS class, shape, or aesthetic.

## Authority and placement

The shared procedure owns the questions every interface must answer. Each project owns the answers:

- The project UI contract records its project-owned vocabulary, primitive catalog location,
  behavioral distinctions, responsive rules, and deterministic gate.
- The catalog may be embedded in its UI contract, live in a linked project document, or be expressed
  by a maintained component catalog when that is the repository's established authority.
- Executable components, templates, tokens, and tests remain the highest-fidelity implementation
  evidence. Page code composes them and does not create a competing local primitive system.
- Product and domain authorities own mutation meaning, retention, recovery, and navigation targets.
  A visual standard never invents those semantics.

Do not copy names or visual recipes between projects. A passive badge in one product may be an
interactive filter in another. What must transfer is an explicit, accessible distinction between
interaction, annotation, state, and mutation.

## Minimum semantic catalog

A project with reusable interface elements records only the families it actually uses, normally:

1. Action controls and intent hierarchy, including navigation versus mutation and pending/disabled
   feedback.
2. Fields and choices, with labels, validation, controlled state, and error focus.
3. Navigation and selection, including current state, keyboard access, and responsive behavior.
4. Passive annotations and statuses, with non-color meaning and no false interaction affordance.
5. Repeated-record anatomy, preserving identity, metadata, status, and actions across responsive
   renderings.
6. Dismiss, close, and delete as separate operations: close changes presentation; dismiss removes a
   recoverable or derived item from a working surface; delete removes durable data and follows the
   product's destructive-action contract.
7. Empty, loading, stale, success, warning, and error feedback with an honest recovery action when
   one exists.
8. Overlays, disclosure, help, focus return, and escape behavior using native or established
   framework primitives.

Higher-level page compositions stay registered project patterns rather than being flattened into
generic atoms. A catalog should reduce divergence, not turn every layout into an abstraction.

## Adoption without conflict

For an existing project:

1. Inventory the rendered components, styles, tests, and current UI contract before naming a
   standard.
2. Map existing names to semantic roles and preserve established framework/library conventions.
3. Record collisions explicitly—for example, one treatment serving both status and navigation—and
   choose a project-local migration rather than redefining historical behavior globally.
4. Register only stable, repeated families. Leave surface-specific composition with its owning page
   or feature.
5. Add a deterministic gate for the project's actual invariants and validate representative existing
   surfaces before tightening it estate-wide.

An established project contract narrows this reference. When they differ on names, geometry, or
component structure, the project wins. When a local rule would weaken native semantics,
accessibility, destructive-action safety, or explicit domain authority, reconcile the local rule
instead of treating visual consistency as higher authority.

## Drift prevention and repair

Use the same checked-in deterministic checker from local development, tests, hooks, CI, and any
scheduled maintenance. The scheduler is a thin trigger, never the primitive authority.

- Auto-repair is limited to safe mechanical transformations whose semantics are already determined,
  such as restoring an exact canonical import or replacing a deprecated alias with its registered
  equivalent.
- A fixer preserves content, unrelated edits, file mode, and idempotence; it refuses concurrent
  changes and reruns the checker after writing.
- Missing destinations, accessible names, lifecycle decisions, responsive information hierarchy,
  destructive behavior, and new component variants are semantic findings. They produce `HOLD` for
  review rather than guessed repairs.
- Hooks run read-only against active work. A scheduled fixer uses a project-defined clean-target
  guard, never commits or pushes unless separately authorized, and reports every changed file.
- A project that cannot run scheduled work still applies the contract through its local gate; a cron
  is optional operational enforcement, not a portability requirement.

Validation is proportional to the change: checker unit fixtures for parsing and repair boundaries,
contract/reference closure, affected component tests, and rendered proof for visible behavior.
