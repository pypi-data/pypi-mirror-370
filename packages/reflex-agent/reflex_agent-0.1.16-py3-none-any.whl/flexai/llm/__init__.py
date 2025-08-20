from collections.abc import AsyncGenerator
from dataclasses import dataclass

from flexai.message import AIMessage, Message, TextBlock

from .client import Client as Client


# Fallback client implementation that provides minimal functionality for testing and defaults
@dataclass(frozen=True)
class DefaultClient(Client):
    # Provider identifier for the default/stub client
    provider: str = "default"

    async def get_chat_response(
        self,
        messages: list[Message],
        **kwargs,
    ) -> AIMessage:
        # Mock implementation that always returns a blank TextBlock
        # This serves as a placeholder when no real LLM provider is configured
        return AIMessage(
            content=[
                TextBlock(
                    text="[DEFAULT CLIENT IS BEING USED]",
                )
            ]
        )

    async def stream_chat_response(
        self,
        messages: list[Message],
        **kwargs,
    ) -> AsyncGenerator[AIMessage, None]:
        # Mock implementation that always returns a blank TextBlock
        # Yields a single AIMessage with empty send_message tool call
        yield AIMessage(
            content=[
                TextBlock(
                    text="[DEFAULT CLIENT IS BEING USED]",
                )
            ]
        )
