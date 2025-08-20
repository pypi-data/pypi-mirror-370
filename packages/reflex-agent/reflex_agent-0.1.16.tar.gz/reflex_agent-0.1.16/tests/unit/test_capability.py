import pytest

from flexai.capabilities import LimitToolUse
from flexai.capability import Capability
from flexai.message import AIMessage, Message, TextBlock, ToolCall, UserMessage


class ConcreteCapability(Capability):
    async def modify_prompt(self, prompt: str) -> str:
        return prompt + " modified"

    async def modify_messages(self, messages: list[Message]) -> list[Message]:
        return [*messages, UserMessage("Additional message")]

    async def modify_response(
        self, messages: list[Message], response: AIMessage
    ) -> AIMessage:
        response.content += " (modified)"
        return response


@pytest.mark.asyncio
async def test_concrete_capability():
    cap = ConcreteCapability()

    # Test modify_prompt
    prompt = "Original prompt"
    modified_prompt = await cap.modify_prompt(prompt)
    assert modified_prompt == "Original prompt modified"

    # Test modify_messages
    messages = [UserMessage("Hello")]
    modified_messages = await cap.modify_messages(messages)
    assert len(modified_messages) == 2
    assert isinstance(modified_messages[1], UserMessage)

    # Test modify_response
    response = AIMessage("AI response")
    modified_response = await cap.modify_response(messages, response)
    assert modified_response.content == "AI response (modified)"


@pytest.mark.asyncio
async def test_default_capability_behavior():
    cap = Capability()

    prompt = "Test prompt"
    async for message in cap.modify_prompt(prompt):
        result = message
    assert result == prompt

    messages = [UserMessage("Test")]
    async for message in cap.modify_messages(messages):
        result = message
    assert result == messages

    response = AIMessage("Test response")
    async for message in cap.modify_response(messages, response):
        result = message
    assert result == response


@pytest.mark.asyncio
async def test_limit_tool_use_capability():
    messages = [
        UserMessage([ToolCall(id="1", name="tool", input="input")]),
        AIMessage("this is a message"),
    ]
    response = UserMessage([ToolCall(id="2", name="tool", input="input")])
    cap1 = LimitToolUse(max_tool_uses=1)
    async for _ in cap1.modify_response(messages, response):
        pass
    assert isinstance(response.content[0], TextBlock)
    assert response.content[0].text == "Exceeded tool usage limit: 1"

    response = UserMessage([ToolCall(id="2", name="tool", input="input")])
    cap2 = LimitToolUse(max_tool_uses=2)
    async for _ in cap2.modify_response(messages, response):
        pass
    assert "message" not in response.content[0].input
