---
name: scaffold-deploy
description: Take a working localhost app to a live, secure deployment — container + managed platform + CI + backups. Use when the user says "deploy this", "ship it", "go live", "host my app", "set up deployment", "Dockerfile", "set up CI/CD", or is ready to move a project from localhost to production. Generative counterpart to the infra-devops / infra-sre audit gates.
---

# scaffold-deploy

Get from "works on my machine" to "live, with TLS, secrets, and backups" — without hand-rolling a server. This is the generative front-half of the `infra-devops` + `infra-sre` gates.

**Default: containerize + deploy to a managed PaaS** (Railway by default; Render or Fly.io are equivalents). The tradeoff, named: a PaaS gives you TLS, a secret store, automatic rollbacks, and managed Postgres-with-backups out of the box — the right call for a solo builder who shouldn't be patching a VPS. A raw VPS is cheaper and more flexible but puts OS hardening, TLS renewal, and backups on you. Pick the PaaS unless you have a specific reason not to.

## 1. Dockerfile (multi-stage, non-root, pinned)

```dockerfile
# Python / FastAPI
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY . .
RUN useradd -m app && chown -R app /app
USER app                       # never run as root
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`.dockerignore`: `.env`, `.git`, `*.db`, `__pycache__`, `node_modules`, `.venv` — secrets and local data never enter the image.

## 2. Platform config + secrets (Railway default)

```jsonc
// railway.json
{ "build": { "builder": "DOCKERFILE" },
  "deploy": { "healthcheckPath": "/healthz", "restartPolicyType": "ON_FAILURE" } }
```

Set every secret in the **platform's variables UI / CLI** (`railway variables set APP_SECRET_KEY=...`), read at runtime by the typed loader from `scaffold-secrets`. **No `.env` in the image.** Use the platform's managed Postgres add-on (it injects `DATABASE_URL` and runs automated backups).

Add a healthcheck route so the platform knows the app is up:
```python
@app.get("/healthz")
def healthz(): return {"ok": True}
```

## 3. Minimal CI — run the same gate, then deploy

```yaml
# .github/workflows/ci.yml
name: ci
on: { pull_request: {}, push: { branches: [main] } }
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen
      - run: uv run ruff format --check . && uv run ruff check .
      - run: uv run pyright
      - run: uv run pytest -q
  # Railway/Render auto-deploy on push to main once the repo is connected — no deploy step needed here.
  # If you prefer explicit deploys, add the platform's deploy-action gated on `needs: gate`.
```

CI runs the **same pre-push checklist** the local git hook runs — the gate is enforced in two places, so a bypassed local hook still gets caught.

## 4. Reliability basics (the infra-sre half)
- **Backups:** managed Postgres → automated (verify the schedule + do one test restore). Local **SQLite** that you're hosting → a scheduled `sqlite3 .backup` dump to object storage; never rely on the single file.
- **Logs + errors:** ship stdout to the platform's log view; add error tracking (Sentry free tier) before real users.
- **Rollback:** confirm the platform's one-click rollback works *before* you need it.

## Acceptance (maps to infra-devops + infra-sre)
- Image runs as non-root, builds reproducibly, contains no secrets/local data.
- Secrets in the platform store; healthcheck green; CI gate passes on PR.
- Backups configured **and a restore tested**; rollback verified.
- Verify with: `/harden --audit infra-devops` (and `--audit infra-sre` for backups/observability).
