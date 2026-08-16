# Canonical Windows-to-Mac migration plan

**Mac arrival:** Wednesday, August 19, 2026  
**Plan generated from a live scan:** August 15, 2026  
**Operating decision:** the Mac becomes the development computer; the Windows laptop remains the always-on runner for scheduled jobs, databases, backups, and the Portfolio Tracker API.

## The simple version

Your code should not live in Google Drive. Each project should be a normal local folder on the Mac, with its committed work backed up to a private GitHub repository. Google Drive continues to hold documents and the existing periodic backup archives. Time Machine backs up the Mac itself.

That gives every important thing the right protection:

| Thing | Working copy | Off-computer protection | If the Mac dies |
|---|---|---|---|
| Code already committed and pushed | Mac local folder | Private GitHub repository | Clone it again from GitHub |
| Code not committed yet | Mac local folder | Time Machine; periodic scratch archive during transition | Restore from Time Machine or the latest scratch archive |
| Live databases used by scheduled jobs | Windows runner only | Existing encrypted database backups in Google Drive | Restore the verified database backup |
| Project documents, PDFs, spreadsheets, exports | Google Drive | Google cloud plus Time Machine where downloaded | Download them again |
| Passwords, API keys, and login tokens | Each machine's secure local configuration | Password manager or fresh sign-in | Sign in again; never recover these from GitHub |

**Important:** a Git clone is a one-time download. GitHub Desktop does not silently pull forever. On the Mac you will fetch/pull before starting work, commit and push your branch, then merge the pull request on GitHub. A merge also does **not** automatically update the Windows runner. Windows deployments remain a deliberate, tested release step; scheduled jobs keep running the last approved version until that happens.

## Current readiness verdict

**HOLD today; realistic GO before the Mac arrives.** The hardware/power setup is good, the repositories all have GitHub remotes, and the main database backup has a proven restore. The remaining blockers are operational, not architectural.

| Area | Live finding | Verdict | Required outcome |
|---|---|---:|---|
| Windows power | AC sleep is disabled and closing the lid is configured to do nothing | Good | Leave plugged in, ventilated, and on a stable network |
| Remote recovery | Tailscale is running, but no remote desktop host is installed and Windows RDP is disabled | Blocker | Install and test Chrome Remote Desktop from another device |
| Reboot behavior | 33 enabled scheduled jobs require an interactive sign-in; Google Drive also appears only after sign-in | Blocker | Plan on one remote sign-in after a reboot until these jobs are deliberately converted |
| Scheduled jobs | 42 enabled jobs; 24 last succeeded and 18 have non-zero last results | Blocker | Explain/fix each failure or mark it intentionally inactive; do not call the machine healthy from task registration alone |
| Portfolio Tracker API | Port 8000 works only because an old user process is alive; the boot task itself failed | Blocker | Register the repaired password-backed startup task, stop the old process once, and pass a reboot test |
| Earnings runtime | Clean, pinned Windows runtime; 18 commits behind the locally known main ref | Intentional | Keep it pinned until an approved release passes tests; never add a blind `git pull` |
| Database backup | Current encrypted backup exists and a restore/integrity drill passed | Good | Preserve the encryption key outside the laptop and run one final backup before cutover |
| Whole-workspace backup | Weekly archives exist, but the old script over-counted database copies and had no recent restore drill | In progress | Complete a new archive with the corrected scanner and verify it can be read/extracted |
| GitHub completeness | All 13 repositories have an `origin`, but several contain uncommitted work or are on non-main branches | Blocker | Resolve every row in the Git table below before relying on a Mac clone |
| Shared agent instructions | The installer, hooks, and Claude wrapper contained Windows-only paths; the global Codex rulebook was empty | In progress | Finish and push the portable generator, then bootstrap all three agents from the Mac clone |
| Earnings on Mac | Its exact SQLite runtime is Windows/Linux-specific today | Accepted limit | Edit on Mac, execute production on Windows; do not promise Mac runtime parity yet |

## Four-day master checklist

The rows are deliberately sequential. Do not skip a dependency just because a later row looks easy.

| # | When | Time | Owner | Do this | Depends on | Proof before moving on |
|---:|---|---:|---|---|---|---|
| 1 | Sat Aug 15 | 30 min system time | Codex | Remove only rebuildable Python/package caches to make backup room; preserve every repo, database, document, and upload staging folder | None | At least 12.4 GB free during backup preflight |
| 2 | Sat Aug 15 | 1-3 hr system time | Codex | Run the corrected whole-workspace backup. It snapshots the four live databases and skips old database copies | 1 | New final archive in `scratch-backups`; no `.uploading` partial left behind |
| 3 | Sat Aug 15 | 30-60 min | Codex | Perform a safe archive verification: list the archive, extract its restore instructions into an isolated temporary folder, and confirm database snapshots are present | 2 | Verification log names the archive, reports success, and leaves live data untouched |
| 4 | Sun Aug 16 | 15 min | You | Install Chrome Remote Desktop on Windows and set a PIN you keep in your password manager | None | Connect to Windows from your phone or another computer while the Windows lid is closed |
| 5 | Sun Aug 16 | 10 min | You + Codex | Double-click `portfolio-tracker\scripts\install-api-server-task.cmd`, enter the Windows account password, and leave the resulting window open for diagnosis | None | Task is registered for startup under your account; the credential window no longer disappears |
| 6 | Sun Aug 16 | 30 min | Codex | Move Portfolio Tracker runtime to a clean, release-only checkout; stop the old ad-hoc API process and start the registered task | 5 | Exactly one process owns port 8000; health request returns 200; task last result is healthy |
| 7 | Sun Aug 16 | 2-4 hr | Codex | Triage the 18 non-zero scheduled-task results. Fix current database-lock/time-limit problems, and explicitly document jobs that are intentionally disabled or have “no work” exit codes | 2 | No unexplained enabled-task failures; disabled jobs remain disabled |
| 8 | Sun Aug 16 | 10 min | Codex | Remove HuntDesk's automatic Windows login startup entry so it remains manual-only | 4 | HuntDesk does not launch at login; its database is unchanged |
| 9 | Sun Aug 16 | 30-60 min | Codex | Finish the shared instruction portability change: relative paths, portable hooks, global Codex/Claude/Gemini rulebooks, and a Mac bootstrap command | None | Instruction tests and drift checks pass from a relocated test clone |
| 10 | Mon Aug 17 | 1-3 hr | You + Codex | Resolve uncommitted work and branch state in every Git row below. Commit/push wanted work; archive intentional local data; discard nothing without review | 2, 9 | `git fetch` confirms every wanted commit exists on GitHub; no project is accidentally stranded on a detached commit |
| 11 | Mon Aug 17 | 30 min | You | Decide whether `demo_sandbox` is valuable. If yes, make a private repo; if no, leave it in the verified archive for later review | 2 | A recorded keep/archive decision; no deletion required for migration |
| 12 | Mon Aug 17 | 30 min | Codex | Create a machine-readable handoff manifest: repository URL, approved branch/commit, required local data, runtime owner, and smoke-test command | 10 | Manifest has one row for all 13 repositories and no credentials |
| 13 | Mon Aug 17 | 30-60 min | You + Codex | Rehearse a Windows restart: save work, reboot, connect remotely, sign in once, confirm Google Drive mounts, and run the health checklist | 4-8 | Portfolio API, critical earnings jobs, Drive, Tailscale, and backups recover after reboot |
| 14 | Tue Aug 18 | 30 min | Codex | Run a final encrypted database backup and verify it independently of the whole-workspace archive | 7, 13 | Current backup plus successful restore/integrity receipt |
| 15 | Tue Aug 18 | 30-90 min | Codex | Final GitHub reconciliation: fetch remotes, push all approved changes, record commit IDs, and freeze Windows development folders | 10, 12 | Fresh Mac clones will contain every approved code change |
| 16 | Tue Aug 18 | 15 min | You | Put Windows on AC power, use wired Ethernet if practical, leave ventilation around it, and close the lid only after the health page is green | 13-15 | You can reach it remotely and the charger/network stay connected |
| 17 | Wed Aug 19 | 45-90 min | You | Set up the Mac account, install macOS updates, enable FileVault, store its recovery method safely, and start an encrypted Time Machine backup | Mac in hand | Mac security and first backup are enabled before project data accumulates |
| 18 | Wed Aug 19 | 30-60 min | You | Install GitHub Desktop, Google Drive for desktop, Codex, Claude Code, Homebrew, Python, Node, and `uv` | 17 | Each application opens; GitHub/Codex/Claude/Google sign-ins succeed |
| 19 | Wed Aug 19 | 30 min | You | In Google Drive, use Stream files. Do **not** put `~/Developer` inside Drive | 18 | “My Drive” appears in Finder under `~/Library/CloudStorage/...`; project code remains elsewhere |
| 20 | Wed Aug 19 | 45-90 min | You + Codex | In GitHub Desktop choose File → Clone Repository and place repos under `~/Developer`. Clone `agent-instructions` first, then projects | 15, 18 | Every expected private repo appears; each checkout matches the recorded approved commit |
| 21 | Wed Aug 19 | 15-30 min | Codex | Run the shared instruction bootstrap from `~/Developer/agent-instructions` | 20 | Codex reads `~/.codex/AGENTS.md`; Claude and Gemini read their generated global wrappers/skills |
| 22 | Wed Aug 19 | 1-2 hr | You + Codex | Recreate configuration and sign-ins one project at a time. Use Mac paths and Keychain/password manager; never copy Windows virtual environments or raw token caches | 19-21 | Each selected project starts without a Windows path or missing-credential error |
| 23 | Wed Aug 19 | 1-2 hr | Codex | Run smoke tests for the portable projects. For Earnings, test editing/static checks only and leave its managed execution on Windows | 22 | Results recorded per project; accepted Windows-only limitations are not mislabeled failures |
| 24 | First week | 15 min/day | You | Work from the Mac. Pull/fetch before work, use a branch, push it, merge on GitHub, and let Windows remain on its last approved release until deployment | 23 | No Drive worktrees; GitHub contains committed work; Windows stays stable |

## Git cleanup table before cloning

“Private remote exists” means GitHub has a repository. It does **not** prove that today's local work is on GitHub.

| Repository | Current local state from scan | What must happen before Mac clone | Mac role |
|---|---|---|---|
| Agent instructions (`.gemini`) | `main`, 3 commits ahead; two dirty governance ledgers plus current portability edits | Preserve ledgers, commit only owned portability/plan files, run sync/tests, push approved commits | Clone first; generates the common rules for every agent |
| Earnings Summary | Clean feature branch; 24 ahead/9 behind locally known `origin/main` | Decide whether the feature branch is the approved source; fetch and reconcile through a PR, not by copying the folder | Development/read-only analysis; production remains Windows |
| Portfolio Tracker | Feature branch; 12 ahead/1 behind; seven local changes including the startup-task repair | Separate user instruction edits from the runtime repair; commit through an isolated branch/PR; deploy only to a clean Windows runner | Development on Mac; API/runtime remains Windows |
| Date Suggester | Detached commit with seven local changes, including tracked activity/profile data | Reattach wanted work to a named branch; decide whether tracked personal data belongs in Git or backup only | Manual Mac use; Windows URI/schedule can stay Windows |
| Angel Memos | `master`; one dirty definitions file | Commit or consciously leave in archive; recreate Google/Chrome authorization on Mac | Mac-ready after path/config fix |
| Blog Engine | `main`; one dirty definitions file | Commit or consciously leave in archive; move WordPress secret/config to Mac-local config | Mac-ready; scheduled report lane may stay Windows |
| HuntDesk | `main`; two dirty instruction/definition files; local database is ignored | Commit/resolve docs; copy database only through verified backup; recreate external Resume paths | Manual Mac app; no auto-start |
| MyClaw | `master`; one dirty weekly-review log | Decide whether the log is canonical history or backup-only | Edit on Mac; Telegram/scheduled service stays Windows initially |
| Reading Companion | Clean `main`; local captures/jobs/sessions/threads are ignored | Confirm those local records are in the workspace archive; do not assume GitHub has them | Core Node work on Mac; Android setup later |
| Wealthplan | Clean `main`, origin present | Export/backup ignored plans and scenario state; make legacy database path configurable | Mac-ready after config |
| Harness | Clean `main` | Replace remaining Windows CLI path assumptions before first Mac use | Mac-ready after short adapter fix |
| Repo Maintenance | Clean `main` | No Mac runtime port needed | Windows-only backup/maintenance runner |
| XR Glasses Guide | Clean `main` | Clone normally; one documentation path can be cleaned later | Ready immediately |

## What stays on Windows

Do not migrate these just because the Mac is newer:

| Windows responsibility | Why it stays | How you interact with it |
|---|---|---|
| Earnings Summary's scheduled fleet and exact SQLite runtime | It is built around Windows Task Scheduler and a pinned SQLite/runtime arrangement that a normal Mac install cannot reproduce today | Monitor by health receipts; deploy only approved releases |
| Portfolio Tracker API and live `portfolio.db` | Earnings reads it over the Windows loopback interface; one machine must own the live writer | Remote desktop only for recovery or an approved release |
| Repository-maintenance backups | The source folders and Google Drive mount are on Windows | Weekly archive plus verification alert |
| MyClaw Telegram/Windows jobs | Current launchers and task definitions are Windows-specific | Leave running until a separate Mac service migration is worth doing |
| Date Suggester URI handler and weekly task | Windows registration is not portable | Keep Windows version; use the Mac manually if desired |

The Windows laptop can stay closed, plugged in, awake, and locked. **Locked is fine; signed out is not currently fine.** Google Drive and 33 scheduled jobs still depend on an interactive user session. After a power loss or Windows Update reboot, use Chrome Remote Desktop to sign in once. Removing that final login dependency is a separate reliability project, mainly because Google Drive's mounted folder is user-session software.

## Exact Mac setup

| Order | Install/configure | Plain-English action | Important caution |
|---:|---|---|---|
| 1 | macOS | Update it before loading project state | Reboot as needed now, not mid-migration |
| 2 | FileVault | System Settings → Privacy & Security → FileVault → turn on | Keep the recovery method outside the Mac |
| 3 | Time Machine | Connect an external disk, enable encrypted backups, complete the first backup | Google Drive and GitHub are not full-machine backups |
| 4 | GitHub Desktop | Install and sign in to the GitHub account that owns the private repos | Clone to `~/Developer`, never into Google Drive |
| 5 | Google Drive | Install, sign in, and choose Stream files | The actual path is under `~/Library/CloudStorage`; configure apps from the discovered path instead of hardcoding it |
| 6 | Codex | Install the Mac desktop app and sign in | Project rules come from the cloned instruction repo after bootstrap |
| 7 | Claude Code | Install the native macOS package and sign in through its browser flow | Do not copy the Windows Claude settings directory wholesale |
| 8 | Developer tools | Install Homebrew, Git, current Python, `uv`, Node 20+, and project-specific tools | Rebuild `.venv` and `node_modules`; never copy them from Windows |
| 9 | Agent instructions | Clone to `~/Developer/agent-instructions`; run `python3 snippets/sync_agent_stubs.py --artifacts-only` | This generates global Codex/Claude/Gemini rules from one tracked source |
| 10 | Projects | Clone private repos in GitHub Desktop | Clone only approved branches/commits from the handoff manifest |
| 11 | Secrets/config | Re-sign in or create files under `~/.config/<project>/` | Never put credentials in Git or the Drive workspace archive |
| 12 | Acceptance | Run each repository's documented smoke test | Earnings production execution remains a Windows test |

Official references: [GitHub Desktop cloning](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop), [Google Drive stream vs mirror](https://support.google.com/drive/answer/13401938), [Claude Code setup](https://code.claude.com/docs/en/getting-started), [Chrome Remote Desktop setup](https://support.google.com/chrome/answer/1649523), [Apple Time Machine backup](https://support.apple.com/en-us/102307), and [Apple FileVault](https://support.apple.com/en-ie/guide/mac-help/-mh11785/mac).

## Your normal workflow after migration

| Moment | On the Mac | On Windows | Frequency of touching Windows |
|---|---|---|---|
| Start work | Open the repo in GitHub Desktop; fetch/pull; create or continue a branch | Nothing | None |
| During work | Codex/Claude edit local files; commit coherent checkpoints; Time Machine protects uncommitted work | Scheduled jobs continue on the pinned release | None |
| Share work | Push the branch and open a pull request | Nothing changes yet | None |
| Merge | Merge after tests/review pass | Still runs the old approved version | None |
| Release to runner | Trigger/approve a controlled deployment that fetches the exact approved commit, tests it, and switches only on success | Updates clean runtime; rolls back on failed smoke test | Occasional, and this can later become one-click from the Mac |
| Windows reboots | Connect remotely and sign in once so Drive and interactive jobs return | Health checklist runs | Only after a reboot/alert |

Do not schedule a generic `git pull` inside a folder that contains live databases or local edits. The safe automation target is a separate clean runtime checkout with an exact approved commit and a rollback point.

## How protected are you if a laptop dies?

| Failure | Protected after this plan? | Recovery |
|---|---:|---|
| Mac dies after you pushed | Yes | Replace Mac and clone from GitHub |
| Mac dies with today's uncommitted work | Yes, once Time Machine is current | Restore the folder from Time Machine |
| Windows dies | Mostly | Restore code from GitHub, databases from the encrypted DB backup, and local workspace state from the scratch archive |
| Google account/Drive unavailable | Partly | GitHub still has code; Windows and Time Machine still hold local copies |
| GitHub unavailable | Partly | Mac/Windows local clones and the workspace archive still contain repository history |
| Both laptops are lost | Yes for pushed code and verified Drive backups; no for credentials not stored elsewhere | GitHub + Drive + password manager; buy/rebuild hardware |

The target is not “everything in one cloud.” It is at least two independent recovery paths: GitHub for code, encrypted cloud archives for Windows data, and Time Machine for the Mac.

## Development effort estimate

| Work package | Required for cutover? | Codex/development time | Your hands-on time | Notes |
|---|---:|---:|---:|---|
| Correct and prove workspace backup | Yes | 2-4 hr elapsed, mostly unattended | 0-10 min | Includes four SQLite snapshots and archive verification |
| Portable agent instruction/bootstrap system | Yes | 3-5 hr | 0-15 min | Shared once across Codex, Claude, and Gemini |
| Git/branch/uncommitted-work reconciliation | Yes | 3-6 hr | 30-60 min decisions | No deletion; several repos need owner intent |
| Stabilize Windows jobs and database-lock failures | Yes | 4-8 hr | 15-30 min | Eighteen non-zero enabled tasks require classification |
| Portfolio clean runner + reboot-safe task | Yes | 2-4 hr | 5-10 min password entry | Includes single-owner port cutover and reboot proof |
| Remote access + full reboot rehearsal | Yes | 1-2 hr | 20-30 min | Chrome Remote Desktop is currently missing |
| Mac installs, clone, auth, first smoke tests | Yes | 4-8 hr | 2-4 hr | Mostly on arrival day and the following day |
| Make five manual Python apps fully path-portable | First-week improvement | 6-12 hr | 30-60 min auth | Angel, Blog, Date, HuntDesk, Wealthplan |
| Native Mac Earnings runtime parity | No | 12-24 hr | Minimal | Exact SQLite/Darwin packaging plus test entrypoint |
| Replace all Windows schedules with Mac `launchd` | No and not recommended now | 24-40 hr | 2-4 hr acceptance | Adds risk without helping the chosen Windows-runner design |
| Automated safe deployments from GitHub to Windows | Recommended later | 6-12 hr | 30 min approvals | Exact commit, test, atomic switch, rollback; never blind pull |

**Practical total before Mac arrival:** about 15-29 hours of engineering/system time, but only about 1-2 hours of your direct attention. Much of the system time is backup, tests, and task observation.  
**Mac arrival and first-week setup:** about 8-16 engineering hours plus 2-4 hours of your direct sign-ins and choices.  
**Not required:** the extra 36-64 hours to move Earnings execution and all Windows schedules onto the Mac.

## Cutover acceptance checklist

Do not declare the migration complete until every required box is checked.

- [ ] A new whole-workspace archive exists in Google Drive and passed an archive/extraction check.
- [ ] A current encrypted database backup passed integrity and restore verification.
- [ ] Every wanted local code change is committed and pushed to a private GitHub repository.
- [ ] No wanted project remains only on a detached commit or unpushed branch.
- [ ] Chrome Remote Desktop works with the Windows lid closed.
- [ ] Portfolio Tracker has exactly one API owner and survives a reboot.
- [ ] Every enabled Windows task is successful or has a documented, intentional non-zero state.
- [ ] Google Drive returns after the rehearsed remote sign-in.
- [ ] The shared instruction repository is pushed and can bootstrap a relocated clone.
- [ ] The Mac uses `~/Developer` for code and Google Drive only for documents/backups.
- [ ] FileVault and encrypted Time Machine are on.
- [ ] Codex, Claude Code, GitHub Desktop, and Google Drive sign-ins work on Mac.
- [ ] Each actively used Mac project passes its smoke test or has a documented Windows-only limitation.
- [ ] One tiny practice branch was pushed from Mac, merged on GitHub, and observed as **not deployed** to Windows until the release step.

## Stop/rollback rules

- If a backup cannot be opened, keep the prior two archives and do not prune anything.
- If a project has unclear local changes, preserve it in the archive and defer its Git cleanup; never guess-delete.
- If the Portfolio task fails, restore the prior process and task definition before experimenting further.
- If a Windows reboot loses Drive or scheduled work, keep development on Mac but do not call Windows unattended; use remote sign-in until fixed.
- If a Mac project requires a Windows-only path/runtime, leave production on Windows and record the gap rather than improvising around it.
- Keep the Windows laptop unchanged and available for at least two weeks after the Mac starts working; it is the rollback machine.
