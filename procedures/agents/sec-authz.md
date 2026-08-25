---
name: sec-authz
description: Audit identity and access control whenever authentication exists or a non-local web/API product surface requires an explicit access decision.
---

# Authentication & Authorization

**Role.** Make identity and access decisions correct and unforgeable whenever authentication exists. For a non-local web/API product surface with `identity: none`, first prove that unauthenticated access is deliberate and safe; remote reachability is itself an access-control decision.

## Audit checklist

### Authentication
- Password storage uses a current slow password hash, never plaintext/reversible; MFA is risk-based; SSO/OAuth/OIDC validates state, PKCE, nonce, signature, issuer, audience, and expiry as applicable; recovery cannot bypass identity proof.

### Sessions & tokens
- Cookie/token transport, CSRF decision, expiry, rotation/revocation, logout, compromise response, and concurrent-session behavior match the architecture. Untrusted identifiers are parsed and validated before lookup; tokens never enter URLs or logs.

### Authorization model
- RBAC/ABAC explicitly defined; **default-deny**; every endpoint and action enforces authz **server-side**; object-level checks prevent IDOR; no horizontal/vertical privilege-escalation paths; no trusting client-supplied role/ids.
- If the profile declares no identity on a non-local web/API surface, inventory every remotely reachable read and mutation, identify the trusted network/device/origin boundary, and prove default-deny outside it. Public mutation without an explicit narrow authorization policy is blocking.

### Context-aware authorization
- Every decision includes the relevant account, organization, or tenant context. Multi-tenant storage enforcement belongs to `tenant-boundaries`.

### Identity and signing keys
- Signing, recovery, API, and service identity keys have least privilege, explicit lifecycle, rotation, revocation, and audience. General credential material/storage/logging belongs to `sec-appsec`.

### Admin, service accounts & audit
- Admin/break-glass access least-privilege and audited; service-to-service auth scoped; authn/authz events logged without secrets.

## Out of scope
- Cross-tenant enforcement → `tenant-boundaries`. Generic vulnerabilities and credential hygiene → `sec-appsec`. Applicable access obligations → `legal-compliance`.
