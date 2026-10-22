---
name: storage-lifecycle
description: Keep application and task storage bounded with simple cleanup and retention; protect unique data and use existing owners.
---

# Storage lifecycle

Use for accumulating temporary output, caches, logs, backups, task worktrees, or a storage cleanup. Start with the existing producer and cleanup interface. For personal applications, prefer a few directories, bounded retention, and cleanup in the producer over a new service, ledger, or framework. This procedure grants no deletion or production authority.

## Default approach

- Separate durable user data, regenerable caches, temporary output, and backups. Keep their lifecycle with the owning application. A directory name or file age alone does not establish that its contents are disposable.
- Reuse inputs and existing outputs when their identity and freshness match. Avoid copying entire databases, private-state trees, dependency environments, or backup sets for a small test. Isolate writable tests with synthetic fixtures.
- Choose copy scope before allocation: prefer a query, small fixture, or existing approved consistent snapshot when sufficient. Use the supported database snapshot mechanism when a fresh copy is required. Do not recursively include backup pools, caches, temporary runs, or other checkout copies unless they supply a named recovery need; preserve unique state wherever it lives.
- Retain the smallest independently recoverable set for each source and purpose under its owning policy. Extra prior snapshots need distinct recovery coverage, required history, or a separate failure domain; a new timestamp, agent session, or task alone is not a retention reason. Do not change an approved retention policy or retire a protected copy implicitly.
- Clean task-owned temporary output after use, including failure and interruption. Use a context manager or equivalent teardown where possible. Let the next invocation or an existing maintenance job recover abandoned output. Keep the minimum useful reproduction for an unresolved failure, rather than every attempt.
- Bound accumulating logs, caches, retries, and backups by size, count, or age appropriate to that producer. Retry unchanged pending backups instead of creating duplicate copies. Keep required recovery coverage. Exact limits and cadence belong to application configuration; there is no universal byte budget or expiry period.
- When buildup recurs, fix the creating or retrying producer and its supersession/teardown behavior, not only the accumulated files. Distinguish small durable failure evidence from reproducible bulk payload; use the owning release process rather than retaining every failed attempt forever or clearing it from failure status alone.
- Before a large run, check available space against its expected peak and required recovery headroom. Apply existing project limits. Add reservation machinery only when concurrent allocations or observed failures justify it.
- At task closure, stop task-owned consumers and retire verified disposable output within existing authority. State the reason and release condition for meaningful retained output in the existing task record; do not create a separate catalog for ordinary scratch files.

## One-off review

Use this sequence for a storage audit or cleanup, not for each small scratch allocation.

1. Identify the canonical host, exact roots, current writers, and owning cleanup/backup commands. Inspect preview semantics: a command named dry-run may still write logs, prune staging, or change Git metadata.
2. Measure the largest relevant directories first. Distinguish user data from dependencies, caches, test payload, exports, worktrees, and recovery material. Report inaccessible or unmeasured scopes as unknown. Avoid reading private payloads to measure storage.
3. Run a genuinely read-only plan. For proposed retirement, establish ownership, regenerability or preservation, and absence of active dependencies. Preserve unique history, user edits, current source pins, and necessary recovery state. Do not approve a worktree from its branch name, detached HEAD, or clean status alone; classify ignored/untracked files and installed-path dependencies too. Use the managing application's lifecycle when applicable.
4. Apply only the exact authorized scope through its existing owner, rechecking changed targets and active consumers. Keep code/worktree retirement separate from branch deletion. Leave unknown or access-denied targets untouched and report partial results.
5. Verify the result and remaining free space. Distinguish logical file sizes, allocated blocks, and actual recovered disk space. A local test or manual run proves neither remote deployment nor future scheduled execution.

## Escalate only for a demonstrated need

Repeated large growth, concurrent maintenance, remote backup failures, or unique-state migration may require stronger controls. Read only the applicable sections of [storage-lifecycle.REFERENCE.md](storage-lifecycle.REFERENCE.md). Reuse existing owner locks, receipts, and monitoring. Keep project paths, installed schedules, retention values, and historical incidents with their project or private operations record.

Test the changed mechanism with isolated fixtures: normal cleanup, failure/interruption, active or changed targets, and preservation of unique data as applicable. Do not run production cleanup to test a reporting change. Verify a restore when backup/recovery behavior changes. Add a regression for a proved defect; do not build a new test framework for a one-off inventory.
