# Canonical Windows-to-Mac migration plan

**Mac arrival:** Wednesday, August 19, 2026  
**Plan generated from a live scan:** August 15, 2026; refreshed August 22, 2026
**Operating decision:** all development moves to the Mac. Windows remains a production-only runner for Earnings, Portfolio, and Windows-resident backups. MyClaw's two state jobs and Date Suggester's weekly job move only through separate stop-old-before-start-new canaries.

## Mac continuation status — August 22, 2026

This section is the current sequential checklist. It supersedes older Windows-era
`WAITING` and `BLOCKED` labels below where the verified facts differ.

| # | Status | Result / next gate |
|---:|---|---|
| 1 | DONE | Inventoried and freshly fetched all 14 Mac repositories in place under `/Applications`; no repository was moved. |
| 2 | DONE | Weekly backup covers every actual repository root, `/Applications/agent-instructions`, `/Applications/bhanu-resume-system`, and restored `~/Documents/Claude/Projects`; it excludes `~/Migration-Recovery`, `.app` bundles, credentials, databases, environments, dependencies, caches, builds, and temporary files while retaining `.git` and dirty work. |
| 3 | DONE | The four Drive recovery artifacts are present under `~/Migration-Recovery`, byte-identical to Drive, and intact where the format supports an independent test (`zstd -t` for both archives and `git bundle verify` for Codex memory). The encrypted database artifact was not decrypted because its key remains outside the migration flow. |
| 4 | DONE | Restored the five non-Git reference folders under `~/Documents/Claude/Projects` without converting them to repositories. The archived Resume copy remains isolated under `~/Migration-Recovery/windows-resume-2026-08-21`. |
| 5 | OWNER HOLD | Resume remains on its dedicated recovery branch while newer Windows-local Resume work is reconciled. Mac instruction sync deliberately skips creating Resume wrapper files, while its safety-hook configuration remains wired. |
| 6 | DONE | Mac bootstrap and shared instruction generation work. All 14 real repositories use `/Applications/agent-instructions/githooks`, and non-repository `.app`/Utilities folders are excluded. Both subscription-authenticated CLI wrappers passed harmless live checks on August 22: `CODEX_TRANSPORT_OK` and `CLAUDE_TRANSPORT_OK`; no API-key fallback was used. |
| 7 | DEFERRED BY OWNER | FileVault is on. The owner explicitly accepts the active weekly Google Drive workspace snapshot as interim protection until an external Time Machine disk is purchased. This is not independent of the Google account. |
| 8 | PARTIAL | Rebuilt the actively used Resume Python environment from declared dependencies. Earnings and Portfolio production execution/data remain Windows-only; no Windows environment, token directory, database, or scheduled job was migrated. |
| 9 | DONE | The Saturday 01:30 user LaunchAgent is installed and loaded. The latest live run exited 0 and published `mac_workspace_2026-08-22_162603.tar.gz` to Drive `scratch-backups`; 6,021 files verified. It includes an online SQLite snapshot of HuntDesk that passed restore `integrity_check` (`ok`, schema version 20), while still excluding raw live databases and sidecars. |
| 10 | DONE FROM PRIOR SESSION; NO NEW RUN | A prior live archive `mac_workspace_2026-08-21_223225.tar.gz` exists. It independently verifies all 5,892 manifest files and restored into an isolated temporary directory with Git metadata for all 14 repositories and representative files intact. No archive was pruned. |
| 11 | DEFERRED / PARTIAL | Encrypted Time Machine remains deferred. Resume recovery is committed locally; push and merge remain separate owner-approved actions. |
| 12 | DONE | Live Windows inspection found 44 tasks in `\earnings-summary\`: all 42 Task-Scheduler-owned manifest tasks, plus two healthy repo-maintenance tasks stored in that folder. `refresh_scenario_priors` exists and is Ready. The 43rd manifest lane, `capture_poller`, intentionally runs as the healthy `es-poller` Windows service instead of a scheduled task. Running the verifier from the clean production `runtime` checkout reports: `OK All 43 tasks parsed, registered and enabled`. The scratch checkout's 35 wrong-root findings are the expected guard against auditing/deploying from scratch. Morning Markets Brief is unrelated. |
| 13 | PARTIAL | HuntDesk is manual-only on Mac and is not a retained Windows service. Its 448 offline tests passed; its Mac DB now has a recurring transactionally consistent Drive snapshot and a successful restore integrity check. Still reconcile the authoritative Windows/Mac DB and source state before declaring sole-Mac ownership; do not schedule HuntDesk. |
| 14 | HARDENED; CUTOVER PENDING | Windows MyClaw is clean and aligned at `fd28eee`; weekly review and monthly curation are Ready and last exited 0. No `telegram_bridge` scheduled task is registered, so there is no active Windows Telegram poller to preserve or transfer. MyClaw PR #1 is merged after a J2 Sol PASS: the jobs now require a clean canonical branch aligned with origin, share one mutex, stage only procedure-owned paths, preserve immutable history byte-for-byte, reject out-of-scope changes, and push explicitly without force. Five focused tests pass. The preserved Mac checkout remains untouched; reconcile it and perform stop-Windows-before-start-Mac activation before declaring cutover. |
| 15 | PENDING / WINDOWS HEALTHY | `DateSuggester_Weekly` is Ready on Windows, last exited 0, and next runs August 23 at 09:00. Port it only after Mac OAuth, path/scheduling fixes, stop-old-before-start-new, and a no-duplicate canary. Retire or separately port the Windows-only URI handler. |

### Mac repository inventory (fresh fetch on August 21)

| Repository | Actual Mac path | Branch | Origin alignment | Worktree | Tracked files | Approx. size |
|---|---|---|---|---|---:|---:|
| agent-instructions | `/Applications/agent-instructions` | `main` | aligned with `origin/main` | clean before this status update | 91 | 647 MB |
| earnings-summary | `/Applications/earnings-summary` | `main` | aligned with `origin/main` | clean | 3,189 | 187 MB |
| portfolio-tracker | `/Applications/portfolio-tracker` | `main` | aligned with `origin/main` | clean | 170 | 3.3 MB |
| date-suggester | `/Applications/date-suggester` | `main` | aligned with `origin/main` | clean | 91 | 2.3 MB |
| angel-memos | `/Applications/angel-memos` | `master` | aligned with `origin/master` | clean | 75 | 1.5 MB |
| blog-engine | `/Applications/blog-engine` | `main` | aligned with `origin/main` | clean | 54 | 676 KB |
| harness | `/Applications/harness` | `main` | aligned with `origin/main` | clean | 34 | 436 KB |
| huntdesk | `/Applications/huntdesk` | `main` | aligned with `origin/main` | dirty; preserved | 159 | 78 MB |
| myclaw | `/Applications/myclaw` | `master` | behind `origin/master` by 1 | dirty; preserved, not pulled | 77 | 1.3 MB |
| reading-companion-app | `/Applications/reading-companion-app` | `main` | aligned with `origin/main` | clean | 145 | 1.5 MB |
| repo-maintenance | `/Applications/repo-maintenance` | `main` | aligned with `origin/main` | clean | 10 | 216 KB |
| wealthplan | `/Applications/wealthplan` | `main` | aligned with `origin/main` | clean | 60 | 892 KB |
| xr-glasses-dev-guide | `/Applications/xr-glasses-dev-guide` | `main` | aligned with `origin/main` | clean | 17 | 488 KB |
| bhanu-resume-system | `/Applications/bhanu-resume-system` | `codex/windows-resume-recovery-2026-08-21` | based at current `origin/main` | dirty recovery diff; preserved | 69 | 4.1 MB |

**What “mostly hands-off Windows” means:** in a normal week, you should not touch Windows. After a Windows restart, expect a two-minute remote sign-in so Google Drive and user-session-dependent jobs return. If the laptop loses power and does not turn itself back on, remote desktop cannot turn it on; check the BIOS “power on after AC loss” option if the laptop supports it.

## The simple version

Your code should not live in Google Drive. Each project should be a normal local folder on the Mac, with its committed work backed up to a private GitHub repository. Google Drive continues to hold documents and the existing periodic backup archives. Time Machine backs up the Mac itself.

That gives every important thing the right protection:

| Thing | Working copy | Off-computer protection | If the Mac dies |
|---|---|---|---|
| Code already committed and pushed | Mac local folder | Private GitHub repository | Clone it again from GitHub |
| Code not committed yet | Mac local folder | A **completed, recent** Time Machine backup | Restore from Time Machine; commit and push at the end of every work session |
| Live databases used by scheduled jobs | Windows runner only | Existing encrypted database backups in Google Drive | Restore the verified database backup |
| Project documents, PDFs, spreadsheets, exports | Google Drive | Google cloud plus Time Machine where downloaded | Download them again |
| Passwords, API keys, and login tokens | Each machine's secure local configuration | Password manager or fresh sign-in | Sign in again; never recover these from GitHub |
| Shared agent rules and Codex memory | Rules in the private instruction repo; memory local to Codex | Private GitHub for rules; verified Google Drive Git bundle for memory | Clone the rules and restore/import memory only if needed; reconnect apps/plugins |
| Resume and other `Documents\Claude\Projects` folders | Private GitHub for Resume; local Windows folders for five reference collections | Verified Google Drive archive of all six folders | Clone Resume; extract the five reference folders into Mac Documents if needed |

**Important:** a Git clone is a one-time download. GitHub Desktop does not silently pull forever. On the Mac you will fetch/pull before starting work, commit and push your branch, then merge the pull request on GitHub. A merge also does **not** automatically update the Windows runner. Windows deployments remain a deliberate, tested release step; scheduled jobs keep running the last approved version until that happens.

## Historical pre-arrival readiness record (superseded by the checklist above)

This section preserves the August 15 baseline for audit history. Its counts and verdict are not current; use the dated continuation checklist above for operational decisions.

| Area | Live finding | Verdict | Required outcome |
|---|---|---:|---|
| Windows power | AC sleep is disabled and closing the lid is configured to do nothing | Good | Leave plugged in, ventilated, and on a stable network |
| Remote recovery | Tailscale is running, but no remote desktop host is installed and Windows RDP is disabled | Blocker | Install and test Chrome Remote Desktop from another device |
| Reboot behavior | 33 enabled scheduled jobs run only after you sign in; Google Drive also appears only after sign-in | Blocker | Plan on one remote sign-in after a reboot until these jobs are deliberately converted |
| Scheduled jobs | 42 enabled jobs; 24 last succeeded and 18 have non-zero last results | Blocker | Explain/fix each failure or mark it intentionally inactive; do not call the machine healthy from task registration alone |
| Portfolio Tracker API | A clean release runtime now passes all 238 tests, reaches the existing live database through an absolute path, and passed a temporary health probe; port 8000 is still owned by the old user process | Owner step next | Register the repaired password-backed startup task, then Codex can cut over once and pass a reboot test |
| Earnings runtime | Clean Windows folder running one exact tested version; 18 commits behind the locally known main ref | Intentional | Keep that exact version until an approved release passes tests; never add a blind `git pull` |
| Database backup | Current encrypted backup exists and a restore/integrity drill passed | Good | Preserve the encryption key outside the laptop and run one final backup before cutover |
| Whole-workspace backup | New August 15 archive exists; corrected scanner captured four live databases and skipped 20 old copies; all 92,571 entries opened and restore instructions stream-extracted successfully | Good | Preserve the successful listing/extraction result and run one final pre-cutover backup |
| GitHub completeness | All 14 Git repositories now have an `origin`; 13 are private and Earnings Summary is public. Several still contain uncommitted work or are on non-main branches | Blocker | Decide whether Earnings should become private, then resolve every unfinished Git row below before relying on Mac clones |
| Shared agent instructions | Portable source rules, hooks, bootstrap, and managed Codex CLI resolution are committed and pushed; 126 instruction tests and the artifacts-only drift check pass | Good locally; Mac test pending | Bootstrap all three agents and run both CLI transport checks on the Mac |
| Local agent state | Codex memory was a clean local Git repo with no remote and was outside the workspace archive | Protected snapshot | A verified Git bundle now exists in Google Drive; sign-ins, task history, plugin connections, and machine caches are intentionally recreated instead of copied |
| Earnings on Mac | Its exact SQLite runtime is Windows/Linux-specific today | Accepted limit | Edit on Mac, execute production on Windows; do not promise Mac runtime parity yet |

## Four-day master checklist

The rows are deliberately sequential. Do not skip a dependency just because a later row looks easy.

| # | Status | When | Time | Owner | Do this | Depends on | Proof before moving on |
|---:|---|---|---:|---|---|---|---|
| 1 | DONE | Sat Aug 15 | 30 min system time | Codex | Remove only rebuildable Python/package caches to make backup room; preserve every repo, database, document, and upload staging folder | None | Backup preflight has enough free space |
| 2 | DONE | Sat Aug 15 | 13 min system time | Codex | Run the corrected whole-workspace backup. It snapshots the four live databases and skips old database copies | 1 | New final archive in `scratch-backups`; no partial upload left behind |
| 3 | DONE | Sat Aug 15 | 10-20 min | Codex | Open the entire archive, stream-extract its restore instructions, and confirm database snapshots are present | 2 | All 92,571 entries opened; restore instructions and database snapshots were present; live data was untouched |
| 4 | YOU NEXT | Sun Aug 16 | 20-30 min | You | Install Chrome Remote Desktop on Windows, set a PIN in your password manager, turn on Windows restart notifications/set active hours, and check the BIOS “power on after AC loss” option if available | None | Connect from another device while the Windows lid is closed; restart behavior is recorded |
| 5 | DONE | Sun Aug 16 | 30-60 min | Codex | Build and test a clean, release-only Portfolio Tracker folder. Configure an absolute `DATABASE_URL` to the **one existing live database** so the clean folder cannot create a second empty database | None | Runtime at `9e0a9d3` passes 238 tests and lint; a temporary port-18000 probe reports healthy database, migration, and active-account state against the existing live database |
| 6 | YOU NEXT | Sun Aug 16 | 10 min | You + Codex | Right-click `C:\Users\Bhanu\.gemini\antigravity\runtime\portfolio-tracker\scripts\install-api-server-task.cmd` and choose **Run as administrator**. Enter username `DESKTOP-7S6IAK5\Bhanu` and your actual Microsoft/local password; a Windows Hello PIN will not work. Never paste the password into Codex | 5 | The black window says the task was registered. Type `exit` after success. If the account is passwordless or the password is rejected, stop—do not repeatedly retry—and use the documented alternate account setup. Re-register if the password changes |
| 6A | BLOCKED | Sun Aug 16 | 30 min | Codex | Outside 03:00–05:00 PT, stop the old API process, start the registered clean-runtime task, and prove the cutover and rollback | 5, 6 | Exactly one process owns port 8000 and exactly one live database is used; health succeeds, task reports success, and reboot recovery passes |
| 7 | CODEX WORKING | Sun Aug 16 | 2-4 hr | Codex | Outside 03:00–05:00 PT, explain or fix the 18 non-zero scheduled-task results, including database-lock/time-limit problems and intentional “no work” codes | 2 | No enabled task has an unexplained failure; intentionally disabled jobs remain disabled; at least one next real critical run is observed rather than replaced by a risky manual rerun |
| 8 | DONE | Sun Aug 16 | 10 min | Codex | Remove HuntDesk's automatic Windows login startup entry so it remains manual-only | None | HuntDesk no longer launches at login; its database is unchanged |
| 9 | DONE | Sun Aug 16 | 1-2 hr | Codex | Finish shared instruction portability: path-neutral source rules/hooks, global Codex/Claude/Gemini rules, managed Codex CLI resolution, and a Mac bootstrap command that does not rewrite the guide from a machine-specific project list | None | 126 instruction tests and `--check --artifacts-only` pass; full project check is intentionally waiting on the `demo_sandbox` decision |
| 10 | CODEX WORKING | Mon Aug 17 | 1-3 hr | You + Codex | Compare, commit, and push wanted work in every Git row below; preserve uncertain local data and discard nothing without review | 2, 9 | Fresh fetch confirms every wanted commit exists on GitHub; no project is stranded on a detached commit |
| 11 | YOUR DECISION BY MONDAY | Mon Aug 17 | 30-45 min | You | Decide whether `demo_sandbox` is valuable and whether Earnings should stay public. Have an external disk ready for encrypted Time Machine and confirm the database-backup encryption key is stored outside Windows in your password manager or another secure place | 2 | Decisions are recorded; the recovery key exists off the laptop; nothing is deleted merely to migrate |
| 12 | WAITING | Mon Aug 17 | 30-60 min | Codex | Create the project inventory file and complete the full shared-instruction project check after `demo_sandbox` is either promoted or explicitly archived/excluded | 10, 11 | Inventory covers all 14 Git repositories plus five non-Git Claude folders; full instruction check passes and contains no credentials |
| 13 | BLOCKED | Mon Aug 17 | 30-60 min | You + Codex | Outside 03:00–05:00 PT, rehearse a Windows restart: save work, reboot, connect remotely, sign in once, confirm Google Drive mounts, and run the health checklist | 4, 6A, 7-8 | Portfolio API, critical earnings jobs, Drive, Tailscale, and backups recover after reboot |
| 14 | WAITING | Tue Aug 18 | 30 min | Codex | Run a final encrypted database backup and verify it independently of the whole-workspace archive | 7, 13 | Current backup plus successful restore/integrity proof |
| 15 | WAITING | Tue Aug 18 | 30-90 min | Codex | Final GitHub comparison: fetch remotes, push approved changes, and record commit IDs. Stop editing Windows development folders afterward, but do not move, delete, lock, or make them read-only | 10, 12 | Fresh Mac clones will contain every approved code change; Windows remains a rollback copy |
| 16 | WAITING | Tue Aug 18 | 15 min | You | Put Windows on AC power, use wired Ethernet if practical, leave ventilation around it, and close the lid only after the health page is green | 13-15 | You can reach it remotely and the charger/network stay connected |
| 17 | WAITING | Wed Aug 19 | 45-90 min | You | Set up the Mac account, install macOS updates, enable FileVault, store its recovery method safely, and start an encrypted Time Machine backup | Mac and external disk in hand | Mac security and first backup are enabled before project data accumulates |
| 18 | WAITING | Wed Aug 19 | 30-60 min | You | Install and sign in to GitHub Desktop, Google Drive, Claude Code, and OpenAI's **ChatGPT desktop app, which includes Codex**, from `https://chatgpt.com/download/`. Enter passwords only into official apps or macOS prompts | 17 | Each official application opens and its sign-in succeeds |
| 19 | WAITING | Wed Aug 19 | 45-60 min | You + Codex | In Google Drive, use Stream files; do **not** put `~/Developer` inside Drive. Codex downloads the newest verified database, scratch, Claude-project, and Codex-memory backups into local `~/Migration-Recovery`, then starts another encrypted Time Machine backup | 18 | Project code remains outside Drive and the newest recovery set now exists in Google Drive, on the Mac, and on encrypted Time Machine |
| 20 | WAITING | Wed Aug 19 | 45-90 min | You + Codex | In GitHub Desktop choose File → Clone Repository and place repos under `~/Developer`. Clone `agent-instructions` first, then each repo; switch to the branch recorded in the project inventory | 15, 18 | Codex verifies that every checkout's commit matches the recorded commit |
| 21 | WAITING | Wed Aug 19 | 45-90 min | You + Codex | Codex installs developer tools and the managed Codex CLI, then runs the shared bootstrap. You complete the separate browser sign-ins for the managed Codex CLI and Claude CLI | 20 | Shared rules/hooks are installed; one harmless prompt succeeds through both `snippets/codex_cli.py` and `snippets/claude_cli.py` without API keys |
| 21A | WAITING | Wed Aug 19 | 15-30 min | Codex | Verify the Codex-memory Git bundle from `~/Migration-Recovery`, compare it with any memory repo the Mac app created, and import without overwriting newer Mac state | 19, 21 | Mac can read the prior memory history; the bundle remains available as rollback |
| 22 | WAITING | Wed Aug 19 | 1-2 hr | You + Codex | Codex creates Mac configuration one project at a time; you enter credentials only into official prompts. Rebuild environments instead of copying Windows virtual environments or token caches | 19-21 | Each selected project starts without a Windows-path or missing-login error |
| 23 | WAITING | Wed Aug 19 | 1-2 hr | Codex | Run quick start-up checks for portable projects. For Earnings, test editing/static checks only and leave managed execution on Windows | 22 | Results are recorded per project; Windows-only limits are clearly labeled |
| 24 | WAITING | First week | 15 min/day | You | Work from the Mac and follow the exact GitHub Desktop loop below. Connect Time Machine at least daily and commit/push at the end of each work session | 23 | No Drive worktrees; GitHub contains committed work; a recent Time Machine backup protects anything uncommitted |

## Git cleanup table before cloning

“Remote exists” means GitHub has a repository. It does **not** prove that today's local work is on GitHub. The live GitHub check now covers 14 repositories: 13 private and one public, Earnings Summary. Changing that repository's visibility is an owner decision because it affects anyone who may already use its public URL.

| Repository | Current local state from scan | What must happen before Mac clone | Mac role |
|---|---|---|---|
| Agent instructions (`.gemini`) | Portability/bootstrap plan is committed and pushed on `main`; one independently managed governance ledger changed again after the commit | Preserve the ledger and do not mix it into migration commits | Clone first; generates the common rules for every agent |
| Earnings Summary | Clean feature branch, synchronized with its remote feature branch; 28 ahead/4 behind `origin/main` after live fetch; GitHub repository is public | Decide whether the feature branch is the approved source and whether the repository should become private; compare through a PR, not by copying the folder | Development/read-only analysis; production remains Windows |
| Portfolio Tracker | Existing performance feature branch remains separate with eight local paths. Reboot repair PR #56 and fresh-install repair PR #57 are merged; clean runtime `9e0a9d3` passes 238 tests and a live-database health probe | Keep user instruction edits separate; you register the credentialed task, then Codex performs the one-owner cutover and reboot proof | Development on Mac; API/runtime remains Windows |
| Date Suggester | Detached commit with seven local changes, including tracked activity/profile data | Reattach wanted work to a named branch; decide whether tracked personal data belongs in Git or backup only | Manual Mac use; Windows URI/schedule can stay Windows |
| Angel Memos | `master`; one dirty definitions file | Commit or consciously leave in archive; recreate Google/Chrome authorization on Mac | Mac-ready after path/config fix |
| Blog Engine | `main`; one dirty definitions file | Commit or consciously leave in archive; move WordPress secret/config to Mac-local config | Mac-ready; scheduled report lane may stay Windows |
| HuntDesk | `main`; two dirty instruction/definition files; local database is ignored | Commit/resolve docs; copy database only through verified backup; recreate external Resume paths | Manual Mac app; no auto-start |
| MyClaw | Mac checkout is dirty and behind one clean Windows state commit; preserved without overwrite | Reconcile the preserved state after the scheduler hardening branch passes review | Develop on Mac; move only the two verified weekly/monthly state jobs through a controlled cutover |
| Reading Companion | Clean `main`; local captures/jobs/sessions/threads are ignored | Confirm those local records are in the workspace archive; do not assume GitHub has them | Core Node work on Mac; Android setup later |
| Wealthplan | Clean `main`, origin present | Export/backup ignored plans and scenario state; make legacy database path configurable | Mac-ready after config |
| Harness | Clean `main` | Replace remaining Windows CLI path assumptions before first Mac use | Mac-ready after short adapter fix |
| Repo Maintenance | Clean `main` | No Mac runtime port needed | Windows-only backup/maintenance runner |
| XR Glasses Guide | Clean `main` | Clone normally; one documentation path can be cleaned later | Ready immediately |
| Resume evidence system | Newly committed and pushed to a new private GitHub repository; 34 deterministic tests pass | Clone normally; archived scratch scripts have known legacy lint warnings but active tests are green | Active private Mac project; HuntDesk consumes only approved outputs |
| Five non-Git Claude project folders | 332 archive entries across Blog Investment Memo, Papers, Private/Public Investment Analyst, Resume parent content, and SoftwareCo Co-Founder are now in a verified Drive archive | Restore as reference folders under `~/Documents/Claude/Projects`; do not turn binary/reference collections into Git repos merely for migration | Documents/reference material, not working code repos |

## What to do with the old code copies in Google Drive

Do not edit them and do not clone from them. Before Mac cutover, have Codex identify the exact parent folder that contains the old Windows code copies, then rename only that parent folder to `OLD-WINDOWS-CODE-DO-NOT-EDIT`. Keep it unchanged for two weeks as an extra rollback copy. Work only from `~/Developer` on the Mac. After two weeks, compare the old folder with GitHub and the verified August 15 archive before deciding whether to delete anything.

The three purpose-built backup folders are different: keep `earnings-summary-db-backups` and `scratch-backups`. Treat `earnings-summary-backup` as legacy until its contents and last successful writer are explicitly confirmed; do not delete it during migration.

## What stays on Windows

Do not migrate these just because the Mac is newer:

| Windows responsibility | Why it stays | How you interact with it |
|---|---|---|
| Earnings Summary's scheduled fleet and exact SQLite runtime | It is built around Windows Task Scheduler and an exact tested SQLite/runtime arrangement that a normal Mac install cannot reproduce today | Monitor by saved health results; deploy only approved releases |
| Portfolio Tracker API and live `portfolio.db` | Earnings reads this local Windows API; one machine must own the live database writer | Remote desktop only for recovery or an approved release |
| Repository-maintenance backups | The source folders and Google Drive mount are on Windows | Weekly archive plus verification alert |
| MyClaw weekly/monthly state jobs (temporary) | They mutate shared Git-tracked memory and must remain serialized on one clean canonical checkout | Move both together only after scheduler hardening, state reconciliation, and a stop-Windows-before-start-Mac canary; no Telegram task is registered |

HuntDesk is not on this list: it is a manual Mac application and must not be scheduled. Date Suggester is also not a permanent Windows responsibility; migrate its weekly job only after fresh Mac OAuth, portability, stop-old-before-start-new, wake/catch-up, and one no-duplicate canary digest; remove emailed URI controls unless a Mac handler is proven. Windows Git cleanup and Claude-memory streamlining retire after Windows development freezes. Design Conformance remains an on-demand skill. Morning Markets Brief is paused/dormant on both known hosts with an owner decision not to resume; archive/delete its definitions later if permanent retirement is desired.

Every Windows application release is an exact-commit boundary: record the approved Git SHA, fetch without merging, build/test a clean candidate at that SHA, classify database/schema and scheduler compatibility, export task definitions, and take plus restore-test a consistent pre-switch database snapshot. Stop the owning process or scheduler only for the atomic switch, run its health check, and on failure roll back code, database, and task definitions together unless backward compatibility was explicitly proven. Never deploy with a blind `git pull`, from a dirty worktree, or while both hosts can write the same database or consume the same queue.

The Windows laptop can stay closed, plugged in, awake, and locked. **Locked is fine; signed out is not currently fine.** Google Drive and 33 scheduled jobs still depend on a signed-in user. After a power loss or Windows Update reboot, use Chrome Remote Desktop to sign in once. Before cutover, turn on Windows restart notifications, set sensible active hours, and check whether the BIOS supports “power on after AC loss.” Removing the final login dependency is a separate reliability project, mainly because Google Drive's mounted folder is user-session software.

## Exact Mac setup

| Order | Install/configure | Plain-English action | Important caution |
|---:|---|---|---|
| 1 | macOS | Update it before loading project state | Reboot as needed now, not mid-migration |
| 2 | FileVault | System Settings → Privacy & Security → FileVault → turn on | Keep the recovery method outside the Mac |
| 3 | Time Machine | Connect an external disk, enable encrypted backups, complete the first backup | Google Drive and GitHub are not full-machine backups |
| 4 | GitHub Desktop | Install and sign in to the GitHub account that owns the private repos | Clone to `~/Developer`, never into Google Drive |
| 5 | Google Drive | Install, sign in, and choose Stream files | The actual path is under `~/Library/CloudStorage`; configure apps from the discovered path instead of hardcoding it |
| 6 | OpenAI desktop app | Install the **ChatGPT desktop app, which includes Codex**, from [chatgpt.com/download](https://chatgpt.com/download/) and sign in | Desktop sign-in alone does not authenticate the separate CLI used by project automation |
| 7 | Claude Code | Install the native macOS package and sign in through its browser flow | Do not copy the Windows Claude settings directory wholesale; separately test the CLI wrapper |
| 8 | Developer tools | Install Homebrew, Git, current Python, `uv`, Node 20+, and project-specific tools | Rebuild `.venv` and `node_modules`; never copy them from Windows |
| 9 | Agent instructions and CLIs | Clone to `~/Developer/agent-instructions`, run `sh snippets/bootstrap_mac.sh`, complete the printed Codex/Claude CLI sign-ins, then run the two transport checks | This generates global rules from one tracked source and proves tiered agent calls actually work on Mac |
| 10 | Projects | Clone each intended repository, switch to the branch recorded in the project inventory, and have Codex verify its commit | A clone starts on the repository's default branch; it does not automatically select another approved branch or commit |
| 11 | Secrets/config | Re-sign in or create files under `~/.config/<project>/` | Never put credentials in Git or the Drive workspace archive |
| 12 | Acceptance | Run each repository's documented quick start-up check | Earnings production execution remains a Windows test |

Official references: [OpenAI's current Mac app](https://help.openai.com/en/articles/9275200-using-the-chatgpt-macos-app), [Codex first-run flow](https://openai.com/codex/get-started/), [GitHub Desktop cloning](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop), [Google Drive stream vs mirror](https://support.google.com/drive/answer/13401938), [Claude Code setup](https://code.claude.com/docs/en/getting-started), [Chrome Remote Desktop setup](https://support.google.com/chrome/answer/1649523), [Apple Time Machine backup](https://support.apple.com/en-us/102307), and [Apple FileVault](https://support.apple.com/en-ie/guide/mac-help/-mh11785/mac).

## Your normal workflow after migration

The exact GitHub Desktop loop is: **Fetch origin → create or select your branch → work → review changed files → commit → push origin → create a pull request → merge on GitHub → switch back to `main` → fetch/pull again.** Merging does not update Windows. Windows changes only during a separate approved release.

| Moment | On the Mac | On Windows | Frequency of touching Windows |
|---|---|---|---|
| Start work | Open the repo in GitHub Desktop; fetch/pull; create or continue a branch | Nothing | None |
| During work | Codex/Claude edit local files; commit coherent checkpoints; Time Machine protects uncommitted work | Scheduled jobs continue on the exact tested release | None |
| Share work | Push the branch and open a pull request | Nothing changes yet | None |
| Merge | Merge after tests/review pass | Still runs the old approved version | None |
| Release to runner | Trigger/approve a controlled deployment that fetches the exact approved commit, tests it, and switches only on success | Updates clean runtime; rolls back on failed quick start-up check | Occasional, and this can later become one-click from the Mac |
| Windows reboots | Connect remotely and sign in once so Drive and sign-in-only jobs return | Health checklist runs | Only after a reboot/alert |

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
| Resume/Claude-project inventory, private remote, and verified archive | Yes | 3-5 hr | 15-30 min | Resume is now privately pushed; six outside-workspace folders are now archived |
| Mac installs, clone, auth, first quick start-up checks | Yes | 4-8 hr | 2-4 hr | Mostly on arrival day and the following day |
| Make five manual Python apps fully path-portable | First-week improvement | 6-12 hr | 30-60 min auth | Angel, Blog, Date, HuntDesk, Wealthplan |
| Native Mac Earnings runtime parity | No | 12-24 hr | Minimal | Exact SQLite/Darwin packaging plus test entrypoint |
| Replace all Windows schedules with Mac `launchd` | No and not recommended now | 24-40 hr | 2-4 hr acceptance | Adds risk without helping the chosen Windows-runner design |
| Automated safe deployments from GitHub to Windows | Recommended later | 6-12 hr | 30 min approvals | Exact commit, test, atomic switch, rollback; never blind pull |

**Planning range before Mac arrival, not a promise:** about 18-36 hours of engineering/system time and about 1.5-3 hours of your direct attention. The actual GO decision still depends on the task classifications, Portfolio reboot, remote-access test, Git comparison, and backup proof. Much of the system time is backup, tests, and task observation.

**Mac arrival and first-week setup:** about 8-16 engineering hours plus 2-4 hours of your direct sign-ins and choices.
**Not required:** the extra 36-64 hours to move Earnings execution and all Windows schedules onto the Mac.

## Cutover acceptance checklist

Do not declare the migration complete until every required box is checked.

- [ ] A new whole-workspace archive exists in Google Drive and passed an archive/extraction check.
- [ ] A current encrypted database backup passed integrity and restore verification.
- [ ] The database-backup encryption key is stored securely somewhere other than the Windows laptop.
- [ ] The newest verified database, scratch, Claude-project, and Codex-memory backups also exist locally on Mac and in encrypted Time Machine, not only in one Google account.
- [ ] Every wanted local code change is committed and pushed to its intended GitHub repository.
- [ ] You have explicitly decided whether the currently public Earnings Summary repository should remain public or become private.
- [ ] No wanted project remains only on a detached commit or unpushed branch.
- [ ] Chrome Remote Desktop works with the Windows lid closed.
- [ ] Portfolio Tracker has exactly one API owner and survives a reboot.
- [ ] Every enabled Windows task is successful or has a documented, intentional non-zero state.
- [ ] Google Drive returns after the rehearsed remote sign-in.
- [ ] The shared instruction repository is pushed and can bootstrap a relocated clone.
- [ ] The Mac uses `~/Developer` for code and Google Drive only for documents/backups.
- [ ] FileVault and encrypted Time Machine are on.
- [ ] Codex, Claude Code, GitHub Desktop, and Google Drive sign-ins work on Mac.
- [ ] Both subscription CLI wrappers—not only the desktop apps—complete a harmless Mac prompt successfully.
- [ ] The prior Codex-memory bundle verifies and is imported or intentionally retained as rollback.
- [ ] Each actively used Mac project passes its quick start-up check or has a documented Windows-only limitation.
- [ ] One tiny practice branch was pushed from Mac, merged on GitHub, and observed as **not deployed** to Windows until the release step.

## Stop/rollback rules

- If a backup cannot be opened, keep the prior two archives and do not prune anything.
- If a project has unclear local changes, preserve it in the archive and defer its Git cleanup; never guess-delete.
- If the Portfolio task fails, restore the prior process and task definition before experimenting further.
- If a Windows reboot loses Drive or scheduled work, keep development on Mac but do not call Windows unattended; use remote sign-in until fixed.
- If a Mac project requires a Windows-only path/runtime, leave production on Windows and record the gap rather than improvising around it.
- Keep the Windows laptop unchanged and available for at least two weeks after the Mac starts working; it is the rollback machine.
