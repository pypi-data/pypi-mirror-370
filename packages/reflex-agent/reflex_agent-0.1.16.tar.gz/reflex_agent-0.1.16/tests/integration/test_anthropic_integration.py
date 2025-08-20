"""Integration tests for Anthropic client.

These tests use real API calls and require ANTHROPIC_API_KEY to be set.
Run with: pytest tests/integration/test_anthropic_integration.py -v

This file demonstrates how to reuse the generic test utilities for a new provider.
"""

import os

# Import test constants
import sys

import pytest

from flexai import Agent, UserMessage
from flexai.llm.anthropic import AnthropicClient
from flexai.message import AIMessage, TextBlock

# Import shared utilities
from .utils import (
    # Assertions
    CommonAssertions,
    MathResult,
    # Models
    Person,
    # Tool fixtures
    ProviderConfig,
    # Test data
    TestMessages,
    agent_integration_template,
    # Generic test templates
    basic_chat_template,
    multi_turn_template,
    # Helpers
    multiple_models_helper,
    streaming_template,
    structured_output_template,
    system_message_template,
    temperature_control_template,
    tool_calling_template,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.constants import AnthropicModels

# =============================================================================
# ANTHROPIC-SPECIFIC CONFIGURATIONS
# =============================================================================

# Skip condition for Anthropic tests
skip_no_anthropic = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping Anthropic integration tests",
)


class AnthropicConfig(ProviderConfig):
    """Configuration for Anthropic provider."""

    BASIC_MODEL = AnthropicModels.BASIC_MODEL
    STRUCTURED_MODEL = AnthropicModels.STRUCTURED_MODEL
    MODELS_TO_TEST = AnthropicModels.MODELS_TO_TEST


# Apply skip condition to all tests in this file
pytestmark = skip_no_anthropic


# =============================================================================
# ANTHROPIC-SPECIFIC FIXTURES
# =============================================================================


@pytest.fixture
def anthropic_client():
    """Create an Anthropic client for basic testing."""
    return AnthropicClient(model=AnthropicConfig.BASIC_MODEL, max_tokens=4096)


@pytest.fixture
def anthropic_structured_client():
    """Create an Anthropic client for structured output testing."""
    return AnthropicClient(model=AnthropicConfig.STRUCTURED_MODEL, max_tokens=4096)


class TestAnthropicIntegration:
    """Integration tests for Anthropic client."""

    async def test_basic_chat_response(self, anthropic_client):
        """Test basic chat functionality with Anthropic."""
        await basic_chat_template(anthropic_client)

    async def test_system_message(self, anthropic_client):
        """Test chat with system message."""
        await system_message_template(anthropic_client)

    async def test_structured_output(self, anthropic_structured_client):
        """Test structured output with Pydantic models."""
        await structured_output_template(
            anthropic_structured_client, Person, expected_field_value="teacher"
        )

    async def test_structured_output_math(self, anthropic_structured_client):
        """Test structured output with a math problem."""
        await structured_output_template(anthropic_structured_client, MathResult)

    async def test_tool_calling(self, anthropic_client, math_tool):
        """Test tool calling functionality."""
        await tool_calling_template(anthropic_client, math_tool)

    async def test_streaming_response(self, anthropic_client):
        """Test streaming chat responses."""
        await streaming_template(anthropic_client)

    async def test_agent_integration(self, anthropic_client):
        """Test using Anthropic client with Agent."""
        await agent_integration_template(anthropic_client)

    async def test_agent_streaming(self, anthropic_client):
        """Test agent streaming with Anthropic client using run method."""
        agent = Agent(
            llm=anthropic_client,
            prompt="You are a storyteller. Tell very short stories.",
        )

        chunks = []
        # Enable streaming to get multiple chunks
        async for chunk in agent.run(TestMessages.STREAMING_STORY, stream=True):
            chunks.append(chunk)
            if len(chunks) > 20:  # Safety limit
                break

        # With streaming enabled, we should get at least one chunk
        assert len(chunks) >= 1

        # Should have some message content - could be TextBlocks or Messages
        message_chunks = [
            chunk
            for chunk in chunks
            if isinstance(chunk, (AIMessage, TextBlock)) or hasattr(chunk, "content")
        ]
        assert len(message_chunks) > 0

    async def test_error_handling(self, anthropic_structured_client):
        """Test error handling with invalid structured output."""
        # Use a more explicit request that should definitely not match Person schema
        messages = [
            UserMessage(
                "Return only the number 42 and nothing else. No names, no ages, no occupations."
            )
        ]

        # This should fail because the response won't match the Person schema
        try:
            result = await anthropic_structured_client.get_structured_response(
                messages, Person
            )
            # If it didn't raise an error, check if the result is actually valid
            if (
                hasattr(result, "name")
                and hasattr(result, "age")
                and hasattr(result, "occupation")
            ):
                # Model provided a valid Person structure - this is acceptable
                pass
            else:
                # Result is malformed
                pytest.fail(
                    f"Expected either ValueError or valid Person, got: {result}"
                )
        except (ValueError, TypeError):
            # This is the expected behavior - the parsing failed
            pass

    async def test_different_anthropic_models(self):
        """Test different Anthropic models."""
        test_message = UserMessage("Say 'success' if you can read this")

        def assert_success_response(response):
            CommonAssertions.assert_valid_response(response)
            assert "success" in str(response.content).lower()

        def anthropic_client_factory(model):
            # Use 4096 max_tokens to be compatible with all models
            return AnthropicClient(model=model, max_tokens=4096)

        results = await multiple_models_helper(
            anthropic_client_factory,
            AnthropicConfig.MODELS_TO_TEST,
            test_message,
            assert_success_response,
        )

        # All models should pass
        for model, result in results.items():
            if result != "passed":
                pytest.fail(f"Model {model} failed: {result}")

    async def test_temperature_control(self, anthropic_client):
        """Test that temperature affects response diversity."""
        await temperature_control_template(anthropic_client)

    async def test_multi_turn_conversation(self, anthropic_client):
        """Test maintaining conversation state across multiple turns."""
        await multi_turn_template(anthropic_client)
