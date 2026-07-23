---
name: log-redaction
description: Design guidance for keeping secrets out of logs and exception output (AGENTS.md Universal Safety Rule 4). Use when writing code that calls an HTTP API, redacting secrets in logs, fixing a credential leak in logs/exceptions/tracebacks, or auditing a project for secret leaks. Triggers include "redact secrets", "credential leak in logs", "API key in exception", "leaked token in traceback", "audit for secret leaks".
---

# Log Redaction

The leak surface is **stringified exceptions**, not your own `print` statements. `requests.HTTPError`, timeouts, and connection errors embed the full request URL — query string intact — in their message. Any `log.error(str(exc))` or uncaught traceback then writes the API key to stderr / disk on the next failure. This skill is the design home for AGENTS.md Universal Safety Rule 4, which carries only the one-line tripwire.

**Canonical implementation: `earnings-summary/src/log_redact.py`.** It is the single source of truth — copy it or `sys.path` to it; do not re-derive the regexes. Add new provider param/key names there, not in scattered call sites.

## The four moves

### 1. Redact before any log

Route every untrusted string — exception text, response bodies, anything that may carry a URL/header/JSON body — through `redact()` before it touches a logger. `redact()` masks credential query params (`apikey`, `api_key`, `access_token`, `auth_token`, `password`, `secret`, case-insensitive), `Bearer` tokens, JSON-body secrets, and email local-parts.

```python
from src.log_redact import redact

try:
    resp = requests.get(url, params={"apikey": api_key})
    resp.raise_for_status()
except requests.HTTPError as exc:
    log.error("fetch failed: %s", redact(exc))   # apikey=*** in the log
    raise
```

If you must write the redactor fresh (no access to the canonical file), this is the minimum — credential query params only; the canonical version also covers Bearer/JSON/email:

```python
import re

_CRED_RE = re.compile(
    r"(?P<param>apikey|api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)=(?P<val>[^&\s]+)",
    re.IGNORECASE,
)

def redact(text: object) -> str:
    return _CRED_RE.sub(lambda m: f"{m.group('param')}=***", str(text))
```

### 2. Re-raise propagated HTTP exceptions with `from None`

When a function calls `raise_for_status()` and its caller does **not** wrap the call, the original `HTTPError` propagates with the credentialed URL in `__traceback__` and `__cause__`. Replace it with a clean exception and drop the chain — `from None` suppresses both the implicit context and the original traceback frames that carry the URL.

```python
def fetch_quote(symbol: str) -> Quote:
    resp = requests.get(BASE_URL, params={"symbol": symbol, "apikey": api_key})
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise FetchError(f"quote fetch failed ({resp.status_code}): {redact(exc)}") from None
    return Quote.model_validate(resp.json())
```

Use plain `raise` (no `from`) only when the caller is guaranteed to redact at the boundary. `from None` is the safe default for a function whose callers you don't control.

### 3. Prefer headers over query params

Secrets in the URL leak via the exception path above, server access logs, browser history, and proxy logs. Headers leak through none of those. If the API accepts either, use a header — it removes the leak surface entirely rather than masking it after the fact.

```python
# ❌ secret in URL — leaks via exception message, access logs, proxies
requests.get(url, params={"apikey": api_key})

# ✅ secret in header — never in the URL string
requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
# or: headers={"x-api-key": api_key}
```

### 4. Audit procedure — env var → call site

To find a project's leak surface, enumerate every credential read from the environment, then trace each to the network call that consumes it:

1. **Enumerate reads.** Grep for `os.environ.get`, `os.getenv`, `os.environ[`, and (TS/JS) `process.env.`. Each hit naming a credential-ish var (`*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`) is a candidate.
2. **Trace each to its call site.** Follow the variable to the `requests`/`httpx`/`fetch`/`axios` call. Note whether it goes into `params=` (URL — leak surface) or `headers=` (safe).
3. **Check the failure path.** For each leak-surface call, confirm `raise_for_status` / the propagated exception is either wrapped with `redact()` + `from None`, or the caller redacts at the boundary. An unwrapped `params=` call is a finding.
4. **Verify the redactor is wired, not just present.** A `log_redact.py` that no call site imports is a false sense of security.

## Tests (structural, never on wording)

- `redact("https://x?apikey=SECRET")` does **not** contain `SECRET`.
- `redact()` of text with no secret is unchanged (no over-masking).
- Each credential param name in the set is masked (parametrize over the list).
- Round-trip: the masked output still parses / is human-readable (the param name survives, only the value is gone).

Do not assert on the exact mask string or message text — those change.

## Anti-patterns

- `log.error(str(exc))` on an HTTP exception without `redact()` — the canonical leak.
- `raise CustomError(...) from exc` on an HTTP error — `from exc` re-attaches the credentialed traceback you were trying to drop. Use `from None`.
- Redacting your own log messages but letting an uncaught traceback escape to a crash handler / Sentry / stderr — the traceback is the leak, not the message.
- A second copy of the regex in some other module — it drifts. Import the canonical `redact`.
- Masking the param name too (`***=***`) — keep the name for triage; mask only the value.
