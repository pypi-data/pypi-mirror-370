from collections.abc import AsyncGenerator
from dataclasses import dataclass

from flexai.capability import Capability
from flexai.message import Message, MessageContent


@dataclass
class TruncateMessages(Capability):
    """Truncate the input messages to the LLM to a maximum number."""

    # The maximum number of messages to keep.
    max_messages: int

    async def modify_messages(
        self, messages: list[Message]
    ) -> AsyncGenerator[MessageContent | list[Message], None]:
        yield messages[-self.max_messages :]
