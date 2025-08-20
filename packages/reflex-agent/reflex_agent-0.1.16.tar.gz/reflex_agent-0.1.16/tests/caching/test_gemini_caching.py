"""Caching tests for Gemini client.

These tests focus specifically on caching functionality and require GEMINI_API_KEY to be set.
Run with: pytest tests/caching/test_gemini_caching.py -v

IMPORTANT: These tests currently focus on IMPLICIT CACHING - automatic caching behavior
that occurs behind the scenes in Gemini 2.5 models. The tests verify that cache metrics
are properly tracked via cache_read_tokens and cache_write_tokens in usage metadata.

EXPLICIT CACHING (future enhancement): Google's Gemini API also supports explicit context
caching via the cachedContents API, which allows manual cache creation and management.
This would require extending the GeminiClient to expose cache management methods
like client.caches.create(), client.caches.get(), etc.

This file tests Gemini-specific caching behavior, efficiency, and token tracking.
"""

import os

import pytest

from flexai import UserMessage
from flexai.llm.gemini import GeminiClient
from tests.constants import GeminiModels

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not available, skip loading

# Import caching utilities
from tests.caching.utils import (
    CachingTestHelpers,
    basic_cache_tracking_template,
    cache_streaming_template,
    cache_with_tools_template,
    repeated_requests_cache_template,
)

# Import shared utilities from integration tests
from tests.integration.utils import CommonAssertions, create_math_tool

# =============================================================================
# GEMINI CACHING CONFIGURATIONS
# =============================================================================

# Skip condition for Gemini caching tests
skip_no_gemini = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set - skipping Gemini caching tests",
)


class GeminiCachingConfig:
    """Configuration for Gemini caching tests."""

    BASIC_MODEL = GeminiModels.CACHING_MODEL
    FLASH_MODEL = GeminiModels.FLASH_MODEL


# Apply skip condition to all tests in this file
pytestmark = skip_no_gemini


# =============================================================================
# GEMINI CACHING FIXTURES
# =============================================================================


@pytest.fixture
def gemini_client():
    """Create a Gemini client for caching tests using Vertex AI."""
    return GeminiClient(
        model=GeminiCachingConfig.BASIC_MODEL,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


@pytest.fixture
def gemini_flash_client():
    """Create a Gemini Flash client for caching tests using Vertex AI."""
    return GeminiClient(
        model=GeminiCachingConfig.FLASH_MODEL,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


@pytest.fixture
def gemini_thinking_client():
    """Create a Gemini client with thinking capabilities for caching tests using Vertex AI."""
    return GeminiClient(
        model=GeminiCachingConfig.BASIC_MODEL,
        default_thinking_budget=100,
        project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
        location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
        use_vertex=True,
    )


@pytest.fixture
def math_tool():
    """Create a math tool for caching tests."""
    return create_math_tool()


class TestGeminiBasicCaching:
    """Basic caching functionality tests for Gemini."""

    async def test_basic_cache_tracking(self, gemini_client):
        """Test basic cache tracking functionality."""
        await basic_cache_tracking_template(gemini_client)

    async def test_cache_streaming(self, gemini_client):
        """Test cache tracking in streaming responses."""
        await cache_streaming_template(gemini_client)

    async def test_cache_with_tools(self, gemini_client, math_tool):
        """Test cache behavior with tool calls."""
        await cache_with_tools_template(gemini_client, math_tool)

    async def test_repeated_requests_caching(self, gemini_client):
        """Test cache behavior with repeated requests."""
        await repeated_requests_cache_template(gemini_client)

    async def test_cache_metrics_validation(self, gemini_client):
        """Test that cache metrics are properly validated."""
        response = await gemini_client.get_chat_response(
            [UserMessage("Test cache metrics validation")]
        )

        CommonAssertions.assert_valid_response(response)
        metrics = CachingTestHelpers.extract_cache_metrics(response)
        CachingTestHelpers.assert_cache_metrics_valid(metrics)

    async def test_implicit_caching_actually_works(self, gemini_client):
        """Test that implicit caching actually provides cache hits on repeated requests."""
        import asyncio

        # Helper function to make a request with timeout and extract metrics
        async def make_request_with_timeout(messages, request_num):
            print(f"Making request {request_num}...")
            response = await asyncio.wait_for(
                gemini_client.get_chat_response(messages), timeout=120
            )
            CommonAssertions.assert_valid_response(response)
            metrics = CachingTestHelpers.extract_cache_metrics(response)
            print(
                f"Request {request_num} - Input: {metrics.input_tokens}, Cache reads: {metrics.cache_read_tokens}"
            )
            return metrics

        # Create large context that meets Gemini Pro's 2,048+ token requirement
        context_base = (
            "You are analyzing TechCorp Inc., a B2B SaaS analytics company. "
            "Founded in 2018, grew to 200+ employees, serves 500+ enterprise clients, "
            "processes 10TB daily data, $50M ARR, 40% growth, 95% retention. "
            "Tech stack: AWS microservices, Kubernetes, PostgreSQL, MongoDB, Kafka, "
            "React/TypeScript frontend, Python/Go backend, TensorFlow ML models. "
        ) * 50  # Repeat to ensure 2,048+ tokens

        try:
            # Try up to 10 requests, but exit early on first cache hit
            all_metrics = []
            max_requests = 10

            for request_num in range(1, max_requests + 1):
                # Generate a unique question for each request
                question = f"Question {request_num}: What aspect of TechCorp's strategy should be analyzed?"
                messages = [UserMessage(f"{context_base}\n\n{question}")]

                metrics = await make_request_with_timeout(messages, request_num)
                all_metrics.append(metrics)

                # Check for cache hits after the first request
                if request_num > 1 and metrics.cache_read_tokens > 0:
                    print(
                        f"🎯 EARLY SUCCESS: Cache hit detected on request {request_num}!"
                    )
                    print(f"   Cache reads: {metrics.cache_read_tokens} tokens")
                    break

                # Small delay between requests
                await asyncio.sleep(0.5)

            # Validate token requirement for Gemini Pro
            assert all_metrics[0].input_tokens >= 2048, (
                f"Context too small for Gemini Pro caching: {all_metrics[0].input_tokens} tokens (need 2,048+)"
            )

            # Check for cache hits in subsequent requests (excluding first)
            total_cache_reads = sum(m.cache_read_tokens for m in all_metrics[1:])

            # Print analysis
            print("\n=== IMPLICIT CACHING ANALYSIS ===")
            print(f"Model: {GeminiCachingConfig.BASIC_MODEL}")
            print(f"Requests made: {len(all_metrics)} of {max_requests} max")
            print(f"Input tokens: {[m.input_tokens for m in all_metrics]}")
            print(f"Cache reads: {[m.cache_read_tokens for m in all_metrics]}")
            print(f"Total cache reads in subsequent requests: {total_cache_reads}")

            # Assert that we got at least some cache hits
            assert total_cache_reads > 0, (
                f"Expected cache hits in subsequent requests with {all_metrics[0].input_tokens}+ token context, "
                f"but got 0 total cache reads after {len(all_metrics)} requests. Implicit caching may not be working."
            )

            # Calculate and report efficiency
            subsequent_input_tokens = sum(m.input_tokens for m in all_metrics[1:])
            efficiency = (total_cache_reads / subsequent_input_tokens) * 100
            cache_hit_request = next(
                (
                    i
                    for i, m in enumerate(all_metrics[1:], 2)
                    if m.cache_read_tokens > 0
                ),
                None,
            )

            print(f"✅ Cache hit achieved on request {cache_hit_request}")
            print(
                f"✅ Cache efficiency: {efficiency:.1f}% of subsequent tokens served from cache"
            )

        except asyncio.TimeoutError as e:
            print("❌ TIMEOUT: Request took longer than 2 minutes")
            raise AssertionError(
                "Caching test timed out - API calls taking too long"
            ) from e
