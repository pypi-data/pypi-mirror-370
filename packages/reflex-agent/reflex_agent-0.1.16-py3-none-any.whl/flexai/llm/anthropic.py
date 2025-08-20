from __future__ import annotations

import base64
import json
import os
import time
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass, field
from typing import Any

from anthropic import AsyncAnthropic, AsyncAnthropicBedrock
from anthropic.types import ToolUseBlock
from pydantic import BaseModel

from flexai.llm.client import Client
from flexai.message import (
    AIMessage,
    DataBlock,
    GroundingBlock,
    ImageBlock,
    Message,
    MessageContent,
    SystemMessage,
    TextBlock,
    ToolCall,
    ToolResult,
    URLContextBlock,
    Usage,
    UserMessage,
)
from flexai.tool import Tool


def get_tool_call(tool_use: ToolUseBlock) -> ToolCall:
    """Get the tool call from a tool use block.

    Args:
        tool_use: The tool use block to get the call from.

    Returns:
        The tool call from the tool use block.
    """
    return ToolCall(
        id=tool_use.id,
        name=tool_use.name,
        input=tool_use.input,
    )


@dataclass(frozen=True)
class AnthropicClient(Client):
    """Client for interacting with the Anthropic language model."""

    # The provider name.
    provider: str = "anthropic"

    # The client to use for interacting with the model.
    client: AsyncAnthropic | AsyncAnthropicBedrock = field(
        default_factory=lambda: AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    )

    # The model to use for generating responses.
    model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

    # The maximum number of tokens to generate in a response.
    max_tokens: int = 8192

    # Whether to cache messages or not.
    cache_messages: bool = False

    # Extra headers to include in the request.
    extra_headers: dict = field(default_factory=dict)

    async def get_chat_response(
        self,
        messages: list[Message],
        *,
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        disable_thinking: bool = False,
        temperature: float = 1.0,
        force_tool: bool = True,
        allow_tool: bool = True,
        **kwargs,
    ) -> AIMessage:
        if not messages:
            raise ValueError(
                "Anthropic requires at least one messages to process your request."
            )

        # If we were sent a model, call instead get_structured_response.
        if "model" in kwargs:
            # Extract the model parameter and remove it from kwargs to avoid recursion
            model_class = kwargs.pop("model")
            (
                structured_response,
                usage_info,
            ) = await self._get_structured_response_with_usage(
                messages,
                model_class,
                system=system,
                tools=tools,
                **kwargs,
            )
            # Convert structured response to AIMessage with the model as content
            return AIMessage(
                content=str(structured_response),
                usage=usage_info,
            )

        # Send the messages to the model and get the response.
        start = time.time()
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
        agent = kwargs.get("agent")
        if agent:
            params.update(agent.config.extra_llm_params)
        response = await self.client.messages.create(**params)
        generation_time = time.time() - start

        # Parse out the tool uses from the response.
        tool_uses = [
            get_tool_call(message)
            for message in response.content
            if isinstance(message, ToolUseBlock)
        ]

        # Get the content to return.
        content_to_return = tool_uses or "\n".join(
            [message.text for message in response.content]
        )
        return AIMessage(
            content=content_to_return,
            usage=Usage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cache_read_tokens=response.usage.cache_read_input_tokens,
                cache_write_tokens=response.usage.cache_creation_input_tokens,
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
        if not messages:
            raise ValueError(
                "Anthropic requires at least one messages to process your request."
            )

        # Initialize variables to store the tool information.
        tool_call: ToolCall | None = None
        text_block: TextBlock | None = None

        # Track the usage.
        usage = Usage()

        # Iterate over the response stream.
        start = time.time()
        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            temperature=temperature,
            force_tool=force_tool,
            allow_tool=allow_tool,
            disable_thinking=disable_thinking,
            stream=True,
        )
        agent = kwargs.get("agent")
        if agent:
            params.update(agent.config.extra_llm_params)
        response_stream = await self.client.messages.create(**params)
        async for chunk in response_stream:
            # Add the usage.
            # This is the starting chunk.
            if hasattr(chunk, "message"):
                usage.input_tokens += chunk.message.usage.input_tokens
                usage.output_tokens += chunk.message.usage.output_tokens
                usage.cache_read_tokens += chunk.message.usage.cache_read_input_tokens
                usage.cache_write_tokens += (
                    chunk.message.usage.cache_creation_input_tokens
                )
            # This is the continuation chunk.
            if hasattr(chunk, "usage"):
                usage.output_tokens += chunk.usage.output_tokens

            # Content start blocks.
            if chunk.type == "content_block_start":
                content = chunk.content_block
                # This is a text block.
                if content.type == "text":
                    text_block = TextBlock(content.text)
                    yield text_block

                # This is a tool block.
                else:
                    # Yield the initial tool call with no input.
                    tool_call = ToolCall(id=content.id, name=content.name, input="")
                    yield tool_call

            # A continuation of the content block.
            elif chunk.type == "content_block_delta":
                delta = chunk.delta
                # This is a text delta.
                if delta.type == "text_delta":
                    if text_block is None:
                        raise ValueError("Text block is None.")
                    text_block = text_block.append(delta.text)
                    yield TextBlock(delta.text)

                # This is a tool delta.
                else:
                    if tool_call is None:
                        raise ValueError("Tool call is None.")
                    # Add to the input buffer and yield the partial JSON.
                    tool_call = tool_call.append_input(delta.partial_json)
                    yield TextBlock(delta.partial_json)

            # The end of the content block.
            elif chunk.type == "message_stop":
                # Parse the tool from the buffer and convert it to a tool call.
                usage.generation_time = time.time() - start

                # Send the final text message.
                content = None
                if text_block:
                    content = text_block
                    text_block = None
                elif tool_call:
                    # Send the tool call message.
                    content = tool_call.load_input()
                    tool_call = None

                # Send the final message.
                if content:
                    yield AIMessage(
                        content=[content],
                        usage=usage,
                    )

    def _add_cache_control(self, params: dict) -> dict:
        """Add cache control to the params.

        Args:
            params: The params to add cache control to.

        Returns:
            The params with cache control added.
        """
        cache_control = {
            "cache_control": {
                "type": "ephemeral",
            }
        }

        # Cache tool definitions.
        if "tools" in params and len(params["tools"]) > 0:
            params["tools"][-1].update(**cache_control)

        if not self.cache_messages:
            return params

        # Cache the system message.
        if params.get("system"):
            params["system"][0].update(**cache_control)

        # Find the most recent user message
        user_idxs = [
            idx
            for idx, message in enumerate(params["messages"])
            if message["role"] == "user"
        ]
        for idx in user_idxs[-2:]:
            message = params["messages"][idx]
            if isinstance(message["content"], str):
                message["content"] = [{"type": "text", "text": message["content"]}]
            message["content"][-1].update(**cache_control)

        return params

    def _get_params(
        self,
        messages: list[Message],
        system: str | SystemMessage,
        tools: list[Tool] | None,
        temperature: float,
        force_tool: bool,
        allow_tool: bool,
        stream: bool,
        disable_thinking: bool,
    ) -> dict:
        """Get the common params to send to the model.

        Args:
            messages: The messages to send to the model.
            system: The system message to send to the model.
            tools: The tools to send to the model.
            temperature: The temperature to use for the model.
            force_tool: Whether to force the model to use the tools.
            allow_tool: Whether to allow tool calls in the content.
            stream: Whether to stream the response.
            disable_thinking: Whether to disable thinking.

        Returns:
            The common params to send to the model.
        """
        # Convert the system prompt to a list of message content.
        if isinstance(system, str):
            system = SystemMessage([TextBlock(system)])

        kwargs = {
            "max_tokens": self.max_tokens,
            "messages": self._format_content(messages, allow_tool),
            "model": self.model,
            "temperature": temperature,
            "extra_headers": self.extra_headers,
            **({"thinking": {"type": "disabled"}} if disable_thinking else {}),
        }

        # Only add system message if it's not empty
        system_content = self._format_message_content(
            system.normalize().content, allow_tool
        )
        if system_content and any(
            content.get("text", "").strip() for content in system_content
        ):
            kwargs["system"] = system_content

        # If tools are provided, force the model to use them (for now).
        if tools:
            kwargs["tools"] = sorted(
                [self.format_tool(tool) for tool in tools], key=lambda x: x["name"]
            )
            if force_tool:
                kwargs["tool_choice"] = {"type": "any"}
        else:
            kwargs["tools"] = []

        if stream:
            kwargs["stream"] = True

        # Add cache control to the params.
        return self._add_cache_control(kwargs)

    async def _get_structured_response_with_usage(
        self,
        messages: list[Message],
        model: type[BaseModel],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> tuple[BaseModel, Usage]:
        """Get the structured response from the chat model with usage tracking.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: Tools to use in the response.
            temperature: The temperature to use for the model.
            kwargs: Additional keyword arguments to pass to the model.

        Returns:
            A tuple of (structured response, usage information).

        Raises:
            TypeError: If the response is not a string.
        """
        schema = model.model_json_schema()
        system = f"""{system}
Return your answer according to the 'properties' of the following schema:
{schema}
Return only the JSON object with the properties filled in.
Do not include anything in your response other than the JSON object.
Do not begin your response with ```json or end it with ```.
"""
        response = await self.get_chat_response(
            messages,
            system=system,
            tools=tools,
            temperature=temperature,
            force_tool=False,
            **kwargs,
        )
        content = response.content
        try:
            if not isinstance(content, str):
                raise TypeError("The response is not a string.")
            return model.model_validate_json(content), response.usage
        except Exception as e:
            # Try again, printing the exception.
            messages = [
                *messages,
                response,
                UserMessage(
                    f"There was an error while parsing. Make sure to only include the JSON. Error: {e}"
                ),
            ]
            return await self._get_structured_response_with_usage(
                messages,
                model=model,
                system=system,
                tools=tools,
                temperature=temperature,
                **kwargs,
            )

    async def get_structured_response(
        self,
        messages: list[Message],
        model: type[BaseModel],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        temperature: float = 1.0,
        **kwargs,
    ) -> BaseModel:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: Tools to use in the response.
            temperature: The temperature to use for the model.
            kwargs: Additional keyword arguments to pass to the model.

        Returns:
            The structured response from the model.
        """
        structured_response, _ = await self._get_structured_response_with_usage(
            messages,
            model,
            system=system,
            tools=tools,
            temperature=temperature,
            **kwargs,
        )
        return structured_response

    @staticmethod
    def format_tool(tool: Tool) -> dict:
        """Convert the tool to a description.

        Args:
            tool: The tool to format.

        Returns:
            A dictionary describing the tool.
        """
        if tool.fn.__name__.startswith("str_replace_editor"):
            return {
                "type": "text_editor_20250124",
                "name": "str_replace_editor",
            }

        input_schema = {
            "type": "object",
            "properties": {},
        }
        for param_name, param_type in tool.params:
            input_schema["properties"][param_name] = {
                "type": param_type,
            }

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": input_schema,
        }

    @classmethod
    def _format_message_content(
        cls,
        contents: Sequence[
            ImageBlock
            | TextBlock
            | ToolCall
            | ToolResult
            | URLContextBlock
            | GroundingBlock
        ],
        allow_tool: bool = True,
    ) -> list[dict[str, Any]]:
        # Filter out URLContextBlock and GroundingBlock since Anthropic doesn't support them
        filtered_contents = [
            content
            for content in contents
            if not isinstance(content, (URLContextBlock, GroundingBlock))
        ]

        return [
            (
                {
                    "type": "text",
                    "text": content.text,
                }
                if not content.cache
                else {
                    "type": "text",
                    "text": content.text,
                    "cache_control": {"type": "ephemeral"},
                }
            )
            if isinstance(content, TextBlock)
            else {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": content.mime_type,
                    "data": base64.b64encode(content.image).decode("utf-8"),
                },
            }
            if isinstance(content, ImageBlock)
            else (
                {
                    "type": "tool_use",
                    "id": content.id,
                    "name": content.name,
                    "input": content.input,
                }
                if allow_tool
                else {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "tool_use": {
                                "id": content.id,
                                "name": content.name,
                                "input": content.input,
                            }
                        }
                    ),
                }
            )
            if isinstance(content, ToolCall)
            else (
                {
                    "type": "tool_result",
                    "tool_use_id": content.tool_call_id,
                    "content": str(content.result),
                    "is_error": content.is_error,
                }
                if allow_tool
                else {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "tool_result": {
                                "tool_call_id": content.tool_call_id,
                                "result": content.result,
                                "is_error": content.is_error,
                            }
                        }
                    ),
                }
            )
            for content in filtered_contents
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
            allow_tool: Whether to allow tool calls in the content.

        Returns:
            The formatted message content.

        Raises:
            ValueError: If the message content type is unknown.
        """
        # If it's a single message, format it.
        if isinstance(value, Message):
            return [
                {
                    "role": value.role,
                    "content": cls._format_message_content(
                        value.normalize().content, allow_tool
                    ),
                }
            ]

        # If it's a list of messages, format each one.
        if isinstance(value, Sequence) and not isinstance(value, str):
            return [cls._format_content(message, allow_tool)[0] for message in value]

        raise ValueError(f"Unknown message content type: {type(value)}")

    @classmethod
    def load_content(
        cls, content: str | list[dict[str, Any]]
    ) -> str | list[MessageContent]:
        """Load the message content from the Anthropic model to dataclasses.

        Args:
            content: The content to load.

        Returns:
            The loaded message content.

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
                case "data":
                    parsed_content.append(DataBlock(**entry))
                case "tool_use":
                    parsed_content.append(ToolCall(**entry))
                case "tool_result":
                    parsed_content.append(
                        ToolResult(
                            tool_call_id=entry.pop("tool_use_id"),
                            result=entry.pop("content"),
                            **entry,
                        )
                    )

        return parsed_content
