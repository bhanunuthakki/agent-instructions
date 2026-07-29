# LLM call contracts

Use this reference when implementing the central call path, model picker, schemas, telemetry, or budgets.

## One entry point

Provider SDK or CLI integration lives in one module. Feature code passes a closed `Purpose` enum, validated inputs, and an expected output schema; it does not pass an ad hoc model ID.

The central entry point owns:

- purpose-to-model resolution;
- provider and transport dispatch;
- timeout and retry policy;
- structured-output validation and one repair attempt;
- ordered operational fallback;
- budget enforcement;
- call telemetry and safe errors.

Unknown purposes fail during configuration or emit an attributable temporary default only when the product explicitly chose that degradation. Do not normalize an unknown purpose into a silent default.

## Structured output

- Define precise Pydantic, Zod, or equivalent models for data returned to program logic.
- Validate JSON at the boundary. Feed the first validation error to one repair attempt without logging sensitive content.
- On final failure, raise a stable domain exception and record the failed schema version and response hash.
- Prose outputs still carry a typed envelope when callers depend on citations, confidence, evidence gaps, or fallback provenance.

## Call ledger

Record success and failure:

`run_id | purpose | prompt_version | schema_version | model | provider | transport | input_tokens | cached_input_tokens | output_tokens | reasoning_tokens | public_list_cost_estimate_usd | elapsed_ms | success | retries | fallback_path | safe_error_code`

Store prompt and response hashes in ordinary production telemetry. Keep full text only in an access-controlled eval store when replayability requires it.

Public-list cost is the comparison basis even for subscription transports; transport attribution separately answers whether the call used membership or metered billing.

## Budgets and failures

- Enforce a monthly or run-level budget per purpose before dispatch.
- Budget, authorization, missing transport, and invalid configuration errors fail loudly and do not trigger an operational fallback.
- Timeout, transient CLI exit, and provider unavailability may use the registered ordered fallback.
- Every fallback attempt writes its own ledger row and links to the originating run.
- Scheduled independent batches defer a transiently quota-starved item, tally it, continue, and retry next run.

## Acceptance contract

A purpose is governed when:

- every call site routes through the central entry point;
- model selection is purpose-based and current-source verified;
- structured data validates or raises;
- success and failure telemetry is queryable by provider and transport;
- the degradation path is attributable;
- a representative eval gates meaningful prompt or model changes;
- budgets block before spend and cannot be swallowed by fallback.
