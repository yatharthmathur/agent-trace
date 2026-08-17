# How we identify LLM providers

`@trace` sees a return value. To extract model, tokens, and text we first decide **which response schema** that value follows. We do **not** import OpenAI, Anthropic, or OpenRouter SDKs. We match documented envelopes (JSON dicts or SDK objects with the same attributes).

Maintenance is: when a provider ships a new envelope, update the fingerprints in `src/agenttrace/provider.py` and the tests.

Sources:

- OpenAI Chat Completions: `object` is `chat.completion` or `chat.completion.chunk`
- OpenAI Responses: `object` is `response`
- Anthropic Messages: `type` is `message`, plus `stop_reason` / `usage.input_tokens`
- OpenRouter: OpenAI-compatible chat object **plus** extras (`native_finish_reason`, `usage.cost`, `id` prefix `gen-`, or `vendor/model`)

OpenRouter is usually the OpenAI Python SDK pointed at `https://openrouter.ai/api/v1`. The class is still `openai.types.chat.ChatCompletion`. Extra fields, not the module name, are what distinguish it.

| Provider | Positive signals | Must not look like |
| --- | --- | --- |
| Anthropic | `type == "message"` and (`stop_reason` present or `usage.input_tokens`); or module `anthropic.*` | `choices`, `object: chat.completion` |
| OpenRouter | chat.completion shape and (`native_finish_reason` or `usage.cost` / `cost_details` / `is_byok` or `id` starts with `gen-` or `model` contains `/`) | Anthropic `type: message` |
| OpenAI | `object` in `chat.completion`, `chat.completion.chunk`, `response`; or module `openai.*` without OpenRouter extras | OpenRouter extras |

Unknown values return `None`. Field extraction (messages, tokens, text) is a later util, keyed off this result.

```python
from agenttrace.provider import Provider, identify_provider

identify_provider(completion)  # Provider.OPENAI | OPENROUTER | ANTHROPIC | None
```
