import pytest

from flexai.message import (
    AIMessage,
    Message,
    MessageContent,
    TextBlock,
    ToolCall,
    ToolResult,
    UserMessage,
)


def test_message_base():
    message = Message(role="test", content="Test content")
    assert message.role == "test"
    assert message.content == "Test content"


def test_user_message():
    user_message = UserMessage("User input")
    assert user_message.role == "user"
    assert user_message.content == "User input"


def test_ai_message():
    ai_message = AIMessage("AI response")
    assert ai_message.role == "assistant"
    assert ai_message.content == "AI response"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {"type": "TextBlock", "text": "Hello, world!"},
            TextBlock("Hello, world!"),
        ),
        (
            {
                "type": "ToolCall",
                "id": "123",
                "name": "example_tool",
                "input": {"param": "value"},
            },
            ToolCall(id="123", name="example_tool", input={"param": "value"}),
        ),
        (
            {
                "type": "ToolResult",
                "tool_call_id": "123",
                "result": "success",
                "execution_time": 1.23,
                "is_error": False,
            },
            ToolResult(
                tool_call_id="123",
                result="success",
                execution_time=1.23,
                is_error=False,
            ),
        ),
    ],
)
def test_message_content_load(data, expected):
    loaded_instance = MessageContent.load(data)
    assert loaded_instance == expected


@pytest.mark.parametrize(
    ("instance", "expected"),
    [
        (
            TextBlock("Hello, world!"),
            {"type": "TextBlock", "text": "Hello, world!", "cache": False},
        ),
        (
            ToolCall(id="123", name="example_tool", input={"param": "value"}),
            {
                "type": "ToolCall",
                "id": "123",
                "name": "example_tool",
                "input": {"param": "value"},
            },
        ),
        (
            ToolResult(
                tool_call_id="123",
                result="success",
                execution_time=1.23,
                is_error=False,
            ),
            {
                "type": "ToolResult",
                "tool_call_id": "123",
                "result": "success",
                "execution_time": 1.23,
                "is_error": False,
            },
        ),
    ],
)
def test_message_content_dump(instance, expected):
    dumped_data = instance.dump()
    assert dumped_data == expected


def test_invalid_message_content_type():
    data = {"type": "InvalidType", "some_field": "some_value"}
    with pytest.raises(ValueError, match="Unknown message content type: InvalidType"):
        MessageContent.load(data)
