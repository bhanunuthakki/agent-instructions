---
name: definitions
description: Build, refresh, or enforce the project’s canonical domain vocabulary in DEFINITIONS.md. Use for `/definitions`, glossary or terminology requests, conflicting domain names, ambiguous state labels, or a new concept that needs a stable code and data name.
---

# Definitions

Use one canonical term for each domain concept at code, schema, API, and decision boundaries. Ordinary explanatory prose may be natural; the invariant is that identifiers and domain claims do not blur distinct concepts or multiply synonyms.

Definitions form a scope chain: global root -> project -> closest owning subtree. Every file declares `Scope`, `Owner`, and `Inherits`. Descendants may add terms but never override an ancestor. An override request proves the ancestor term is too broad: qualify the local concept, narrow the ancestor, or demote it from the higher scope.

## Workflow

1. Scan exported types, public interfaces, tables, state labels, user-visible copy, and existing `DEFINITIONS.md`.
2. Group true synonyms and flag one term used for several concepts.
3. Propose a canonical term for each consequential cluster, naming the current alternatives, locations, and migration tradeoff.
4. Get owner confirmation before changing a public or persisted name.
5. Check the effective ancestor chain. Reject a duplicate term even when the descendant labels it an override or refinement.
6. Add or update the definition. Keep code renames as a separately approved change with an occurrence inventory and migration plan.

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
- Load only the effective definition chain for the task. Cross-project work loads the global file plus the provider and consumer chains, never every glossary.
- Treat same-spelling local concepts across projects as qualified terms, not evidence that their meanings should be merged.

## Vocabulary lifecycle

Track maturity (`observed -> candidate -> ratified`) separately from ownership scope (`subtree -> project -> cross-project -> global`). Recommend Definition-Scope Promotion only after repeated real use with identical meaning: at least two uses for a candidate, three owner-ratified uses for ratified maturity, and at least six uses across two projects for a cross-project/global candidate. Global scope remains owner-ratified. Any downstream override request blocks promotion and puts Definition-Scope Demotion on `HOLD` until a concrete owning `DEFINITIONS.md` is named and proven to be a strict descendant through its declared `Inherits` chain.

Validate a chain with `snippets/definition_governance.py`. Lifecycle changes are reviewable recommendations; never auto-rename public or persisted identifiers.
