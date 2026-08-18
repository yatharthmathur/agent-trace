---
name: agenttrace-trace-api
description: Rules for the @trace decorator and what a traced call must record. Use when designing or implementing agenttrace.trace, LLM extraction, or examples.
---

# `@trace` API

The first public API is:

```python
from agenttrace import trace


@trace
def ask_model(messages: list[dict[str, str]], model: str = "gpt-4.1"):
    return client.chat.completions.create(model=model, messages=messages)
```

Full field list and rationale: [docs/trace-decorator.md](docs/trace-decorator.md).

## Rules

- `@trace` records the **function boundary** (args, return, error, timing). It does not parse function bodies.
- Canonical LLM usage: request fields are parameters; the return value is the SDK response object.
- Outermost `@trace` starts a run; nested `@trace` calls are child spans; the run ends when the outermost call finishes.
- Always log the envelope. Extract `provider`, `model`, messages, output text, tool calls, finish reason, and token counts when the return value is a known OpenAI/Anthropic response.
- Re-raise exceptions after recording.
- Truncate payloads at 64 KiB. Redact `api_key` / `api_token` / `authorization`. Never store the client object.
- Do not follow streams in the first recorder slice.
- Do not add a `Tracer` class, SQLite, or CLI until this decorator records the fields above.

## Do not

- Decorate a zero-arg function that returns only `str` and call that the LLM API (it cannot see model, tokens, or prompt unless they were arguments).
- Dump the entire SDK object as the only stored output; store the compact extracted view.
- Swallow errors or fail the user call because serialization failed.
