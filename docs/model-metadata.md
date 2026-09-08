# Optional model catalogue metadata

`GET /v1/models` and `GET /v1/models/{id}` retain the same raw request IDs
(`auto`, `active:main`, `active:aux`) and existing model fields. Each entry also
includes an optional, generic `metadata` object; clients must continue to work
when it is absent and must not persist display labels in place of raw IDs.

Example (existing description/context fields omitted for brevity):

```json
{
  "id": "active:aux",
  "object": "model",
  "owned_by": "turbofit",
  "metadata": {
    "role": "aux",
    "backing_model": "selected-main-alias",
    "residency": "unknown"
  }
}
```

- `role`: `auto`, `main`, or `aux`; a routing role, not a residency or selection
  indicator. Auto uses main's backing observation.
- `backing_model`: the exact alias in the published local route, preserved even
  when unloaded. Shared-main aux resolves main's alias rather than a stale aux
  name. Missing/malformed/legacy routes and unresolved API policies yield `null`;
  a policy name is not a concrete model identity. An alias is not a weight-file
  path, hash, or proof of current residency.
- `residency`: currently `loading` or `unknown`. Loading means the existing
  authenticated lifecycle status confirms a wake/ensure-ready operation is in
  flight for the effective local role. It does not prove weight allocation or
  successful readiness. With lifecycle disabled, unavailable, malformed or
  orphaned, the result is unknown. A non-waking role is also unknown: existing
  status does not establish ready, intentional idle/unloaded, or failure.
  In particular, failed wake and absent listener are **never** labelled idle.

Metadata takes one read-only lifecycle status observation per response with a
0.5-second request timeout when `TURBOFIT_LIFECYCLE_REQUIRED` is enabled. It never
acquires a lease, wakes a model, repairs readiness, or changes selection. Existing
context-length fallback probes remain unchanged. No residency cache or health
heuristic is used; the observation can change immediately after the response.
Consumers must treat missing or unrecognised residency values as unknown, and
must not disable selection merely because a model is unloaded or unknown.

## Scope of verification

`tests/test_model_metadata.py` covers raw IDs, published identities, shared-main,
strict lifecycle status validation, unknown failure/idle semantics, and real
HTTP catalogue/detail reads against a disposable lifecycle endpoint without
leases or wake. These are observation/control-path tests, not GPU/model inference
or deployment evidence.
