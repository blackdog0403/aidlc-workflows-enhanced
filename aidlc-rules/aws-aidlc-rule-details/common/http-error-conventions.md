# HTTP Error Conventions

Conventions for generated REST / RPC endpoint error responses. Scope is **HTTP-layer errors from a running application**, not workflow-process errors — those are in `common/error-handling.md`.

## Principle

Two classes of error must map to two different status codes because they mean different things to callers and contract tests:

- **Schema / request-shape validation** — the request could not be parsed as the declared type (missing required field, wrong type, out-of-range per schema).
- **Domain / business-rule error** — the request parsed cleanly but its meaning was illegal (division by zero, `sqrt(-1)`, `ln(0)`, overflow, business-rule violation that only makes sense *after* the request is structurally valid).

Collapsing the two into one status code (typically `400` everywhere) breaks contract tests and hides the schema-vs-domain distinction from clients.

## Status Code Mapping

| Error class | Status | Framework default | Notes |
|---|---|---|---|
| Schema / shape validation | **Framework default** — `422` for FastAPI + Pydantic and for Express + express-validator; `400` for Spring Boot `@Valid` | Do not override. | A custom `RequestValidationError` handler that downgrades `422` to `400` "for consistency" is an anti-pattern. |
| Domain / business-rule error | **`400 Bad Request`** | Raise explicitly with a descriptive body. | Only reachable after schema validation has passed. |
| Authentication failure | `401 Unauthorized` | — | Caller has no / invalid credentials. |
| Authorization failure | `403 Forbidden` | — | Caller authenticated but not allowed. |
| Resource not found | `404 Not Found` | — | Requested entity does not exist. |
| Idempotency conflict / state violation | `409 Conflict` | — | Request is valid but conflicts with current state. |
| Rate limit | `429 Too Many Requests` | — | — |
| Unhandled server error | `500 Internal Server Error` | — | Reach this path only via the global error handler; log per `extensions/security/baseline/security-baseline.md` SECURITY-03. |

## Rules

1. **Never re-map the framework's default schema-validation status code.** If the framework emits `422`, the handler must not convert it to `400`.
2. **`400` is reserved for domain errors** that have no more specific code in the table above.
3. If the generated stack uses a framework whose convention differs from the above, follow the framework's convention and record the choice in `aidlc-docs/aidlc-state.md` under `## API Conventions`. Never invent a new mapping.
4. Error response bodies must include WHAT went wrong and HOW to fix it (per `construction/code-generation.md` "Agent-Friendly Error Messages").
5. Every generated HTTP endpoint SHOULD have a contract test asserting the expected status code for at least one schema-validation failure and one domain-error case.

## Anti-Patterns

- Installing a global `RequestValidationError` handler that converts framework-default `422` into `400`.
- Returning `500` for an expected domain error (e.g., `sqrt(-1)` yielding a server error instead of `400`).
- Returning `200` with `{"error": "..."}` in the body for any error. Status code must carry the primary signal.
- Using `404` for "this resource is disabled" when the correct code is `403` (forbidden) or `410` (gone).

## Related

- `common/error-handling.md` — workflow-process errors (separate from this file).
- `construction/code-generation.md` — general code-generation rules; this file is referenced from there for endpoint work.
- `extensions/security/baseline/security-baseline.md` — global error handler / logging requirements.
