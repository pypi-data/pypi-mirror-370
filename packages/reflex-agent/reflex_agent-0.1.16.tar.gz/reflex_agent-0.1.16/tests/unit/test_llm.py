from collections.abc import Sequence
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from flexai.llm.anthropic import AnthropicClient
from flexai.message import AIMessage, SystemMessage, TextBlock, UserMessage
from flexai.tool import Tool


# Test AnthropicClient class
@pytest.fixture
def mock_anthropic_client():
    with patch("flexai.llm.anthropic.AsyncAnthropic") as mock:
        yield mock.return_value


@pytest.mark.asyncio
async def test_anthropic_get_chat_response(mock_anthropic_client):
    client = AnthropicClient(client=mock_anthropic_client)
    mock_anthropic_client.messages.create = AsyncMock(
        return_value=Mock(
            content=[Mock(text="AI response")],
        )
    )
    response = await client.get_chat_response([UserMessage("Hello")])
    assert isinstance(response, AIMessage)
    assert response.content == "AI response"


# @pytest.mark.asyncio
# async def test_anthropic_stream_chat_response(mock_anthropic_client):
#     client = AnthropicClient(client=mock_anthropic_client)

#     async def mock_text_stream():
#         messages = ["Hello", " world"]
#         for message in messages:
#             yield message

#     mock_anthropic_client.messages.stream.return_value.__aenter__.return_value.text_stream = mock_text_stream()
#     responses = [
#         resp async for resp in client.stream_chat_response([UserMessage(content="Hi")])
#     ]
#     assert len(responses) == 2
#     assert all(isinstance(resp, AIMessage) for resp in responses)
#     assert [resp.content for resp in responses] == ["Hello", " world"]


def test_anthropic_to_llm_messages():
    messages = [UserMessage("Hello"), AIMessage("Hi there")]
    llm_messages = AnthropicClient._format_content(messages)
    assert llm_messages == [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "Hi there"}]},
    ]


@pytest.mark.asyncio
async def test_anthropic_get_structured_response(mock_anthropic_client):
    class TestModel(BaseModel):
        name: str
        age: int

    client = AnthropicClient(client=mock_anthropic_client)
    mock_anthropic_client.messages.create = AsyncMock(
        return_value=Mock(
            content=[Mock(text='{"name": "John", "age": 30}')],
        )
    )

    result = await client.get_structured_response([UserMessage("Get info")], TestModel)
    assert isinstance(result, TestModel)
    assert result.name == "John"
    assert result.age == 30


def test_anthropic_add_cache_control():
    client = AnthropicClient(cache_messages=True)
    params = {
        "system": AnthropicClient._format_message_content(
            SystemMessage(
                [TextBlock("System message 1"), TextBlock("System message 2")]
            )
            .normalize()
            .content
        ),
        "tools": [{"name": "tool1"}, {"name": "tool2"}],
        "messages": [
            {"content": "Message 1", "role": "user"},
            {"content": "Message 2", "role": "assistant"},
            {"content": "Message 3", "role": "user"},
            {"content": "Message 4", "role": "assistant"},
            {"content": "Message 5", "role": "user"},
        ],
    }
    result = client._add_cache_control(params)

    # Check the system message is cached.
    assert isinstance(result["system"], Sequence)
    assert not isinstance(result["system"], str)
    assert len(result["system"]) == 2
    assert result["system"][0]["type"] == "text"
    assert result["system"][0]["text"] == "System message 1"
    assert result["system"][0]["cache_control"]["type"] == "ephemeral"
    assert "cache_control" not in result["system"][1]

    # Check only the last tool is cached.
    assert isinstance(result["tools"], Sequence)
    assert not isinstance(result["tools"], str)
    assert len(result["tools"]) == 2
    assert result["tools"][0]["name"] == "tool1"
    assert result["tools"][1]["name"] == "tool2"
    assert "cache_control" not in result["tools"][0]
    assert result["tools"][1]["cache_control"]["type"] == "ephemeral"

    # Check that the last two user messages are cached.
    assert isinstance(result["messages"], Sequence)
    assert not isinstance(result["messages"], str)
    assert len(result["messages"]) == 5
    assert isinstance(result["messages"][0]["content"], str)
    assert isinstance(result["messages"][1]["content"], str)
    assert isinstance(result["messages"][3]["content"], str)

    assert isinstance(result["messages"][2]["content"], Sequence)
    assert not isinstance(result["messages"][2]["content"], str)
    assert result["messages"][2]["content"][0]["cache_control"]
    assert isinstance(result["messages"][4]["content"], Sequence)
    assert not isinstance(result["messages"][4]["content"], str)
    assert result["messages"][4]["content"][0]["cache_control"]


def test_anthropic_tool_format():
    def complex_function(a: int, b: str, c: list) -> dict:
        """A more complex function for testing."""
        return {}

    tool = Tool.from_function(complex_function)
    description = AnthropicClient.format_tool(tool)

    assert description["name"] == "complex_function"
    assert description["description"] == "A more complex function for testing."
    assert description["input_schema"] == {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "string"},
            "c": {"type": "array"},
        },
    }
