"""Identify which LLM provider produced a response object."""

from types import SimpleNamespace

import pytest

from agenttrace.provider import Provider, identify_provider


def test_openai_chat_completion_dict() -> None:
    value = {
        "id": "chatcmpl-abc",
        "object": "chat.completion",
        "created": 1710000000,
        "model": "gpt-4.1",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "Hello"},
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
    }
    assert identify_provider(value) is Provider.OPENAI


def test_openai_chat_completion_chunk_dict() -> None:
    value = {
        "id": "chatcmpl-abc",
        "object": "chat.completion.chunk",
        "created": 1710000000,
        "model": "gpt-4.1",
        "choices": [
            {
                "index": 0,
                "delta": {"content": "He"},
                "finish_reason": None,
            }
        ],
    }
    assert identify_provider(value) is Provider.OPENAI


def test_openai_responses_api_dict() -> None:
    value = {
        "id": "resp_abc",
        "object": "response",
        "status": "completed",
        "model": "gpt-4.1",
        "output": [{"type": "message", "role": "assistant", "content": []}],
    }
    assert identify_provider(value) is Provider.OPENAI


def test_openai_sdk_like_object() -> None:
    value = SimpleNamespace(
        id="chatcmpl-abc",
        object="chat.completion",
        model="gpt-4.1",
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(role="assistant", content="Hello"),
            )
        ],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2),
    )
    assert identify_provider(value) is Provider.OPENAI


def test_openai_module_path_without_openrouter_extras() -> None:
    class ChatCompletion:
        def __init__(self) -> None:
            self.id = "chatcmpl-abc"
            self.object = "chat.completion"
            self.model = "gpt-4.1"
            self.choices: list[object] = []

    ChatCompletion.__module__ = "openai.types.chat.chat_completion"
    assert identify_provider(ChatCompletion()) is Provider.OPENAI


def test_anthropic_message_dict() -> None:
    value = {
        "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Hello!"}],
        "model": "claude-opus-4",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 12, "output_tokens": 6},
    }
    assert identify_provider(value) is Provider.ANTHROPIC


def test_anthropic_sdk_module_path() -> None:
    class Message:
        def __init__(self) -> None:
            self.type = "message"
            self.role = "assistant"
            self.stop_reason = "end_turn"
            self.content = [{"type": "text", "text": "Hello"}]
            self.usage = SimpleNamespace(input_tokens=12, output_tokens=6)

    Message.__module__ = "anthropic.types.message"
    assert identify_provider(Message()) is Provider.ANTHROPIC


def test_openrouter_native_finish_reason() -> None:
    value = {
        "id": "gen-123",
        "object": "chat.completion",
        "created": 1710000000,
        "model": "openai/gpt-4o",
        "choices": [
            {
                "finish_reason": "stop",
                "native_finish_reason": "stop",
                "message": {"role": "assistant", "content": "Hello there!"},
            }
        ],
        "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
    }
    assert identify_provider(value) is Provider.OPENROUTER


def test_openrouter_usage_cost() -> None:
    value = {
        "id": "chatcmpl-looks-openai",
        "object": "chat.completion",
        "model": "gpt-4o",
        "choices": [{"finish_reason": "stop", "message": {"content": "Hi"}}],
        "usage": {
            "prompt_tokens": 8,
            "completion_tokens": 4,
            "total_tokens": 12,
            "cost": 0.00014,
            "cost_details": {"upstream_inference_cost": 0.0001},
        },
    }
    assert identify_provider(value) is Provider.OPENROUTER


def test_openrouter_vendor_slash_model() -> None:
    value = {
        "id": "unused",
        "object": "chat.completion",
        "model": "anthropic/claude-sonnet-4.6",
        "choices": [{"finish_reason": "stop", "message": {"content": "Hi"}}],
    }
    assert identify_provider(value) is Provider.OPENROUTER


def test_openrouter_module_path() -> None:
    class Completion:
        def __init__(self) -> None:
            self.object = "chat.completion"
            self.model = "openai/gpt-4o"

    Completion.__module__ = "openrouter.client"
    assert identify_provider(Completion()) is Provider.OPENROUTER


def test_openrouter_via_openai_sdk_still_detected_from_extras() -> None:
    class ChatCompletion:
        def __init__(self) -> None:
            self.id = "gen-aaaaaaaa"
            self.object = "chat.completion"
            self.model = "openai/gpt-4o"
            self.choices = [
                SimpleNamespace(finish_reason="stop", native_finish_reason="stop")
            ]

    ChatCompletion.__module__ = "openai.types.chat.chat_completion"
    assert identify_provider(ChatCompletion()) is Provider.OPENROUTER


@pytest.mark.parametrize(
    "value",
    [
        None,
        "chat.completion",
        42,
        {},
        {"object": "list"},
        {"type": "error", "message": "nope"},
        {"choices": []},
    ],
)
def test_unknown_values_are_none(value: object) -> None:
    assert identify_provider(value) is None


def test_anthropic_is_not_openai_chat() -> None:
    value = {
        "type": "message",
        "stop_reason": "end_turn",
        "content": [],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    assert identify_provider(value) is Provider.ANTHROPIC
    assert identify_provider(value) is not Provider.OPENAI
