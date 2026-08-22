# Mac workspace backup

This Mac-only job archives local workspace material to Google Drive.
It is not an Earnings or Portfolio Tracker database backup. Windows remains the
sole owner and backup writer for both live databases.

## Scope

- `~/Developer` (including `.git` and uncommitted work)
- `/Applications/agent-instructions` (the active shared-instruction clone)
- the known working repositories stored directly under `/Applications`:
  `earnings-summary`, `portfolio-tracker`, `date-suggester`, `angel-memos`,
  `blog-engine`, `harness`, `huntdesk`, `reading-companion-app`,
  `repo-maintenance`, `wealthplan`, and `bhanu-resume-system`
- `~/Documents/Claude/Projects`, when present

`~/Migration-Recovery` is deliberately excluded from this job. It holds
recovery artifacts downloaded from Google Drive, so re-archiving it to the
same Drive would be redundant. Protect it locally with Time Machine instead.

The job dynamically finds `GoogleDrive-*/My Drive` beneath
`~/Library/CloudStorage`, then targets `scratch-backups`. It never places a
worktree in Google Drive.

## Exclusions

Credentials, tokens, `.env` files, key material, live SQLite databases and
their `-wal`/`-shm` sidecars, virtual environments, `node_modules`, caches,
build output, temporary files, and local agent/tool state (`.codex`,
`.codex-membership`, `.claude`, `.gemini`, `.agents`, `.tools`) are excluded.
`.git` is intentionally retained.

## Dry run and activation gate

Run before any activation:

```sh
python3 snippets/backup_mac_workspace.py --dry-run
```

The proposed schedule is Saturday at 01:30 America/Los_Angeles, outside the
Windows production window of 03:00–05:00. The disabled launchd template is
`launchd/com.bhanu.mac-workspace-backup.plist.disabled`; do not load or rename
it until the owner approves a successful dry run.

## Live run, verification, retention

```sh
python3 snippets/backup_mac_workspace.py
python3 snippets/backup_mac_workspace.py --verify \
  ~/Library/CloudStorage/GoogleDrive-*/My\ Drive/scratch-backups/mac_workspace_*.tar.gz
```

Each archive is built in the local temporary directory, re-opened, checked for
its manifest and restore guide, checksum-verified, copied to Drive under an
`.uploading` name, and atomically renamed only after the copy completes. Three
completed archives are retained by default; retention applies only after a new
verified archive is published. Each invocation writes a structured summary to
`~/Library/Logs/MacWorkspaceBackup`; launchd also captures stdout/stderr.

## Restore drill

1. Download/copy an archive to a local temporary folder.
2. Run `--verify` against that local file.
3. Extract into a new local directory, never directly into `~/Developer`.
4. Inspect each repository's Git status; copy back only the intended files.
5. Recreate excluded credentials and environments through normal setup.

Never restore a live Earnings or Portfolio Tracker database from this archive.
Use the Windows-tested encrypted backup/restore procedure for those databases.
