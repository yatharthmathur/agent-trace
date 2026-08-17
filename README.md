# AgentTrace

A Python package that records what an AI agent did — model calls, tools, errors — so you can inspect the run later.

Install target: **`pip install agenttrace`** (not published yet). This repo is the package source.

## Status

Provider identification is in `agenttrace.provider`. `@trace` comes later; logged fields are in [docs/trace-decorator.md](docs/trace-decorator.md). See [docs/mvp.md](docs/mvp.md).

## Layout

```
src/agenttrace/   # installable package (PEP 561 typed)
tests/            # unit tests (added when behavior exists)
docs/             # product notes, not code
```

Requires **Python 3.10+**. Local default is 3.12 (`.python-version`).

## Tooling

Use **uv** and **ruff**. Type-check with **ty**. Do not add Poetry, pip-tools, Black, isort, flake8, or mypy.

```bash
uv sync
uv run pre-commit install
uv run ruff check .
uv run ruff format .
uv run ty check src tests
uv run pytest
```

`pre-commit` runs `ruff check` on staged files. After `uv sync`, install the hook once with `uv run pre-commit install`.

## Docker

Docker is the supported way to run the same checks on any machine:

```bash
docker compose run --rm check
```

That runs Ruff, ty, and pytest against the tree.
