from __future__ import annotations

import base64
import json
import os
import time
from collections.abc import AsyncGenerator, Sequence
from dataclasses import InitVar, dataclass, field
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from flexai.llm.client import Client
from flexai.message import (
    AIMessage,
    ImageBlock,
    Message,
    MessageContent,
    SystemMessage,
    TextBlock,
    ToolCall,
    ToolResult,
    Usage,
)
from flexai.tool import Tool


def get_tool_call(tool_use) -> ToolCall:
    """Get the tool call from a tool use block.

    Args:
        tool_use: The tool use block to get the call from.

    Returns:
        The tool call from the tool use block.
    """
    return ToolCall(
        id=tool_use.id,
        name=tool_use.function.name,
        input=json.loads(tool_use.function.arguments),
    )


BASE_MODEL = TypeVar("BASE_MODEL", bound=BaseModel)


@dataclass(frozen=True)
class OpenAIClient(Client):
    """Client for interacting with the OpenAI language model."""

    # The provider name.
    provider: str = "openai"

    # The API key to use for interacting with the model.
    api_key: InitVar[str] = field(default=os.environ.get("OPENAI_API_KEY", ""))

    # The base URL to use for interacting with the model.
    base_url: InitVar[str] = field(default="https://api.openai.com/v1")

    # The client to use for interacting with the model.
    client: AsyncOpenAI = field(default_factory=AsyncOpenAI)

    # The model to use for generating responses.
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def __post_init__(self, api_key, base_url, **kwargs):
        object.__setattr__(
            self,
            "client",
            AsyncOpenAI(api_key=api_key, base_url=base_url),
        )

    async def get_chat_response(
        self,
        messages: list[Message],
        *,
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        temperature: float = 1.0,
        force_tool: bool = True,
        disable_thinking: bool = False,
        allow_tool: bool = True,
        **kwargs,
    ) -> AIMessage:
        # Send the messages to the model and get the response.
        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            temperature=temperature,
            force_tool=force_tool,
            allow_tool=allow_tool,
            disable_thinking=disable_thinking,
            stream=False,
        )
        start = time.time()
        response = await self.client.chat.completions.create(**params)
        generation_time = time.time() - start

        # Parse out the tool uses from the response.
        message = response.choices[0].message
        tool_uses = [get_tool_call(message) for message in (message.tool_calls or [])]

        # Get the content to return.
        content_to_return = tool_uses or message.content
        return AIMessage(
            content=content_to_return,
            usage=Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                generation_time=generation_time,
            ),
        )

    async def stream_chat_response(
        self,
        messages: list[Message],
        *,
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        allow_tool: bool = True,
        disable_thinking: bool = False,
        temperature: float = 1.0,
        force_tool: bool = True,
        **kwargs,
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        stream = await self.client.chat.completions.create(
            **self._get_params(
                messages=messages,
                system=system,
                tools=tools,
                temperature=temperature,
                force_tool=force_tool,
                allow_tool=allow_tool,
                disable_thinking=disable_thinking,
                stream=True,
            )
        )
        current_tool_call: ToolCall | None = None
        current_text_block: TextBlock | None = None

        async for chunk in stream:
            if not isinstance(chunk.choices, list) or not chunk.choices:
                continue
            content = chunk.choices[0].delta.content

            if content:
                yield TextBlock(text=content)
                if not current_text_block:
                    current_text_block = TextBlock(text="")
                current_text_block = current_text_block.append(content)

            for tool_call in chunk.choices[0].delta.tool_calls or []:
                if not current_tool_call:
                    current_tool_call = ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        input="",
                    )
                    yield current_tool_call

                if tool_call.function.arguments:
                    yield TextBlock(text=tool_call.function.arguments)
                    current_tool_call = current_tool_call.append_input(
                        tool_call.function.arguments
                    )

        message_content = []

        if current_text_block:
            message_content.append(current_text_block)

        if current_tool_call:
            current_tool_call = current_tool_call.load_input()
            message_content.append(current_tool_call)

        yield AIMessage(content=message_content)

    def _get_params(
        self,
        messages: list[Message],
        system: str | SystemMessage,
        tools: list[Tool] | None,
        temperature: float,
        force_tool: bool = False,
        allow_tool: bool = False,
        disable_thinking: bool = False,
        stream: bool = False,
    ) -> dict:
        """Get the common params to send to the model.

        Args:
            messages: The messages to send to the model.
            system: The system message to send to the model.
            tools: The tools to send to the model.
            temperature: The temperature to use for the model.
            force_tool: unused
            allow_tool: unused
            disable_thinking: Whether to disable thinking.
            stream: Whether we are streaming.

        Returns:
            The common params to send to the model.
        """
        if isinstance(system, str):
            system = SystemMessage(system)
        kwargs = {
            "model": self.model,
            "messages": self._format_content([system, *messages]),
            "temperature": temperature,
        }

        # If tools are provided, force the model to use them (for now).
        if tools:
            kwargs["tools"] = [self.format_tool(tool) for tool in tools]
            kwargs["tool_choice"] = "required"
            kwargs["parallel_tool_calls"] = False

        if stream:
            kwargs["stream"] = True

        return kwargs

    async def get_structured_response(
        self,
        messages: list[Message],
        model: type[BASE_MODEL],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        temperature: float = 1.0,
    ) -> BASE_MODEL:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: unused.
            temperature: The temperature to use for the model.

        Returns:
            The structured response from the model.

        Raises:
            ValueError: If the response cannot be parsed.
        """
        # Send the messages to the model and get the response.
        response = await self.client.beta.chat.completions.parse(
            **self._get_params(
                messages=messages, system=system, temperature=temperature, tools=[]
            ),
            response_format=model,
        )
        result = response.choices[0].message.parsed
        if result is None:
            raise ValueError("Failed to parse the response.")
        return result

    @staticmethod
    def format_tool(tool: Tool) -> dict:
        """Convert the tool to a description.

        Args:
            tool: The tool to format.

        Returns:
            A dictionary describing the tool.
        """
        input_schema = {
            "type": "object",
            "properties": {},
        }
        for param_name, param_type in tool.params:
            input_schema["properties"][param_name] = {
                "type": param_type,
            }

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": input_schema,
            },
        }

    @classmethod
    def _format_message_content(
        cls,
        contents: Sequence[ImageBlock | TextBlock | ToolCall | ToolResult],
    ) -> list[dict[str, Any]]:
        return [
            {"type": "text", "text": content.text}
            if isinstance(content, TextBlock)
            else {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{content.mime_type};base64,{base64.b64encode(content.image).decode('utf-8')}",
                },
            }
            if isinstance(content, ImageBlock)
            else {
                "type": "function",
                "id": content.id,
                "function": {
                    "name": content.name,
                    "arguments": json.dumps(content.input),
                },
            }
            if isinstance(content, ToolCall)
            else {
                "role": "tool",
                "tool_call_id": content.tool_call_id,
                "content": json.dumps(content.result),
            }
            for content in contents
        ]

    @classmethod
    def _format_content(
        cls,
        value: Message | Sequence[Message],
        allow_tool: bool = True,
    ) -> list[dict[str, Any]]:
        """Format the message content for the Anthropic model.

        Args:
            value: The value to format.
            allow_tool: unused.

        Returns:
            The formatted message content.

        Raises:
            ValueError: If the message content type is unknown.
        """
        # Anthropic message format.
        if isinstance(value, Message):
            content = value.normalize().content
            if value.role == "user":
                # Tool calls use a "tool" role instead of "user".
                messages = []
                # OpenAI wants ToolResults, which currently are simply items in value.content, to be their own messages
                # Following is logic to extract those into their own messages, and then format the remainder of value.content as a single entity
                result_content = []
                for item in content:
                    if isinstance(item, ToolResult):
                        messages.extend(cls._format_message_content([item]))
                    else:
                        result_content.append(item)
                if result_content:
                    messages.append(
                        {
                            "role": value.role,
                            "content": cls._format_message_content(result_content),
                        }
                    )
                return messages

            tool_calls = []
            non_tool_calls = []
            for item in content:
                if isinstance(item, ToolCall):
                    tool_calls.append(item)
                else:
                    non_tool_calls.append(item)

            final_message: dict[str, Any] = {
                "role": value.role,
            }

            if non_tool_calls:
                final_message["content"] = cls._format_message_content(non_tool_calls)

            if tool_calls:
                final_message["tool_calls"] = cls._format_message_content(tool_calls)

            return [final_message]

        # If it's a list of messages, format them.
        if isinstance(value, Sequence) and not isinstance(value, str):
            return [
                cls._format_content(item, allow_tool=allow_tool)[0] for item in value
            ]

        raise ValueError(f"Unknown message content type: {type(value)}")

    @classmethod
    def load_content(
        cls, content: str | list[dict[str, Any]]
    ) -> str | list[MessageContent]:
        """Load the message content from the Anthropic model to dataclasses.

        Args:
            content: The content to load.

        Returns:
            The loaded message content

        Raises:
            TypeError: If content is not a sequence of dictionaries.
        """
        # If it's a string, return it.
        if isinstance(content, str):
            return content

        # If it's a list of dictionaries, parse them.
        if not isinstance(content, Sequence) or isinstance(content, str):
            raise TypeError("Content must be a sequence of dictionaries.")
        parsed_content: list[MessageContent] = []

        for entry in content:
            match entry.pop("type"):
                case "text":
                    parsed_content.append(TextBlock(**entry))
                case "function":
                    parsed_content.append(
                        ToolCall(
                            id=entry["id"],
                            name=entry["function"]["name"],
                            input=json.loads(entry["function"]["arguments"]),
                        )
                    )
                case "tool":
                    parsed_content.append(
                        ToolResult(
                            tool_call_id=entry.pop("tool_call_id"),
                            result=json.loads(entry.pop("content")),
                            **entry,
                        )
                    )

        return parsed_content
