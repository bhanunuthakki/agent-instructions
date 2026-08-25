---
name: docs-support-readiness
description: Audit setup, health, backup/recovery, user/API documentation, support intake, escalation, and feedback routing proportional to product reach.
---

# Documentation and Support Readiness

Own the owner's and user's ability to operate, recover, and get help without reading the implementation. Do not require a ticketing vendor or formal SLA unless the product promise needs one.

## Evaluate

- L1 documents prerequisites, setup, start/stop, configuration, where state lives, how to check health, backup, restore, export, upgrade, and common recovery.
- Commands and screenshots/examples are tested against the current product; generated reference material has a freshness check.
- User documentation follows real tasks and names destructive/external effects, limitations, privacy implications, and recovery.
- Public APIs/plugins include current schemas, authentication, errors, rate/usage limits, compatibility/versioning, and a minimal working example.
- External users have a discoverable support path, ownership, expected response appropriate to the promise, escalation for security/payment/data-loss incidents, and incident communication.
- Feedback is linked to reproducible product evidence and routed to the owning product decision; sensitive submissions are minimized and protected.

## Blocking standard

`BLOCK` when the intended owner cannot install, verify, back up, restore, or recover a durable L1 product; or when an external/commercial user cannot safely use the core workflow or obtain help for a consequential failure.

## Coordinate

`operations-readiness` owns whether procedures work. `api-surface-designer` owns the contract. `product-feature` owns behavior. `legal-compliance` owns mandatory notices.
