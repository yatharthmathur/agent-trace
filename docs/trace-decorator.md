# `@trace` decorator — what to log

Bread-and-butter API:

```python
from agenttrace import trace


@trace
def ask_model(messages: list[dict[str, str]], model: str = "gpt-4.1"):
    return client.chat.completions.create(model=model, messages=messages)
```

`@trace` records **the function boundary**, not the source inside the function. It can see arguments, the return value, exceptions, and timing. It cannot see locals, and it cannot see `create(...)` kwargs unless those values were also parameters (or the wrapped callable *is* `create`).

## Canonical shape

Return the SDK response object (or pass request fields in as arguments). This call is enough to reconstruct an LLM step:

| Visible at the boundary | Example |
| --- | --- |
| Function name | `ask_model` |
| Arguments | `messages`, `model` |
| Return value | OpenAI `ChatCompletion` / Anthropic `Message` |
| Exception | timeout, 429, API error |
| Timing | start, end, duration |

Avoid wrapping a function that takes nothing and returns only a string. That loses model, tokens, and prompt:

```python
# Weak: decorator sees no input and only a string out
@trace
def ask_model():
    completion = client.chat.completions.create(model="gpt-4.1", messages=[...])
    return completion.choices[0].message.content
```

Wrapping `client.chat.completions.create` itself is also valid and captures request kwargs directly. That is a later convenience, not a different data model.

## Run / span behavior

- The outermost `@trace` call starts a **run** if none is active.
- Nested `@trace` calls become **child spans** (parent = the currently running decorated function).
- The run ends when the outermost function returns or raises.

No `Tracer` object is required for this API.

## Record for one `@trace` call

Three layers. Always write layer 1. Write layer 2 when the return value (or args) look like an LLM request/response. Write layer 3 on failure.

### 1. Envelope (always)

| Field | Why |
| --- | --- |
| `span_id` | Identity |
| `run_id` | Which flight-recorder tape |
| `parent_id` | Tree (null at the outermost call) |
| `name` | Function name (`ask_model`) |
| `qualname` | Module + function, for disambiguation |
| `kind` | `llm` if we extracted LLM fields, else `call` |
| `status` | `ok` or `error` |
| `started_at` / `ended_at` | UTC RFC 3339 |
| `duration_ms` | Latency |
| `input` | JSON snapshot of args + kwargs (see serialization) |
| `output` | JSON snapshot of the return value, or `null` on error |
| `truncated` | True if input/output was cut |

Do not store the `client` object, bound methods, or raw HTTP handles. Drop kwargs named `api_key`, `api_token`, `authorization`.

### 2. LLM fields (when recognizable)

First call `identify_provider(return_value)` ([docs/provider-identification.md](provider-identification.md)). Then extract using that provider's schema. If identification returns `None`, skip this layer.

| Field | Source (OpenAI chat) | Source (Anthropic messages) |
| --- | --- | --- |
| `provider` | type/module (`openai`) | type/module (`anthropic`) |
| `model` | `response.model` or kwarg `model` | `response.model` or kwarg `model` |
| `response_id` | `response.id` | `response.id` |
| `input_messages` | kwarg `messages` | kwarg `messages` |
| `output_text` | `choices[0].message.content` | text blocks in `content` |
| `tool_calls` | `choices[0].message.tool_calls` | `tool_use` blocks |
| `finish_reason` | `choices[0].finish_reason` | `stop_reason` |
| `input_tokens` | `usage.prompt_tokens` | `usage.input_tokens` |
| `output_tokens` | `usage.completion_tokens` | `usage.output_tokens` |

If the return value is not a known SDK object, skip this layer. `input` / `output` still hold the generic snapshots.

Optional request knobs (`temperature`, `max_tokens`, `tool_choice`) belong in `input` only when they were actual arguments. Do not invent them.

### 3. Error (when the function raises)

| Field | Why |
| --- | --- |
| `error.type` | Exception class name |
| `error.message` | String |
| `error.stack` | Traceback text |

Re-raise after recording. The decorator must not swallow the error.

## Serialization rules

- Pydantic v2: `model_dump(mode="json")`
- dataclass: `dataclasses.asdict`
- Mapping / sequence / primitives: as JSON
- Everything else: `repr`, truncated
- Cap encoded input/output at 64 KiB and set `truncated: true`
- Do not follow streams in this slice. If the return value is an iterator/stream, log `output: {"streamed": true}` and leave consumption to a later wrapper

## What not to log

- API keys and `Authorization` headers
- The HTTP request/response bytes
- Cost in currency (tokens are enough)
- Prompt-eval scores
- Unbounded stdout from the process

## Example record

For the canonical `ask_model(messages, model=...)` that returns a `ChatCompletion`:

```json
{
  "name": "ask_model",
  "kind": "llm",
  "status": "ok",
  "duration_ms": 1840,
  "input": {
    "model": "gpt-4.1",
    "messages": [
      {"role": "user", "content": "Why was my order delayed?"}
    ]
  },
  "output": {
    "id": "chatcmpl-abc",
    "model": "gpt-4.1",
    "output_text": "Your order shipped yesterday.",
    "finish_reason": "stop",
    "input_tokens": 24,
    "output_tokens": 8
  },
  "provider": "openai"
}
```

`output` here is the **extracted** LLM view, not a full `model_dump` of `ChatCompletion`. Keep a compact extracted view as the default; a raw dump can wait until someone needs it.
