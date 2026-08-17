---
name: agenttrace-python
description: Python packaging and toolchain rules for AgentTrace (uv, ruff, src layout, Python 3.10+). Use when adding dependencies, changing pyproject.toml, or creating Python files.
---

# Python package rules

AgentTrace is an installable package named `agenttrace`. Import it as `agenttrace`. Code lives in `src/agenttrace/`. Tests live in `tests/`.

## Toolchain

| Job | Tool |
| --- | --- |
| Package/env/lock | uv |
| Lint + format | ruff |
| Types | ty |
| Tests | pytest |

Do not add Poetry, pip-tools, pipenv, `setup.py`, `requirements.txt`, Black, isort, flake8, or mypy.

## Commands

```bash
uv sync
uv add <package>                 # runtime
uv add --dev <package>           # dev only
uv lock
uv run ruff check .
uv run ruff format .
uv run ty check src tests
uv run pytest
```

Commit `uv.lock`. Never edit it by hand.

## Python versions

- `requires-python = ">=3.10"` is the support floor (3.9 is EOL; ty officially starts at 3.10).
- Write code that runs on 3.10–3.14. Ruff `target-version` is `py310`.
- Do not use 3.11+ / 3.12+ / 3.13+ syntax unless it is guarded with `sys.version_info`.
- Prefer `list[str]`, `dict[str, int]`, and `X | None` over `typing.List` / `Optional`.
- Local/dev default interpreter is 3.12 (`.python-version` and the Docker image). That does not raise the support floor.

## Layout

- One package under `src/agenttrace/`. No nested apps, no `lib/` folder.
- Keep `py.typed` in the package.
- Runtime dependencies stay empty until a slice needs them. Prefer the stdlib.
