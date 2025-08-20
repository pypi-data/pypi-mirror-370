# Reflex Agent

`reflex-agent` is a flexible framework to create AI agents with modular capabilities and tool integrations.

## Installation

```bash
pip install reflex-agent
```

You can also install `anthropic` or `openai` clients with:

```bash
pip install reflex-agent[anthropic]
pip install reflex-agent[openai]
pip install reflex-agent[anthropic,openai] # for both
```

## Features

- **Zero Dependencies**: The core install has no extra dependencies - bring your own LLM.
- **Modular Capabilities**: The base agent loop is simple and can be modified through capabilities to add features like memory and chain of thought.
- **Simple Tool Use**: Use any Python function as a tool that the agent can call.
- **Client-Server Architecture**: Designed for easy use in a client-server architecture - allowing for stepping through the agent loop.
- **Async by Default**: All functions are async by default.

## Usage

### Agents

Agents are entities that you can chat with. To create a basic agent, by specifiying an LLM and a system prompt.

We currently have built-in support for OpenAI and Anthropic models.

```python
from flexai import Agent
from flexai.llm.openai import OpenAIClient
from flexai.llm.anthropic import AnthropicClient


openai_agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are a helpful assistant.",
)

anthropic_client = Agent(
    llm=AnthropicClient(model="claude-3-5-sonnet-20240620"),
    prompt="You are a helpful assistant.",
)
```

To interact with an agent, pass in a list of messages. There are two ways to interact with an agent - `stream` and `step`.

Streaming allows the agent to use multiple messages (such as inner tool uses) before returning a final response.

```python
import asyncio
from flexai import Agent, UserMessage
from flexai.llm.openai import OpenAIClient

agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are an expert mathematician.",
)

async def get_agent_response(messages):
    async for response in agent.stream(messages):
        print(response)


asyncio.run(get_agent_response([UserMessage("What's 2 + 2?")]))
```

Stepping allows you to step through the agent loop, allowing you to see the agent's internal state at each step.

```python
import asyncio
from flexai import Agent, UserMessage
from flexai.llm.openai import OpenAIClient

agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are an expert mathematician.",
)

async def get_agent_response(messages):
    response = await agent.step(messages)
    print(response)

asyncio.run(get_agent_response([UserMessage("What's 2 + 2?")]))
```

### Memory

Agents are stateless by default - all state management is done on the user end.
You can save the agent's output messages to have an extended conversation.

```python
import asyncio
from flexai import Agent, UserMessage
from flexai.llm.openai import OpenAIClient

agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are an expert mathematician.",
)

async def get_agent_response(messages):
    response = await agent.step(messages):
    print(response)
    messages.append(response)
    messages.append(UserMessage("Tell me some key themes from your story."))
    response = await agent.step(messages):
    print(response)

asyncio.run(get_agent_response([UserMessage("Tell me a random story")]))
```

### Tools

Tools are Python functions that the agent can call. The function's signature and docstring are used to determine when and how the tool is called.

```python
import asyncio
from flexai import Agent, UserMessage
from flexai.llm.openai import OpenAIClient

def read_file(file_path: str) -> str:
    """Read a file and get the contents."""
    with open(file_path, "r") as file:
        return file.read()

def write_file(file_path: str, contents: str) -> None:
    """Write contents to a file."""
    with open(file_path, "w") as file:
        file.write(contents)

agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are an expert mathematician.",
    tools=[
        read_file,
        write_file,
    ]
)


async def get_agent_response(messages):
    # Stream allows the agent to use multiple tool uses in one go.
    async for message in agent.stream(messages):
        print(message)

asyncio.run(get_agent_response([UserMessage("Read the README.md file and create a copy at README2.md with a high level summary.")]))
```

### Capabilities

Capabilities allow you to modify the core agent loop and change the behavior of the agent.

You can plug in to the agent loop to modify messages, responses, and system messages. For example, the `TruncateMessages` capability truncates the input messages to the LLM to a maximum.

```python
@dataclass
class TruncateMessages(Capability):
    """Truncate the input messages to the LLM to a maximum number."""

    # The maximum number of messages to keep.
    max_messages: int

    async def modify_messages(self, messages: list[Message]) -> list[Message]:
        return messages[-self.max_messages :]
```

This capability is built-in to the framework to use:

```python
import asyncio
from flexai import Agent, UserMessage
from flexai.llm.openai import OpenAIClient
from flexai.capabilities import TruncateMessages

agent = Agent(
    llm=OpenAIClient(model="gpt-4o-mini"),
    prompt="You are an expert mathematician.",
    capabilities=[TruncateMessages(max_messages=3)],
)
```
