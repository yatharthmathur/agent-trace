# AgentTrace agent notes

This repository is a **Python package** (`agenttrace`), not a hosted service.

Current slice: repo bootstrap (layout, uv/ruff/ty, Docker). Do not add recorder, storage, CLI, or schemas until asked.

Read:

- [docs/mvp.md](docs/mvp.md) for product intent
- `.cursor/skills/` for repo rules (packaging, typing, Docker, TDD, MVP scope)

Run checks with `docker compose run --rm check` when Docker is available, otherwise `uv run ruff check . && uv run ruff format --check . && uv run ty check src tests`.
