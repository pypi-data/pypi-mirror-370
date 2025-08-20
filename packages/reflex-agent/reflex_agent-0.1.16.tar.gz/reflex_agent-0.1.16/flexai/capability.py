"""Capabilities define hooks that can plug into the agent's pipeline."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from flexai.message import AIMessage, Message, MessageContent, SystemMessage

if TYPE_CHECKING:
    from flexai.agent import Agent


@dataclass
class Capability:
    """Base class for defining cognitive capabilities of an agent.

    Provides hooks to modify the agent's behavior at different stages of
    the conversation pipeline, allowing for customization of prompts,
    messages, and responses.
    """

    def setup(self, agent: Agent):
        """Perform any setup required by the capability.

        Args:
            agent: The agent that the capability is attached to.
        """

    async def modify_prompt(
        self, prompt: SystemMessage
    ) -> AsyncGenerator[MessageContent | SystemMessage, None]:
        """Modify the system prompt before it's sent to the LLM.

        Args:
            prompt: The current system prompt.

        Yields:
            Intermediate message chunks followed by the modified system prompt.
        """
        yield prompt

    async def modify_messages(
        self, messages: list[Message]
    ) -> AsyncGenerator[MessageContent | Message | list[Message], None]:
        """Modify the conversation messages before sending them to the LLM.

        This method can be used to add, remove, or alter messages in the
        conversation history before they are processed by the language model.

        Args:
            messages: The current conversation messages.

        Yields:
            Intermediate message chunks followed by the modified list of messages.
        """
        yield messages

    async def modify_response(
        self, messages: list[Message], response: AIMessage
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        """Modify the AI-generated response before sending it to the user.

        This method allows for post-processing of the AI's response, which
        can include filtering, reformatting, or augmenting the content.

        Args:
            messages: The current conversation messages.
            response: The AI-generated response.

        Yields:
            Intermediate message chunks followed by the modified AI response.
        """
        yield response

    async def modify_tool_results(
        self,
        messages: list[Message],
        tool_call_message: Message[Sequence[MessageContent] | str],
        tool_results: list[MessageContent],
    ) -> AsyncGenerator[Message | MessageContent, None]:
        """Hook to modify the tool calls and results before sending them to the user.

        All of the input arguments (messages, tool_call_message, and tool_results) may be modified in
        place.

        If followup messages are yielded, this will override terminating tool
        determination.

        Args:
            messages: The current conversation messages.
            tool_call_message: The AI message containing the tool call(s).
            tool_results: The ToolResult fragments, should correspond 1:1
                with calls in tool_call_message.

        Yields:
            Intermediate message chunks or followup messages to continue the loop.
        """
        if False:
            yield  # make sure it's a generator
        return
