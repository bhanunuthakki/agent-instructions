---
name: scaffold-secrets
description: Set up secrets/env handling so credentials never enter the repo and load typed at startup. Use when the user says "set up secrets", "manage env vars", "stop committing credentials", "configure API keys", ".env setup", "secrets management", or when a project keeps credential files (credentials.json, token.json, .env) in its tree. Generative counterpart to the sec-appsec secrets-hygiene gate.
---

# scaffold-secrets

Make secrets **never live in the repo**, **load typed and fail-loud**, and **be easy to rotate**. This is the generative front-half of the `sec-appsec` secrets check and the partner of the `log-redaction` skill (which keeps them out of *logs*). The pre-commit git hook already *blocks* committed secrets — this prevents the situation arising.

Default stack: Python → `pydantic-settings`; TypeScript → `zod` over `process.env`. Same five steps either way.

## 1. Ignore the secret files (do this first)

Append to `.gitignore` (create if absent). Keep the `.example` tracked.

```gitignore
# secrets & local data — never commit
.env
.env.*
!.env.example
credentials.json
token.json
*.pem
*.key
*.p12
*.pfx
secrets/
*.db
*.sqlite3
```

If any secret file is *already tracked*, untrack it without deleting: `git rm --cached <file>` then commit. (Rotate the key afterward — assume an already-committed secret is compromised.)

## 2. A documented `.env.example` (tracked, no real values)

```dotenv
# Copy to .env and fill in. Never put real values here.
DATABASE_URL=postgresql://user:pass@localhost:5432/app
PLAID_CLIENT_ID=
PLAID_SECRET=
# App secret for signing sessions — generate with: python -c "import secrets;print(secrets.token_urlsafe(32))"
APP_SECRET_KEY=
```

## 3. Typed loader — fail loud if a secret is missing

```python
# src/<pkg>/settings.py  — the ONLY place env vars are read
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    database_url: str
    plaid_client_id: str
    plaid_secret: str = Field(min_length=1)
    app_secret_key: str = Field(min_length=32)

settings = Settings()  # raises at import if anything required is missing/blank — never a silent default
```

```typescript
// src/env.ts
import { z } from "zod";
export const env = z.object({
  DATABASE_URL: z.string().url(),
  APP_SECRET_KEY: z.string().min(32),
}).parse(process.env);   // throws on boot if misconfigured
```

No `os.getenv("X", "fallback")` for secrets — a fallback hides a misconfiguration. Read env **only** in this module; everything else imports `settings`/`env`.

## 4. Don't leak them downstream
Pass secrets in **headers** (`Authorization`, `x-api-key`), never URL query params or CLI args (they land in shell history, process lists, and exception strings). For redaction in logs/exceptions, see the `log-redaction` skill.

## 5. Production secrets + rotation
- **Local** → `.env` (gitignored). **Production** → the platform's secret store (Railway/Render/Fly/Vercel env vars), never an `.env` baked into a Docker image. See `scaffold-deploy`.
- Rotation: because the loader is the single read-point, rotating a key is "change it in the secret store + restart" — no code change. Treat any secret that ever hit git history as compromised and rotate it.

## Acceptance (maps to sec-appsec)
- No secret file tracked by git; `.gitignore` covers all credential patterns. → verify: `git ls-files | grep -iE 'credentials|token|\.env$|\.pem$'` returns nothing.
- All env read through one typed loader; missing/blank secret raises at startup, never a silent default.
- Secrets passed via headers, not URLs/args. Verify with: `/harden --audit sec-appsec`.
