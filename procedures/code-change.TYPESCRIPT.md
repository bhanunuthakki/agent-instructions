# TypeScript design and boundary reference

Use this reference when reading, designing, or modifying TypeScript code under `code-change`.

## Core rules

| Principle | Rule |
|---|---|
| **Make illegal states unrepresentable** | Replace boolean flags and correlated optional fields with discriminated unions (`type RequestState<T> = { status: "loading" } \| { status: "ok"; data: T } \| { status: "error"; error: Error }`). |
| **Constructive modeling** | Encode invariants in structure rather than runtime wishes: `[T, ...T[]]` for non-empty arrays, `[T, T][]` for pairs, and `{ start: number; duration: number }` when ordering matters. Keep plain `T[]` when every consumer is already total on empty arrays. |
| **Branded primitives** | Brand distinct semantic identifiers or units (`type UserId = string & { readonly __brand: unique symbol }`) so positional parameters cannot be swapped. Produce brands only through a verifying parser or type guard (`input is UserId`), never via raw `as`. |
| **`unknown` at boundaries** | Untrusted data (`JSON.parse`, `fetch`, `process.env`, storage, IPC, LLM payloads) enters as `unknown`. Parse once at the system boundary into a named domain type using the repository's schema library (such as `z.infer<typeof Schema>`) or a verifying type guard. Do not pass `Record<string, unknown>` into domain logic. |
| **Narrowing hierarchy** | Narrow in this order: discriminant `switch` > `in` operator > `typeof` / `instanceof` > verifying user-defined type guard (`isX` / `hasX`) > `as` only after proven validation. A lying type guard is worse than `as` because it hides the unsafe assumption behind a safe call site. |
| **`satisfies` over `as`** | Use `satisfies` to validate that a value matches a contract without widening literal types or silencing compiler errors. |
| **Compile-time exhaustiveness** | Place `const _exhaustive: never = value;` in the `default` arm of discriminated switches so adding a variant fails typechecking at every unhandled site. |
