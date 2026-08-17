---
name: agenttrace-tdd
description: Test-driven development rules for AgentTrace. Use before writing or changing production code, tests, fixtures, or CI.
---

# AgentTrace TDD

Unit tests are required. Production behavior is specified by a failing test first.

## Cycle

1. Write one failing pytest that names the behavior.
2. Run `docker compose run --rm test` and confirm it fails for the right reason.
3. Write the smallest production code that makes it pass.
4. Refactor only while tests stay green.
5. Do not commit a new behavior that has no test.

## Rules

- Put tests in `tests/`. Name them `test_<behavior>.py`.
- Prefer focused unit tests over end-to-end tests until the CLI exists.
- Schema changes need fixture + validation tests (`tests/test_schema.py`).
- Do not delete or skip a failing test to make CI green.
- Do not test implementation trivia (private helper names) when a public API assertion will do.
- External networks are forbidden in unit tests. Fake LLM/tool calls.
- Time and UUIDs in tests should be deterministic when order or exact values matter.

## Coverage expectations by slice

| Slice | Tests that must exist |
| --- | --- |
| Schema (current) | Fixtures validate; invalid documents are rejected |
| Recorder | Nested spans, status rollup, exception capture, export shape |
| SQLite | Round-trip run + spans; list ordering |
| CLI | `list` / `show` / `export` against a temp DB |

## Running tests

Always use Docker Compose, not a host-installed pytest, unless Docker cannot run and the user asks for a fallback:

```bash
docker compose run --rm test
```

See the `agenttrace-docker` skill.
