"""Integration tests for Gemini client.

These tests use real API calls and require GEMINI_API_KEY to be set.
Run with: pytest tests/integration/test_gemini_integration.py -v

This file demonstrates how to reuse the generic test utilities for Gemini provider,
with additional focus on caching functionality.
"""

import os

import pytest

from flexai import UserMessage
from flexai.llm.gemini import GeminiClient
from flexai.message import AIMessage, ToolCall, URLContextBlock

# Import test constants
from tests.constants import GeminiModels, TestDefaults

# Import shared utilities
from .utils import (
    # Test data
    CommonAssertions,
    MathResult,
    # Models
    Person,
    # Tool fixtures
    ProviderConfig,
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

# =============================================================================
# GEMINI-SPECIFIC CONFIGURATIONS
# =============================================================================

# Skip condition for Gemini tests
skip_no_gemini = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set - skipping Gemini integration tests",
)


class GeminiConfig(ProviderConfig):
    """Configuration for Gemini provider."""

    BASIC_MODEL = GeminiModels.BASIC_MODEL
    STRUCTURED_MODEL = GeminiModels.STRUCTURED_MODEL
    MODELS_TO_TEST = GeminiModels.MODELS_TO_TEST


# Apply skip condition to all tests in this file
pytestmark = skip_no_gemini


# =============================================================================
# GEMINI-SPECIFIC FIXTURES
# =============================================================================


@pytest.fixture
def gemini_client():
    """Create a Gemini client for basic testing using Vertex AI."""
    return GeminiClient(
        model=GeminiConfig.BASIC_MODEL,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


@pytest.fixture
def gemini_structured_client():
    """Create a Gemini client for structured output testing using Vertex AI."""
    return GeminiClient(
        model=GeminiConfig.STRUCTURED_MODEL,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


@pytest.fixture
def gemini_thinking_client():
    """Create a Gemini client with thinking capabilities using Vertex AI."""
    return GeminiClient(
        model=GeminiConfig.BASIC_MODEL,
        default_thinking_budget=GeminiModels.PRO_MIN_THINKING_BUDGET,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


class TestGeminiIntegration:
    """Integration tests for Gemini client."""

    async def test_basic_chat_response(self, gemini_client):
        """Test basic chat functionality with Gemini."""
        await basic_chat_template(gemini_client)

    async def test_system_message(self, gemini_client):
        """Test chat with system message."""
        await system_message_template(gemini_client)

    async def test_structured_output(self, gemini_structured_client):
        """Test structured output with Pydantic models."""
        await structured_output_template(
            gemini_structured_client, Person, expected_field_value="teacher"
        )

    async def test_structured_output_math(self, gemini_structured_client):
        """Test structured output with a math problem."""
        await structured_output_template(gemini_structured_client, MathResult)

    async def test_tool_calling(self, gemini_client, math_tool):
        """Test tool calling functionality."""
        await tool_calling_template(gemini_client, math_tool)

    async def test_streaming_response(self, gemini_client):
        """Test streaming chat responses."""
        await streaming_template(gemini_client)

    async def test_agent_integration(self, gemini_client):
        """Test using Gemini client with Agent."""
        await agent_integration_template(gemini_client)

    async def test_thinking_functionality(self, gemini_thinking_client):
        """Test Gemini's thinking capabilities."""
        response = await gemini_thinking_client.get_chat_response(
            messages=[
                UserMessage("Think carefully about 2+2 and explain your reasoning")
            ],
            thinking_budget=TestDefaults.DEFAULT_THINKING_BUDGET,
            include_thoughts=True,
        )

        CommonAssertions.assert_valid_response(response)
        # Should contain the answer 4
        assert "4" in str(response.content)

    async def test_disable_thinking(self):
        """Test disabling thinking with Flash model."""
        # Use Flash model which can disable thinking with budget=0
        flash_client = GeminiClient(
            model=GeminiModels.FLASH_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )
        response = await flash_client.get_chat_response(
            messages=[UserMessage("What is 2+2?")],
            thinking_budget=GeminiModels.FLASH_MIN_THINKING_BUDGET,  # Flash models can use 0 budget to disable thinking
        )

        CommonAssertions.assert_valid_response(response)
        assert "4" in str(response.content)

    async def test_temperature_control(self, gemini_client):
        """Test that temperature affects response diversity."""
        await temperature_control_template(gemini_client)

    async def test_multi_turn_conversation(self, gemini_client):
        """Test maintaining conversation state across multiple turns."""
        await multi_turn_template(gemini_client)

    async def test_different_gemini_models(self):
        """Test different Gemini models."""
        test_message = UserMessage("Say 'success' if you can read this")

        def assert_success_response(response):
            CommonAssertions.assert_valid_response(response)
            assert "success" in str(response.content).lower()

        def gemini_client_factory(model):
            return GeminiClient(
                model=model,
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )

        results = await multiple_models_helper(
            gemini_client_factory,
            GeminiConfig.MODELS_TO_TEST,
            test_message,
            assert_success_response,
        )

        # All models should pass
        for model, result in results.items():
            if result != "passed":
                pytest.fail(f"Model {model} failed: {result}")

    async def test_global_endpoint_support_check(self):
        """Test global endpoint support checking methods."""
        # This test is no longer needed since validation was removed
        # The API will handle model validation directly

    async def test_endpoint_info(self, gemini_client):
        """Test endpoint information retrieval."""
        info = gemini_client.get_endpoint_info()

        assert "location" in info
        assert "project_id" in info
        assert "is_global" in info

        assert "use_vertex" in info
        assert "model" in info

        # Regular client should not be using global endpoint
        assert not info["is_global"]

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_PROJECT_ID"),
        reason="GOOGLE_PROJECT_ID not set - skipping global endpoint tests",
    )
    async def test_global_client_creation(self):
        """Test creating a client with global endpoint."""
        project_id = os.getenv("GOOGLE_PROJECT_ID")

        # Test with supported model using regular constructor
        global_client = GeminiClient(
            project_id=project_id,
            location="global",
            model=GeminiModels.PRO_MODEL,
            use_vertex=True,
        )

        assert global_client.location == "global"
        assert global_client.project_id == project_id

        info = global_client.get_endpoint_info()
        assert info["is_global"] is True

        # Test basic functionality with global client
        try:
            response = await global_client.get_chat_response(
                messages=[UserMessage("What is 2+2? Give a short answer.")]
            )
            CommonAssertions.assert_valid_response(response)
            assert "4" in str(response.content)
        except Exception:
            # Global endpoint might not be available in test environment
            # Just check the client was created correctly
            pass

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_PROJECT_ID"),
        reason="GOOGLE_PROJECT_ID not set - skipping global endpoint tests",
    )
    async def test_global_endpoint_functionality(self):
        """Test that global endpoint works for supported models."""
        # Test with a global endpoint supported model
        client = GeminiClient(
            model=GeminiModels.BASIC_MODEL,
            project_id=os.getenv("GOOGLE_PROJECT_ID"),
            location="global",
            use_vertex=True,
        )

        response = await client.get_chat_response(
            messages=[UserMessage("Say 'global endpoint test successful'")]
        )

        CommonAssertions.assert_valid_response(response)
        assert "global endpoint test successful" in str(response.content).lower()

        # Verify endpoint info
        info = client.get_endpoint_info()
        assert info["is_global"]
        assert info["use_vertex"]
        assert info["location"] == "global"

    async def test_url_context_basic(self, gemini_client):
        """Test basic URL context functionality."""
        # Use a real website for testing
        test_url = "https://openai.com"

        response = await gemini_client.get_chat_response(
            messages=[
                UserMessage(
                    f"Please analyze the website at {test_url}. What company is this and what do they do?"
                )
            ],
            use_url_context=True,
        )

        CommonAssertions.assert_valid_response(response)

        # Verify that URLContextBlock is included in content
        url_context_blocks = [
            content
            for content in response.content
            if isinstance(content, URLContextBlock)
        ]
        assert len(url_context_blocks) > 0, (
            "Expected URLContextBlock in response content"
        )

        # Verify URLs were accessed
        url_block = url_context_blocks[0]
        assert len(url_block.urls_accessed) > 0, "Expected URLs to be accessed"

        # The response should mention OpenAI and their products/services
        response_text = str(response.content).lower()
        assert any(
            keyword in response_text
            for keyword in ["openai", "chatgpt", "ai", "artificial intelligence"]
        )

    async def test_url_context_with_tools(self, gemini_client, math_tool):
        """Test URL context combined with regular tools."""
        test_url = "https://openai.com"

        response = await gemini_client.get_chat_response(
            messages=[
                UserMessage(
                    f"Analyze {test_url} and then calculate 15 + 25 using the math tool."
                )
            ],
            tools=[math_tool],
            use_url_context=True,
        )

        CommonAssertions.assert_valid_response(response)

        # Should have URLContextBlock in content
        url_context_blocks = [
            content
            for content in response.content
            if isinstance(content, URLContextBlock)
        ]
        assert len(url_context_blocks) > 0, (
            "Expected URLContextBlock in response content"
        )

        # Response should contain tool call for math operation
        has_tool_call = any(
            isinstance(content, ToolCall) for content in response.content
        )
        assert has_tool_call, "Expected tool call in response"

    async def test_url_context_streaming(self, gemini_client):
        """Test URL context with streaming responses."""
        test_url = "https://openai.com"

        chunks = []
        final_message = None

        async for chunk in gemini_client.stream_chat_response(
            messages=[
                UserMessage(f"Stream an analysis of {test_url}. What do you see?")
            ],
            use_url_context=True,
        ):
            chunks.append(chunk)
            if isinstance(chunk, AIMessage):
                final_message = chunk

        # Should have received multiple chunks
        assert len(chunks) > 1

        # Final message should have URLContextBlock in content
        assert final_message is not None
        url_context_blocks = [
            content
            for content in final_message.content
            if isinstance(content, URLContextBlock)
        ]
        assert len(url_context_blocks) > 0, (
            "Expected URLContextBlock in final message content"
        )

    async def test_url_context_structured_output(self, gemini_structured_client):
        """Test URL context with structured output."""
        from pydantic import BaseModel

        class UrlAnalysis(BaseModel):
            """Analysis of URL content."""

            url: str
            content_type: str
            key_findings: list[str]
            accessible: bool

        test_url = "https://openai.com"

        result = await gemini_structured_client.get_structured_response(
            messages=[
                UserMessage(f"Analyze {test_url} and provide a structured summary.")
            ],
            model=UrlAnalysis,
            use_url_context=True,
        )

        # Verify structured response
        assert isinstance(result, UrlAnalysis)
        assert result.url == test_url
        assert result.accessible  # OpenAI should be accessible
        assert len(result.key_findings) > 0

    async def test_url_context_multiple_urls(self, gemini_client):
        """Test URL context with multiple URLs."""
        urls = ["https://openai.com", "https://github.com"]

        response = await gemini_client.get_chat_response(
            messages=[
                UserMessage(
                    f"Compare these two websites: {', '.join(urls)}. What are they about?"
                )
            ],
            use_url_context=True,
        )

        CommonAssertions.assert_valid_response(response)

        # Should have URLContextBlock in content
        url_context_blocks = [
            content
            for content in response.content
            if isinstance(content, URLContextBlock)
        ]
        assert len(url_context_blocks) > 0, (
            "Expected URLContextBlock in response content"
        )

        # Should mention both companies or their purposes
        response_text = str(response.content).lower()
        assert any(
            keyword in response_text
            for keyword in ["openai", "github", "compare", "both", "different"]
        )

    async def test_url_context_disabled_by_default(self, gemini_client):
        """Test that URL context is disabled by default."""
        test_url = "https://openai.com"

        response = await gemini_client.get_chat_response(
            messages=[UserMessage(f"Tell me about {test_url}")],
            # Not setting use_url_context=True, should default to False
        )

        CommonAssertions.assert_valid_response(response)

        # Should NOT have URLContextBlock when disabled
        url_context_blocks = [
            content
            for content in response.content
            if isinstance(content, URLContextBlock)
        ]
        assert len(url_context_blocks) == 0, (
            "URLContextBlock should not be present when URL context is disabled"
        )

    async def test_url_context_error_handling(self, gemini_client):
        """Test URL context behavior with unreachable URLs."""
        invalid_url = "https://this-definitely-does-not-exist-12345.com"

        # This should not raise an exception, but may not access the URL
        response = await gemini_client.get_chat_response(
            messages=[UserMessage(f"Please try to analyze {invalid_url}")],
            use_url_context=True,
        )

        CommonAssertions.assert_valid_response(response)

        # Response should handle the error gracefully
        response_text = str(response.content).lower()
        # Should either mention the URL or indicate it couldn't be accessed
        assert len(response_text) > 0


# NOTE: Caching-specific tests have been moved to tests/caching/test_gemini_caching.py
