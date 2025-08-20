import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from flexai.agent import Agent, send_message
from flexai.message import (
    AIMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolResult,
    UserMessage,
)


@pytest.fixture
def mock_llm():
    return AsyncMock()


@pytest.fixture
def mock_capability():
    return AsyncMock()


def test_agent_initialization():
    agent = Agent()
    assert len(agent.capabilities) == 0

    def custom_tool(x):
        return x

    custom_capability = Mock()
    agent_with_custom = Agent(tools=[custom_tool], capabilities=[custom_capability])
    assert custom_tool.__name__ in agent_with_custom.toolbox
    assert len(agent_with_custom.capabilities) == 1


@pytest.mark.asyncio
async def test_modify_messages(mock_capability):
    correct_argument_found = False

    async def yielder(*args):
        if args[0] == messages:
            nonlocal correct_argument_found
            correct_argument_found = True
        yield messages

    mock_capability.modify_messages = yielder
    agent = Agent(capabilities=[mock_capability])
    messages = [
        UserMessage("Test 1"),
        AIMessage("Response 1"),
        UserMessage("Test 2"),
        UserMessage("Test 3"),
    ]
    async for message in agent.modify_messages(messages):
        result = message

    assert correct_argument_found
    assert result == messages


@pytest.mark.asyncio
async def test_get_system_message(mock_capability):
    agent = Agent(prompt="Original prompt", capabilities=[mock_capability])
    correct_argument_found = False

    async def yielder(*args):
        if args[0] == SystemMessage("Original prompt"):
            nonlocal correct_argument_found
            correct_argument_found = True
        yield SystemMessage("Modified prompt")

    mock_capability.modify_prompt = yielder

    async for message in agent.get_system_message():
        result = message

    assert correct_argument_found
    assert result == SystemMessage("Modified prompt")


@pytest.mark.asyncio
async def test_invoke_tool():
    def sync_tool(x):
        return x * 2

    async def async_tool(x):
        return x * 3

    agent = Agent(tools=[sync_tool, async_tool])

    async for message in agent.invoke_tool(
        ToolCall(id="1", name="sync_tool", input={"x": 2}), []
    ):
        sync_result = message
    assert sync_result.result == 4
    assert not sync_result.is_error

    async for message in agent.invoke_tool(
        ToolCall(id="1", name="async_tool", input={"x": 2}), []
    ):
        async_result = message
    assert async_result.result == 6
    assert not async_result.is_error


@pytest.mark.asyncio
async def test_step(mock_llm):
    agent = Agent(llm=mock_llm)
    messages: list[Message] = [UserMessage("Test")]
    mock_llm.get_chat_response.return_value = AIMessage("Response")

    result = None
    async for response in agent.run(messages):
        result = response
    assert result is not None

    mock_llm.get_chat_response.assert_called_once()
    assert isinstance(result, AIMessage)
    assert result.content == "Response"


@pytest.mark.asyncio
async def test_multiple_tool_execution():
    def tool1(x):
        return x * 2

    def tool2(y):
        return y + 10

    agent = Agent(tools=[tool1, tool2])
    response = AIMessage(
        [
            ToolCall(id="1", name="tool1", input={"x": 5}),
            ToolCall(id="2", name="tool2", input={"y": 7}),
        ]
    )

    results = []
    for tool_call in response.content:
        async for message in agent.invoke_tool(tool_call, []):
            final_response = message
        results.append(final_response)
    assert len(results) == 2
    assert results[0].result == 10
    assert results[1].result == 17


@pytest.mark.asyncio
async def test_error_handling_in_tools():
    def faulty_tool():
        raise ValueError("Tool error")

    agent = Agent(tools=[faulty_tool])
    tool_call = ToolCall(id="1", name="faulty_tool", input={})
    async for message in agent.invoke_tool(tool_call, []):
        result = message

    assert result.is_error
    assert "Tool error" in result.result


@pytest.mark.asyncio
async def test_capability_chaining():
    mock_capability1 = AsyncMock()
    mock_capability2 = AsyncMock()

    generator_one_calls = []
    gen_one_return = "Generator 1 Return"

    async def generator1(*args):
        nonlocal generator_one_calls
        generator_one_calls.append(args)
        yield gen_one_return

    generator_two_calls = []

    async def generator2(*args):
        nonlocal generator_two_calls
        generator_two_calls.append(args)
        yield ""

    mock_capability1.modify_messages = generator1
    mock_capability2.modify_messages = generator2

    agent = Agent(capabilities=[mock_capability1, mock_capability2])
    messages: list[Message] = [UserMessage("test")]

    async for _ in agent.modify_messages(messages):
        pass

    assert len(generator_one_calls) == 1
    assert len(generator_two_calls) == 1
    assert generator_two_calls[0][0] == gen_one_return


@pytest.mark.asyncio
async def test_agent_stream():
    class TestAgent(Agent):
        async def invoke_tool(self, tool_call, messages):
            yield ToolResult(
                tool_call_id=tool_call.id,
                result="Tool result",
                execution_time=0.1,
                is_error=False,
            )

    def mock_tool(x):
        return x

    mock_llm = AsyncMock()
    agent = TestAgent(llm=mock_llm, tools=[mock_tool, send_message])
    messages: list[Message] = [UserMessage("Initial message")]

    # Mock the responses from the LLM
    mock_llm.get_chat_response.side_effect = [
        AIMessage([ToolCall(id="1", name="mock_tool", input={"x": "x"})]),
        AIMessage(
            [ToolCall(id="2", name="send_message", input={"message": "Finished"})]
        ),
    ]

    out_messages = messages.copy()
    async for message in agent.run(messages):
        if isinstance(message, Message):
            print(message)
            out_messages.append(message)

    assert len(out_messages) == 4  # Initial + Tool call + Tool result + Final response
    assert isinstance(out_messages[0], UserMessage)
    assert isinstance(out_messages[1], AIMessage)
    assert isinstance(out_messages[2], UserMessage)
    assert isinstance(out_messages[3], AIMessage)
    assert out_messages[1].content[0].input["x"] == "x"
    assert out_messages[2].content == [
        ToolResult(
            tool_call_id="1", result="Tool result", execution_time=0.1, is_error=False
        )
    ]
    assert out_messages[3].content == "Finished"


@pytest.mark.asyncio
async def test_rate_limiting_simulation():
    async def slow_tool():
        await asyncio.sleep(0.1)
        return "Slow result"

    agent = Agent(tools=[slow_tool])
    tool_call = ToolCall(id="1", name="slow_tool", input={})

    async for message in agent.invoke_tool(tool_call, []):
        result = message

    assert result.execution_time >= 0.1
    assert result.result == "Slow result"
