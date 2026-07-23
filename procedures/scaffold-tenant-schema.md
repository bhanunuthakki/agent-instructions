---
name: scaffold-tenant-schema
description: Generate secure-by-default multi-tenant database schema, Postgres Row-Level Security policies, a tenant-context object, and reversible Alembic migrations. Use when the user says "make it multi-tenant", "add tenant isolation", "tenant_id", "set up the database schema", "scaffold the DB", "row level security" / "RLS", "scaffold migrations", "design the tables", or starts a SaaS / multi-user app with a database. The generative counterpart to the sec-tenant-isolation, backend-multitenancy, and data-engineer audit gates.
---

# Scaffold: Multi-Tenant Schema + RLS

Generate a tenant-isolated data layer that is **secure by default and unbypassable**, so the hardening fleet's L2 gates pass on the first audit instead of forcing a retrofit. Do not hand-roll per-query `WHERE tenant_id = ...` and hope reviewers catch the misses — make the database refuse cross-tenant access at the row level. Code standards (typing, Deep Modules, no silent fallbacks, fail loudly) are always-on from `AGENTS.md`; this skill only adds the tenant-data specifics.

## Default (state it, then build it)

**Shared-DB + shared-schema (pool) + `tenant_id` on every tenant-owned table + PostgreSQL Row-Level Security as the unbypassable scope.** Why this default for a solo builder: one database is cheapest to run, migrate, and back up, and RLS moves the isolation guarantee *below* application code — so a forgotten `WHERE` clause leaks nothing, because Postgres itself filters every row by the current tenant. The audit fleet's #1 multi-tenant breach vector (a raw query that skips the scope) becomes structurally impossible.

Alternatives, one line each: **silo** (DB-per-tenant) = strongest isolation, highest ops cost — reach for it only under a hard compliance demand; **bridge** (shared-DB, schema-per-tenant) = middle ground, painful migrations at scale; **Supabase** (managed Postgres with auth + RLS built in) = the fastest secure-by-default path for a beginner — same RLS model, less infra to run yourself.

> Pivoting to silo/bridge changes nothing below except where the scope lives. Keep `tenant_id` and the context object regardless — they are what make the model portable.

## Workflow

1. **Confirm the default** (or the chosen alternative) and the ORM. Default stack: SQLAlchemy 2.0 typed + Alembic + Postgres, Pydantic v2 at boundaries.
2. **Generate the table template** (§a) for every tenant-owned table: `tenant_id` first-class, composite indexes lead with `tenant_id`, provenance columns on any ingested data.
3. **Generate the RLS policy SQL** (§b) and wire the per-request `SET LOCAL` at the auth edge.
4. **Generate the tenant-context object** (§c) — set once at request entry, threaded by construction, immutable downstream.
5. **Generate the first reversible Alembic migration** (§d) — `upgrade` creates table + enables RLS + policy; `downgrade` reverses all of it.
6. **Hand off to the audit:** end with the verify line and the checklist below.

## (a) Table template — `tenant_id`, composite indexes, provenance

`tenants` is the one table NOT scoped by `tenant_id` (it *is* the tenant registry). Every other tenant-owned table carries `tenant_id` from day one, even while single-tenant — adding it later is the expensive retrofit the data-engineer gate exists to prevent. Provenance columns (`source`, `fetched_at`, `run_id`) go on any table populated by a pipeline/ingest, so every row traces back to its origin.

```python
# models.py — SQLAlchemy 2.0 typed
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Document(Base):
    """Template for a tenant-owned, pipeline-ingested table."""
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # Tenant scope — first-class, NOT NULL, FK to the registry, cascade on purge.
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)

    # Provenance (data-engineer): every ingested row traces to its source + run.
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    run_id: Mapped[UUID] = mapped_column(nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        # Composite index leads with tenant_id — matches every scoped query.
        Index("ix_documents_tenant_created", "tenant_id", "created_at"),
        # Idempotent upsert key for the pipeline: one row per (tenant, source, run).
        Index("uq_documents_provenance", "tenant_id", "source", "run_id", unique=True),
    )
```

Rules baked in: `tenant_id NOT NULL` + FK with `ON DELETE CASCADE` (offboarding purge is `DELETE FROM tenants WHERE id = …` and the rows follow); every composite index leads with `tenant_id`; a unique provenance key gives the pipeline an idempotent upsert target.

## (b) RLS policy SQL — the unbypassable scope

RLS reads the current tenant from a **session GUC** (`app.current_tenant`) that the auth edge sets per request. `USING` filters reads; `WITH CHECK` blocks writing a row under the wrong tenant. `FORCE ROW LEVEL SECURITY` makes it apply even to the table owner — without it the owner role silently bypasses RLS, which is the most common scaffold mistake.

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;   -- applies even to the table owner

CREATE POLICY tenant_isolation ON documents
    USING       (tenant_id = current_setting('app.current_tenant')::uuid)
    WITH CHECK  (tenant_id = current_setting('app.current_tenant')::uuid);
```

The app must connect as a **non-superuser, non-`BYPASSRLS` role** (superusers and `BYPASSRLS` roles ignore policies entirely). Set the tenant per request with `SET LOCAL` so it is scoped to the transaction and cannot leak to the next checkout of a pooled connection:

```python
# db.py — set the tenant on the connection for the life of one request transaction
from contextlib import contextmanager
from collections.abc import Iterator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


@contextmanager
def tenant_session(session: Session, tenant_id: UUID) -> Iterator[Session]:
    # SET LOCAL is transaction-scoped: auto-reset on commit/rollback, pool-safe.
    # Bind as a parameter, never f-string the UUID in — SET LOCAL can't be
    # parameterized directly, so route it through set_config() which can.
    session.execute(
        text("SELECT set_config('app.current_tenant', :tid, true)"),
        {"tid": str(tenant_id)},
    )
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
```

After this, **ordinary ORM queries are automatically tenant-scoped** — `session.query(Document).all()` returns only the current tenant's rows because Postgres filters them, not the app. That is the point: scoping cannot be forgotten.

## (c) Tenant-context object — set once, threaded by construction

A typed, frozen context built once at the auth edge and passed down. It is never re-derived mid-request and never mutated — eliminating the "which tenant am I?" ambiguity that leads to cross-tenant bugs in async tasks and webhooks.

```python
# context.py
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: UUID
    user_id: UUID
```

```python
# deps.py — FastAPI: resolve tenant from the authenticated session, open a
# tenant-scoped DB session. Default-deny: no valid session ⇒ 401, never a
# fallback tenant.
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .context import TenantContext
from .db import SessionLocal, tenant_session


def get_tenant_context(claims: SessionClaims = Depends(verify_session)) -> TenantContext:
    if claims.tenant_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return TenantContext(tenant_id=claims.tenant_id, user_id=claims.user_id)


def get_db(ctx: TenantContext = Depends(get_tenant_context)) -> Iterator[Session]:
    session = SessionLocal()
    try:
        with tenant_session(session, ctx.tenant_id) as scoped:
            yield scoped
    finally:
        session.close()
```

For background jobs/webhooks the same `TenantContext` is constructed at the job's entry point from the persisted payload and passed into `tenant_session` — the job never runs without a tenant. Pass the context object, not a bare `tenant_id` threaded through ≥3 layers (Deep Modules).

## (d) First reversible Alembic migration

`upgrade` creates the table, the indexes, **and** the RLS enablement + policy in one unit. `downgrade` reverses every step in inverse order — a migration that creates RLS but can't drop it is not reversible, and the data-engineer gate blocks on that.

```python
# alembic/versions/0001_documents_with_rls.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_documents_rls"
down_revision = None  # set to the tenants-table migration if separate


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fetched_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_tenant_created", "documents",
                    ["tenant_id", "created_at"])
    op.create_index("uq_documents_provenance", "documents",
                    ["tenant_id", "source", "run_id"], unique=True)

    op.execute("ALTER TABLE documents ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documents FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON documents "
        "USING (tenant_id = current_setting('app.current_tenant')::uuid) "
        "WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid)"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON documents")
    op.execute("ALTER TABLE documents NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE documents DISABLE ROW LEVEL SECURITY")
    op.drop_index("uq_documents_provenance", table_name="documents")
    op.drop_index("ix_documents_tenant_created", table_name="documents")
    op.drop_table("documents")
```

## SQLite alternative (portable, weaker)

No RLS in SQLite — isolation has to live in the ORM base query, which is **bypassable by any raw SQL**, so use it only for local/dev or a genuinely single-tenant tool. Force every read through a scoped session helper and never expose an unscoped one:

```python
def scoped(session: Session, model: type[Base], ctx: TenantContext):
    return session.query(model).filter(model.tenant_id == ctx.tenant_id)
```

The weakness is real: a teammate writing `session.execute(text("SELECT ..."))` skips it silently. Migrate to Postgres + RLS before admitting a second tenant.

## Tests (structural, not wording)

Prove isolation, don't assert on messages: (1) writing a row under tenant A then querying as tenant B returns **zero rows**; (2) attempting to `INSERT`/`UPDATE` a row with a `tenant_id` ≠ the session GUC **raises** (the `WITH CHECK` violation); (3) `DELETE FROM tenants WHERE id = A` cascades A's rows to zero; (4) `downgrade` then `upgrade` leaves the schema and policy intact.

## Anti-patterns

- Relying on application `WHERE tenant_id = …` as the *only* scope — one forgotten clause is a breach. RLS is the floor; app-level filters are convenience, not the guarantee.
- Connecting the app as a superuser or `BYPASSRLS` role — silently disables every policy.
- Omitting `FORCE ROW LEVEL SECURITY` — the table owner then bypasses RLS.
- `SET` instead of `SET LOCAL` (or f-stringing the tenant id) — leaks the tenant across pooled-connection checkouts / opens SQL injection.
- Adding `tenant_id` "later, once we have customers" — that is the retrofit the backend-multitenancy gate is built to prevent. Day one.
- Threading a bare `tenant_id` through every function instead of one `TenantContext` (Deep Modules: pass-through variable).
- Silently dropping rows that fail validation in the pipeline — quarantine and fail loudly (data-engineer).

## Acceptance

Verify with: `/harden --audit sec-tenant-isolation`

The scaffold is correct when it passes the three audit checklists:
- **sec-tenant-isolation** — scope is **default and unbypassable** (RLS via `USING`/`WITH CHECK`); fetch-by-id is implicitly tenant-checked; no opt-in scoping; automated negative test proves A can't reach B; offboarding cascade-purges a tenant.
- **backend-multitenancy** — tenancy model chosen deliberately with tradeoffs named; a `TenantContext` set once at the edge and threaded by construction; `tenant_id` on every tenant-owned table from day one; async/webhook paths carry and apply context.
- **data-engineer** — typed columns + PK/FK/unique/not-null constraints; provenance (`source`, `fetched_at`, `run_id`) on ingested tables; idempotent upsert key; migrations versioned and **reversible** (`downgrade` undoes RLS too).
