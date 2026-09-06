---
name: explain-change
description: After an LLM writes or edits code, explain the outcome, impact, risk, and proof in plain language at a depth proportional to the change. Use when the user says "explain this change", "what did you just change", "explain in plain language", "is this safe to keep", "what could break", "review what you wrote", or "walk me through the diff". This is comprehension + risk for a non-coder, NOT a bug-hunt (use /code-review for that).
---

# Explain Change

Help the owner understand and act on an actual change without requiring them to read code. Inspect the diff and available execution evidence; the global completion contract owns the common handoff.

Scale the explanation to consequence and uncertainty. A small, well-verified change may need only its outcome, affected surface, and proof. For material work, connect the user-visible effect to the significant design or engineering choice and its practical consequences. Group by behavior or system effect; use a comparison, diagram, or short demonstration when it makes a decision easier. Requested technical depth calls for precise, relevant detail rather than an exhaustive tutorial. Describe only implementation facts established by the diff or supplied evidence; label a possible consequence as conditional.

Explain costs, maintenance or exit burdens, and operating or recovery responsibilities when they materially change. Cover relevant data/schema, authentication, money, deletion, credentials, external-write, and production effects without listing untouched surfaces. Distinguish code changes from effects actually executed, and rendered observations from source inspection.

Recommend the next action when one remains. Anchor confidence to the checks actually run and the important unverified behavior; avoid blanket safety verdicts. Give commands or click paths when useful for independent confirmation. Do not require a scorecard, repeated summary, or a fixed number of sections.

This explanation does not replace bug review or a required release gate. Route a specific unresolved risk to the applicable review; do not start a broad audit merely to fill out the handoff.
