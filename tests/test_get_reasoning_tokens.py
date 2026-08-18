"""get_reasoning_tokens — extract thinking/reasoning token counts from LLM responses.

Field paths by provider and API surface:

  OpenAI Chat Completions
    usage.completion_tokens_details.reasoning_tokens

  OpenAI Responses API
    usage.output_tokens_details.reasoning_tokens

  Anthropic Messages (extended / adaptive thinking)
    usage.output_tokens_details.thinking_tokens

  OpenRouter
    usage.completion_tokens_details.reasoning_tokens   (passes through upstream)
"""

from types import SimpleNamespace

import pytest

from agenttrace.provider import Provider, get_reasoning_tokens

# ── OpenAI Chat Completions ────────────────────────────────────────────────────


def test_openai_chat_reasoning_tokens_dict() -> None:
    value = {
        "object": "chat.completion",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
            "completion_tokens_details": {
                "reasoning_tokens": 150,
                "audio_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0,
            },
        },
    }
    assert get_reasoning_tokens(Provider.OPENAI, value) == 150


def test_openai_chat_reasoning_tokens_sdk_object() -> None:
    value = SimpleNamespace(
        object="chat.completion",
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=20,
            completion_tokens_details=SimpleNamespace(
                reasoning_tokens=12,
                audio_tokens=0,
            ),
        ),
    )
    assert get_reasoning_tokens(Provider.OPENAI, value) == 12


def test_openai_chat_no_reasoning_tokens_when_absent() -> None:
    value = {
        "object": "chat.completion",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "completion_tokens_details": {
                "audio_tokens": 0,
            },
        },
    }
    assert get_reasoning_tokens(Provider.OPENAI, value) is None


def test_openai_chat_no_reasoning_tokens_when_zero() -> None:
    value = {
        "object": "chat.completion",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    }
    # Zero is a valid value: model ran but didn't use any reasoning budget.
    assert get_reasoning_tokens(Provider.OPENAI, value) == 0


def test_openai_chat_none_when_no_usage() -> None:
    value = {"object": "chat.completion"}
    assert get_reasoning_tokens(Provider.OPENAI, value) is None


def test_openai_chat_none_when_no_details() -> None:
    value = {
        "object": "chat.completion",
        "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
    }
    assert get_reasoning_tokens(Provider.OPENAI, value) is None


# ── OpenAI Responses API ───────────────────────────────────────────────────────


def test_openai_responses_api_reasoning_tokens_dict() -> None:
    value = {
        "object": "response",
        "usage": {
            "input_tokens": 75,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 1186,
            "output_tokens_details": {"reasoning_tokens": 1024},
            "total_tokens": 1261,
        },
    }
    assert get_reasoning_tokens(Provider.OPENAI, value) == 1024


def test_openai_responses_api_reasoning_tokens_sdk_object() -> None:
    value = SimpleNamespace(
        object="response",
        usage=SimpleNamespace(
            input_tokens=75,
            output_tokens=1186,
            output_tokens_details=SimpleNamespace(reasoning_tokens=1024),
        ),
    )
    assert get_reasoning_tokens(Provider.OPENAI, value) == 1024


def test_openai_responses_api_none_when_no_output_details() -> None:
    value = {
        "object": "response",
        "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    }
    assert get_reasoning_tokens(Provider.OPENAI, value) is None


# ── Anthropic Messages ─────────────────────────────────────────────────────────


def test_anthropic_thinking_tokens_dict() -> None:
    value = {
        "type": "message",
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 17,
            "output_tokens": 700,
            "output_tokens_details": {"thinking_tokens": 550},
        },
    }
    assert get_reasoning_tokens(Provider.ANTHROPIC, value) == 550


def test_anthropic_thinking_tokens_sdk_object() -> None:
    value = SimpleNamespace(
        type="message",
        stop_reason="end_turn",
        usage=SimpleNamespace(
            input_tokens=17,
            output_tokens=700,
            output_tokens_details=SimpleNamespace(thinking_tokens=550),
        ),
    )
    assert get_reasoning_tokens(Provider.ANTHROPIC, value) == 550


def test_anthropic_none_when_thinking_not_enabled() -> None:
    value = {
        "type": "message",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 12, "output_tokens": 6},
    }
    assert get_reasoning_tokens(Provider.ANTHROPIC, value) is None


def test_anthropic_none_when_no_usage() -> None:
    value = {"type": "message", "stop_reason": "end_turn"}
    assert get_reasoning_tokens(Provider.ANTHROPIC, value) is None


# ── OpenRouter ─────────────────────────────────────────────────────────────────


def test_openrouter_reasoning_tokens_dict() -> None:
    value = {
        "object": "chat.completion",
        "model": "openai/o3",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
            "cost": 0.002,
            "completion_tokens_details": {
                "reasoning_tokens": 180,
            },
        },
    }
    assert get_reasoning_tokens(Provider.OPENROUTER, value) == 180


def test_openrouter_none_when_no_reasoning_tokens() -> None:
    value = {
        "object": "chat.completion",
        "model": "openai/gpt-4o",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "cost": 0.0001,
        },
    }
    assert get_reasoning_tokens(Provider.OPENROUTER, value) is None


# ── Edge cases ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("value", [None, "text", 42, {}, []])
def test_primitive_values_return_none(value: object) -> None:
    assert get_reasoning_tokens(Provider.OPENAI, value) is None
    assert get_reasoning_tokens(Provider.ANTHROPIC, value) is None
    assert get_reasoning_tokens(Provider.OPENROUTER, value) is None
