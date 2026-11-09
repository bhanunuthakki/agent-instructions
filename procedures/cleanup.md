---
name: cleanup
description: Clean up session resources and redundant history, retaining only what is needed for reconstruction. Use for /cleanup or an end-of-session cleanup request.
---

# Session cleanup

`/cleanup` and `cleanup this session` authorize cleanup of disposable resources
owned by this session across the tools and services it used. Use
[storage lifecycle](storage-lifecycle.md) for recovery rules.

Keep the smallest set needed to reconstruct current work, required history, and
open obligations. A file does not need retention merely because it is unique,
old, from a failed attempt, or part of a transcript. Retain information for a
specific reconstruction need, rather than keeping every container that held it.

1. Use session history and native inventories to identify owned files, worktrees,
   workers, temporary monitors, browser tabs, and service artifacts. Inspect the
   relevant locations. Ownership and content determine scope; age, directory
   names, and clean Git status alone do not.
2. Stop temporary session-owned consumers before removing their resources.
   Keep requested persistent monitors, shared services, and active work.
   Resolve host authority before remote operations.
3. Reuse canonical sources and existing recovery copies. Preserve only missing
   decisions, preferences, user edits, source evidence, and failure details needed
   to reconstruct or resume the work. Consolidate these into their existing owner
   when necessary. Verify that retained sources and references are available.
   Avoid a fresh archive when the retained set already meets the need. For
   Windows/Mac artifacts, retain the payload on its canonical host and a reference
   on the other host. Reuse an existing index; do not copy remote content to prove
   it exists. Verify the survivor and repair references before retiring a duplicate.
4. Remove redundant notes, completed plans, duplicate exports, rebuildable caches,
   and disposable test output through their owning interface. Close temporary
   session tabs. Use native worktree lifecycle tools after checking tracked,
   untracked, ignored, and unpushed work and installed-path dependencies. Preserve
   necessary changes or inputs once; retire their redundant checkout afterward.
   Branch retirement is a separate action under its owning authority.
5. Apply the same reconstruction rule to session transcripts and service history.
   They have no blanket retention exemption. Retire session-owned redundant
   records through supported interfaces when their necessary information survives.
   Keep records required by an explicit recovery, audit, or retention policy.
   Account-wide history deletion and unrelated user work remain outside scope.
6. Execute confirmed disposable cleanup without another approval request. Isolate
   an unknown or inaccessible target; continue independent cleanup. A meaningful
   hold needs a concrete missing reconstruction input, active dependency, or
   governing policy. Report that gap and how to resolve it. Follow required native
   confirmations; do not bypass them or edit service databases directly.
7. Verify removed paths, stopped processes/listeners, worktree registration, and
   retained references as applicable. Report removals, the reconstruction set,
   and unresolved scope. Do not create a cleanup catalog, log, or backup without
   a distinct need. Say when no session-owned resource exists.

This instruction does not authorize production cleanup or changes to another
owner's retention policy. A request to update cleanup policy does not itself
execute a cleanup sweep.
