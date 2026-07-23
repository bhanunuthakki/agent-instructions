---
name: scaffold-auth
description: Generate secure-by-default authentication for a web app — the generative counterpart to the sec-authz audit gate. Use when the user says "add login", "set up authentication", "build auth", "add user accounts", "scaffold auth", "register/login/logout", "password hashing", "session cookies", or "protect these routes". Emits working argon2id + cookie-session + default-deny FastAPI code a beginner can adopt as-is, then pass to /harden --audit sec-authz.
---

# Scaffold Auth

Generate the highest-risk surface — authentication and access control — correct the first time, so it passes the `sec-authz` audit instead of getting graded after the fact. This skill emits **real, runnable** code, not a tutorial. Apply the always-on Code Standards and Deep Modules rules from `AGENTS.md`; don't restate them here.

## Step 0 — One stack question (then default)

Ask only this, then proceed with the default if unanswered:

> "Default stack is **FastAPI + SQLAlchemy 2.0 + PostgreSQL**, sessions via an **HttpOnly cookie**. Keep it, or are you on something else?"

- **Default:** FastAPI + Postgres + cookie session. Everything below targets this.
- **Fastest beginner path (one line):** **Supabase** gives Postgres + auth + RLS built-in — secure-by-default with no auth code to write. Recommend it if the user has zero backend experience; the rest of this skill is the from-scratch path.

## Decision: session cookie vs. JWT (pick cookie, by default)

- **Default — opaque session cookie** (below). Server holds session state, so logout/revocation is instant and there is no token-validation footgun. Tradeoff: a server-side session store (a `sessions` table or Redis) is required; doesn't scale to fully-stateless multi-service fanout for free.
- **Alternative — short-lived JWT (~15 min) + rotating refresh token.** Stateless access checks scale horizontally. Tradeoff: you now own `alg`/`aud`/`exp`/signature validation (never `alg:none`), refresh-token rotation + reuse-detection, and a revocation list — three places a beginner gets it wrong. Only choose this if you actually have multiple services validating tokens independently.

Generate the cookie path unless the user names the multi-service need.

## What to generate

Emit these files. Wire `auth_router` into the app and apply `require_user` to every protected route.

### `security.py` — password hashing (argon2id) + cookie config

```python
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

# argon2id is the default variant; these are sane interactive params (~64 MB, 3 passes).
_hasher = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=4)

SESSION_COOKIE_NAME = "session"
SESSION_TTL = timedelta(hours=12)


def hash_password(plaintext: str) -> str:
    """Return an argon2id PHC-format hash. Never store plaintext or a fast hash (md5/sha)."""
    return _hasher.hash(plaintext)


def verify_password(plaintext: str, stored_hash: str) -> bool:
    """Constant-time-ish verify. Returns False on mismatch; never raises to the caller."""
    try:
        return _hasher.verify(stored_hash, plaintext)
    except (VerifyMismatchError, VerificationError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    """True when params changed since this hash was made — re-hash on next successful login."""
    return _hasher.check_needs_rehash(stored_hash)


def session_expiry() -> datetime:
    return datetime.now(timezone.utc) + SESSION_TTL
```

> `passlib` alternative if you prefer it: `CryptContext(schemes=["argon2"], deprecated="auto")` then `pwd_context.hash(...)` / `.verify(...)`. Same security; `argon2-cffi` directly is one fewer dependency.

### `models.py` — user + server-side session

```python
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # never exposed in any schema
    role: Mapped[str] = mapped_column(String(32), default="member")  # server-authoritative
    is_active: Mapped[bool] = mapped_column(default=True)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)  # the cookie value
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column()
    user: Mapped[User] = relationship()
```

The cookie carries only the opaque `Session.id` (a UUID) — never the user id, role, or any signed claim the client could tamper with. Revocation = delete the row.

### `dependencies.py` — default-deny `require_user` + authz helpers

```python
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db          # your async-session provider
from .models import Session, User
from .security import SESSION_COOKIE_NAME


async def require_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    session_id: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
) -> User:
    """Default-deny gate. EVERY protected route depends on this. No cookie ⇒ 401, full stop."""
    if session_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    row = await db.scalar(select(Session).where(Session.id == session_id))
    if row is None or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalid or expired")
    user = await db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User inactive")
    return user


CurrentUser = Annotated[User, Depends(require_user)]


def require_role(*allowed: str):
    """Vertical authz. Trust User.role from the DB, NEVER a client-supplied role/header."""
    async def guard(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient role")
        return user
    return guard


def authorize_owns(user: User, resource_owner_id) -> None:
    """Object-level authz against IDOR. Call inside every handler that loads a record by id."""
    if resource_owner_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")  # 404, not 403 — don't leak existence
```

### `routes.py` — register / login / logout

```python
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .dependencies import CurrentUser
from .models import Session, User
from .security import (
    SESSION_COOKIE_NAME, hash_password, needs_rehash, session_expiry, verify_password,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class PublicUser(BaseModel):  # response model — password_hash CANNOT leak through this
    id: str
    email: EmailStr
    role: str


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME, value=session_id,
        httponly=True,      # JS can't read it (XSS can't steal the session)
        secure=True,        # HTTPS only (set False ONLY for localhost dev)
        samesite="lax",     # CSRF defense for top-level nav; use "strict" if no cross-site flows
        max_age=12 * 60 * 60, path="/",
    )


@auth_router.post("/register", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
async def register(body: Credentials, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    if await db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@auth_router.post("/login", response_model=PublicUser)
async def login(body: Credentials, response: Response, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    user = await db.scalar(select(User).where(User.email == body.email))
    # Verify even when user is None to keep timing uniform (no user-enumeration oracle).
    ok = verify_password(body.password, user.password_hash) if user else verify_password(body.password, _DUMMY_HASH)
    if not user or not ok or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)
    session = Session(user_id=user.id, expires_at=session_expiry())
    db.add(session)
    await db.commit()
    _set_session_cookie(response, str(session.id))
    return user


@auth_router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    user: CurrentUser, response: Response, db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    # require_user already proved the caller owns a live session; revoke all of this user's sessions.
    await db.execute(delete(Session).where(Session.user_id == user.id))
    await db.commit()
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


# Precomputed once at import: a valid argon2id hash of a random string, for the timing-equalizer above.
_DUMMY_HASH = hash_password("x" * 16)
```

### Secrets

Read DB URL / signing keys from env, but **don't commit them**. For anything past local dev, source from a manager (AWS Secrets Manager, Doppler, Vault) with per-environment, least-privilege credentials — never one shared god credential. The `.env` stays in `.gitignore`; this is enforced by the pre-commit hook (`AGENTS.md` Safety Rule 3).

## OAuth / OIDC (only if the user wants social login)

Don't hand-roll it — use `authlib`. Non-negotiables the audit checks: send and verify **`state`** (CSRF), use **PKCE** (`code_challenge`/`code_verifier`), verify the **`nonce`** in the ID token, and **validate the ID token** signature + `iss`/`aud`/`exp` against the provider JWKS. Reject `alg:none`.

## Defaults summary

| Decision | Default | When to deviate |
|---|---|---|
| Hash | argon2id (`argon2-cffi`) | never use md5/sha/bcrypt-without-reason |
| Session | opaque cookie + `sessions` table | multi-service → short-lived JWT + rotating refresh |
| Cookie flags | `HttpOnly` + `Secure` + `SameSite=Lax` | `Secure=False` for localhost only; `Strict` if no cross-site nav |
| Authz posture | default-deny `require_user` on every route | — |
| Role source | `User.role` from DB | never a client header/body field |
| IDOR response | 404 (don't leak existence) | 403 only when existence is already public |

## Verify with: `/harden --audit sec-authz`

Each generated piece maps to a `sec-authz` checklist criterion:

- **Slow hash, never plaintext** → `security.hash_password` (argon2id) + `needs_rehash` on login.
- **No auth-bypass / no user-enumeration** → constant-time `_DUMMY_HASH` path in `login`.
- **Cookies HttpOnly + Secure + SameSite** → `_set_session_cookie`.
- **Revocation on logout** → `logout` deletes server-side `Session` rows.
- **Short-lived sessions / expiry checked** → `expires_at` validated in `require_user`.
- **JWT alg/aud/exp/signature validated, no `alg:none`** → only if JWT path chosen; the default cookie path sidesteps it entirely.
- **OAuth state/PKCE/nonce/token validation** → the OAuth section (authlib).
- **Default-deny, server-side authz on every endpoint** → `require_user` dependency; no route reads identity from the body.
- **Object-level checks prevent IDOR** → `authorize_owns` in every by-id handler.
- **No trusting client-supplied role/ids** → `require_role` reads `User.role` from DB; `password_hash` excluded from `PublicUser`.
- **Tokens never in URLs; secrets in a manager** → cookie-only transport; env/secrets-manager note.
- **Tenant-aware authz** → out of scope here; pair with `scaffold-tenant-schema` + `/harden --audit sec-tenant-isolation`.

## Anti-patterns

- Returning the ORM `User` (with `password_hash`) directly instead of through a `PublicUser` response model.
- Storing the user id or role *in* the cookie — that's a forgeable client-supplied identity.
- A protected route that reads `user_id` from the request body or a query param instead of from `require_user`.
- `Secure=False` or `SameSite=None` shipped to production.
- Branching on `if "admin" in role` (substring) instead of an explicit set membership / enum.
- Logging the password, the session id, or the full request URL on error (`AGENTS.md` Safety Rule 4).
- Writing the OAuth flow by hand instead of using authlib — `state`/PKCE/nonce are exactly what beginners drop.

## Acceptance test (structural only)

Test behavior, not copy (per `AGENTS.md` Testing Discipline): a protected route returns 401 with no cookie and 200 after login; `password_hash` never appears in any response body; logout makes the prior cookie return 401; two registrations with the same email — the second is rejected; `hash_password` output starts with `$argon2id$` and differs across two calls on the same input.
