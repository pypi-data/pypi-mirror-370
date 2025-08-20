"""Shared utilities for unit tests.

Common mock factories, fixtures, assertion helpers, and test utilities used across
all unit test files. This module eliminates duplicate code and provides consistent
testing patterns for all LLM client implementations.

This module is provider-agnostic and contains no provider-specific code.
"""

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from flexai.message import (
    AIMessage,
    SystemMessage,
    TextBlock,
    ToolCall,
    ToolResult,
    Usage,
    UserMessage,
)
from flexai.tool import Tool

# =============================================================================
# COMMON TEST DATA
# =============================================================================


class TestData:
    """Common test data for various scenarios."""

    # Basic messages
    SIMPLE_USER_MESSAGE = "Hello, how are you?"
    SIMPLE_AI_RESPONSE = "Hello! I'm doing well, thank you for asking."
    SYSTEM_MESSAGE = "You are a helpful assistant."
    PIRATE_SYSTEM = "You are a pirate. Respond in pirate speak."

    # Math examples
    MATH_QUESTION = "What is 15 + 27?"
    MATH_ANSWER = "42"
    TOOL_MATH_REQUEST = "Use the add_numbers tool to calculate 15 + 23"

    # Multi-turn conversation
    CONVERSATION_INTRO = "My name is Alice and I'm a software engineer."
    CONVERSATION_FOLLOWUP = "What's my profession?"

    # Edge cases
    EMPTY_MESSAGE = ""
    VERY_LONG_MESSAGE = "A" * 10000
    UNICODE_MESSAGE = "Hello 🌍! ñáéíóú 中文 العربية"

    # Tool call examples
    TOOL_CALL_ID = "call_123"
    TOOL_NAME = "add_numbers"
    TOOL_ARGS = {"a": 15, "b": 23}
    TOOL_RESULT = 38


# =============================================================================
# GENERIC MOCK FACTORIES
# =============================================================================


class GenericMockFactory:
    """Generic factory for creating mock objects without provider-specific details."""

    @staticmethod
    def create_usage_data(
        input_tokens: int = 10,
        output_tokens: int = 20,
        generation_time: float = 0.5,
        cache_tokens: int = 0,
    ) -> dict[str, Any]:
        """Create generic usage data dictionary."""
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "generation_time": generation_time,
            "cache_tokens": cache_tokens,
        }

    @staticmethod
    def create_mock_response(
        content: str = TestData.SIMPLE_AI_RESPONSE,
        has_tool_calls: bool = False,
        usage_data: dict | None = None,
    ) -> Mock:
        """Create a generic mock response that can be adapted by providers."""
        if usage_data is None:
            usage_data = GenericMockFactory.create_usage_data()

        response = Mock()
        response.content = content
        response.has_tool_calls = has_tool_calls
        response.usage_data = usage_data

        return response

    @staticmethod
    def create_mock_tool_call(
        tool_id: str = TestData.TOOL_CALL_ID,
        tool_name: str = TestData.TOOL_NAME,
        tool_args: dict | None = None,
    ) -> dict:
        """Create a generic mock tool call."""
        if tool_args is None:
            tool_args = TestData.TOOL_ARGS

        return {"id": tool_id, "name": tool_name, "args": tool_args}

    @staticmethod
    def create_mock_streaming_chunks(
        content_parts: list[str], include_final_chunk: bool = True
    ) -> list[dict]:
        """Create generic streaming chunk data."""
        chunks = []

        for part in content_parts:
            chunks.append({"type": "content", "data": part})

        if include_final_chunk:
            chunks.append({"type": "final", "data": None})

        return chunks


# =============================================================================
# ERROR SIMULATION HELPERS
# =============================================================================


class ErrorSimulator:
    """Helpers for simulating various error conditions."""

    @staticmethod
    def create_api_error(
        status_code: int = 500, message: str = "Internal Server Error"
    ):
        """Create a generic API error."""
        error = Exception(message)
        error.status_code = status_code
        return error

    @staticmethod
    def create_rate_limit_error():
        """Create a generic rate limiting error."""
        error = Exception("Rate limit exceeded")
        error.status_code = 429
        return error

    @staticmethod
    def create_auth_error():
        """Create a generic authentication error."""
        error = Exception("Invalid API key")
        error.status_code = 401
        return error

    @staticmethod
    def create_timeout_error():
        """Create a generic timeout error."""
        import asyncio

        return asyncio.TimeoutError("Request timed out")

    @staticmethod
    def create_network_error():
        """Create a generic network error."""
        return ConnectionError("Network error")

    @staticmethod
    def create_malformed_response():
        """Create a generic malformed response."""
        response = Mock()
        response.is_malformed = True
        return response

    @staticmethod
    def create_invalid_json_response():
        """Create a response with invalid JSON."""
        return "Invalid JSON: {broken"

    @staticmethod
    def create_empty_response():
        """Create an empty response."""
        response = Mock()
        response.content = None
        return response


# =============================================================================
# GENERIC CLIENT MOCKING HELPERS
# =============================================================================


class ClientMockHelper:
    """Generic helpers for mocking LLM clients."""

    @staticmethod
    def create_mock_client() -> Mock:
        """Create a generic mock client."""
        return Mock()

    @staticmethod
    def create_async_mock_method(return_value=None):
        """Create an async mock method."""
        return AsyncMock(return_value=return_value)

    @staticmethod
    def create_streaming_mock_method(chunks: list):
        """Create an async mock method that yields chunks."""

        async def async_generator():
            for chunk in chunks:
                yield chunk

        return AsyncMock(return_value=async_generator())

    @staticmethod
    def patch_method(obj, method_name: str, mock_method):
        """Generic method patcher."""
        return patch.object(obj, method_name, mock_method)

    @staticmethod
    def patch_init_method(client_class, mock_client):
        """Generic client initialization patcher."""

        def patched_init(self, *args, **kwargs):
            object.__setattr__(self, "client", mock_client)

        return patch.object(client_class, "__post_init__", patched_init)


# =============================================================================
# COMMON FIXTURES
# =============================================================================


@pytest.fixture
def simple_math_tool():
    """Create a simple math tool for testing."""

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together.

        Args:
            a: The first number
            b: The second number

        Returns:
            The sum of a and b
        """
        return a + b

    return Tool.from_function(add_numbers)


@pytest.fixture
def complex_calculator_tool():
    """Create a more complex calculator tool."""

    def calculate(operation: str, a: float, b: float) -> float:
        """Perform basic arithmetic operations.

        Args:
            operation: The operation to perform (add, subtract, multiply, divide)
            a: The first number
            b: The second number

        Returns:
            The result of the calculation
        """
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else float("inf"),
        }

        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")

        return operations[operation](a, b)

    return Tool.from_function(calculate)


@pytest.fixture
def error_prone_tool():
    """Create a tool that throws errors for testing error handling."""

    def faulty_function(should_error: bool = True) -> str:
        """A function that can throw errors for testing.

        Args:
            should_error: Whether to throw an error

        Returns:
            Success message if no error

        Raises:
            ValueError: If should_error is True
        """
        if should_error:
            raise ValueError("This tool intentionally failed")
        return "Success!"

    return Tool.from_function(faulty_function)


@pytest.fixture
def async_tool():
    """Create an async tool for testing async tool execution."""

    async def async_function(delay: float = 0.1) -> str:
        """An async function for testing.

        Args:
            delay: How long to wait before returning

        Returns:
            Success message after delay
        """
        import asyncio

        await asyncio.sleep(delay)
        return f"Completed after {delay} seconds"

    return Tool.from_function(async_function)


@pytest.fixture
def test_messages():
    """Create a set of test messages for various scenarios."""
    return {
        "simple": [UserMessage(TestData.SIMPLE_USER_MESSAGE)],
        "math": [UserMessage(TestData.MATH_QUESTION)],
        "tool_request": [UserMessage(TestData.TOOL_MATH_REQUEST)],
        "conversation": [
            UserMessage(TestData.CONVERSATION_INTRO),
            AIMessage("Nice to meet you, Alice!"),
            UserMessage(TestData.CONVERSATION_FOLLOWUP),
        ],
        "empty": [UserMessage(TestData.EMPTY_MESSAGE)],
        "unicode": [UserMessage(TestData.UNICODE_MESSAGE)],
        "long": [UserMessage(TestData.VERY_LONG_MESSAGE)],
    }


@pytest.fixture
def mock_usage():
    """Create mock usage data."""
    usage_data = GenericMockFactory.create_usage_data()
    return Usage(
        input_tokens=usage_data["input_tokens"],
        output_tokens=usage_data["output_tokens"],
        generation_time=usage_data["generation_time"],
    )


# =============================================================================
# ASSERTION HELPERS
# =============================================================================


class CommonUnitAssertions:
    """Common assertion helpers for unit tests."""

    @staticmethod
    def assert_valid_ai_message(response: AIMessage, min_content_length: int = 1):
        """Assert that an AI message is valid."""
        assert isinstance(response, AIMessage)
        assert response.content is not None

        if isinstance(response.content, str):
            assert len(response.content) >= min_content_length
        elif isinstance(response.content, list):
            assert len(response.content) > 0
        else:
            pytest.fail(f"Unexpected content type: {type(response.content)}")

    @staticmethod
    def assert_valid_usage(usage: Usage):
        """Assert that usage data is valid."""
        assert isinstance(usage, Usage)
        assert usage.input_tokens > 0
        assert usage.output_tokens >= 0
        assert usage.generation_time > 0

    @staticmethod
    def assert_contains_tool_calls(response: AIMessage) -> list[ToolCall]:
        """Assert that response contains tool calls and return them."""
        assert isinstance(response.content, list)
        tool_calls = [item for item in response.content if isinstance(item, ToolCall)]
        assert len(tool_calls) > 0
        return tool_calls

    @staticmethod
    def assert_tool_call_valid(tool_call: ToolCall, expected_name: str | None = None):
        """Assert that a tool call is valid."""
        assert isinstance(tool_call, ToolCall)
        assert tool_call.id is not None
        assert tool_call.name is not None
        assert isinstance(tool_call.input, dict)

        if expected_name:
            assert tool_call.name == expected_name

    @staticmethod
    def assert_streaming_chunks_valid(chunks: list, min_chunks: int = 1):
        """Assert that streaming chunks are valid."""
        assert len(chunks) >= min_chunks

        # Should have at least one TextBlock
        text_blocks = [chunk for chunk in chunks if isinstance(chunk, TextBlock)]
        assert len(text_blocks) > 0

        # Should have final AI message
        ai_messages = [chunk for chunk in chunks if isinstance(chunk, AIMessage)]
        assert len(ai_messages) > 0

    @staticmethod
    def assert_error_response(response, expected_error_type: type | None = None):
        """Assert that a response indicates an error."""
        if isinstance(response, ToolResult):
            assert response.is_error
            assert response.result is not None
        elif expected_error_type:
            assert isinstance(response, expected_error_type)

    @staticmethod
    def assert_mock_called_once(mock_method):
        """Assert that a mock method was called exactly once."""
        mock_method.assert_called_once()

    @staticmethod
    def assert_mock_not_called(mock_method):
        """Assert that a mock method was not called."""
        mock_method.assert_not_called()


# =============================================================================
# TEST SCENARIO GENERATORS
# =============================================================================


class TestScenarios:
    """Generate test scenarios for comprehensive testing."""

    @staticmethod
    def edge_case_inputs():
        """Generate edge case inputs for robustness testing."""
        return [
            ("empty_string", ""),
            ("only_whitespace", "   \n\t  "),
            ("very_long", "A" * 50000),
            ("unicode_mixed", "Hello 🌍! ñáéíóú 中文 العربية русский"),
            ("special_chars", "!@#$%^&*()[]{}|\\:;\"'<>?,./"),
            ("json_like", '{"key": "value", "array": [1, 2, 3]}'),
            ("html_like", "<html><body>Hello</body></html>"),
            ("code_like", "def function():\n    return 'hello'"),
            ("newlines", "Line 1\nLine 2\n\nLine 4"),
            ("tabs", "Col1\tCol2\tCol3"),
            ("null_chars", "text\x00with\x00nulls"),
            ("control_chars", "text\x01\x02\x03control"),
            ("mixed_encoding", "café naïve résumé"),
            ("zero_width", "zero\u200bwidth\u200cspace"),
            ("rtl_text", "العربية نص من اليمين إلى اليسار"),
        ]

    @staticmethod
    def error_scenarios():
        """Generate error scenarios for testing."""
        return [
            ("api_error", ErrorSimulator.create_api_error),
            ("rate_limit", ErrorSimulator.create_rate_limit_error),
            ("auth_error", ErrorSimulator.create_auth_error),
            ("timeout", ErrorSimulator.create_timeout_error),
            ("network_error", ErrorSimulator.create_network_error),
            ("malformed_response", ErrorSimulator.create_malformed_response),
            ("invalid_json", ErrorSimulator.create_invalid_json_response),
            ("empty_response", ErrorSimulator.create_empty_response),
        ]

    @staticmethod
    def tool_scenarios():
        """Generate tool testing scenarios."""
        return [
            ("no_tools", []),
            ("single_tool", ["simple_math_tool"]),
            ("multiple_tools", ["simple_math_tool", "complex_calculator_tool"]),
            ("error_tool", ["error_prone_tool"]),
            ("async_tool", ["async_tool"]),
        ]

    @staticmethod
    def message_scenarios():
        """Generate message testing scenarios."""
        return [
            ("simple_text", [UserMessage("Hello")]),
            ("empty_message", [UserMessage("")]),
            ("unicode_message", [UserMessage(TestData.UNICODE_MESSAGE)]),
            ("long_message", [UserMessage(TestData.VERY_LONG_MESSAGE)]),
            (
                "multi_turn",
                [
                    UserMessage("First message"),
                    AIMessage("First response"),
                    UserMessage("Second message"),
                ],
            ),
            ("system_message", [SystemMessage("System"), UserMessage("User")]),
        ]


# =============================================================================
# COMMON PYDANTIC MODELS FOR TESTING
# =============================================================================


class TestPerson(BaseModel):
    """Test model for structured output testing."""

    name: str
    age: int
    occupation: str


class TestMathProblem(BaseModel):
    """Test model for math problem structured output."""

    problem: str
    answer: int
    explanation: str


class TestComplexData(BaseModel):
    """Test model with complex nested data."""

    title: str
    items: list[dict[str, Any]]
    metadata: dict[str, str | int | bool]


class TestEmptyModel(BaseModel):
    """Test model with no fields."""


class TestOptionalModel(BaseModel):
    """Test model with optional fields."""

    required_field: str
    optional_field: str | None = None
    optional_int: int | None = 42


# =============================================================================
# ASYNC HELPERS
# =============================================================================


async def collect_async_generator(async_gen: AsyncGenerator) -> list:
    """Collect all items from an async generator into a list."""
    items = []
    async for item in async_gen:
        items.append(item)
    return items


async def run_with_timeout(coro, timeout: float = 5.0):
    """Run a coroutine with a timeout."""
    import asyncio

    return await asyncio.wait_for(coro, timeout=timeout)


def create_async_mock_generator(items: list):
    """Create an async generator mock from a list of items."""

    async def async_gen():
        for item in items:
            yield item

    return async_gen()


# =============================================================================
# PERFORMANCE TESTING HELPERS
# =============================================================================


class PerformanceHelper:
    """Helpers for performance testing."""

    @staticmethod
    def measure_time(func):
        """Decorator to measure function execution time."""
        import functools
        import time

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start
            return result, duration

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            return result, duration

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    @staticmethod
    def assert_performance(duration: float, max_duration: float):
        """Assert that execution time is within acceptable limits."""
        assert duration <= max_duration, (
            f"Execution took {duration:.2f}s, expected <= {max_duration}s"
        )


# =============================================================================
# ROBUSTNESS TESTING HELPERS
# =============================================================================


class RobustnessHelper:
    """Helpers for testing edge cases and robustness."""

    @staticmethod
    def create_partial_response():
        """Create a partial response for testing incomplete data handling."""
        response = Mock()
        response.is_partial = True
        response.content = "Partial"
        return response

    @staticmethod
    def create_circular_reference():
        """Create objects with circular references for testing."""
        obj1 = {"name": "obj1", "ref": None}
        obj2 = {"name": "obj2", "ref": obj1}
        obj1["ref"] = obj2
        return obj1

    @staticmethod
    def create_deeply_nested_data(depth: int = 100):
        """Create deeply nested data structure."""
        result = "deep"
        for i in range(depth):
            result = {"level": i, "data": result}
        return result

    @staticmethod
    def create_large_payload(size_mb: int = 1):
        """Create a large payload for testing size limits."""
        # Create approximately size_mb megabytes of data
        char_count = size_mb * 1024 * 1024
        return "A" * char_count


# =============================================================================
# MEMORY AND RESOURCE TESTING
# =============================================================================


class ResourceTestHelper:
    """Helpers for testing memory and resource usage."""

    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    @staticmethod
    def assert_memory_limit(max_memory_mb: float):
        """Assert that memory usage is below a limit."""
        current_memory = ResourceTestHelper.get_memory_usage()
        assert current_memory <= max_memory_mb, (
            f"Memory usage {current_memory:.1f}MB exceeds limit {max_memory_mb}MB"
        )

    @staticmethod
    def create_memory_pressure():
        """Create memory pressure for testing."""
        # Create a large list to consume memory
        return list(range(1000000))


# =============================================================================
# GENERIC EDGE CASE TEST TEMPLATES
# =============================================================================


class EdgeCaseTestTemplates:
    """Generic test templates for edge cases that all providers should handle."""

    @staticmethod
    async def test_edge_case_inputs_template(
        client, mock_client, create_response_func, scenario_name, input_text
    ):
        """Generic template for testing edge case inputs."""
        # Create appropriate response for the input
        expected_response = f"Processed: {scenario_name}"
        mock_response = create_response_func(content=expected_response)

        # Mock the appropriate client method (provider-specific)
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            # OpenAI style
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            # Anthropic style
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            # Gemini style
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage(input_text)]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response, min_content_length=0)
        assert expected_response in str(response.content)  # More flexible assertion
        CommonUnitAssertions.assert_valid_usage(response.usage)

    @staticmethod
    async def test_empty_response_content_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing empty response content."""
        mock_response = create_response_func(content="")

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage("Test")]
        response = await client.get_chat_response(messages)

        assert isinstance(response, AIMessage)
        # Check if content is empty string or empty list
        if isinstance(response.content, str):
            assert response.content == ""
        elif isinstance(response.content, list):
            # For providers that return list, check if text blocks are empty
            text_content = "".join(
                [
                    block.text
                    for block in response.content
                    if isinstance(block, TextBlock)
                ]
            )
            assert text_content == ""
        CommonUnitAssertions.assert_valid_usage(response.usage)

    @staticmethod
    async def test_null_response_content_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing null response content."""
        mock_response = create_response_func(content=None)

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage("Test")]
        response = await client.get_chat_response(messages)

        assert isinstance(response, AIMessage)
        # Different providers may handle null differently
        assert (
            response.content is None or response.content == "" or response.content == []
        )

    @staticmethod
    async def test_very_large_response_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing very large responses."""
        large_content = RobustnessHelper.create_large_payload(size_mb=1)
        mock_response = create_response_func(content=large_content)

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage("Generate large response")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)

        # Check content size regardless of response format
        content_length = 0
        if isinstance(response.content, str):
            content_length = len(response.content)
        elif isinstance(response.content, list):
            content_length = sum(
                [
                    len(block.text)
                    for block in response.content
                    if isinstance(block, TextBlock)
                ]
            )

        assert content_length > 1000000  # At least 1MB

    @staticmethod
    async def test_unicode_response_template(client, mock_client, create_response_func):
        """Generic template for testing unicode characters in response."""
        unicode_content = "Hello 🌍! 你好 العالم мир"
        mock_response = create_response_func(content=unicode_content)

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage("Respond with unicode")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)

        # Check unicode content regardless of response format
        if isinstance(response.content, str):
            assert unicode_content in response.content
        elif isinstance(response.content, list):
            text_content = "".join(
                [
                    block.text
                    for block in response.content
                    if isinstance(block, TextBlock)
                ]
            )
            assert unicode_content in text_content

    @staticmethod
    async def test_circular_reference_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing circular references in message data."""
        mock_response = create_response_func()

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        # Create circular reference
        circular_data = RobustnessHelper.create_circular_reference()

        # This should either handle gracefully or raise an appropriate error
        messages = [UserMessage(f"Process this data: {circular_data}")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)

    @staticmethod
    async def test_api_error_handling_template(client, mock_client, error_factory):
        """Generic template for testing API error handling."""
        error = error_factory()

        # Mock the appropriate client method to raise error
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(side_effect=error)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(side_effect=error)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(side_effect=error)

        messages = [UserMessage("Test")]

        with pytest.raises(Exception):
            await client.get_chat_response(messages)

    @staticmethod
    async def test_timeout_handling_template(client, mock_client):
        """Generic template for testing timeout handling."""
        timeout_error = ErrorSimulator.create_timeout_error()

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(side_effect=timeout_error)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(side_effect=timeout_error)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(side_effect=timeout_error)

        messages = [UserMessage("Test")]

        with pytest.raises(Exception):
            await run_with_timeout(client.get_chat_response(messages), timeout=1.0)

    @staticmethod
    async def test_network_error_template(client, mock_client):
        """Generic template for testing network error handling."""
        network_error = ErrorSimulator.create_network_error()

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(side_effect=network_error)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(side_effect=network_error)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(side_effect=network_error)

        messages = [UserMessage("Test")]

        with pytest.raises(ConnectionError):
            await client.get_chat_response(messages)

    @staticmethod
    async def test_concurrent_requests_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing concurrent requests."""
        import asyncio

        # Create different responses for each request
        responses = [create_response_func(content=f"Response {i}") for i in range(5)]

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(side_effect=responses)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(side_effect=responses)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(side_effect=responses)

        # Create concurrent requests
        tasks = [
            client.get_chat_response([UserMessage(f"Request {i}")]) for i in range(5)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 5
        for i, result in enumerate(results):
            CommonUnitAssertions.assert_valid_ai_message(result)
            assert f"Response {i}" in str(result.content)

    @staticmethod
    async def test_memory_usage_template(client, mock_client, create_response_func):
        """Generic template for testing memory usage with large responses."""
        # Create very large response
        large_content = "X" * (10 * 1024 * 1024)  # 10MB response
        mock_response = create_response_func(content=large_content)

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "messages"):
            mock_client.messages.create = AsyncMock(return_value=mock_response)
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=mock_response)

        messages = [UserMessage("Generate large response")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)

        # Verify content size
        content_length = 0
        if isinstance(response.content, str):
            content_length = len(response.content)
        elif isinstance(response.content, list):
            content_length = sum(
                [
                    len(block.text)
                    for block in response.content
                    if isinstance(block, TextBlock)
                ]
            )

        assert content_length == 10 * 1024 * 1024

        # Clean up large object
        del response, large_content

    @staticmethod
    async def test_temperature_edge_values_template(
        client, mock_client, create_response_func
    ):
        """Generic template for testing temperature with edge values."""
        mock_response = create_response_func()

        messages = [UserMessage("Test")]

        # Test extreme temperature values
        for temp in [0.0, 1.0, 2.0, -1.0]:  # Include invalid values
            try:
                # Mock the appropriate client method
                if hasattr(mock_client, "chat") and hasattr(
                    mock_client.chat, "completions"
                ):
                    mock_client.chat.completions.create = AsyncMock(
                        return_value=mock_response
                    )
                elif hasattr(mock_client, "messages"):
                    mock_client.messages.create = AsyncMock(return_value=mock_response)
                elif hasattr(mock_client, "models"):
                    mock_client.models.generate_content = AsyncMock(
                        return_value=mock_response
                    )

                response = await client.get_chat_response(messages, temperature=temp)
                CommonUnitAssertions.assert_valid_ai_message(response)

                # Verify temperature was passed to API (provider-specific verification)
                # This is left to the provider-specific test to verify the exact call format

            except ValueError:
                # Some values might be rejected by the client
                pass


# =============================================================================
# TOOL CALLING EDGE CASE TEMPLATES
# =============================================================================


class ToolEdgeCaseTemplates:
    """Generic test templates for tool calling edge cases."""

    @staticmethod
    async def test_tool_missing_arguments_template(
        client, mock_client, create_tool_response_func, tool
    ):
        """Generic template for testing tool calls with missing arguments."""
        # This needs to be implemented by provider-specific tests
        # because tool call formats vary significantly between providers

    @staticmethod
    async def test_tool_extra_arguments_template(
        client, mock_client, create_tool_response_func, tool
    ):
        """Generic template for testing tool calls with extra arguments."""
        # This needs to be implemented by provider-specific tests

    @staticmethod
    async def test_tool_wrong_types_template(
        client, mock_client, create_tool_response_func, tool
    ):
        """Generic template for testing tool calls with wrong argument types."""
        # This needs to be implemented by provider-specific tests


# =============================================================================
# STREAMING EDGE CASE TEMPLATES
# =============================================================================


class StreamingEdgeCaseTemplates:
    """Generic test templates for streaming edge cases."""

    @staticmethod
    async def test_streaming_empty_chunks_template(
        client, mock_client, create_streaming_chunks_func
    ):
        """Generic template for testing streaming with empty chunks."""
        chunks = create_streaming_chunks_func(["", "", "Hello", "", "World"])

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=iter(chunks))
        elif hasattr(mock_client, "messages"):
            # Anthropic streaming might be different
            mock_client.messages.stream = AsyncMock(return_value=iter(chunks))
        elif hasattr(mock_client, "models"):
            # Gemini streaming might be different
            mock_client.models.generate_content = AsyncMock(return_value=iter(chunks))

        messages = [UserMessage("Stream with empty chunks")]
        collected_chunks = await collect_async_generator(
            client.stream_chat_response(messages)
        )

        # Should handle empty chunks gracefully
        text_chunks = [
            chunk for chunk in collected_chunks if isinstance(chunk, TextBlock)
        ]
        assert len(text_chunks) >= 2  # At least "Hello" and "World"

        # Check final message
        ai_messages = [
            chunk for chunk in collected_chunks if isinstance(chunk, AIMessage)
        ]
        assert len(ai_messages) == 1

    @staticmethod
    async def test_streaming_null_chunks_template(
        client, mock_client, create_null_chunks_func
    ):
        """Generic template for testing streaming with null chunks."""
        chunks = create_null_chunks_func([None, "Hello", None, " World", None])

        # Mock the appropriate client method
        if hasattr(mock_client, "chat") and hasattr(mock_client.chat, "completions"):
            mock_client.chat.completions.create = AsyncMock(return_value=iter(chunks))
        elif hasattr(mock_client, "messages"):
            mock_client.messages.stream = AsyncMock(return_value=iter(chunks))
        elif hasattr(mock_client, "models"):
            mock_client.models.generate_content = AsyncMock(return_value=iter(chunks))

        messages = [UserMessage("Stream with null chunks")]
        collected_chunks = await collect_async_generator(
            client.stream_chat_response(messages)
        )

        # Should filter out null chunks
        text_chunks = [
            chunk for chunk in collected_chunks if isinstance(chunk, TextBlock)
        ]
        assert len(text_chunks) == 2
        assert text_chunks[0].text == "Hello"
        assert text_chunks[1].text == " World"
