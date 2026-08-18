---
name: agenttrace-providers
description: Rules for identifying OpenAI, OpenRouter, and Anthropic responses. Use when changing provider fingerprints, LLM extraction, or vendor schema support.
---

# Provider identification

Use `identify_provider(value)` in `agenttrace.provider`. Do not import vendor SDKs as runtime dependencies.

Fingerprints are documented in [docs/provider-identification.md](docs/provider-identification.md).

## get_reasoning_tokens

```python
get_reasoning_tokens(provider, response)  # int | None
```

Returns 0 when the model ran but used no budget. Returns `None` when the field is absent. Field paths per provider: see `docs/provider-identification.md`.

When Anthropic summarizes thinking (`display: "summarized"`), the billed token count still reflects the full internal reasoning — not the shorter summary text. Always log what the API reports, not what you see in the content blocks.

## Rules

- Match **response envelopes** from current public docs (dict or attribute-equivalent SDK object).
- Check Anthropic, then OpenRouter, then OpenAI. OpenRouter is a superset of OpenAI chat.completion.
- OpenRouter via the OpenAI client is still OpenRouter if extras are present (`native_finish_reason`, `usage.cost`, `gen-` id, `vendor/model`).
- Return `None` rather than guessing.
- When a provider API changes, update fingerprints and tests together. That is the maintenance path.
- Do not treat Anthropic `content` blocks as OpenAI `choices`.
- Do not add `openai`, `anthropic`, or `openrouter` to package dependencies for identification.
