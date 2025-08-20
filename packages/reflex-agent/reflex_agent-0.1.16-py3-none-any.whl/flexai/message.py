"""Message types for agent-LLM communication in the FlexAI framework."""

from __future__ import annotations

import itertools
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Generic, TypedDict

from typing_extensions import TypeVar


def all_subclasses(cls: type) -> set[type]:
    """Return a set of all subclasses (direct & indirect) of a given class.

    Args:
        cls: A python class that we want to know all the subclasses for

    Returns:
        A set of all subclasses (direct & indirect) of cls.
    """
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses.update(all_subclasses(subclass))
    return subclasses


@dataclass(frozen=True)
class MessageContent:
    def dump(self) -> dict[str, Any]:
        """Return the dataclass as a dictionary.

        Returns:
            The dataclass as a dictionary.
        """
        return {"type": self.__class__.__name__, **asdict(self)}

    @classmethod
    def load(cls, data: Mapping[str, Any]) -> MessageContent:
        """Load the dataclass from a dictionary.

        Args:
            data: The dictionary to load.

        Returns:
            The dataclass instance.

        Raises:
            ValueError: If the message content type is unknown.
        """
        # Check all subclasses of MessageContent.
        for subclass in all_subclasses(cls):
            if subclass.__name__ == data["type"]:
                data = {k: v for k, v in data.items() if k != "type"}
                return subclass(**data)

        raise ValueError(f"Unknown message content type: {data['type']}")


_CONTENT_co = TypeVar(
    "_CONTENT_co",
    bound=Sequence[MessageContent] | str,
    default=(Sequence[MessageContent] | str),
    covariant=True,
)

_OTHER_CONTENT_co = TypeVar(
    "_OTHER_CONTENT_co",
    bound=Sequence[MessageContent] | str,
    default=(Sequence[MessageContent] | str),
    covariant=True,
)


def normalize_content(
    content: Sequence[MessageContent] | str,
) -> tuple[
    TextBlock | ImageBlock | ToolCall | ToolResult | URLContextBlock | GroundingBlock,
    ...,
]:
    """Normalize the content to a tuple of TextBlock or ImageBlock.

    Args:
        content: The content to normalize.

    Returns:
        A tuple of TextBlock or ImageBlock.
    """
    return (
        (TextBlock(content),)
        if isinstance(content, str)
        else tuple(
            itertools.chain.from_iterable(
                (
                    (
                        (content,)
                        if isinstance(
                            content,
                            (
                                TextBlock,
                                ImageBlock,
                                ToolCall,
                                ToolResult,
                                URLContextBlock,
                            ),
                        )
                        else ()
                    )
                    if not isinstance(content, DataBlock)
                    else content.into_text_and_image_blocks()
                )
                for content in content
            )
        )
    )


class MessageDict(TypedDict):
    role: str
    content: str | Sequence[Mapping[str, Any]]


@dataclass
class Message(Generic[_CONTENT_co]):
    """Base class for all message types in the conversation flow."""

    # The role of the message (user or assistant).
    role: str

    # The content of the message.
    content: _CONTENT_co

    @classmethod
    def load(cls, data: MessageDict):
        contents = data["content"]
        content = (
            contents
            if isinstance(contents, str)
            else tuple(MessageContent.load(content) for content in contents)
        )
        return cls(
            role=data["role"],
            content=content,  # pyright: ignore [reportArgumentType]
        )

    def with_content(self, content: _OTHER_CONTENT_co) -> Message[_OTHER_CONTENT_co]:
        """Create a new message with the specified content.

        Args:
            content: The content to set.

        Returns:
            A new Message instance with the specified content.
        """
        return replace(self, content=content)  # pyright: ignore [reportReturnType]

    def dump(self):
        return {
            "role": self.role,
            "content": self.content
            if isinstance(self.content, str)
            else [content.dump() for content in self.content],
        }

    def normalize(
        self,
    ) -> Message[
        tuple[
            ImageBlock
            | TextBlock
            | ToolCall
            | ToolResult
            | URLContextBlock
            | GroundingBlock,
            ...,
        ]
    ]:
        """Normalize the message content.

        Returns:
            A new Message instance with normalized content.
        """
        return self.with_content(normalize_content(self.content))

    def exclude_image_blocks(
        self,
    ) -> Message[
        tuple[TextBlock | ToolCall | ToolResult | URLContextBlock | GroundingBlock, ...]
    ]:
        """Exclude image blocks from the message content.

        Returns:
            A new Message instance with image blocks excluded.
        """
        normalized_content = self.normalize().content

        return self.with_content(
            tuple(
                content
                for content in normalized_content
                if not isinstance(content, ImageBlock)
            )
        )


@dataclass
class SystemMessage(Message[_CONTENT_co]):
    """A top level system message."""

    role: str = field(init=False, default="system")


@dataclass
class UserMessage(Message[_CONTENT_co]):
    """A message sent by a user."""

    role: str = field(init=False, default="user")


@dataclass
class AIMessage(Message[_CONTENT_co]):
    """A message generated by the AI."""

    # The resource usage for the message.
    role: str = field(init=False, default="assistant")

    # The resource usage for the message.
    usage: Usage = field(default_factory=lambda: Usage())


@dataclass(frozen=True)
class TextBlock(MessageContent):
    """A block of text content."""

    text: str

    cache: bool = False

    def append(self, text: str) -> TextBlock:
        """Append text to the block.

        Args:
            text: The text to append.

        Returns:
            A new TextBlock instance with the appended text.
        """
        return replace(self, text=self.text + text)


@dataclass(frozen=True)
class ThoughtBlock(TextBlock):
    """A block of text content, corresponding to a model's inner thoughts."""


@dataclass(frozen=True)
class ImageBlock(MessageContent):
    """A block of image content."""

    # The image data as bytes.
    image: bytes

    # The MIME type of the image.
    mime_type: str


@dataclass(frozen=True)
class DataBlock(MessageContent):
    """A block of structured data."""

    data: Mapping[str, Any]

    cache: bool = False

    def with_data(self, data: Mapping[str, Any]) -> DataBlock:
        """Create a new DataBlock with the specified data.

        Args:
            data: The data to set.

        Returns:
            A new DataBlock instance with the specified data.
        """
        return replace(self, data=data)

    def set(self, key: str, value: Any) -> DataBlock:
        """Set a key-value pair in the data block.

        It does not modify the original DataBlock, but returns a new one.

        Args:
            key: The key to set.
            value: The value to set.

        Returns:
            A new DataBlock instance with the updated data.
        """
        new_data = {**self.data, key: value}
        return replace(self, data=new_data)

    def into_text_and_image_blocks(self) -> list[TextBlock | ImageBlock]:
        """Convert the data block into text and image blocks.

        Returns:
            A tuple of text and image blocks.
        """
        return [
            (
                ImageBlock(
                    image=value["image"],
                    mime_type=value["mime_type"],
                )
                if (
                    isinstance(value, Mapping)
                    and "image" in value
                    and "mime_type" in value
                    and isinstance(value["image"], bytes)
                    and isinstance(value["mime_type"], str)
                )
                else TextBlock(text=json.dumps({key: value}), cache=self.cache)
            )
            if not isinstance(value, ImageBlock)
            else value
            for key, value in self.data.items()
        ]


@dataclass(kw_only=True, frozen=True)
class ToolUseChunk(MessageContent):
    """A chunk reported by the tool during execution."""

    # A unique identifier for the tool call this came from.
    id: str

    # The name of the tool this is from.
    tool_name: str

    # Associated data.
    content: Any


@dataclass(kw_only=True, frozen=True)
class ToolCall(MessageContent):
    """A tool call message sent by the agent."""

    # A unique identifier for the tool call.
    id: str

    # The name of the tool to call.
    name: str

    # The input parameters for the tool.
    input: Any

    def append_input(self, chunk: str) -> ToolCall:
        """Append a chunk to the input data.

        Args:
            chunk: The chunk of text to append from the stream.

        Returns:
            A new ToolCall instance with the appended input.

        Raises:
            TypeError: If input is not a string.
        """
        if not isinstance(self.input, str):
            raise TypeError("Input must be a string to append.")
        return replace(self, input=self.input + chunk)

    def load_input(self) -> ToolCall:
        """Load the input string as JSON.

        Returns:
            A new ToolCall instance with the input loaded as JSON.

        Raises:
            TypeError: If input is not a string.
        """
        if not isinstance(self.input, str):
            raise TypeError("Input must be a string to load as JSON.")
        try:
            data = json.loads(self.input)
        except json.JSONDecodeError:
            data = {}
        return replace(self, input=data)


@dataclass(kw_only=True, frozen=True)
class ToolResult(MessageContent):
    """A tool result message created after invoking a tool."""

    # The associated tool call identifier.
    tool_call_id: str

    # The result of the tool invocation.
    result: Any

    # The execution time of the tool invocation.
    execution_time: float = 0.0

    # Whether an error occurred during invocation.
    is_error: bool = False


@dataclass(frozen=True)
class URLContextBlock(MessageContent):
    """A block containing URL context metadata from web content access."""

    # The URLs that were accessed
    urls_accessed: Sequence[str] = field(default_factory=list)

    # Additional metadata from the URL context tool
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GroundingBlock(MessageContent):
    """A block containing Google Search grounding metadata."""

    # The search queries that were executed
    search_queries: Sequence[str] = field(default_factory=list)

    # The grounding chunks with source information
    grounding_chunks: Sequence[Mapping[str, Any]] = field(default_factory=list)

    # The grounding supports mapping content to sources
    grounding_supports: Sequence[Mapping[str, Any]] = field(default_factory=list)

    # Search entry point for widget rendering
    search_entry_point: Mapping[str, Any] = field(default_factory=dict)

    # Additional grounding metadata
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class Usage:
    """Track resource usage for a message."""

    # The number of input tokens used to generate the message.
    input_tokens: int = 0

    # The number of output tokens used to generate the message.
    output_tokens: int = 0

    # The number of tokens read from the cache.
    cache_read_tokens: int = 0

    # The number of tokens written to the cache.
    cache_write_tokens: int = 0

    # The time taken to generate the message.
    generation_time: float = 0.0
