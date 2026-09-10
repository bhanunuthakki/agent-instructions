---
name: machine-operations
description: Resolve this machine's approved credential source and client before OpenRouter or Linear operations, or the live host authority before cross-machine work. Does not authorize spend, sending, publication, or production mutation.
---

# Machine operations

Use this narrow adapter before an OpenRouter, Linear, credential-resolution, or cross-machine operation. It owns configured source/client selection; the user task and project contracts own permission and product semantics. Never read an entire secret-bearing file into tool output or model context. Load only the named variable inside the process that needs it.

## OpenRouter on this Mac

For a user-requested OpenRouter operation on this Mac, use `OPENROUTER_API_KEY` from `/Applications/agent-instructions/.env` when the active project has no narrower credential. Load only that variable at runtime; never print it, copy it into a project, or commit it. Credential availability does not authorize calls or spend beyond the user's task. If the file is unavailable or invalid, report the configuration blocker without searching for other credentials.

## Linear on this Mac

For a user-requested Linear operation on this Mac, use `LINEAR_API_KEY` from `/Applications/agent-instructions/.env` when the active project has no narrower credential. Load only that variable at runtime; never print it, copy it into a project, or commit it. The canonical CLI client is `/Applications/agent-instructions/snippets/linear_cli.py`. If this configured source is unavailable, report the blocker rather than searching unrelated files. Follow the applicable Linear workflow for task scope and mutation authority.

## Host and scheduler resolution

Use the live target's configured network identity. Loopback names the machine running the client, not the remote host. Read the affected project's listener, database, recovery, and scheduler owners before cross-machine work; no remembered hostname or sibling checkout becomes a fallback authority. Resolve services and state read-only first. Public listeners, production changes, and GUI/resource handoffs require their existing task authority.

For this fleet, resolve private host identities and routes through `<private-state-root>/operations/HOSTS.md`; its adjacent `JOBS.md` owns the job register. The private-state root is the absolute `AGENT_INSTRUCTIONS_PRIVATE_STATE_ROOT` when set, or `<instruction-checkout>/.private-state` by default. Keep exact private origins in that registry and runtime configuration, not copied into global or project instructions. The registry records intended ownership and dated evidence, not live discovery: compare the target's current listener, service, and scheduler configuration before changing an endpoint or owner. If the registry is unavailable or disagrees with the live target, report the discrepancy without guessing a fallback or changing production. Moving a job requires preserving state, disabling its old owner, and verifying the new owner and recovery path; generated-instruction checks alone do not prove runtime alignment.

For subscription-backed scheduling or a material agent burst, use [agent-operations.SCHEDULING.md](agent-operations.SCHEDULING.md) and the named project schedule registry. This adapter does not duplicate its windows or install jobs. Other machines use their configured adapter; do not infer that the Mac paths above exist or are authorized there.

## Service boundaries and canonical state

When a project designates one host as the owner of live state and services, preserve that single authority across all checkouts and machines. Databases, saved plan files, user edits, and scheduled writers belong to that host; a development checkout is not a second operational instance. Do not copy live state into it for ongoing use, accept live data entry there, or enable duplicate schedulers or background workers. A source-code pull does not deploy the canonical service or transfer state ownership.

For requests such as "pull and open latest", "launch", or operational inspection:

1. Resolve the project's canonical state and service owner and its private route through the host registry above, including the configured Tailscale origin where applicable. Verify the current service and route read-only before opening it. Do not substitute the development machine's localhost address or start a local server to satisfy the request.
2. Open the verified canonical route. If the checkout is newer than the live service, distinguish pulled code from the deployed version; follow the project's deployment procedure only within existing task authority.
3. If ownership, route, or reachability cannot be verified, report the specific blocker. Do not create a local operational fallback, silently change the state owner, or start a second application. An ownership migration requires explicit authority, preserved state and recovery, and verification that the old writer is disabled before the new writer becomes active.

For local development verification of such a project:

- Start a server only for a bounded automated or rendered test using isolated synthetic fixtures. Explicitly select disposable test storage; exclude production databases, copied user data, saved live plans, production credentials, scheduled writers, and external write side effects. If that isolation cannot be established, do not launch it.
- Before launch, establish ownership of the test process, its child processes, and listener, plus a cleanup path that runs on success, failure, and interruption. Keep the test under task supervision; do not install a service, auto-restart job, or detached persistent server.
- Immediately when verification ends, terminate the test server and its children and verify that their listeners are closed. A browser tab closing or a test command exiting is not proof that the server stopped. If cleanup fails, report the remaining resource and resolve it before claiming completion; never hand a test URL to the user as the operational application.
- If a duplicate is discovered, stop any task-owned test instance and verify cleanup. For an unrelated process, inspect ownership and report the conflict before any action requiring additional authority. Do not delete or merge divergent user state as incidental cleanup.
