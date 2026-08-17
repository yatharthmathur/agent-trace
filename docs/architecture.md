# Architecture (MVP)

Keep the system to three parts: **SDK**, **store**, **CLI**. One Python package. One SQLite file. No network services.

```
Agent process
    └── agenttrace.Tracer
            ├── in-process span tree (contextvars)
            └── SqliteStore  →  agenttrace.db
                                    ▲
CLI (list / show / export) ─────────┘
                                    │
                              JSON export
                              (schema v1)
```

## Package layout

```
src/agenttrace/          # production code (empty until slice 1)
schemas/v1/              # interchange contract
tests/                   # pytest; required for every behavior
docs/                    # product and architecture
.cursor/skills/          # rules for later agent work
```

Do not add services, `apps/`, or a frontend package during the MVP.

## Data model

A **run** is the flight-recorder tape for one agent execution.

A **span** is one unit of work inside that run. Spans form a tree via `parent_id`.

| Span `kind` | Meaning |
| --- | --- |
| `llm` | A model call (chat/completion). Store provider, model, usage, input, output. |
| `tool` | A tool/function invocation. Store tool name, arguments, result. |
| `agent` | A sub-agent or explicit loop boundary. Optional in simple runs. |

Status is `ok` or `error`. Failures live on the span (`error.type`, `error.message`, `error.stack`) and roll up to `run.status`.

Full field definitions: [`schemas/v1/trace.schema.json`](../schemas/v1/trace.schema.json). Narrative rules: the `agenttrace-schema` skill.

## Runtime rules

- Use `contextvars` for the current run/span so helpers work across nested calls without passing `run` everywhere internally. The public `with tracer.run()` API still takes an explicit handle.
- Recording must never crash the agent. Store/serialize failures are logged and swallowed after a test-covered fallback.
- Payloads are JSON-serializable. Non-serializable values become a short error placeholder, not a hard fail.
- Truncate oversized input/output (default 64 KiB encoded JSON) and set `truncated: true`.
- Timestamps are UTC RFC 3339. IDs are UUID4 strings.
- Schema version is `1.0.0` until a breaking change requires `1.1.0` or `2.0.0`.

## Persistence

SQLite tables (slice 2):

- `runs(id, name, status, started_at, ended_at, metadata_json, schema_version)`
- `spans(id, run_id, parent_id, kind, name, status, started_at, ended_at, attributes_json, input_json, output_json, error_json, truncated)`

Indexes: `spans(run_id)`, `runs(started_at DESC)`.

No ORM required. `sqlite3` in the stdlib is enough.

## CLI

Entry point `agenttrace`:

- `list` — recent runs: id, name, status, started_at, span count
- `show <run_id>` — indented tree; print error and payloads
- `export <run_id> [--out file]` — schema-valid JSON document

Default DB path: `./agenttrace.db`, overridable with `--db` or `AGENTTRACE_DB`.

## Docker

`docker compose run --rm test` is the supported test command. See the `agenttrace-docker` skill. Do not add Postgres/Redis containers.

## What not to build

No HTTP API, no collector process, no background workers. The agent writes SQLite; the CLI reads SQLite. That is the whole system.
