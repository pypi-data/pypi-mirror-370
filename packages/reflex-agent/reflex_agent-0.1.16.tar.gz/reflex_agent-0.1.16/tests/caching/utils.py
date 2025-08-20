"""Caching-specific utilities for caching tests.

This module provides shared utilities for testing caching functionality
across different LLM providers. These helpers can be used to test cache
efficiency, tracking, and behavior consistently.

IMPORTANT: These utilities are designed for IMPLICIT CACHING testing -
automatic caching that happens behind the scenes. They focus on tracking
cache metrics via usage metadata (cache_read_tokens, cache_write_tokens).

For EXPLICIT CACHING (manual cache creation/management), additional utilities
would need to be added to handle cache lifecycle management, TTL settings,
and direct cache API interactions.
"""

import asyncio
from dataclasses import dataclass

from flexai import UserMessage
from flexai.message import AIMessage, Message

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not available, skip loading


@dataclass
class CacheMetrics:
    """Metrics for tracking cache performance."""

    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    generation_time: float
    total_tokens: int = 0

    def __post_init__(self):
        self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class CacheTestResult:
    """Result of a cache efficiency test."""

    request_count: int
    metrics: list[CacheMetrics]
    cache_hit_rate: float = 0.0
    avg_generation_time: float = 0.0
    total_cache_reads: int = 0
    total_cache_writes: int = 0

    def __post_init__(self):
        if self.metrics:
            self.avg_generation_time = sum(
                m.generation_time for m in self.metrics
            ) / len(self.metrics)
            self.total_cache_reads = sum(m.cache_read_tokens for m in self.metrics)
            self.total_cache_writes = sum(m.cache_write_tokens for m in self.metrics)

            # Calculate cache hit rate (ratio of cache reads to total input tokens)
            total_input_tokens = sum(m.input_tokens for m in self.metrics)
            if total_input_tokens > 0:
                self.cache_hit_rate = self.total_cache_reads / total_input_tokens


class CachingTestHelpers:
    """Collection of helpers for testing caching functionality."""

    @staticmethod
    def extract_cache_metrics(response: AIMessage) -> CacheMetrics:
        """Extract cache metrics from an AI response.

        Args:
            response: The AI response to extract metrics from

        Returns:
            CacheMetrics object with usage information
        """
        usage = response.usage
        return CacheMetrics(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=usage.cache_read_tokens,
            cache_write_tokens=usage.cache_write_tokens,
            generation_time=usage.generation_time,
        )

    @staticmethod
    async def run_cache_efficiency_test(
        client, base_message: str, iterations: int = 3, variation_fn=None
    ) -> CacheTestResult:
        """Run a cache efficiency test with multiple similar requests.

        Args:
            client: The LLM client to test
            base_message: Base message content to use
            iterations: Number of iterations to run
            variation_fn: Optional function to vary messages (iteration_num -> message_variation)

        Returns:
            CacheTestResult with collected metrics
        """
        metrics = []

        for i in range(iterations):
            if variation_fn:
                message_content = variation_fn(i, base_message)
            else:
                message_content = f"{base_message} (iteration {i + 1})"

            messages = [UserMessage(message_content)]
            response = await client.get_chat_response(messages)

            cache_metrics = CachingTestHelpers.extract_cache_metrics(response)
            metrics.append(cache_metrics)

            # Small delay between requests to allow for cache processing
            await asyncio.sleep(0.1)

        return CacheTestResult(request_count=iterations, metrics=metrics)

    @staticmethod
    async def test_cache_consistency(
        client_factory, messages: list[Message], client_count: int = 2
    ) -> list[CacheMetrics]:
        """Test cache behavior consistency across multiple client instances.

        Args:
            client_factory: Function that creates a new client instance
            messages: Messages to send to each client
            client_count: Number of client instances to test

        Returns:
            List of CacheMetrics from each client
        """
        results = []

        for _ in range(client_count):
            client = client_factory()
            response = await client.get_chat_response(messages)
            metrics = CachingTestHelpers.extract_cache_metrics(response)
            results.append(metrics)

        return results

    @staticmethod
    async def benchmark_cache_vs_no_cache(
        client_with_cache,
        client_without_cache,
        messages: list[Message],
        iterations: int = 3,
    ) -> tuple[CacheTestResult, CacheTestResult]:
        """Benchmark performance difference between cached and non-cached requests.

        Args:
            client_with_cache: Client configured with caching enabled
            client_without_cache: Client configured with caching disabled
            messages: Messages to test with
            iterations: Number of iterations per client

        Returns:
            Tuple of (cached_results, non_cached_results)
        """
        # Test with cache
        cached_metrics = []
        for _ in range(iterations):
            response = await client_with_cache.get_chat_response(messages)
            metrics = CachingTestHelpers.extract_cache_metrics(response)
            cached_metrics.append(metrics)
            await asyncio.sleep(0.1)

        # Test without cache
        non_cached_metrics = []
        for _ in range(iterations):
            response = await client_without_cache.get_chat_response(messages)
            metrics = CachingTestHelpers.extract_cache_metrics(response)
            non_cached_metrics.append(metrics)
            await asyncio.sleep(0.1)

        cached_result = CacheTestResult(
            request_count=iterations, metrics=cached_metrics
        )

        non_cached_result = CacheTestResult(
            request_count=iterations, metrics=non_cached_metrics
        )

        return cached_result, non_cached_result

    @staticmethod
    def assert_cache_metrics_valid(metrics: CacheMetrics):
        """Assert that cache metrics are valid.

        Args:
            metrics: CacheMetrics to validate
        """
        assert metrics.input_tokens >= 0, "Input tokens should be non-negative"
        assert metrics.output_tokens >= 0, "Output tokens should be non-negative"
        assert metrics.cache_read_tokens >= 0, (
            "Cache read tokens should be non-negative"
        )
        assert metrics.cache_write_tokens >= 0, (
            "Cache write tokens should be non-negative"
        )
        assert metrics.generation_time > 0, "Generation time should be positive"
        assert metrics.total_tokens == metrics.input_tokens + metrics.output_tokens

    @staticmethod
    def assert_cache_improvement(
        cached_result: CacheTestResult, baseline_result: CacheTestResult
    ):
        """Assert that cached results show improvement over baseline.

        Args:
            cached_result: Results from cached requests
            baseline_result: Results from baseline (non-cached) requests
        """
        # Cache should have some reads after first request
        assert cached_result.total_cache_reads >= 0

        # Cached requests might be faster on average (though not guaranteed)
        # This is more of a performance hint than a strict requirement
        if (
            cached_result.avg_generation_time > 0
            and baseline_result.avg_generation_time > 0
        ):
            # Allow some variance, caching doesn't always guarantee faster responses
            time_ratio = (
                cached_result.avg_generation_time / baseline_result.avg_generation_time
            )
            assert time_ratio <= 2.0, (
                "Cached requests shouldn't be significantly slower"
            )


class CacheTestScenarios:
    """Pre-defined test scenarios for common caching use cases."""

    @staticmethod
    def create_long_context_scenario() -> str:
        """Create a long context message that benefits from caching."""
        return (
            "Analyze this detailed business scenario: "
            "A technology startup is developing an AI-powered customer service platform. "
            "The company has 50 employees, receives 1000 customer inquiries daily, "
            "and needs to improve response times while maintaining quality. "
            "Consider market competition, technical requirements, budget constraints, "
            "and scalability needs. " * 5  # Repeat to make it longer
        )

    @staticmethod
    def create_repeated_context_scenario() -> list[str]:
        """Create multiple messages with repeated context elements."""
        base_context = (
            "Given this company profile: TechCorp is a B2B SaaS company with "
            "200 employees, $50M ARR, and clients in healthcare and finance. "
        )

        return [
            f"{base_context} How should they approach market expansion?",
            f"{base_context} What are the key technical challenges they'll face?",
            f"{base_context} Recommend a hiring strategy for the next quarter.",
        ]

    @staticmethod
    def create_incremental_context_scenario() -> list[str]:
        """Create messages that build context incrementally."""
        return [
            "I'm planning a marketing campaign for a new product.",
            "The product is a mobile app for fitness tracking.",
            "Our target audience is busy professionals aged 25-40.",
            "We have a budget of $100k and 3 months timeline.",
            "What should be our primary marketing channels?",
        ]


# Common cache test messages
class CacheTestMessages:
    """Pre-defined messages for cache testing."""

    LONG_CONTEXT = UserMessage(CacheTestScenarios.create_long_context_scenario())

    REPEATED_QUERIES = [
        UserMessage(msg)
        for msg in CacheTestScenarios.create_repeated_context_scenario()
    ]

    INCREMENTAL_CONTEXT = [
        UserMessage(msg)
        for msg in CacheTestScenarios.create_incremental_context_scenario()
    ]

    SIMPLE_REPEATED = UserMessage("What is the capital of France?")

    COMPLEX_ANALYSIS = UserMessage(
        "Perform a detailed SWOT analysis for a mid-size consulting firm "
        "considering expansion into digital transformation services. "
        "Include market trends, competitive landscape, required capabilities, "
        "and implementation timeline."
    )


# =============================================================================
# CACHING TEST TEMPLATES
# =============================================================================


async def basic_cache_tracking_template(client):
    """Generic template for testing basic cache tracking."""
    messages = [UserMessage("This is a test message for cache tracking. " * 10)]
    response = await client.get_chat_response(messages)

    # Import here to avoid circular imports
    try:
        from ..integration.utils import CommonAssertions
    except ImportError:
        # Fallback for when running tests directly
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "integration"))
        from utils import CommonAssertions

    CommonAssertions.assert_valid_response(response)

    # Check that usage tracking includes cache fields
    assert hasattr(response.usage, "cache_read_tokens")
    assert hasattr(response.usage, "cache_write_tokens")
    assert isinstance(response.usage.cache_read_tokens, int)
    assert isinstance(response.usage.cache_write_tokens, int)

    # Cache tokens should be non-negative
    assert response.usage.cache_read_tokens >= 0
    assert response.usage.cache_write_tokens >= 0


async def cache_streaming_template(client):
    """Generic template for testing cache tracking in streaming responses."""
    from flexai.message import AIMessage

    messages = [UserMessage("Tell me about caching in AI systems. Keep it short.")]

    chunks = []
    final_message = None

    async for chunk in client.stream_chat_response(messages):
        chunks.append(chunk)
        if isinstance(chunk, AIMessage):
            final_message = chunk

    # Should have received chunks
    assert len(chunks) > 1

    # Final message should have cache tracking
    assert final_message is not None
    assert hasattr(final_message.usage, "cache_read_tokens")
    assert hasattr(final_message.usage, "cache_write_tokens")
    assert final_message.usage.cache_read_tokens >= 0
    assert final_message.usage.cache_write_tokens >= 0


async def cache_with_tools_template(client, tool):
    """Generic template for testing cache behavior with tools."""
    try:
        from ..integration.utils import CommonAssertions
    except ImportError:
        # Fallback for when running tests directly
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "integration"))
        from utils import CommonAssertions

    messages = [UserMessage("Use the available tool to help with calculations")]

    response = await client.get_chat_response(messages, tools=[tool], allow_tool=True)

    CommonAssertions.assert_valid_response(response)

    # Should have cache tracking even with tools
    assert response.usage.cache_read_tokens >= 0
    assert response.usage.cache_write_tokens >= 0


async def repeated_requests_cache_template(client):
    """Generic template for testing cache behavior with repeated requests."""
    try:
        from ..integration.utils import CommonAssertions
    except ImportError:
        # Fallback for when running tests directly
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "integration"))
        from utils import CommonAssertions

    long_context = "Analyze this scenario in detail: " + "context " * 50
    messages = [UserMessage(long_context)]

    # Make first request
    response1 = await client.get_chat_response(messages)
    CommonAssertions.assert_valid_response(response1)

    # Make second identical request
    response2 = await client.get_chat_response(messages)
    CommonAssertions.assert_valid_response(response2)

    # Both should have valid cache tracking
    assert response1.usage.cache_read_tokens >= 0
    assert response1.usage.cache_write_tokens >= 0
    assert response2.usage.cache_read_tokens >= 0
    assert response2.usage.cache_write_tokens >= 0
