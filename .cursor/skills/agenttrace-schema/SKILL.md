---
name: agenttrace-schema
description: Event and export schema rules for AgentTrace runs and spans. Use when changing trace fields, JSON export, SQLite columns, fixtures, or recorder payloads.
---

# AgentTrace schema rules

The interchange contract is [`schemas/v1/trace.schema.json`](schemas/v1/trace.schema.json). Exported JSON must validate against it. Fixtures in `tests/fixtures/` must stay valid.

## Document shape

```
{
  "schema_version": "1.0.0",
  "run": { ... },
  "spans": [ ... ]
}
```

- `schema_version` is currently the constant `1.0.0`.
- A run has `id`, `name`, `status` (`running` | `succeeded` | `failed`), `started_at`, `ended_at`, `metadata`.
- Spans form a tree: `parent_id` is null for roots, otherwise another span `id` in the same run.
- Every span `run_id` must equal `run.id`.
- IDs are UUID4 strings. Timestamps are UTC RFC 3339 ending in `Z`.

## Span kinds

Only `llm`, `tool`, and `agent`.

| Kind | Required `attributes` |
| --- | --- |
| `llm` | `provider`, `model` (optional: `input_tokens`, `output_tokens`, `finish_reason`) |
| `tool` | `tool_name` (optional: `tool_call_id`) |
| `agent` | none required |

Do not add a span kind named `error`. Errors are `status: "error"` plus an `error` object (`type`, `message`, optional `stack`).

If `status` is `error`, `error` must be present. If `status` is `ok`, `error` must be `null`.

## Payloads

- `input` and `output` are JSON values (`null` allowed when unknown).
- Prefer structured objects over free-text blobs when the caller has structure.
- Oversized payloads are truncated; set `truncated: true`.
- Do not store secrets on purpose. Do not build a redaction product in MVP; just avoid adding API keys into examples and tests.

## Alignment (not a dependency)

Field *ideas* may match OpenTelemetry GenAI (`provider`, `model`, token counts, tool name). Do not require the OpenTelemetry SDK. Do not emit dotted `gen_ai.*` keys as the native export format.

## Changing the schema

1. Update `schemas/v1/trace.schema.json`.
2. Update fixtures and schema tests in the same change.
3. Additive optional fields may stay on `1.0.x`. Removing or renaming fields is a breaking bump (`2.0.0`) and needs an explicit user decision.
4. SQLite columns must round-trip the export document without loss of required fields.
