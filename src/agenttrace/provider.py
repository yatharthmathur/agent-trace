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
