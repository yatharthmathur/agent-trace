---
name: agenttrace-sdk
description: Python SDK and CLI API conventions for AgentTrace. Use when implementing Tracer, spans, CLI commands, or usage examples.
---

# AgentTrace SDK conventions

Package name: `agenttrace`. Public surface stays small.

## Tracer

```python
from agenttrace import Tracer

tracer = Tracer(db_path="agenttrace.db")  # path optional; default ./agenttrace.db

with tracer.run(name="my-agent", metadata={"version": "1"}) as run:
    with run.llm(name="plan", provider="openai", model="gpt-4.1") as span:
        span.set_input(...)
        span.set_output(...)
        span.set_usage(input_tokens=1, output_tokens=2)
    with run.tool(name="lookup", tool_name="search") as span:
        span.set_input({"q": "..."})
        span.set_output({"hits": []})
```

Also required:

- `run.span(kind=..., name=..., **attributes)` for generic spans (`agent` included).
- Context managers set `started_at` on enter and `ended_at` on exit.
- An exception inside a context manager records `error`, sets span `status` to `error`, sets run `status` to `failed`, then re-raises.
- Recording/persistence failures must not replace the original agent exception.

## Naming

- Use `run` / `span` in APIs, not `trace` / `event` / `log` as the primary nouns.
- CLI binary: `agenttrace`.
- Subcommands: `list`, `show <run_id>`, `export <run_id>`.
- `--db` and env `AGENTTRACE_DB` select the SQLite path.

## Do not

- Do not take a vendor API key in the SDK (this is not a proxy).
- Do not auto-patch `openai` until slice 1–3 work and tests exist for the wrapper.
- Do not expose an HTTP client.
- Do not log full payloads to stdout by default; the store is the record.
