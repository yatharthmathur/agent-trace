# AgentTrace MVP

AgentTrace is a **local flight recorder** for AI agents, shipped as a **Python pip package**. It records what a run did — model calls, tool calls, errors, timing — and lets you inspect that run later.

It is **not** an observability platform. There is no hosted service, no multi-tenant UI, no eval suite, and no prompt playground in this MVP.

## Problem

When an agent fails or behaves oddly, logs are usually incomplete. You cannot answer:

- Which model was called, in what order, with what input?
- Which tools ran, with what arguments and results?
- Where did the first error occur in the tree of work?
- How long did each step take?

## Product principle

Capture a complete, inspectable record of a single agent run on the developer’s machine. Prefer a small, reliable library over a dashboard.

If a proposed feature needs accounts, a server farm, or a product catalog (evals, datasets, alerts, billing), it is out of scope.

## In scope (later slices)

- `@trace` decorator as the first API (`from agenttrace import trace`)
- Record nested calls as a span tree; extract LLM fields from known SDK responses
- Persist a run locally (SQLite is the likely default)
- CLI to list, show, and export a run
- Failures as first-class data, not lost stdout

What a traced call stores: [docs/trace-decorator.md](trace-decorator.md).

## Out of scope

- Hosted/SaaS product, accounts, auth, multi-user access
- Eval/scoring/datasets/prompt playground
- Cost analytics dashboards
- Framework auto-instrumentation before the explicit SDK works
- OpenTelemetry collector dependency
- Extra datastores (Postgres, Redis, object storage)

## How we will build it

Work **one slice at a time**. The current slice is repository bootstrap:

1. Package layout, uv/ruff/ty, Docker, boilerplate
2. Recorder API (when asked)
3. Persistence
4. CLI

Do not skip ahead.

## Packaging decisions

| Decision | Choice |
| --- | --- |
| Distribution | Installable Python package `agenttrace` (`src/` layout) |
| Python | `>=3.10` (3.9 is EOL; ty supports 3.10+) |
| Tooling | uv, ruff, ty, pytest, pre-commit |
| Dev environment | Docker Compose `check` service |
