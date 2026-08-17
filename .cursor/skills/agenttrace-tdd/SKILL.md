---
name: agenttrace-tdd
description: Test-driven development rules for AgentTrace. Use before writing or changing production behavior, tests, or pytest settings.
---

# TDD (when there is behavior)

Unit tests are required for product behavior. This bootstrap slice has no product tests yet. Do not add placeholder tests that assert nothing.

## When implementing a slice

1. Write one failing pytest that names the behavior.
2. Run it with `uv run pytest` (or `docker compose run --rm check` once tests are part of that command).
3. Write the smallest typed production code that makes it pass.
4. Refactor only while tests stay green.

## Rules

- Tests live in `tests/`. Name files `test_<behavior>.py`.
- Tests are typed like production code.
- External networks are forbidden in unit tests.
- Do not delete or skip a failing test to make CI green.
- Prefer public-API assertions over private helpers.

## Running tests

```bash
uv run pytest
```

Add pytest to the Docker `check` command only after the first real test exists (pytest exits non-zero on an empty suite).
