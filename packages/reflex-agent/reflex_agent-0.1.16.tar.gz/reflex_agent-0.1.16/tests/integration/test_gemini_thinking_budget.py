"""Integration tests for Gemini thinking budget functionality.

These tests verify that thinking budget parameters are accepted and work
correctly with Gemini 2.5 Pro and Flash models.

Based on: https://ai.google.dev/gemini-api/docs/thinking#set-budget

Run with: pytest tests/integration/test_gemini_thinking_budget.py -v
"""

import os

import pytest

from flexai import UserMessage
from flexai.llm.gemini import GeminiClient
from tests.constants import GeminiModels

# Import shared utilities
from tests.integration.utils import CommonAssertions

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not available, skip loading


# =============================================================================
# THINKING TEST CONFIGURATION
# =============================================================================

# Skip condition for Gemini tests
skip_no_gemini = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set - skipping Gemini thinking integration tests",
)

# Apply skip condition to all tests in this file
pytestmark = skip_no_gemini


class ThinkingTestConfig:
    """Configuration for thinking-specific tests."""

    # Gemini 2.5 models that support thinking
    PRO_MODEL = GeminiModels.PRO_MODEL  # Min thinking budget: 128
    FLASH_MODEL = (
        GeminiModels.FLASH_MODEL
    )  # Min thinking budget: 0 (can disable thinking)

    # Test prompts
    SIMPLE_TASK = "What is 15 + 27? Show your work."
    COMPLEX_TASK = (
        "A train leaves station A at 2 PM traveling at 60 mph. "
        "Another train leaves station B at 3 PM traveling at 80 mph toward station A. "
        "If the stations are 300 miles apart, at what time will they meet?"
    )


# =============================================================================
# THINKING BUDGET TESTS
# =============================================================================


class TestThinkingBudget:
    """Test thinking budget functionality on Gemini 2.5 models."""

    async def test_thinking_budget_pro_model(self):
        """Test thinking budget with Gemini Pro model."""
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with thinking budget
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.COMPLEX_TASK)],
            thinking_budget=1024,
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0

        # Response should contain the mathematical concepts
        response_text = str(response.content).lower()
        assert any(word in response_text for word in ["time", "meet", "hour", "miles"])

        print(f"Pro model response length: {len(str(response.content))} characters")

    async def test_thinking_budget_flash_model(self):
        """Test thinking budget with Gemini Flash model."""
        client = GeminiClient(
            model=ThinkingTestConfig.FLASH_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with thinking budget
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.COMPLEX_TASK)],
            thinking_budget=1024,
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0

        # Response should contain the mathematical concepts
        response_text = str(response.content).lower()
        assert any(word in response_text for word in ["time", "meet", "hour", "miles"])

        print(f"Flash model response length: {len(str(response.content))} characters")

    async def test_different_thinking_budgets(self):
        """Test different thinking budget values."""
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        budgets = [GeminiModels.PRO_MIN_THINKING_BUDGET, 512, 1024, 2048]
        results = []

        for budget in budgets:
            response = await client.get_chat_response(
                messages=[UserMessage(ThinkingTestConfig.SIMPLE_TASK)],
                thinking_budget=budget,
            )

            CommonAssertions.assert_valid_response(response)
            response_length = len(str(response.content))
            results.append((budget, response_length))

            # Should contain the answer 42
            assert "42" in str(response.content)

        # Print results for analysis
        print("\nThinking Budget Results:")
        for budget, length in results:
            print(f"Budget {budget}: {length} characters")

        # All responses should be valid
        assert all(length > 0 for _, length in results)

    async def test_pro_minimal_thinking_budget(self):
        """Test Pro model with minimal thinking budget (128)."""
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with minimal thinking budget (128 is minimum for Pro models)
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.SIMPLE_TASK)],
            thinking_budget=GeminiModels.PRO_MIN_THINKING_BUDGET,  # Minimal budget for Pro models
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0

        # Should still contain the answer
        assert "42" in str(response.content)

        print(
            f"Pro response with minimal thinking budget (128): {len(str(response.content))} characters"
        )

    async def test_include_thoughts_parameter(self):
        """Test the include_thoughts parameter."""
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with include_thoughts enabled
        response = await client.get_chat_response(
            messages=[UserMessage("Think step by step: What is 8 × 7?")],  # noqa: RUF001
            thinking_budget=512,
            include_thoughts=True,
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0

        # Should contain the answer 56
        assert "56" in str(response.content)

        print(
            f"Response with include_thoughts: {len(str(response.content))} characters"
        )

    async def test_model_comparison(self):
        """Compare thinking behavior between Pro and Flash models."""
        task = "Explain why 2 + 2 = 4 using basic mathematical principles."

        pro_client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )
        flash_client = GeminiClient(
            model=ThinkingTestConfig.FLASH_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test both models with same thinking budget
        pro_response = await pro_client.get_chat_response(
            messages=[UserMessage(task)], thinking_budget=512
        )

        flash_response = await flash_client.get_chat_response(
            messages=[UserMessage(task)], thinking_budget=512
        )

        # Both should produce valid responses
        CommonAssertions.assert_valid_response(pro_response)
        CommonAssertions.assert_valid_response(flash_response)

        pro_length = len(str(pro_response.content))
        flash_length = len(str(flash_response.content))

        print(f"Pro model response: {pro_length} characters")
        print(f"Flash model response: {flash_length} characters")

        # Both should contain mathematical concepts
        for response in [pro_response, flash_response]:
            response_text = str(response.content).lower()
            assert any(
                term in response_text
                for term in ["addition", "math", "number", "equal"]
            )

    async def test_default_thinking_budget(self):
        """Test client with default thinking budget."""
        # Create client with default thinking budget
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            default_thinking_budget=256,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Call without specifying thinking_budget (should use default)
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.SIMPLE_TASK)]
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0
        assert "42" in str(response.content)

        print(
            f"Response with default thinking budget: {len(str(response.content))} characters"
        )

    async def test_override_default_thinking_budget(self):
        """Test overriding default thinking budget with a specific value."""
        # Create client with default thinking budget
        client = GeminiClient(
            model=ThinkingTestConfig.PRO_MODEL,
            default_thinking_budget=512,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Override with a different thinking budget
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.SIMPLE_TASK)], thinking_budget=1024
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0
        assert "42" in str(response.content)

        print(
            f"Response with overridden thinking budget: {len(str(response.content))} characters"
        )

    async def test_flash_thinking_disabled(self):
        """Test that Flash model can work with thinking budget of 0."""
        client = GeminiClient(
            model=ThinkingTestConfig.FLASH_MODEL,
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Flash models can have thinking budget of 0 (disabled)
        response = await client.get_chat_response(
            messages=[UserMessage(ThinkingTestConfig.SIMPLE_TASK)], thinking_budget=0
        )

        CommonAssertions.assert_valid_response(response)
        assert len(str(response.content)) > 0

        # Should still contain the answer
        assert "42" in str(response.content)

        print(
            f"Flash response with thinking disabled: {len(str(response.content))} characters"
        )
