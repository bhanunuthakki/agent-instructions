# Workbook Standards

Use this reference whenever a case-study spreadsheet is created, changed, or audited.

## Architecture and ownership

The logical flow is `Sources + Assumptions -> Canonical Builds -> Outputs -> Checks`. Checks are terminal and never feed the analysis. Put reader-facing outputs toward the left while preserving an intentional supplied template.

Create separate tabs only for a distinct grain, source, reusable calculation, output audience, or audit purpose. Each reusable metric has one calculation owner. Outputs link to finished calculations; intermediate schedules link upstream rather than copy values.

## Layout and navigation

Use a consistent hierarchy where it fits: title, short purpose and period, navigation on major outputs, brief logic definitions above dense calculated fields, then headers. Do not force this onto raw inputs.

For vertically stacked analyses, add clear section headings and navigation markers. Keep normal row heights, readable widths, deliberate freeze panes, and working tabs free of oversized decorative whitespace. Update links after structural changes.

## Formula and input colors

In working model areas:

- blue: hardcoded inputs and editable assumptions
- green: links to another sheet
- black: same-sheet links and calculations
- red: external workbook links, if any

Use dark presentation text for output results. Apply colors to formula type, not labels or perceived importance.

## Definitions and assumptions

The definitions tab is a concise control panel and glossary, not a textbook. Include active assumptions and metrics used in outputs or the memo. Remove obsolete items and define material terms a finance reader could misinterpret.

Use one authoritative control for each setting. Every blue input must be active and traceable. For calculated build columns that are not direct fetches, add a brief definition when practical, usually 5 to 10 words, that clarifies logic, timing, or basis.

## Periods, units, and formats

Use an authoritative as-of date and separate source cutoffs where availability differs. Propagate them through formulas, charts, titles, and definitions. Define lifecycle boundaries explicitly, including whether the boundary period belongs before or after the cutoff.

Keep number formats consistent across KPI and output tabs: appropriate currency scale and symbol, parentheses for negatives, dashes for zero, usually one decimal for percentages, whole numbers for counts, and real dates. Avoid false precision and display-text numbers.

## Checks

A useful check independently calculates source truth and compares it with the analysis. It does not compare two downstream formulas or use a typed expected value when a source-derived expectation is available.

Cover source and unique-key counts, major totals, roll-forward identities, timing boundaries, eligibility populations, duplicates, and chart completeness as relevant. Show the analysis result, independent expectation or criterion, difference, and status. Do not pass unavailable tests as zero.

## Charts and final hygiene

Charts should answer a decision question and use canonical ranges. Show full history when short, segment mix when it changes interpretation, and every material component plus total when claiming a complete decomposition. Avoid charts that merely repeat readable tables.

After structural edits, verify formulas, named ranges, chart sources, validations, hyperlinks, first/middle/last periods, and visible layout. Keep raw inputs unchanged and scan the workbook for formula errors.
