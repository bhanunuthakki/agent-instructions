---
name: scaffold-auth
description: Establish stack-appropriate authentication and authorization after the product profile requires external identity or multiple users. Use for login, accounts, sessions, protected routes, or identity-provider integration.
---

# Scaffold Authentication

Authentication is not a default feature of a personal local tool. Use this workflow only when the selected product profile admits external identities, multiple users, protected remote access, or an explicit login requirement.

## Decide from the repository

1. Inspect the framework, deployment profile, identity boundary, data sensitivity, route model, and maintained auth options already present.
2. Verify consequential framework or provider choices against current primary documentation.
3. Prefer a maintained stack-native or managed implementation when it reduces security ownership without violating local ownership, privacy, exit, or cost constraints. Do not inject a universal framework, database, identity vendor, password flow, or token format.
4. Choose the smallest method that satisfies the profile. Server-side sessions are usually simpler for one web application; federated identity may be safer than owning passwords; stateless tokens require a demonstrated multi-service need.

## Required contract

- Default-deny protection on every non-public route and object-level authorization on every resource lookup.
- Typed, validated identity/session input; client claims never establish role, tenant, ownership, or entitlement.
- Secure cookie/session or token settings, bounded lifetime, rotation/revocation, logout, and account/key lifecycle.
- CSRF defense for ambient browser credentials, safe redirects, rate limits, enumeration resistance, and replay protection where relevant.
- Password hashing and recovery only when passwords are actually owned; use maintained algorithms and current parameters.
- Explicit verification/MFA policy proportional to risk, plus administrative and break-glass behavior.
- Secret storage and rotation through `scaffold-secrets`; sanitized failures and audit events without credential material.
- Data model and migration semantics for users, identities, sessions, recovery, and deletion. Do not add tenancy unless the profile separately requires it.

## Evidence

Implement through `code-change`. Add positive and negative tests for anonymous access, expired/revoked sessions, role boundaries, IDOR, CSRF/replay as applicable, rate limits, recovery, and secret leakage. Exercise the real login/logout/recovery flow in the supported browser or client. Then run the `sec-authz` hardening gate. Missing current provider/framework evidence is `HOLD`, not permission to improvise generic auth code.
