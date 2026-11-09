---
name: storage-lifecycle
description: Keep application and task storage bounded with simple cleanup and retention; protect unique data and use existing owners.
---

# Storage lifecycle

Use for accumulating temporary output, caches, logs, backups, task worktrees, or a storage cleanup. Start with the existing producer and cleanup interface. For personal applications, prefer a few directories, bounded retention, and cleanup in the producer over a new service, ledger, or framework. This procedure grants no deletion or production authority.

## Reconstruction rule

Retain only the smallest set needed to reconstruct current work, required history,
and unresolved obligations. Use existing source, configuration, dependency locks,
private state, and verified recovery copies before keeping another payload. Keep
required provenance and independent recovery coverage. A retained item needs a
specific purpose; uniqueness, failure status, an old hold, or a new session alone
is not enough. Remove rebuildable or superseded material within the authorized
scope once its necessary inputs and references are preserved. Do not demand a
separate approval for each disposable item when the cleanup scope already covers it.

For an unresolved failure, retain the original outcome and the minimum inputs,
versions, and diagnostic evidence needed to reproduce or investigate it. Keep the
full failed payload only when it supplies a missing reconstruction input. Review
legacy holds against their actual dependency; do not renew them merely because
they exist. Uncertainty holds the affected target, not independent cleanup.

Apply the same rule to recovery backups. Prefer one current verified recovery
snapshot per canonical source in its approved backup destination. An extra local,
peer-machine, or historical copy needs a specific missing-state, migration, or
recovery purpose. Retire redundant copies after the survivor is verified; keep
only references on the non-owning computer. An unavailable or unverified cloud
snapshot cannot replace the last known recovery input. A weekly snapshot can
leave up to seven days of newer work outside that recovery point. Keep the owning
job's verification and pending-upload checks; no timestamp alone proves coverage.

## Cross-machine storage

Resolve the canonical host through [machine operations](machine-operations.md).
Keep each working dataset, export, recovery artifact, and diagnostic payload on
its owning host. The other host keeps only an index or reference to that source;
never create or retain a second working payload for convenient access. Reuse the
existing host registry, project reconstruction manifest, capture index, or recovery
redirect. Include the canonical host, native path or private route, source identity
or hash when available, and purpose. Do not add a synchronization service, new
catalog, or database when an existing index is sufficient.

Compare inventory metadata and native hashes without transferring payloads. For
an existing duplicate, verify the canonical survivor and its required dependencies,
repair references, then retire the noncanonical copy through its owner within the
authorized scope. A missing or offline source remains unavailable; do not download
another copy, guess a fallback, or promote the index into a second authority.
Different required sources or versions are not duplicates. A Google Drive
placeholder or cache is managed by its provider. Use its supported space-release
method; deleting a synced entry can also delete the remote recovery copy. Unique local edits must reach
their proper owner before a redundant container is removed. Source checkouts and
isolated synthetic tests follow their existing development lifecycle.

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
3. Run a genuinely read-only plan. For proposed retirement, establish ownership, regenerability or preservation, and absence of active dependencies. Preserve user edits, current source pins, necessary recovery state, and history required for reconstruction or an explicit policy. Do not approve a worktree from its branch name, detached HEAD, or clean status alone; cross-check `git worktree list` against merge state, uncommitted tracked edits (`wip`) versus untracked throwaways (`scratch`), active or pinned session transcripts (including background worker worktrees spawned from active chats), and installed-path dependencies. Use the managing application's lifecycle when applicable.
4. Apply only the exact authorized scope through its existing owner, rechecking changed targets and active consumers. Keep code/worktree retirement separate from branch deletion. Leave unknown or access-denied targets untouched and report partial results.
5. Verify the result and remaining free space. Distinguish logical file sizes, allocated blocks, and actual recovered disk space. A local test or manual run proves neither remote deployment nor future scheduled execution.

## Escalate only for a demonstrated need

Repeated large growth, concurrent maintenance, remote backup failures, or unique-state migration may require stronger controls. Read only the applicable sections of [storage-lifecycle.REFERENCE.md](storage-lifecycle.REFERENCE.md). Reuse existing owner locks, receipts, and monitoring. Keep project paths, installed schedules, retention values, and historical incidents with their project or private operations record.

Test the changed mechanism with isolated fixtures: normal cleanup, failure/interruption, active or changed targets, and preservation of unique data as applicable. Do not run production cleanup to test a reporting change. Verify a restore when backup/recovery behavior changes. Add a regression for a proved defect; do not build a new test framework for a one-off inventory.
