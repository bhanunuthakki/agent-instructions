# Workspace reconstruction

`config/workspace_reconstruction.json` is the canonical, hand-maintained project
population and offline command contract. It links the durable Linear assessment.
The assessment counted11 projects in August; the current generated `AGENTS_GUIDE.md`
project census contains13. The checker compares identities to that census and rejects
omissions/duplicates instead of preserving a historical number by dropping projects.
Earnings Summary's own11-subsystem manifest remains a separate, linked product inventory.

From this repository, with an ordinary Python3.11+ interpreter:

```shell
python snippets/workspace_reconstruction.py validate --workspace-root <workspace>
python snippets/workspace_reconstruction.py plan --workspace-root <workspace> --mode full
python snippets/workspace_reconstruction.py run --workspace-root <workspace> --mode fast
python snippets/workspace_reconstruction.py run --workspace-root <workspace> --mode full --clean-home
```

`BHANU_DEVELOPER_ROOT` supplies the default workspace root; absent that, the parent of
this checkout is used. No personal home or Windows drive is hardcoded. Resolve Python
from each project's `.venv`/`venv`, or pass repeatable `--python project=/path/to/python`.
The explicit override is also the route for shared ordinary test runtimes, such as
harness's parent-directory pytest command. The runner never installs dependencies.
Use each record's install/toolchain/lock metadata separately after reviewing network
and state effects. Named secret/state locations are inventory only and are never opened.

Each project has one local entrypoint through this checked-in dispatcher:

```shell
python <instructions-root>/snippets/workspace_reconstruction.py run --project <project> --mode fast --workspace-root <workspace>
```

A selected project receipt states`scope=selected_projects`. It cannot claim whole-workspace
readiness. Every invoked check reports pass/fail/skip, a specific category and reason,
exit code when available, duration and a SHA256 of combined output. Output bytes are not
emitted or saved, avoiding accidental credential/private-data logs. Inspect a failing
command directly in its owned development environment when detailed diagnostics are needed.
Missing interpreters, Python modules, executables, installed Node dependencies or Android
tool configuration fail as`missing_tool`; they are never silently skipped. Plan mode emits
`not_run`, never a verification pass. Source syntax compilation parses without importing
application code or writing bytecode. The documentation-only XR guide checks local links;
that is not source-freshness or hardware verification.

## Scope and exceptions

The manifest's executable commands are reviewed offline test/lint/type/build commands.
`offline_safe` records that review; it is not an operating-system network sandbox.
No application startup, model eval, package install, calendar/broker sync, WordPress/Vercel
publication, resume production compile or maintenance operation belongs in the contract.
In particular, repo-maintenance's`DryRun` modes mutate logs/backups/Git metadata and are
excluded; only hermetic memory-runner tests and source parsing run there.

Python checks use the existing project or explicitly supplied interpreter and never `uv`
auto-install. Reading Companion includes Core type/tests, browser/serverless JS syntax,
and both Android client build/unit-test targets with Gradle`--offline`. Missing Gradle,
JDK, SDK or cached artifacts is unavailable evidence, not a successful Android check.
Tracker includes frontend typecheck/build alongside backend checks. Device hardware,
external source freshness and deployed services remain separate operational evidence.

Project hooks retain their current owners and narrower boundaries. The shared instruction
hook and hosted instruction CI call this same manifest validator; CI uses`--schema-only`
because sibling private projects are absent there. That explicitly validates contract
shape/population, not sibling source existence or check execution. Each application's
existing public-boundary/UI hook may remain narrower than its full offline contract.
Earnings Summary retains its Make/CI gates; this dispatcher invokes those same targets.
No stronger project gate is replaced. The central command and each project rulebook remain
available without a native skill loader. A future change that adds a project check should
update this contract and its project-owned hook/CI where applicable, without silently
widening operational authority.

## Replacement-agent drill and recovery

Read `GLOBAL.md`, the relevant `AGENTS.md`, this file and the manifest. Validate inventory,
review the planned commands, provision ordinary runtimes/dependencies separately, then run
`--clean-home` on the supported Windows baseline. The runner creates and removes its own
temporary home/config directories, removes API credentials from subprocess environment,
and redirects native Claude/Codex/Gemini homes and Git global config. It neither invokes
nor auto-loads a native agent skill. Existing configured SDK/cache paths may be supplied
for offline builds; record those prerequisites in the drill evidence.

A successful Mac source/test run is not the required Windows drill. Retain the actual
Windows receipt with platform, manifest hash and all command outcomes. The current task's
Windows execution is coordinated separately with the canonical host owner. Do not claim
it happened merely because the runner or synthetic tests pass.

Application source may currently be uncommitted in other projects. The receipt lists
only declared check sources and public LLM entrypoints that are untracked or modified, without enumerating
private files or overwriting user work. `declared_contract_ready` requires successful declared checks across the workspace and
committed declared check/LLM authorities. It does not establish that every application
dependency or the complete workspace can be reconstructed. Mode and selected-project
scope remain explicit; a selected-project run cannot set this field. Preserve it and arrange an owner-reviewed commit/backup;
do not commit other tasks' work merely to turn a readiness field green.

The manifest inventories actual provider seams, including Reading Companion's unresolved
SDK/purpose/budget tranche. Registration is not live substitution proof. Prompt/schema
version ownership stays with local source and the usage index; missing independent versions
or incomplete fake-provider matrices are explicit BHA56 follow-up evidence, not an assertion
that every model is interchangeable. Restore canonical sources first, then separately
approved private state, then replace a provider adapter and run the affected deterministic
matrix and purpose eval. Never read credential values to prove inventory completeness.
