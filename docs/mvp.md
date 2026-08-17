# AgentTrace MVP

AgentTrace is a **local flight recorder** for AI agents. It records what a run did — model calls, tool calls, errors, timing — and lets you inspect that run later.

It is **not** an observability platform. There is no hosted service, no multi-tenant UI, no eval suite, and no prompt playground in this MVP.

## Problem

When an agent fails or behaves oddly, logs are usually incomplete: stdout, a truncated LLM response, maybe a stack trace. You cannot answer:

- Which model was called, in what order, with what input?
- Which tools ran, with what arguments and results?
- Where did the first error occur in the tree of work?
- How long did each step take?

A flight recorder answers those questions from one artifact: a **run trace**.

## Product principle

Capture a complete, inspectable record of a single agent run on the developer’s machine. Prefer a small, reliable recorder over a dashboard.

If a proposed feature needs accounts, a server farm, or a product catalog (evals, datasets, alerts, billing), it is out of scope.

## Who it is for

A developer writing or debugging an agent locally. They instrument the agent, run it, then inspect the trace with a CLI.

## Core loop

1. Start a run.
2. Record nested spans: LLM calls, tool calls, optional sub-agent spans.
3. Record errors on the failing span and on the run.
4. End the run.
5. List runs and show one run as a tree.

## In scope

| Capability | What “done” means |
| --- | --- |
| Explicit Python SDK | `start_run`, nested spans, `llm` / `tool` helpers, `end` / context managers |
| Run + span model | One run is a tree of spans with timestamps, status, input, output, error |
| Persistence | SQLite file on disk (default `agenttrace.db`) |
| Inspect | CLI: `list`, `show <run_id>` (tree + details) |
| Export | CLI: `export <run_id>` writes a JSON document that validates against `schemas/v1/trace.schema.json` |
| Failures | Exceptions and failed tool/LLM calls are first-class, not lost stdout |
| Dev env | Docker Compose is the supported way to run tests on any machine |
| Quality | Unit tests exist before production code (TDD). Tests run in Docker |

## Out of scope

Do not implement these unless the MVP above is finished and the user explicitly expands scope:

- Hosted/SaaS product, accounts, auth, multi-user access
- Web app beyond a possible later HTML export
- Evaluation, scoring, datasets, prompt versioning
- Cost analytics dashboards (storing token counts is in scope; charts are not)
- Auto-instrumentation of LangChain, LlamaIndex, CrewAI, etc.
- OpenTelemetry SDK / OTLP collector (field names may align; no OTel dependency)
- Sampling, retention jobs, PII redaction pipelines
- Postgres, Redis, message queues, object storage
- Real-time streaming UI

## Implementation slices (after this spec)

Do these in order. Each slice ships with tests.

1. **Recorder API (in-memory)** — start/end run, nested spans, status, errors; export matches the JSON schema.
2. **SQLite store** — persist and reload runs; `list` query.
3. **CLI** — `agenttrace list`, `show`, `export`.
4. **OpenAI-compatible wrapper** (optional follow-on) — record chat completions without manual span calls.
5. **Standalone HTML export** (optional follow-on) — one file you can open in a browser. Still not a server.

This repository’s first change is slice 0: spec, schema, skills, and a Dockerized test harness. Product code for slices 1–3 comes next.

## Target SDK (slice 1)

```python
from agenttrace import Tracer

tracer = Tracer(db_path="agenttrace.db")

with tracer.run(name="support-agent") as run:
    with run.llm(name="plan", provider="openai", model="gpt-4.1") as span:
        span.set_input({"messages": [{"role": "user", "content": "..."}]})
        span.set_output({"text": "..."})
        span.set_usage(input_tokens=12, output_tokens=80)

    with run.tool(name="search", tool_name="web_search") as span:
        span.set_input({"query": "..."})
        span.set_output({"results": []})
```

Uncaught exceptions in a `run` or span context manager mark that node `error` and the run `failed`.

## Success criteria

The MVP is complete when all of the following are true:

- A Python agent can record a nested LLM + tool run with a few lines of SDK code.
- After the process exits, `agenttrace show <id>` prints the full tree, including payloads and any error.
- `agenttrace export <id>` produces JSON that passes `schemas/v1/trace.schema.json`.
- `docker compose run --rm test` is green on a clean machine with only Docker installed.
- There is no extra runtime service besides the agent process and a SQLite file.

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Language | Python 3.12+ | Matches where most agents are written; pytest is the TDD default |
| Store | SQLite file | Zero ops, portable, queryable; not a platform |
| Interchange | Versioned JSON schema | Tests and CLI export share one contract |
| Telemetry standard | Align names with GenAI conventions; no OTel SDK | Avoid lock-in and avoid dragging in a collector |
| Inspect UX | CLI first | Enough to inspect a run; HTML is polish |
| Instrumentation | Explicit SDK first | Predictable; wrappers come after the recorder is solid |
| Packaging | One package `agenttrace` | SDK + CLI together until there is a reason to split |
