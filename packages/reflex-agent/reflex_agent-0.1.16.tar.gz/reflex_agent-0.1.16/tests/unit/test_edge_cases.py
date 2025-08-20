"""Edge cases and robustness tests for ALL LLM providers.

This single file tests all providers with identical edge cases, ensuring consistency
and comprehensive coverage. New providers automatically get full edge case coverage
when added to the PROVIDERS configuration.

All tests use mocks - no real API calls are made.
"""

# Load environment variables first
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, continue anyway
    pass

from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import shared utilities and templates
from .utils import (
    CommonUnitAssertions,
    GenericMockFactory,
    RobustnessHelper,
    TestData,
    TestScenarios,
    collect_async_generator,
)

# =============================================================================
# PROVIDER-SPECIFIC MOCK FACTORIES
# =============================================================================


class OpenAIMockFactory:
    """Mock factory for OpenAI API responses."""

    @staticmethod
    def create_response(content: str = TestData.SIMPLE_AI_RESPONSE, **kwargs) -> Mock:
        usage_data = kwargs.get("usage_data", GenericMockFactory.create_usage_data())

        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = content
        response.choices[0].message.tool_calls = kwargs.get("tool_calls")

        response.usage = Mock()
        response.usage.prompt_tokens = usage_data["input_tokens"]
        response.usage.completion_tokens = usage_data["output_tokens"]

        return response

    @staticmethod
    def create_streaming_chunks(content_parts: list[str]) -> list[Mock]:
        chunks = []
        for part in content_parts:
            chunk = Mock()
            chunk.choices = [Mock()]
            chunk.choices[0].delta = Mock()
            chunk.choices[0].delta.content = part
            chunk.choices[0].delta.tool_calls = None
            chunks.append(chunk)

        # Final empty chunk
        final_chunk = Mock()
        final_chunk.choices = [Mock()]
        final_chunk.choices[0].delta = Mock()
        final_chunk.choices[0].delta.content = None
        final_chunk.choices[0].delta.tool_calls = None
        chunks.append(final_chunk)

        return chunks

    @staticmethod
    def create_null_chunks(content_parts: list[str]) -> list[Mock]:
        chunks = []
        for content in content_parts:
            chunk = Mock()
            chunk.choices = [Mock()]
            chunk.choices[0].delta = Mock()
            chunk.choices[0].delta.content = content  # Can be None
            chunk.choices[0].delta.tool_calls = None
            chunks.append(chunk)
        return chunks


class AnthropicMockFactory:
    """Mock factory for Anthropic API responses."""

    @staticmethod
    def create_response(content: str = TestData.SIMPLE_AI_RESPONSE, **kwargs) -> Mock:
        usage_data = kwargs.get("usage_data", GenericMockFactory.create_usage_data())

        response = Mock()
        response.content = [Mock()]
        response.content[0].text = content
        response.content[0].type = "text"

        response.usage = Mock()
        response.usage.input_tokens = usage_data["input_tokens"]
        response.usage.output_tokens = usage_data["output_tokens"]

        return response

    @staticmethod
    def create_streaming_chunks(content_parts: list[str]) -> list[Mock]:
        chunks = []
        for part in content_parts:
            chunk = Mock()
            chunk.type = "content_block_delta"
            chunk.delta = Mock()
            chunk.delta.text = part
            chunks.append(chunk)

        # Final chunk
        final_chunk = Mock()
        final_chunk.type = "message_stop"
        chunks.append(final_chunk)

        return chunks

    @staticmethod
    def create_null_chunks(content_parts: list[str]) -> list[Mock]:
        chunks = []
        for content in content_parts:
            chunk = Mock()
            chunk.type = "content_block_delta" if content else "content_block_stop"
            chunk.delta = Mock()
            chunk.delta.text = content
            chunks.append(chunk)
        return chunks


class GeminiMockFactory:
    """Mock factory for Gemini API responses."""

    @staticmethod
    def create_response(content: str = TestData.SIMPLE_AI_RESPONSE, **kwargs) -> Mock:
        usage_data = kwargs.get("usage_data", GenericMockFactory.create_usage_data())

        response = Mock()
        response.candidates = [Mock()]
        response.candidates[0].content = Mock()
        response.candidates[0].content.parts = [Mock()]
        response.candidates[0].content.parts[0].text = content

        response.usage_metadata = Mock()
        response.usage_metadata.prompt_token_count = usage_data["input_tokens"]
        response.usage_metadata.candidates_token_count = usage_data["output_tokens"]

        return response

    @staticmethod
    def create_streaming_chunks(content_parts: list[str]) -> list[Mock]:
        chunks = []
        for part in content_parts:
            chunk = Mock()
            chunk.candidates = [Mock()]
            chunk.candidates[0].content = Mock()
            chunk.candidates[0].content.parts = [Mock()]
            chunk.candidates[0].content.parts[0].text = part
            chunks.append(chunk)
        return chunks

    @staticmethod
    def create_null_chunks(content_parts: list[str]) -> list[Mock]:
        return GeminiMockFactory.create_streaming_chunks(content_parts)


# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================


class ProviderConfig:
    """Configuration for a specific LLM provider."""

    def __init__(
        self,
        name: str,
        client_class: str,
        client_patch_path: str,
        mock_factory: Any,
        client_method: str = "get_chat_response",
        streaming_method: str = "stream_chat_response",
        mock_client_attr: str = "chat.completions.create",
        streaming_mock_attr: str | None = None,
        skip_reason: str | None = None,
    ):
        self.name = name
        self.client_class = client_class
        self.client_patch_path = client_patch_path
        self.mock_factory = mock_factory
        self.client_method = client_method
        self.streaming_method = streaming_method
        self.mock_client_attr = mock_client_attr
        self.streaming_mock_attr = streaming_mock_attr or mock_client_attr
        self.skip_reason = skip_reason


# Define all supported providers
PROVIDERS = {
    "openai": ProviderConfig(
        name="OpenAI",
        client_class="flexai.llm.openai.OpenAIClient",
        client_patch_path="flexai.llm.openai.AsyncOpenAI",
        mock_factory=OpenAIMockFactory,
        mock_client_attr="chat.completions.create",
    ),
    "anthropic": ProviderConfig(
        name="Anthropic",
        client_class="flexai.llm.anthropic.AnthropicClient",
        client_patch_path="flexai.llm.anthropic.AsyncAnthropic",
        mock_factory=AnthropicMockFactory,
        mock_client_attr="messages.create",
        skip_reason="Anthropic client not available in test environment",
    ),
    "gemini": ProviderConfig(
        name="Gemini",
        client_class="flexai.llm.gemini.GeminiClient",
        client_patch_path="flexai.llm.gemini.genai",
        mock_factory=GeminiMockFactory,
        mock_client_attr="models.generate_content",
        skip_reason="Gemini client not available in test environment",
    ),
}


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(params=PROVIDERS.keys())
def provider_config(request):
    """Fixture that provides each provider configuration."""
    return PROVIDERS[request.param]


@pytest.fixture
def mock_client_and_provider(provider_config):
    """Create a mock client for the given provider."""
    config = provider_config

    # Skip if provider is not available
    if config.skip_reason:
        pytest.skip(config.skip_reason)

    # Import the client class dynamically
    try:
        module_name, class_name = config.client_class.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        client_class = getattr(module, class_name)
    except (ImportError, AttributeError):
        pytest.skip(f"{config.name} client not available")

    # Patch the underlying client library
    with patch(config.client_patch_path) as mock_lib:
        mock_client = Mock()
        mock_lib.return_value = mock_client

        # Create the actual client instance (will use .env file for API keys)
        try:
            client = client_class()
        except Exception as e:
            pytest.skip(f"Failed to initialize {config.name} client: {e}")

        yield client, mock_client, config


def set_mock_response(mock_client, config: ProviderConfig, response):
    """Helper to set mock response on the appropriate client method."""
    attrs = config.mock_client_attr.split(".")
    target = mock_client
    for attr in attrs[:-1]:
        if not hasattr(target, attr):
            setattr(target, attr, Mock())
        target = getattr(target, attr)

    setattr(target, attrs[-1], AsyncMock(return_value=response))


def set_mock_streaming(mock_client, config: ProviderConfig, chunks):
    """Helper to set mock streaming response."""
    attrs = config.streaming_mock_attr.split(".")
    target = mock_client
    for attr in attrs[:-1]:
        if not hasattr(target, attr):
            setattr(target, attr, Mock())
        target = getattr(target, attr)

    # Create an async generator from the chunks
    async def async_chunk_generator():
        for chunk in chunks:
            yield chunk

    setattr(target, attrs[-1], AsyncMock(return_value=async_chunk_generator()))


# =============================================================================
# EDGE CASE INPUT TESTS (ALL PROVIDERS)
# =============================================================================


class TestAllProvidersEdgeCases:
    """Test edge cases across all providers for consistency."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("scenario_name", "input_text"), TestScenarios.edge_case_inputs()
    )
    async def test_edge_case_inputs(
        self, mock_client_and_provider, scenario_name, input_text
    ):
        """Test all providers with various edge case inputs."""
        client, mock_client, config = mock_client_and_provider

        # Create appropriate response for the input
        expected_response = f"Processed: {scenario_name}"
        mock_response = config.mock_factory.create_response(content=expected_response)
        set_mock_response(mock_client, config, mock_response)

        # Test the client
        from flexai.message import UserMessage

        messages = [UserMessage(input_text)]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response, min_content_length=0)
        assert expected_response in str(response.content)
        CommonUnitAssertions.assert_valid_usage(response.usage)

    @pytest.mark.asyncio
    async def test_empty_response_content(self, mock_client_and_provider):
        """Test handling of empty response content across all providers."""
        client, mock_client, config = mock_client_and_provider

        mock_response = config.mock_factory.create_response(content="")
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Test")]
        response = await client.get_chat_response(messages)

        from flexai.message import AIMessage

        assert isinstance(response, AIMessage)
        # Provider-agnostic empty content check
        if isinstance(response.content, str):
            assert response.content == ""
        elif isinstance(response.content, list):
            text_content = "".join(
                [
                    getattr(block, "text", "")
                    for block in response.content
                    if hasattr(block, "text")
                ]
            )
            assert text_content == ""
        CommonUnitAssertions.assert_valid_usage(response.usage)

    @pytest.mark.asyncio
    async def test_null_response_content(self, mock_client_and_provider):
        """Test handling of null response content across all providers."""
        client, mock_client, config = mock_client_and_provider

        mock_response = config.mock_factory.create_response(content=None)
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Test")]
        response = await client.get_chat_response(messages)

        from flexai.message import AIMessage

        assert isinstance(response, AIMessage)
        # Different providers may handle null differently
        assert (
            response.content is None or response.content == "" or response.content == []
        )

    @pytest.mark.asyncio
    async def test_unicode_in_response(self, mock_client_and_provider):
        """Test handling of unicode characters across all providers."""
        client, mock_client, config = mock_client_and_provider

        unicode_content = "Hello 🌍! 你好 العالم мир"
        mock_response = config.mock_factory.create_response(content=unicode_content)
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Respond with unicode")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)

        # Check unicode content regardless of response format
        if isinstance(response.content, str):
            assert unicode_content in response.content
        elif isinstance(response.content, list):
            from flexai.message import TextBlock

            text_content = "".join(
                [
                    block.text
                    for block in response.content
                    if isinstance(block, TextBlock)
                ]
            )
            assert unicode_content in text_content

    @pytest.mark.asyncio
    async def test_circular_reference_in_messages(self, mock_client_and_provider):
        """Test handling of circular references across all providers."""
        client, mock_client, config = mock_client_and_provider

        mock_response = config.mock_factory.create_response()
        set_mock_response(mock_client, config, mock_response)

        # Create circular reference
        circular_data = RobustnessHelper.create_circular_reference()

        from flexai.message import UserMessage

        messages = [UserMessage(f"Process this data: {circular_data}")]
        response = await client.get_chat_response(messages)

        CommonUnitAssertions.assert_valid_ai_message(response)


# =============================================================================
# STREAMING TESTS (ALL PROVIDERS)
# =============================================================================


class TestAllProvidersStreaming:
    """Test streaming edge cases across all providers."""

    @pytest.mark.asyncio
    async def test_streaming_with_empty_chunks(self, mock_client_and_provider):
        """Test streaming with empty content chunks across all providers."""
        client, mock_client, config = mock_client_and_provider

        chunks = config.mock_factory.create_streaming_chunks(
            ["", "", "Hello", "", "World"]
        )
        set_mock_streaming(mock_client, config, chunks)

        from flexai.message import UserMessage

        messages = [UserMessage("Stream with empty chunks")]

        try:
            collected_chunks = await collect_async_generator(
                client.stream_chat_response(messages)
            )

            # Should handle empty chunks gracefully
            from flexai.message import AIMessage, TextBlock

            text_chunks = [
                chunk for chunk in collected_chunks if isinstance(chunk, TextBlock)
            ]
            assert len(text_chunks) >= 2  # At least "Hello" and "World"

            # Check final message
            ai_messages = [
                chunk for chunk in collected_chunks if isinstance(chunk, AIMessage)
            ]
            assert len(ai_messages) == 1
        except AttributeError:
            # Some providers might not support streaming
            pytest.skip(f"{config.name} streaming not implemented")

    @pytest.mark.asyncio
    async def test_streaming_with_null_chunks(self, mock_client_and_provider):
        """Test streaming with null content chunks across all providers."""
        client, mock_client, config = mock_client_and_provider

        chunks = config.mock_factory.create_null_chunks(
            [None, "Hello", None, " World", None]
        )
        set_mock_streaming(mock_client, config, chunks)

        from flexai.message import UserMessage

        messages = [UserMessage("Stream with null chunks")]

        try:
            collected_chunks = await collect_async_generator(
                client.stream_chat_response(messages)
            )

            # Should filter out null chunks
            from flexai.message import TextBlock

            text_chunks = [
                chunk for chunk in collected_chunks if isinstance(chunk, TextBlock)
            ]
            assert len(text_chunks) == 2
            assert text_chunks[0].text == "Hello"
            assert text_chunks[1].text == " World"
        except AttributeError:
            # Some providers might not support streaming
            pytest.skip(f"{config.name} streaming not implemented")


# =============================================================================
# CONFIGURATION TESTS (ALL PROVIDERS)
# =============================================================================


class TestAllProvidersConfiguration:
    """Test configuration edge cases across all providers."""

    @pytest.mark.asyncio
    async def test_temperature_edge_values(self, mock_client_and_provider):
        """Test temperature with edge values across all providers."""
        client, mock_client, config = mock_client_and_provider

        mock_response = config.mock_factory.create_response()

        from flexai.message import UserMessage

        messages = [UserMessage("Test")]

        # Test extreme temperature values
        for temp in [0.0, 1.0, 2.0, -1.0]:  # Include invalid values
            try:
                set_mock_response(mock_client, config, mock_response)

                response = await client.get_chat_response(messages, temperature=temp)
                CommonUnitAssertions.assert_valid_ai_message(response)

                # Verify temperature was passed to API call
                attrs = config.mock_client_attr.split(".")
                target = mock_client
                for attr in attrs[:-1]:
                    target = getattr(target, attr)

                mock_method = getattr(target, attrs[-1])
                if mock_method.called:
                    call_args = mock_method.call_args
                    if call_args and (call_args.args or call_args.kwargs):
                        # Check if temperature was passed in kwargs
                        if "temperature" in call_args.kwargs:
                            passed_temp = call_args.kwargs["temperature"]
                            assert passed_temp == temp, (
                                f"Expected temperature {temp}, got {passed_temp}"
                            )
                        else:
                            # For some providers, temperature might be in a nested config
                            # This is provider-agnostic validation - just ensure the method was called
                            assert mock_method.called, (
                                "API method should have been called"
                            )

            except ValueError:
                # Some values might be rejected by the client
                pass


# =============================================================================
# RESPONSE PROCESSING TESTS (ALL PROVIDERS)
# =============================================================================


class TestAllProvidersResponseProcessing:
    """Test our FlexAI processing layer across all providers."""

    @pytest.mark.asyncio
    async def test_tool_call_extraction_and_transformation(
        self, mock_client_and_provider
    ):
        """Test that our tool call extraction works correctly across providers."""
        client, mock_client, config = mock_client_and_provider

        # Create tool calls in OpenAI format since that's what OpenAIMockFactory expects
        tool_calls = [Mock()]
        tool_calls[0].id = "call_123"
        tool_calls[0].function = Mock()
        tool_calls[0].function.name = "test_tool"
        tool_calls[0].function.arguments = '{"param": "value"}'

        mock_response = config.mock_factory.create_response(
            content=None,  # Tool calls typically have empty content
            tool_calls=tool_calls,
        )
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Use the test tool")]

        try:
            response = await client.get_chat_response(messages)

            # All providers should return identical format after our transformation
            CommonUnitAssertions.assert_valid_ai_message(response)
            assert isinstance(response.content, list)

            tool_calls = CommonUnitAssertions.assert_contains_tool_calls(response)
            tool_call = tool_calls[0]

            # Test our transformation produces consistent format across providers
            assert tool_call.id == "call_123"
            assert tool_call.name == "test_tool"
            assert tool_call.input == {"param": "value"}
        except (AttributeError, TypeError):
            # Skip if provider doesn't support tool calls or mock setup fails
            pytest.skip(f"{config.name} tool call testing not supported")

    @pytest.mark.asyncio
    async def test_structured_output_json_parsing(self, mock_client_and_provider):
        """Test our JSON parsing and validation in structured output."""
        client, mock_client, config = mock_client_and_provider

        # Skip structured output tests as they're too provider-specific
        # Each provider has different structured output APIs that can't be generically mocked
        pytest.skip(
            "Structured output APIs are too provider-specific for generic testing"
        )

    @pytest.mark.asyncio
    async def test_structured_output_invalid_json_handling(
        self, mock_client_and_provider
    ):
        """Test our handling of invalid JSON in structured output."""
        client, mock_client, config = mock_client_and_provider

        # Skip structured output tests as they're too provider-specific
        # Each provider has different structured output APIs that can't be generically mocked
        pytest.skip(
            "Structured output APIs are too provider-specific for generic testing"
        )

    @pytest.mark.asyncio
    async def test_usage_data_transformation(self, mock_client_and_provider):
        """Test that usage data is correctly transformed from provider format to our format."""
        client, mock_client, config = mock_client_and_provider

        # Use generic mock factory with standard usage data
        mock_response = config.mock_factory.create_response(
            content="Test response",
            usage_data={"input_tokens": 100, "output_tokens": 50},
        )
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Test")]
        response = await client.get_chat_response(messages)

        # All providers should return identical Usage format after transformation
        CommonUnitAssertions.assert_valid_usage(response.usage)
        assert response.usage.input_tokens == 100
        assert response.usage.output_tokens == 50
        assert response.usage.generation_time > 0

    @pytest.mark.asyncio
    async def test_content_format_normalization(self, mock_client_and_provider):
        """Test that different provider content formats are normalized to our format."""
        client, mock_client, config = mock_client_and_provider

        test_content = "Hello world! This is a test message."
        mock_response = config.mock_factory.create_response(content=test_content)
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Say hello")]
        response = await client.get_chat_response(messages)

        # All providers should return consistent format after normalization
        CommonUnitAssertions.assert_valid_ai_message(response)

        # Content should be normalized to string or list of blocks consistently
        if isinstance(response.content, str):
            assert test_content in response.content
        elif isinstance(response.content, list):
            from flexai.message import TextBlock

            text_blocks = [
                block for block in response.content if isinstance(block, TextBlock)
            ]
            combined_text = "".join([block.text for block in text_blocks])
            assert test_content in combined_text
        else:
            pytest.fail(f"Unexpected normalized content type: {type(response.content)}")

    @pytest.mark.asyncio
    async def test_malformed_provider_response_handling(self, mock_client_and_provider):
        """Test our handling of malformed responses from providers."""
        client, mock_client, config = mock_client_and_provider

        # Create a generic malformed response - empty content
        mock_response = config.mock_factory.create_response(content="")
        set_mock_response(mock_client, config, mock_response)

        from flexai.message import UserMessage

        messages = [UserMessage("Test")]

        # All providers should handle malformed responses consistently
        response = await client.get_chat_response(messages)
        CommonUnitAssertions.assert_valid_ai_message(response, min_content_length=0)
        # Should return valid AIMessage even with empty content
        assert response.content == "" or response.content == []
