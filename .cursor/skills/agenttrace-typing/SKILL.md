---
name: agenttrace-typing
description: Typing rules for AgentTrace. Use whenever writing or reviewing Python code, public APIs, tests, or pyproject type-checker settings.
---

# Typing is required

This repository is a typed package (`py.typed`). Untyped Python is not acceptable.

## Rules

- Annotate every function parameter and return type, including tests.
- Annotate public module attributes when the type is not obvious.
- Use modern syntax for the 3.10 floor: `list[str]`, `dict[str, T]`, `X | None`.
- Do not use `Any` unless the value is truly unconstrained; if you must, isolate it and comment why.
- Do not use untyped dicts as domain objects when a `dataclass` or `TypedDict` will do.
- No `# type: ignore` without a specific error code and a one-line reason.
- Keep Ruff `ANN` enabled. Do not disable typing rules to silence a check.

## Checking

```bash
uv run ty check src tests
```

`ty` targets Python 3.10 (`tool.ty.environment.python-version`). If ty and Ruff disagree, fix the code so both pass.

## Public API

Anything exported from `agenttrace` (or listed in `__all__`) must have a precise signature. Callers of a pip package should get useful type errors in their editor.
