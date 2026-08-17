---
name: agenttrace-mvp
description: Product scope for AgentTrace. Use before adding features, APIs, services, or UI so the local flight-recorder MVP is not expanded into a platform.
---

# AgentTrace MVP scope

AgentTrace records one agent run (models, tools, errors, timing) to a local SQLite file and lets a developer inspect that run with a CLI.

## Always do

- Treat [docs/mvp.md](docs/mvp.md) as the product source of truth.
- Keep the system to SDK + SQLite + CLI.
- Prefer finishing slices 1–3 (in-memory recorder, SQLite, CLI) before any optional follow-on.
- If a request would add a new product surface, say so and implement only if the user explicitly expands scope.

## Never do (until scope is explicitly expanded)

- Hosted service, HTTP API, auth, multi-user access
- Eval/scoring/datasets/prompt playground
- Cost dashboards or analytics product
- Extra datastores (Postgres, Redis, S3)
- Framework auto-instrumentation (LangChain, etc.) before the explicit SDK works
- OpenTelemetry SDK or OTLP collector as a dependency
- Real-time streaming UI or a multi-page web app

HTML export of a single run is an allowed follow-on after CLI `show` works. It must be a standalone file, not a server.

## When implementing

1. Read `docs/mvp.md` and `docs/architecture.md`.
2. Follow `agenttrace-schema` for fields and `agenttrace-tdd` for tests.
3. Do not invent parallel event formats.
