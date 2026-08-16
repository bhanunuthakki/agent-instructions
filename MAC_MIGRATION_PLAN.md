# Canonical Windows-to-Mac migration plan

**Mac arrival:** Wednesday, August 19, 2026  
**Plan generated from a live scan:** August 15, 2026  
**Operating decision:** the Mac becomes the development computer; the Windows laptop remains the always-on runner for scheduled jobs, databases, backups, and the Portfolio Tracker API.

**What “mostly hands-off Windows” means:** in a normal week, you should not touch Windows. After a Windows restart, expect a two-minute remote sign-in so Google Drive and 33 jobs return. This cannot be made fully zero-touch in four days while backups depend on Google Drive for desktop. If the laptop loses power and does not turn itself back on, remote desktop cannot turn it on; check the BIOS “power on after AC loss” option if the laptop supports it.

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

## Current readiness verdict

**HOLD today. GO is possible before the Mac arrives, but it is not promised.** Status becomes GO only when every required acceptance box has evidence. The hardware/power setup is good, the repositories all have GitHub remotes, and the main database backup has a proven restore. The remaining blockers are operational, not architectural.

| Area | Live finding | Verdict | Required outcome |
|---|---|---:|---|
| Windows power | AC sleep is disabled and closing the lid is configured to do nothing | Good | Leave plugged in, ventilated, and on a stable network |
| Remote recovery | Tailscale is running, but no remote desktop host is installed and Windows RDP is disabled | Blocker | Install and test Chrome Remote Desktop from another device |
| Reboot behavior | 33 enabled scheduled jobs run only after you sign in; Google Drive also appears only after sign-in | Blocker | Plan on one remote sign-in after a reboot until these jobs are deliberately converted |
| Scheduled jobs | 42 enabled jobs; 24 last succeeded and 18 have non-zero last results | Blocker | Explain/fix each failure or mark it intentionally inactive; do not call the machine healthy from task registration alone |
| Portfolio Tracker API | Port 8000 works only because an old user process is alive; the boot task itself failed | Blocker | Register the repaired password-backed startup task, stop the old process once, and pass a reboot test |
| Earnings runtime | Clean Windows folder running one exact tested version; 18 commits behind the locally known main ref | Intentional | Keep that exact version until an approved release passes tests; never add a blind `git pull` |
| Database backup | Current encrypted backup exists and a restore/integrity drill passed | Good | Preserve the encryption key outside the laptop and run one final backup before cutover |
| Whole-workspace backup | New August 15 archive exists; corrected scanner captured four live databases and skipped 20 old copies; all 92,571 entries opened and restore instructions stream-extracted successfully | Good | Preserve the successful listing/extraction result and run one final pre-cutover backup |
| GitHub completeness | All 14 Git repositories now have an `origin`; 13 are private and Earnings Summary is public. Several still contain uncommitted work or are on non-main branches | Blocker | Decide whether Earnings should become private, then resolve every unfinished Git row below before relying on Mac clones |
| Shared agent instructions | The installer, hooks, and Claude wrapper contained Windows-only paths; the global Codex rulebook was empty | In progress | Finish and push the portable generator, then bootstrap all three agents from the Mac clone |
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
| 5 | CODEX WORKING | Sun Aug 16 | 30-60 min | Codex | Build and test a clean, release-only Portfolio Tracker folder. Configure an absolute `DATABASE_URL` to the **one existing live database** so the clean folder cannot create a second empty database | None | Clean runtime starts against the existing database; database path and current schema are recorded without printing credentials |
| 6 | YOU NEXT | Sun Aug 16 | 10 min | You + Codex | From that clean runtime, double-click `scripts\install-api-server-task.cmd`—not the `.ps1`. Enter your full Windows account name and actual Microsoft/local password; a Windows Hello PIN will not work. Never paste the password into Codex | 5 | The black window says the task was registered. Type `exit` after success; on failure, leave it open and send Codex only the final error message. Re-register if your Windows password changes |
| 6A | BLOCKED | Sun Aug 16 | 30 min | Codex | Outside 03:00–05:00 PT, stop the old API process, start the registered clean-runtime task, and prove the cutover and rollback | 5, 6 | Exactly one process owns port 8000 and exactly one live database is used; health succeeds, task reports success, and reboot recovery passes |
| 7 | CODEX WORKING | Sun Aug 16 | 2-4 hr | Codex | Outside 03:00–05:00 PT, explain or fix the 18 non-zero scheduled-task results, including database-lock/time-limit problems and intentional “no work” codes | 2 | No enabled task has an unexplained failure; intentionally disabled jobs remain disabled; at least one next real critical run is observed rather than replaced by a risky manual rerun |
| 8 | DONE | Sun Aug 16 | 10 min | Codex | Remove HuntDesk's automatic Windows login startup entry so it remains manual-only | None | HuntDesk no longer launches at login; its database is unchanged |
| 9 | CODEX WORKING | Sun Aug 16 | 1-2 hr | Codex | Finish shared instruction portability: path-neutral source rules/hooks, global Codex/Claude/Gemini rules, managed Codex CLI resolution, and a Mac bootstrap command that does not rewrite the guide from a machine-specific project list | None | Instruction tests and `--check --artifacts-only` pass; full project check is intentionally waiting on the `demo_sandbox` decision |
| 10 | CODEX WORKING | Mon Aug 17 | 1-3 hr | You + Codex | Compare, commit, and push wanted work in every Git row below; preserve uncertain local data and discard nothing without review | 2, 9 | Fresh fetch confirms every wanted commit exists on GitHub; no project is stranded on a detached commit |
| 11 | YOU NEXT | Mon Aug 17 | 30-45 min | You | Decide whether `demo_sandbox` is valuable and whether Earnings should stay public. Have an external disk ready for encrypted Time Machine and confirm the database-backup encryption key is stored outside Windows in your password manager or another secure place | 2 | Decisions are recorded; the recovery key exists off the laptop; nothing is deleted merely to migrate |
| 12 | WAITING | Mon Aug 17 | 30-60 min | Codex | Create the project inventory file and complete the full shared-instruction project check after `demo_sandbox` is either promoted or explicitly archived/excluded | 10, 11 | Inventory covers all 14 Git repositories plus five non-Git Claude folders; full instruction check passes and contains no credentials |
| 13 | BLOCKED | Mon Aug 17 | 30-60 min | You + Codex | Outside 03:00–05:00 PT, rehearse a Windows restart: save work, reboot, connect remotely, sign in once, confirm Google Drive mounts, and run the health checklist | 4, 6A, 7-8 | Portfolio API, critical earnings jobs, Drive, Tailscale, and backups recover after reboot |
| 14 | WAITING | Tue Aug 18 | 30 min | Codex | Run a final encrypted database backup and verify it independently of the whole-workspace archive | 7, 13 | Current backup plus successful restore/integrity proof |
| 15 | WAITING | Tue Aug 18 | 30-90 min | Codex | Final GitHub comparison: fetch remotes, push approved changes, and record commit IDs. Stop editing Windows development folders afterward, but do not move, delete, lock, or make them read-only | 10, 12 | Fresh Mac clones will contain every approved code change; Windows remains a rollback copy |
| 16 | WAITING | Tue Aug 18 | 15 min | You | Put Windows on AC power, use wired Ethernet if practical, leave ventilation around it, and close the lid only after the health page is green | 13-15 | You can reach it remotely and the charger/network stay connected |
| 17 | WAITING | Wed Aug 19 | 45-90 min | You | Set up the Mac account, install macOS updates, enable FileVault, store its recovery method safely, and start an encrypted Time Machine backup | Mac and external disk in hand | Mac security and first backup are enabled before project data accumulates |
| 18 | WAITING | Wed Aug 19 | 30-60 min | You | Install and sign in to GitHub Desktop, Google Drive, the current ChatGPT/Codex Mac app, and Claude Code. Enter passwords only into the official app or macOS prompt | 17 | Each official application opens and its sign-in succeeds |
| 19 | WAITING | Wed Aug 19 | 45-60 min | You + Codex | In Google Drive, use Stream files; do **not** put `~/Developer` inside Drive. Codex downloads the newest verified database, scratch, Claude-project, and Codex-memory backups into local `~/Migration-Recovery`, then starts another encrypted Time Machine backup | 18 | Project code remains outside Drive and the newest recovery set now exists in Google Drive, on the Mac, and on encrypted Time Machine |
| 20 | WAITING | Wed Aug 19 | 45-90 min | You + Codex | In GitHub Desktop choose File → Clone Repository and place repos under `~/Developer`. Clone `agent-instructions` first, then projects | 15, 18 | Every expected repo appears and matches the recorded approved commit |
| 21 | WAITING | Wed Aug 19 | 45-90 min | You + Codex | Codex installs developer tools and the managed Codex CLI, then runs the shared bootstrap. You complete the separate browser sign-ins for the managed Codex CLI and Claude CLI | 20 | Shared rules/hooks are installed; one harmless prompt succeeds through both `snippets/codex_cli.py` and `snippets/claude_cli.py` without API keys |
| 21A | WAITING | Wed Aug 19 | 15-30 min | Codex | Verify the Codex-memory Git bundle from `~/Migration-Recovery`, compare it with any memory repo the Mac app created, and import without overwriting newer Mac state | 19, 21 | Mac can read the prior memory history; the bundle remains available as rollback |
| 22 | WAITING | Wed Aug 19 | 1-2 hr | You + Codex | Codex creates Mac configuration one project at a time; you enter credentials only into official prompts. Rebuild environments instead of copying Windows virtual environments or token caches | 19-21 | Each selected project starts without a Windows-path or missing-login error |
| 23 | WAITING | Wed Aug 19 | 1-2 hr | Codex | Run quick start-up checks for portable projects. For Earnings, test editing/static checks only and leave managed execution on Windows | 22 | Results are recorded per project; Windows-only limits are clearly labeled |
| 24 | WAITING | First week | 15 min/day | You | Work from the Mac and follow the exact GitHub Desktop loop below. Connect Time Machine at least daily and commit/push at the end of each work session | 23 | No Drive worktrees; GitHub contains committed work; a recent Time Machine backup protects anything uncommitted |

## Git cleanup table before cloning

“Remote exists” means GitHub has a repository. It does **not** prove that today's local work is on GitHub. The live GitHub check now covers 14 repositories: 13 private and one public, Earnings Summary. Changing that repository's visibility is an owner decision because it affects anyone who may already use its public URL.

| Repository | Current local state from scan | What must happen before Mac clone | Mac role |
|---|---|---|---|
| Agent instructions (`.gemini`) | `main`, 4 commits ahead after a live fetch; one governance ledger changed again plus the final portability/bootstrap edits | Preserve the ledger, commit only owned portability/plan files, run sync/tests, push approved commits | Clone first; generates the common rules for every agent |
| Earnings Summary | Clean feature branch, synchronized with its remote feature branch; 28 ahead/4 behind `origin/main` after live fetch; GitHub repository is public | Decide whether the feature branch is the approved source and whether the repository should become private; compare through a PR, not by copying the folder | Development/read-only analysis; production remains Windows |
| Portfolio Tracker | Feature branch; 12 ahead/1 behind `origin/main`; eight local paths. The startup repair is also being prepared on a separate clean branch | Keep user instruction edits separate; review/merge the isolated runtime-repair PR; deploy only to a clean Windows runner | Development on Mac; API/runtime remains Windows |
| Date Suggester | Detached commit with seven local changes, including tracked activity/profile data | Reattach wanted work to a named branch; decide whether tracked personal data belongs in Git or backup only | Manual Mac use; Windows URI/schedule can stay Windows |
| Angel Memos | `master`; one dirty definitions file | Commit or consciously leave in archive; recreate Google/Chrome authorization on Mac | Mac-ready after path/config fix |
| Blog Engine | `main`; one dirty definitions file | Commit or consciously leave in archive; move WordPress secret/config to Mac-local config | Mac-ready; scheduled report lane may stay Windows |
| HuntDesk | `main`; two dirty instruction/definition files; local database is ignored | Commit/resolve docs; copy database only through verified backup; recreate external Resume paths | Manual Mac app; no auto-start |
| MyClaw | `master`; one dirty weekly-review log | Decide whether the log is official history or backup-only | Edit on Mac; Telegram/scheduled service stays Windows initially |
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
| MyClaw Telegram/Windows jobs | Current launchers and task definitions are Windows-specific | Leave running until a separate Mac service migration is worth doing |
| Date Suggester URI handler and weekly task | Windows registration is not portable | Keep Windows version; use the Mac manually if desired |

The Windows laptop can stay closed, plugged in, awake, and locked. **Locked is fine; signed out is not currently fine.** Google Drive and 33 scheduled jobs still depend on a signed-in user. After a power loss or Windows Update reboot, use Chrome Remote Desktop to sign in once. Before cutover, turn on Windows restart notifications, set sensible active hours, and check whether the BIOS supports “power on after AC loss.” Removing the final login dependency is a separate reliability project, mainly because Google Drive's mounted folder is user-session software.

## Exact Mac setup

| Order | Install/configure | Plain-English action | Important caution |
|---:|---|---|---|
| 1 | macOS | Update it before loading project state | Reboot as needed now, not mid-migration |
| 2 | FileVault | System Settings → Privacy & Security → FileVault → turn on | Keep the recovery method outside the Mac |
| 3 | Time Machine | Connect an external disk, enable encrypted backups, complete the first backup | Google Drive and GitHub are not full-machine backups |
| 4 | GitHub Desktop | Install and sign in to the GitHub account that owns the private repos | Clone to `~/Developer`, never into Google Drive |
| 5 | Google Drive | Install, sign in, and choose Stream files | The actual path is under `~/Library/CloudStorage`; configure apps from the discovered path instead of hardcoding it |
| 6 | Codex desktop | Install the current ChatGPT/Codex Mac app from `chatgpt.com/download` and sign in | Desktop sign-in alone does not authenticate the separate CLI used by project automation |
| 7 | Claude Code | Install the native macOS package and sign in through its browser flow | Do not copy the Windows Claude settings directory wholesale; separately test the CLI wrapper |
| 8 | Developer tools | Install Homebrew, Git, current Python, `uv`, Node 20+, and project-specific tools | Rebuild `.venv` and `node_modules`; never copy them from Windows |
| 9 | Agent instructions and CLIs | Clone to `~/Developer/agent-instructions`, run `sh snippets/bootstrap_mac.sh`, complete the printed Codex/Claude CLI sign-ins, then run the two transport checks | This generates global rules from one tracked source and proves tiered agent calls actually work on Mac |
| 10 | Projects | Clone the intended repos in GitHub Desktop | Clone only approved branches/commits from the project inventory file |
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
