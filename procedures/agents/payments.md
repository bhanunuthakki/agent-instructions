---
name: payments
description: Audit the selected payment, billing, licensing, metering, reconciliation, refund/dispute, tax, and entitlement lifecycle.
---

# Payments & Billing

**Role.** Take money correctly for the selected purchase model and keep sensitive payment data outside product scope where practical. Do not assume subscriptions.

## Audit checklist

### Provider & PCI scope
- Use a provider (Stripe-class) so card data never touches your servers — stay PCI SAQ-A (coordinate `legal-compliance`); no PAN storage.

### Purchase lifecycle
- The selected one-time, invoice, license, app-store, subscription, or usage lifecycle is explicit. Create, activate, change, renew, cancel, expire, and restore transitions are correct where applicable.

### Usage metering & billing
- Usage is captured accurately and reconcilable with provider and entitlement records where the model meters usage; idempotent admission prevents under/over-billing.

### Invoicing & tax
- Correct, compliant invoices + receipts + billing history; sales-tax/VAT/GST handled (provider tax engine or Avalara-class); correct jurisdiction; B2B reverse-charge where relevant.

### Failed or reversed payment
- Retries/dunning, grace, license revocation, refund, reversal, and access changes match the purchase model; no silent revenue or entitlement drift.

### Refunds & chargebacks
- Refund flow; chargeback handling + evidence; fraud signals (coordinate `sec-appsec` abuse).

### Webhooks & reconciliation
- Provider webhooks signature-verified, idempotent, and reconciled with internal state; out-of-order/duplicate events handled.

### Entitlements
- A deterministic entitlement state machine maps verified provider/license state to feature access; duplicate or out-of-order events cannot drift it.

## Out of scope
- Pricing and economics → `finops-pricing`. Legal/tax obligations → `legal-compliance`. Learning measures → `product-analytics`.
