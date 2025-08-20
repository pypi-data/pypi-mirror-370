"""Integration tests for OpenAI client.

These tests use real API calls and require OPENAI_API_KEY to be set.
Run with: pytest tests/integration/ -v
"""

import os
import sys

import pytest

from flexai import Agent, UserMessage
from flexai.llm import openai as openai_module
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

# Import test constants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.constants import OpenAIModels

# Use alias to avoid import conflicts
OpenAIClient = openai_module.OpenAIClient


# =============================================================================
# OPENAI-SPECIFIC CONFIGURATIONS
# =============================================================================

# Skip condition for OpenAI tests
skip_no_openai = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping OpenAI integration tests",
)


class OpenAIConfig(ProviderConfig):
    """Configuration for OpenAI provider."""

    BASIC_MODEL = OpenAIModels.BASIC_MODEL
    STRUCTURED_MODEL = OpenAIModels.STRUCTURED_MODEL
    MODELS_TO_TEST = OpenAIModels.MODELS_TO_TEST


# =============================================================================
# OPENAI-SPECIFIC FIXTURES
# =============================================================================


@pytest.fixture
def openai_client():
    """Create an OpenAI client for basic testing."""
    return OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url="https://api.openai.com/v1",
        model=OpenAIConfig.BASIC_MODEL,
    )


@pytest.fixture
def openai_structured_client():
    """Create an OpenAI client for structured output."""
    return OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url="https://api.openai.com/v1",
        model=OpenAIConfig.STRUCTURED_MODEL,
    )


# Apply skip condition to all tests in this file
pytestmark = skip_no_openai


class TestOpenAIIntegration:
    """Integration tests for OpenAI client."""

    async def test_basic_chat_response(self, openai_client):
        """Test basic chat functionality with OpenAI."""
        await basic_chat_template(openai_client)

    async def test_system_message(self, openai_client):
        """Test chat with system message."""
        await system_message_template(openai_client)

    async def test_structured_output(self, openai_structured_client):
        """Test structured output with Pydantic models."""
        await structured_output_template(
            openai_structured_client, Person, expected_field_value="teacher"
        )

    async def test_structured_output_math(self, openai_structured_client):
        """Test structured output with a math problem."""
        await structured_output_template(openai_structured_client, MathResult)

    async def test_tool_calling(self, openai_client, math_tool):
        """Test tool calling functionality."""
        await tool_calling_template(openai_client, math_tool)

    async def test_streaming_response(self, openai_client):
        """Test streaming chat responses."""
        await streaming_template(openai_client)

    async def test_agent_integration(self, openai_client):
        """Test using OpenAI client with Agent."""
        await agent_integration_template(openai_client)

    async def test_agent_streaming(self, openai_client):
        """Test agent streaming with OpenAI client using run method."""
        agent = Agent(
            llm=openai_client,
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

    async def test_error_handling(self, openai_structured_client):
        """Test error handling with invalid structured output."""
        # Use a more explicit request that should definitely not match Person schema
        messages = [
            UserMessage(
                "Return only the number 42 and nothing else. No names, no ages, no occupations."
            )
        ]

        # This should fail because the response won't match the Person schema
        # The model might try to be helpful and provide a valid Person anyway,
        # so we may need to be more aggressive
        try:
            result = await openai_structured_client.get_structured_response(
                messages, Person
            )
            # If it didn't raise an error, check if the result is actually valid
            # Sometimes the model is clever enough to provide valid data anyway
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

    async def test_different_openai_models(self):
        """Test different OpenAI models."""
        test_message = UserMessage("Say 'success' if you can read this")

        def assert_success_response(response):
            CommonAssertions.assert_valid_response(response)
            assert "success" in str(response.content).lower()

        def openai_client_factory(model):
            return OpenAIClient(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url="https://api.openai.com/v1",
                model=model,
            )

        results = await multiple_models_helper(
            openai_client_factory,
            OpenAIConfig.MODELS_TO_TEST,
            test_message,
            assert_success_response,
        )

        # All models should pass
        for model, result in results.items():
            if result != "passed":
                pytest.fail(f"Model {model} failed: {result}")

    async def test_temperature_control(self, openai_client):
        """Test that temperature affects response diversity."""
        await temperature_control_template(openai_client)

    async def test_multi_turn_conversation(self, openai_client):
        """Test maintaining conversation state across multiple turns."""
        await multi_turn_template(openai_client)
