---
name: agenttrace-docker
description: Docker Compose rules for AgentTrace development and tests. Use when running tests, changing Dockerfile/compose, or adding dependencies.
---

# AgentTrace Docker dev environment

The project must run tests on any machine that has Docker Compose. Do not assume a local Python version.

## Supported command

```bash
docker compose run --rm test
```

That is the default test entrypoint. CI must use the same command.

## Rules

- One Compose service for tests is enough. Do not add Postgres, Redis, Nginx, or a tracing collector.
- Keep the Dockerfile based on `python:3.12-slim`.
- Install the package with `pip install -e ".[dev]"` so tests import `agenttrace`.
- Bind-mount the repo at `/app` in Compose so host edits are tested without rebuilding for every Python change. Rebuild when `pyproject.toml` or the Dockerfile changes.
- `pytest` is the test runner. Do not switch to a different runner without an explicit request.
- Any new runtime or test dependency belongs in `pyproject.toml`, not as an ad-hoc `pip install` in docs.
- `.dockerignore` may skip `.git` and caches; it must not skip `tests/`, `schemas/`, or `src/`.

## Local data

Traces persist in a SQLite file (default `agenttrace.db`). In containers, write it under a mounted working directory so it survives container exit. Do not introduce a Docker volume for a database server.

## Cursor Cloud / other agents

`install` in `.cursor/environment.json` should install `.[dev]` from the repo so agents can run pytest if Docker-in-Docker is unavailable. Prefer Compose when Docker is available. Do not add extra long-running `start` processes; this project has no server.
