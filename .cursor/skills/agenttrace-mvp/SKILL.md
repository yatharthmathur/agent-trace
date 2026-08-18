---
name: agenttrace-mvp
description: Product scope for AgentTrace. Use before adding features so the local pip package is not expanded into a platform, and so work stays on the current slice.
---

# AgentTrace MVP scope

AgentTrace is a **Python library** (`pip install agenttrace`) that records one agent run and lets a developer inspect it later. It is not a hosted product.

## Current slice

Provider identification (`identify_provider`). Do not add `@trace`, SQLite, or CLI until asked.

## Always do

- Treat [docs/mvp.md](docs/mvp.md) as the product source of truth.
- `@trace` is the first public API. Field rules live in `agenttrace-trace-api` and [docs/trace-decorator.md](docs/trace-decorator.md).
- Keep the system a library + optional CLI, not a server.
- If a request would add a new product surface (UI, auth, evals), say so and wait for an explicit scope change.

## Never do (until scope is explicitly expanded)

- Hosted service, HTTP API, auth, multi-user access
- Eval/scoring/datasets/prompt playground
- Extra datastores (Postgres, Redis, S3)
- OpenTelemetry SDK or OTLP collector as a dependency
- Real-time streaming UI or a multi-page web app
