---
name: grill-me
description: Force the Grill-Me requirements-gathering protocol on the current task. Use when the user types "/grill-me" or asks to "grill me", "interview me", "interrogate me", or otherwise wants the agent to interrogate them about a feature, design, or plan before generating any PRD, asset, or code. Also use to restart grilling when an earlier round produced an under-specified plan.
---

# Grill-Me Protocol

Do not generate PRDs, designs, code, or any deliverable until a verified shared design concept is reached. The user has explicitly invoked this protocol — they want to be interrogated, not handed a draft.

## How to grill

- **Walk down each branch of the design tree.** Resolve dependencies between decisions one by one — settle the foundational choice before asking about its dependents. Don't ask leaf questions while the trunk is unresolved.
- **Ask only what's needed to resolve the next foundational decision before its dependents.** Size each round to what the user can genuinely engage with; number the questions and flag the foundational one when it isn't obvious.
- **Probe at the interface boundary.** What's hidden vs. exposed? What's the smallest API that covers known callers? What failure modes are in scope? What's explicitly out of scope?
- **Propose defaults with the tradeoff named.** Instead of "what do you want X to do?", say "X could be (a) ___ — simpler but loses ___, or (b) ___ — handles ___ but adds ___. Which?" The user picks faster from named options than from a blank prompt.
- **Don't ask preferences you can read.** Interrogate the user only on decisions you can't recover from the codebase, prior memories, or sane defaults.
- **No drafts to "make it concrete".** Generating a strawman PRD or code skeleton before requirements are settled defeats the protocol — the user will react to the strawman instead of articulating their actual constraints.

## Stop conditions

End the protocol when **either**:
- The user explicitly says proceed / "go ahead" / "draft it" / "let's see code", **or**
- All open decisions have answers AND probing yields no new branches (you can't think of another consequential question).

When stopping, summarize the agreed design in one paragraph and confirm before generating any deliverable.

## Anti-patterns

- Generating a draft "to make the discussion concrete" before requirements are settled.
- Question-dump rounds — overloading so the user answers the easy ones and the hard ones get lost.
- Abstract questions ("what should X look like?") when concrete options can be named.
- Restating the request back as questions instead of probing for new information.
- Asking questions whose answer is already in `CLAUDE.md` / `GEMINI.md` / memory / the visible codebase.
- Stopping early because the user seems impatient — the cost of a bad spec exceeds the cost of two more rounds.
