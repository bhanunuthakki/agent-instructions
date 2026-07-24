---
name: definitions
description: Build, refresh, or enforce the project's ubiquitous-language vocabulary file (DEFINITIONS.md). Use when the user types "/definitions", asks to "define terms", "build a glossary", "create a vocabulary file", "standardize the terminology", or when conflicting domain terminology appears in the codebase. Also use to propose canonicalization renames when synonyms are detected.
---

# Definitions Protocol

Maintain a `DEFINITIONS.md` at the repo root that fixes the canonical terminology for the project. All code, comments, commits, PRs, and conversation must use these terms verbatim. The point is to prevent semantic drift, eliminate verbose paraphrasing, and make the codebase self-consistent.

## Workflow when invoked

1. **Survey and propose.** Scan the codebase for recurring domain terms (exported types, public functions, tables, state labels), cluster synonyms and conflicts — two terms for one thing, one term for two things — and propose the canonical term for each cluster, naming the alternatives subsumed and where they appear. Grill-Me style: propose with tradeoffs, don't ask blank.
2. **Get user confirmation** on each canonical choice and on conflict resolutions before writing the file.
3. **Write/update `DEFINITIONS.md`** in the format below.
4. **Propose** a rename PR for code that drifts from the canonical names. Do NOT execute renames without separate user approval — list them, count occurrences, and wait.

## File format

```markdown
# Definitions

Canonical terminology for this project. Use these terms verbatim in code (variables, functions, types, columns), comments, commit messages, and PR descriptions. New domain terms must be added here before being used.

## <Term>

**Definition.** <one sentence — what it is>
**Lives in.** <modules / tables / types currently using it>
**Not to be confused with.** <near-synonyms or sibling terms, and how they differ>
**Subsumes.** <alternative spellings or synonyms previously used; if any>

## <Next term>
...
```

## Discipline (always-on, not just when invoked)

- Never coin a new synonym in a response, variable name, commit, or PR description. If a concept doesn't have a defined term yet, propose adding it to `DEFINITIONS.md` before using it.
- Variables, functions, types, columns, and labels use the canonical term verbatim — no abbreviations or paraphrases.
- If reading code surfaces a recurring domain term not yet in `DEFINITIONS.md`, flag it to the user as a candidate addition.
- When two terms in `DEFINITIONS.md` start to look like they overlap, surface the ambiguity rather than silently choosing one.

## Anti-patterns

- Inventing a new term in conversation ("the holdings tracker", "the position monitor") when `DEFINITIONS.md` already has a canonical name.
- Writing a definition that's a paraphrase of the term itself ("A `Position` is a position held").
- Skipping the "Not to be confused with" field — disambiguation is the most useful part of the entry.
- Renaming code without explicit user approval, even when the rename is clearly correct.
- Treating `DEFINITIONS.md` as write-once. It's a living artifact; revisit during `/definitions` runs.
