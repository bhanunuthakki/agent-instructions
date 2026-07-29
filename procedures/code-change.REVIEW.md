# Code review and architecture reference

Use this reference for consequential refactors, architecture design, or code review.

## Depth and ownership

- A module is deep when its interface is materially simpler than the decisions it hides.
- Flag adjacent layers that use the same vocabulary and pass the same data through unchanged.
- If two modules repeatedly change together, move the shared knowledge behind one owner.
- Prefer one general-purpose interface to several near-duplicates unless the resulting parameter surface becomes harder to use.
- Keep one source of truth for each state value and make transaction, retry, and idempotency boundaries explicit.

## Review smells

- Pass-through methods or variables threaded through layers that do not use them.
- `Service`, `Manager`, `Helper`, or `Utils` types that are namespaces rather than abstractions.
- Defensive defaults, broad exception catches, or compatibility shims that can absorb unrelated defects.
- A discriminator that never varies in real inputs; sentinels such as `unknown` comparing equal and licensing a false conclusion.
- Fixtures that reconstruct a schema by hand and silently drift from migrations.
- Network test doubles that can fall through to a live service.
- A successful file or database write that is not followed by integrity or round-trip verification where corruption would be silent.

## Review output

Prioritize concrete, actionable findings with file and line evidence. Separate confirmed defects from risks or missing evidence. Do not add an abstraction solely for testability when a direct interface can be tested.
