---
name: agenttrace-docker
description: Docker Compose rules for AgentTrace checks. Use when running lint/type-check, changing Dockerfile/compose.yaml, or documenting how to run the repo.
---

# Docker

The supported cross-machine command is:

```bash
docker compose run --rm check
```

That syncs the uv environment from `uv.lock`, then runs Ruff (lint + format check) and ty.

## Rules

- `compose.yaml` is the Compose file (not `docker-compose.yml`).
- The image uses official uv (`ghcr.io/astral-sh/uv:0.12.5`) on `python:3.12-slim-trixie`. Pin uv; do not use `latest`.
- Install with `uv sync --locked`. Never `pip install` inside the Dockerfile except via uv.
- Bind-mount the repo at `/app` and keep an anonymous volume on `/app/.venv` so the host venv is not used.
- Rebuild after `pyproject.toml` or `uv.lock` changes: `docker compose build`.
- Do not add Postgres, Redis, Nginx, or other services.
- This image is for **dev/check**, not for publishing. The artifact is the pip package.

## Without Docker

If Docker is unavailable, the same checks are:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run ty check src tests
```
