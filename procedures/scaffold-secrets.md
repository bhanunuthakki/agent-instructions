---
name: scaffold-secrets
description: Establish narrow, typed secret configuration and leak prevention for the repository's actual stack. Use for API keys, environment configuration, credential files, rotation, or secret leakage.
---

# Scaffold Secrets

Inspect tracked files, ignore rules, configuration loaders, deployment/runtime secret stores, logs, exceptions, tests, and CI before editing. Never print secret values during discovery.

Create one typed configuration boundary that:

- loads required secrets from the profile-appropriate external store or environment;
- validates presence and shape at startup without echoing values;
- distinguishes secrets from ordinary configuration;
- passes credentials in headers or typed clients, never URLs or command arguments;
- redacts downstream logs, exceptions, HTTP failures, and diagnostic receipts;
- supports documented rotation and revocation with an owner and verification path.

Ignore only the actual secret-bearing files discovered. Do not blanket-ignore databases, SQLite files, fixtures, or broad filename classes. Preserve repository-owned sample files with obvious placeholders and no usable credential material. Use the repository's existing secret scanner or add the narrowest supported check; do not assume one hook layout.

If a real secret is tracked or exposed, stop external use, identify the affected provider/scope without revealing the value, require rotation/revocation, remove it from current state through an approved safe path, and verify the replacement. Merely untracking or rewriting history does not neutralize a credential.

Test missing/invalid configuration, redaction, scanner positives and placeholders, and startup behavior. Then run `sec-appsec`; use `log-redaction` for networked code.
