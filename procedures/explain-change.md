---
name: explain-change
description: After an LLM writes or edits code, explain the change in plain language for a non-expert reviewer — what changed, what could break, and how to confirm it works. Use when the user says "explain this change", "what did you just change", "explain in plain language", "is this safe to keep", "what could break", "review what you wrote", or "walk me through the diff". This is comprehension + risk for a non-coder, NOT a bug-hunt (use /code-review for that).
---

# explain-change

The user's code is largely LLM-written and they can't easily tell when it's subtly wrong. After a substantial change, give them a review **they can act on without reading the code.** Plain language, no jargon, honest about uncertainty.

Look at the actual diff first (`git diff` / the edits just made). Then produce exactly these five parts:

## 1. What changed (plain English, one line per file)
No code, no jargon. "`auth.py` — added the login and logout endpoints." "`models.py` — added a `tenant_id` column to every table." If you can't say it in one plain line, you don't understand it well enough yet — go read more.

## 2. Why (one sentence)
The intent of the whole change. "So users can log in and only see their own data."

## 3. What could break (the blast radius)
Concrete failure modes, ranked by how much they'd hurt. **Explicitly flag anything that touches:** secrets/credentials · the database schema or migrations (data loss?) · authentication/authorization (could someone see another user's data?) · money/payments · external API calls (cost? rate limits?) · deletion of files or rows. If it touches none of those, say so — that itself is reassuring.

## 4. How you'd know it works (the proof)
The **exact** thing to run or click and the expected result — written so the user can do it themselves. "Run `uvicorn app.main:app`, open http://localhost:8000/docs, call POST /login with a test user — you should get a 200 and a session cookie." Prefer pointing at an automated test or `/verify`; if there's no test for behavior that matters, say a test is missing.

## 5. Verdict (one of three + one reason)
- ✅ **Safe to keep** — low blast radius, verified or trivially verifiable.
- ⚠️ **Keep, but add a test** — works, but a regression here would be silent; name the test to add.
- 🛑 **Look closer first** — it touches a security/data/money surface; recommend the matching audit (`/harden --audit sec-authz` / `sec-tenant-isolation` / etc.) before relying on it.

## Rules
- Be honest about what you're unsure of — "I'm not certain X handles the empty case" beats false confidence. The user is trusting this verdict instead of reading the code.
- Don't grade your own prose or restate the request. Describe the *effect on the running system*.
- This is distinct from `/code-review` (which hunts for bugs) and the hardening audits (which gate on security): this is **comprehension + risk for a non-expert owner.** Hand off to those when the surface warrants it.
