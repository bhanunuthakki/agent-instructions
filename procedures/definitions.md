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
4. For a public or persisted name, verify the task authorizes its meaning and compatibility change; ask only for a consequential decision that remains unresolved.
5. Check the effective ancestor chain. Reject a duplicate term even when the descendant labels it an override or refinement.
6. Add or update the definition and apply authorized renames with an occurrence inventory and migration plan when compatibility requires one. Do not ask again for the exact rename already requested.

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
- Provisional language is allowed during discovery and isolated mockups. Mark it provisional when someone could mistake it for a ratified product state.
- Record a consequential domain meaning in its owning definition chain before propagating it into persisted values, public interfaces, canonical decision states, or cross-project contracts. Owner confirmation is for disputed meaning or consequential compatibility choices, not every new identifier.
- When a new non-durable concept is local and obvious, name it consistently without blocking exploration on a vocabulary ceremony.
- When a domain name crosses persistence, public APIs, durable user decisions, or overlaps an existing term, resolve its definition before propagating it. A local helper crossing modules alone does not create a governance gate.
- Surface ambiguity instead of silently picking whichever synonym appears first.
- Load only the effective definition chain for the task. Cross-project work loads the global file plus the provider and consumer chains, never every glossary.
- Treat same-spelling local concepts across projects as qualified terms, not evidence that their meanings should be merged.

## Vocabulary lifecycle

Track maturity (`observed -> candidate -> ratified`) separately from ownership scope (`subtree -> project -> cross-project -> global`). Usage counts are evidence, not approval thresholds. Recommend scope review only when independent project uses have the same meaning and shared ownership would reduce ambiguity. Ratification records an actual owner decision; do not infer it from repetition. A broader definition requires that broader owner’s authorization. A downstream override request suspends promotion and requires a concrete narrower owner, verified as a strict descendant through its `Inherits` chain. Keep a definition at its current scope until that scope decision is resolved.

Validate a chain with `snippets/definition_governance.py`. Lifecycle changes are reviewable recommendations; never auto-rename public or persisted identifiers from a lifecycle recommendation.
