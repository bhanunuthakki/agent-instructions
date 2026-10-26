---
name: cleanup
description: Clean up the current session's temporary files, worktrees, processes, service resources, and redundant memory. Use for /cleanup or an end-of-session cleanup request.
---

# Session cleanup

`/cleanup` means clean up this session across the tools and services it used.
`cleanup this session` has the same meaning when slash commands are unavailable.
The invocation authorizes cleanup of confirmed disposable session resources.
Preserve unique work, durable data, installed skills, and recovery material.

1. Use the session history and native resource inventory to identify owned files,
   worktrees, workers, temporary monitors, browser tabs, and service artifacts.
   Inspect only relevant locations. Do not start a machine-wide or account-wide
   cleanup. An old timestamp, temporary directory name, or clean Git status does
   not establish ownership or disposability.
2. Stop temporary session-owned consumers before removing their resources.
   Preserve requested persistent monitors, shared services, and resources still
   used by another session. Resolve host authority before remote operations.
3. Remove confirmed disposable files and caches through their owning interface.
   Close session-created temporary tabs. Use native worktree archive/removal
   tools after checking tracked, untracked, ignored, and unpushed work and any
   installed skills or services that depend on the checkout. Preserve unique
   work before retirement. Do not delete branches or force-remove a worktree.
4. Prune redundant session notes and obsolete plans. Keep reusable preferences,
   active skills, final deliverables, unique source evidence, and open obligations.
   Preserve the session transcript and service history. Do not create a new
   cleanup log, backup, or catalog without a distinct recovery need.
5. Apply only the authorized disposable scope. Leave unknown, shared, active,
   protected, or inaccessible resources intact and report why. Ask only if an
   unresolved destructive action is required; continue independent safe cleanup.
   Follow any service-specific confirmation requirement.
6. Verify removed paths, stopped processes/listeners, worktree registration, and
   retained references as applicable. Report what was removed, what was kept,
   and any incomplete scope. Say when no session-owned resource exists.

This is an agent instruction, not a shell deletion command. It does not authorize
production cleanup, deletion of account history, changes to retention policy, or
discarding unrelated user work.
