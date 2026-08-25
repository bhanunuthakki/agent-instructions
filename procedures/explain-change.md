---
name: explain-change
description: After an LLM writes or edits code, explain the outcome, impact, risk, and proof in plain language at a depth proportional to the change. Use when the user says "explain this change", "what did you just change", "explain in plain language", "is this safe to keep", "what could break", "review what you wrote", or "walk me through the diff". This is comprehension + risk for a non-coder, NOT a bug-hunt (use /code-review for that).
---

# explain-change

The user's code is largely LLM-written and they can't easily tell when it's subtly wrong. Give them a review **they can act on without reading the code.** Plain language, no jargon, honest about uncertainty.

Look at the actual diff first (`git diff` / the edits just made). Scale the response to the consequence and uncertainty of the work, not the number of files:

- For a tiny, low-risk, well-verified change, a **TL;DR alone is enough**. It must state the outcome, changed path or surface, validation, and any remaining uncertainty. Do not add empty sections or a ceremonial scorecard.
- For a material change, use the sections below. Combine or omit a section when doing so makes the result clearer without hiding material impact, risk, or missing proof.

## 1. TL;DR

Use no more than three short bullets:

- What changed in the running product and why it matters.
- **Verdict:** ✅ **Safe to keep**, ⚠️ **Keep, but follow up**, or 🛑 **Look closer first**, with one reason.
- The strongest validation result or most important uncertainty.

## 2. Impact scorecard

Give the owner a compact view of the change's effect. Use `Positive`, `No material change`, `Trade-off`, `Risk`, or `Unknown`, plus one short evidence-based reason.

Consider these core areas: frontend/UX · backend/API · data/database · latency/performance · security/privacy · reliability/operations. Add accessibility, compatibility, money/payments, or external-service cost when relevant. Use judgment: omit clearly irrelevant rows, or group several untouched areas into one `No material change` row. Never invent measurements; mark an effect `Unknown` when it was not verified.

## 3. Key changes and implications

Group by user-visible behavior or system effect, not by file. Include only changes that materially affect users, architecture, operations, maintenance, or future work. Normally use no more than three to five bullets. Mention paths in one compact line when they help the owner locate or verify the work; do not narrate every changed file.

## 4. Validation and watchouts

State the checks actually run and their results, behavior not verified, and concrete failure modes ranked by harm. Give an exact command or click path only when it is useful for independent confirmation.

**Explicitly flag anything that touches:** secrets/credentials · database schema or migrations (data loss?) · authentication/authorization (cross-user access?) · money/payments · external API calls or writes (cost? rate limits? side effects?) · deletion of files or rows. Recommend the matching review or hardening audit when the surface warrants it. For material frontend changes, state the user task exercised, rendered proof, and any visual or interaction verification gap. If a material change touches none of these, a single reassurance is enough.

## Rules
- Be honest about what you're unsure of — "I'm not certain X handles the empty case" beats false confidence. The user is trusting this verdict instead of reading the code.
- Don't grade your own prose or restate the request. Describe the *effect on the running system*.
- Prefer decision-relevant implications over exhaustive implementation detail. Do not repeat the same fact across the TL;DR, scorecard, and later sections.
- This is distinct from `/code-review` (which hunts for bugs) and the hardening audits (which gate on security): this is **comprehension + risk for a non-expert owner.** Hand off to those when the surface warrants it.
