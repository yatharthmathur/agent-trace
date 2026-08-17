# AgentTrace agent notes

This repository is a **Python package** (`agenttrace`), not a hosted service.

Current slice: identify LLM provider from a response (`agenttrace.provider`). Do not add `@trace`, storage, or CLI until asked.

Read:

- [docs/mvp.md](docs/mvp.md) for product intent
- [docs/trace-decorator.md](docs/trace-decorator.md) for `@trace` and what it logs
- [docs/provider-identification.md](docs/provider-identification.md) for OpenAI / OpenRouter / Anthropic fingerprints
- `.cursor/skills/` for repo rules (packaging, typing, Docker, TDD, MVP scope)

Run checks with `docker compose run --rm check` when Docker is available, otherwise `uv run ruff check . && uv run ruff format --check . && uv run ty check src tests && uv run pytest`.
