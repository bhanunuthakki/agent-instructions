---
name: design-conformance-audit
description: Deprecated shared adapter for an Earnings Summary-specific semantic conformance audit. Use the project runbook on explicit request or when executing its already registered schedule; use frontend-quality and ux-design for generic frontend review.
---

# Design Conformance Audit (Earnings Summary adapter)

This is not a generic frontend-quality owner and does not create, change, or imply a schedule. The Earnings Summary runbook owns cadence and report location; `frontend-quality` owns generic task reasoning, restraint, and rendered evidence; `ux-design` owns hardening verdicts.

Work in the current Earnings Summary checkout. On this Mac the canonical path is
`/Applications/earnings-summary`. Inspect the current diff before acting and preserve unrelated
changes. Fetching is optional and read-only; never switch branches, pull, commit, push, open a PR,
modify Linear, or create a recurring job unless the user separately authorizes that action.

Read `directives/design_conformance_audit.md`, `directives/design_language.md`,
`src/ui/controls.py`, and `src/ui/tokens.py`. Review `src/pipeline/*.py` and
`src/dashboard/*.py`; exclude `src/report/**`, whose editorial type ramp is intentionally
different.

Focus on semantic drift that deterministic guards cannot identify:

- accent or status colors used decoratively rather than for interaction, selection, unread state,
  or value status;
- monospace typography on labels, headings, buttons, or tabs rather than tickers, numbers, code,
  timestamps, or locators;
- role-level type hierarchy inversions across surfaces;
- panels that bypass the established head, hairline, foot, or gridline-gap anatomy;
- reinvented outline chips or tags that should compose `.k-chip`.
- container economy and redundant nested boundaries; competing page-level layout grammars;
  redundant title/subtitle stacks; decorative bullets or indentation; and unjustified visual differentiation.

Do not re-report deterministic guard failures. Respect sanctioned exceptions in the canonical
runbook. Re-read current code at every candidate location and report only confirmed findings with
exact file and line evidence plus the kit-composing correction.

Run the repository's focused UI-control test when its configured environment is available. Report
findings, verification performed, and limitations. The project runbook determines whether an
explicit or already scheduled run writes its ignored report; do not otherwise change the repository.
