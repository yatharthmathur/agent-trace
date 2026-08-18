"""Detect which LLM provider produced a response.

Fingerprints come from public response schemas, not from importing vendor SDKs.
Update this module when those APIs add a more specific envelope.

Docs: docs/provider-identification.md
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum

_OPENAI_OBJECTS = frozenset({"chat.completion", "chat.completion.chunk", "response"})
_OPENROUTER_CHAT_OBJECTS = frozenset({"chat.completion", "chat.completion.chunk"})


class Provider(str, Enum):
    """LLM provider whose response schema we recognize."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OPENROUTER = "openrouter"


def get_reasoning_tokens(provider: Provider, value: object) -> int | None:
    """Return the thinking/reasoning token count from a response, or None.

    Each provider exposes this at a different nested path:

    - OpenAI Chat Completions:
        usage.completion_tokens_details.reasoning_tokens
    - OpenAI Responses API:
        usage.output_tokens_details.reasoning_tokens
    - Anthropic (extended / adaptive thinking):
        usage.output_tokens_details.thinking_tokens
    - OpenRouter (passes through upstream value):
        usage.completion_tokens_details.reasoning_tokens

    Returns 0 when the model ran but spent no reasoning budget.
    Returns None when the field is absent (thinking not enabled or not supported).
    """
    usage = _get(value, "usage")
    if usage is None:
        return None

    if provider is Provider.ANTHROPIC:
        output_details = _get(usage, "output_tokens_details")
        return _int_or_none(_get(output_details, "thinking_tokens"))

    if provider in (Provider.OPENAI, Provider.OPENROUTER):
        # Chat Completions / OpenRouter path
        completion_details = _get(usage, "completion_tokens_details")
        if completion_details is not None:
            result = _int_or_none(_get(completion_details, "reasoning_tokens"))
            if result is not None:
                return result
        # Responses API path (object == "response")
        output_details = _get(usage, "output_tokens_details")
        return _int_or_none(_get(output_details, "reasoning_tokens"))

    return None


def _int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def identify_provider(value: object) -> Provider | None:
    """Return the provider for an SDK object or JSON-like mapping, if known."""
    if value is None or isinstance(value, (str, bytes, int, float, bool)):
        return None

    module = type(value).__module__.lower()
    if _is_anthropic_module(module):
        return Provider.ANTHROPIC
    if "openrouter" in module:
        return Provider.OPENROUTER

    if _is_anthropic_schema(value):
        return Provider.ANTHROPIC
    if _is_openrouter_schema(value):
        return Provider.OPENROUTER
    if _is_openai_schema(value):
        return Provider.OPENAI
    if _is_openai_module(module):
        return Provider.OPENAI
    return None


def _is_anthropic_module(module: str) -> bool:
    return module == "anthropic" or module.startswith("anthropic.")


def _is_openai_module(module: str) -> bool:
    return module == "openai" or module.startswith("openai.")


def _is_anthropic_schema(value: object) -> bool:
    if _get(value, "type") != "message":
        return False
    if _get(value, "object") in _OPENAI_OBJECTS:
        return False
    if _has(value, "choices"):
        return False
    return _has(value, "stop_reason") or _has(_get(value, "usage"), "input_tokens")


def _is_openai_schema(value: object) -> bool:
    return _get(value, "object") in _OPENAI_OBJECTS


def _is_openrouter_schema(value: object) -> bool:
    if _get(value, "object") not in _OPENROUTER_CHAT_OBJECTS:
        return False
    if _has(_get(value, "usage"), "cost") or _has(_get(value, "usage"), "cost_details"):
        return True
    if _has(_get(value, "usage"), "is_byok"):
        return True
    choice = _first_choice(value)
    if _has(choice, "native_finish_reason"):
        return True
    response_id = _get(value, "id")
    if isinstance(response_id, str) and response_id.startswith("gen-"):
        return True
    model = _get(value, "model")
    return isinstance(model, str) and "/" in model


def _first_choice(value: object) -> object | None:
    choices = _get(value, "choices")
    if not isinstance(choices, Sequence) or isinstance(choices, (str, bytes)):
        return None
    if not choices:
        return None
    return choices[0]


def _has(value: object, key: str) -> bool:
    if value is None:
        return False
    if isinstance(value, Mapping):
        return key in value
    if hasattr(value, key):
        return True
    dumped = _model_dump(value)
    return dumped is not None and key in dumped


def _get(value: object, key: str) -> object | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value.get(key)
    if hasattr(value, key):
        return getattr(value, key)
    dumped = _model_dump(value)
    if dumped is None:
        return None
    return dumped.get(key)


def _model_dump(value: object) -> Mapping[str, object] | None:
    dump = getattr(value, "model_dump", None)
    if not callable(dump):
        return None
    dumped = dump()
    if isinstance(dumped, Mapping):
        return dumped
    return None
