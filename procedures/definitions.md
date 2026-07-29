---
name: definitions
description: Build, refresh, or enforce the project’s canonical domain vocabulary in DEFINITIONS.md. Use for `/definitions`, glossary or terminology requests, conflicting domain names, ambiguous state labels, or a new concept that needs a stable code and data name.
---

# Definitions

Use one canonical term for each domain concept at code, schema, API, and decision boundaries. Ordinary explanatory prose may be natural; the invariant is that identifiers and domain claims do not blur distinct concepts or multiply synonyms.

## Workflow

1. Scan exported types, public interfaces, tables, state labels, user-visible copy, and existing `DEFINITIONS.md`.
2. Group true synonyms and flag one term used for several concepts.
3. Propose a canonical term for each consequential cluster, naming the current alternatives, locations, and migration tradeoff.
4. Get owner confirmation before changing a public or persisted name.
5. Add or update the definition. Keep code renames as a separately approved change with an occurrence inventory and migration plan.

## Entry shape

```markdown
## <Canonical Term>

**Definition.** <what it means>
**Lives in.** <modules, schemas, tables, or UI>
**Not to be confused with.** <nearby concepts and the boundary>
**Subsumes.** <retired synonyms, if any>
```

Omit a field only when it adds no information. A definition that merely repeats the term is not useful.

## Decision rules

- Use existing canonical identifiers verbatim in code, schemas, commits, and PRs.
- When a new concept is local and obvious, name it consistently without blocking work on a vocabulary ceremony.
- When the name crosses modules, persistence, APIs, or user decisions—or overlaps an existing term—propose the definition before propagating it.
- Surface ambiguity instead of silently picking whichever synonym appears first.
