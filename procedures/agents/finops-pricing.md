---
name: finops-pricing
description: Audit operating cost, unit economics, price, packaging, margin, and cost ceilings for the selected personal, free, or paid profile.
---

# FinOps & Pricing

**Role.** Make sure the business makes money per unit and the price reflects value — grounded in the real cost to serve, not guesses.

For personal/free products, report cost, time, and avoidable operational burden as advice. Commercial pricing becomes blocking only for a paid L3 profile.

## Audit checklist

### COGS model (L0 `A` → L3 `B`)
- Per user/account/unit cost includes infrastructure and operations evidence, LLM/resource use, data licenses, payment fees, distribution, and support burden; separate variable, step-fixed, and fixed cost.

### Margin
- Gross + contribution margin per tenant/plan; breakeven volume; worst-case heavy-user margin (no unprofitable whales).

### Pricing model (L3 `B`)
- Structure (flat / seat / usage / tiered / hybrid) matched to a value metric; **value-based, not just cost-plus**; price aligned with when the customer realizes value.

### Packaging & tiers
- Packaging follows the selected flat, seat, usage, tiered, one-time, invoice, app-store, license, or hybrid model. Entitlements and usage limits are enforceable where promised.

### Price points & willingness-to-pay
- Benchmarked against alternatives; tested signal where possible.

### Cost controls
- Cost/resource ceilings at the applicable principal boundary prevent usage from inverting margin (coordinate `llm-evals-orchestrator`, `sec-appsec`).

### Financial guardrails
- Discounting policy; refund exposure; dunning impact (coordinate `payments`); cohort LTV vs CAC sanity.

## Out of scope
- Billing implementation → `payments`. Learning measures → `product-analytics`. Runtime cost telemetry → `operations-readiness`.
