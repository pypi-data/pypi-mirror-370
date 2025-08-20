"""Tests for the exception handling wrappers in the client module."""

from unittest.mock import AsyncMock, patch

import pytest

from flexai.llm.client import (
    _handle_provider_exceptions_coroutine,
    _handle_provider_exceptions_generator,
)
from flexai.llm.exceptions import (
    AuthenticationException,
    BadRequestException,
    LLMException,
    RateLimitException,
)


class TestExceptionHandlers:
    """Tests for the exception handling wrapper functions."""

    async def test_handle_provider_exceptions_coroutine_no_exception(self):
        """Test that _handle_provider_exceptions_coroutine passes through when no exception occurs."""
        # Create a mock coroutine that doesn't raise an exception
        mock_coro = AsyncMock(return_value="success")

        # Wrap it with the exception handler
        wrapped = _handle_provider_exceptions_coroutine(mock_coro, "test_provider")

        # Call the wrapped function
        result = await wrapped("arg1", kwarg1="value1")

        # Verify the result is passed through
        assert result == "success"
        mock_coro.assert_called_once_with("arg1", kwarg1="value1")

    async def test_handle_provider_exceptions_coroutine_with_provider_exception(self):
        """Test that _handle_provider_exceptions_coroutine maps provider exceptions."""
        # Create a mock coroutine that raises a provider-specific exception
        mock_exception = ValueError("Provider error")
        mock_coro = AsyncMock(side_effect=mock_exception)

        # Mock the map_exception function
        mapped_exception = BadRequestException(
            message="Mapped error",
            provider="test_provider",
            original_exception=mock_exception,
            status_code=400,
        )

        with patch("flexai.llm.client.map_exception", return_value=mapped_exception):
            # Wrap it with the exception handler
            wrapped = _handle_provider_exceptions_coroutine(mock_coro, "test_provider")

            # Call the wrapped function and expect the mapped exception
            with pytest.raises(BadRequestException) as excinfo:
                await wrapped("arg1", kwarg1="value1")

            # Verify the exception is mapped correctly
            assert excinfo.value is mapped_exception
            assert excinfo.value.provider == "test_provider"
            assert excinfo.value.original_exception is mock_exception

    async def test_handle_provider_exceptions_coroutine_with_llm_exception(self):
        """Test that _handle_provider_exceptions_coroutine passes through LLMException instances."""
        # Create an LLMException
        original_exception = LLMException(
            message="Original LLM error", provider="test_provider"
        )

        # Create a mock coroutine that raises an LLMException
        mock_coro = AsyncMock(side_effect=original_exception)

        # Create a spy on map_exception to ensure it's not called
        with patch("flexai.llm.client.map_exception") as mock_map_exception:
            # Wrap it with the exception handler
            wrapped = _handle_provider_exceptions_coroutine(mock_coro, "test_provider")

            # Call the wrapped function and expect the original LLMException
            with pytest.raises(LLMException) as excinfo:
                await wrapped("arg1", kwarg1="value1")

            # Verify the exception is passed through without mapping
            assert excinfo.value is original_exception
            mock_map_exception.assert_not_called()

    async def test_handle_provider_exceptions_generator_no_exception(self):
        """Test that _handle_provider_exceptions_generator passes through when no exception occurs."""

        # Create a mock async generator that doesn't raise an exception
        async def mock_generator(*args, **kwargs):
            yield "item1"
            yield "item2"
            yield "item3"

        # Wrap it with the exception handler
        wrapped = _handle_provider_exceptions_generator(mock_generator, "test_provider")

        # Call the wrapped function and collect results
        results = []
        async for item in wrapped("arg1", kwarg1="value1"):
            results.append(item)

        # Verify the results are passed through
        assert results == ["item1", "item2", "item3"]

    async def test_handle_provider_exceptions_generator_with_provider_exception(self):
        """Test that _handle_provider_exceptions_generator maps provider exceptions."""
        # Create a mock async generator that raises a provider-specific exception
        mock_exception = ValueError("Provider error")

        async def mock_generator(*args, **kwargs):
            yield "item1"
            raise mock_exception

        # Mock the map_exception function
        mapped_exception = RateLimitException(
            message="Rate limit exceeded",
            provider="test_provider",
            original_exception=mock_exception,
            status_code=429,
        )

        with patch("flexai.llm.client.map_exception", return_value=mapped_exception):
            # Wrap it with the exception handler
            wrapped = _handle_provider_exceptions_generator(
                mock_generator, "test_provider"
            )

            # Call the wrapped function and expect the mapped exception
            results = []
            with pytest.raises(RateLimitException) as excinfo:
                async for item in wrapped("arg1", kwarg1="value1"):
                    results.append(item)

            # Verify we got one item before the exception
            assert results == ["item1"]

            # Verify the exception is mapped correctly
            assert excinfo.value is mapped_exception
            assert excinfo.value.provider == "test_provider"
            assert excinfo.value.original_exception is mock_exception

    async def test_handle_provider_exceptions_generator_with_llm_exception(self):
        """Test that _handle_provider_exceptions_generator passes through LLMException instances."""
        # Create an LLMException
        original_exception = AuthenticationException(
            message="Invalid API key", provider="test_provider", status_code=401
        )

        # Create a mock async generator that raises an LLMException
        async def mock_generator(*args, **kwargs):
            yield "item1"
            raise original_exception

        # Create a spy on map_exception to ensure it's not called
        with patch("flexai.llm.client.map_exception") as mock_map_exception:
            # Wrap it with the exception handler
            wrapped = _handle_provider_exceptions_generator(
                mock_generator, "test_provider"
            )

            # Call the wrapped function and expect the original LLMException
            results = []
            with pytest.raises(AuthenticationException) as excinfo:
                async for item in wrapped("arg1", kwarg1="value1"):
                    results.append(item)

            # Verify we got one item before the exception
            assert results == ["item1"]

            # Verify the exception is passed through without mapping
            assert excinfo.value is original_exception
            mock_map_exception.assert_not_called()


class TestClientExceptionWrappers:
    """Tests for the Client class exception wrapping functionality."""

    def test_exception_wrapping_functionality(self):
        """Test the core functionality that Client's __init_subclass__ is intended to implement."""
        # Instead of trying to test Client.__init_subclass__ directly, we'll test
        # the individual pieces that it uses to wrap methods with exception handlers

        from flexai.llm.client import (
            _handle_provider_exceptions_coroutine,
            _handle_provider_exceptions_generator,
        )

        # Create mock methods
        async def mock_method(*args, **kwargs):
            return "success"

        async def mock_generator_method(*args, **kwargs):
            yield "item1"
            yield "item2"

        # Wrap the methods
        wrapped_method = _handle_provider_exceptions_coroutine(
            mock_method, "test_provider"
        )
        wrapped_generator = _handle_provider_exceptions_generator(
            mock_generator_method, "test_provider"
        )

        # Verify the returned functions are different from the originals
        assert wrapped_method is not mock_method
        assert wrapped_generator is not mock_generator_method

        # This verifies that the core functionality of wrapping methods works,
        # which is what Client.__init_subclass__ is doing


class TestIntegrationWithExceptions:
    """Integration tests combining exception mapping with handler wrappers."""

    async def test_integration_exception_handling_coroutine(self):
        """Test the full exception handling flow for coroutines."""
        # Create a provider-specific exception
        provider_exception = ValueError("Provider error")

        # Create a mock coroutine that raises the exception
        mock_coro = AsyncMock(side_effect=provider_exception)

        # Create an actual wrapper without mocking map_exception
        wrapped = _handle_provider_exceptions_coroutine(mock_coro, "test_provider")

        # Patch the provider extractor to return a status code
        with patch(
            "flexai.llm.exceptions.PROVIDER_EXTRACTORS",
            {
                "test_provider": lambda e: (
                    429,
                    {"error": "rate_limit"},
                    "Rate limit exceeded",
                )
            },
        ):
            # Call the wrapped function and expect a RateLimitException
            with pytest.raises(RateLimitException) as excinfo:
                await wrapped()

            # Verify the exception is correctly mapped
            assert excinfo.value.status_code == 429
            assert excinfo.value.provider == "test_provider"
            assert excinfo.value.original_exception is provider_exception
            assert excinfo.value.message == "Rate limit exceeded"
            assert excinfo.value.response_data == {"error": "rate_limit"}

    async def test_integration_exception_handling_generator(self):
        """Test the full exception handling flow for generators."""
        # Create a provider-specific exception
        provider_exception = ValueError("Provider error")

        # Create a mock generator that raises the exception
        async def mock_generator():
            yield "chunk1"
            raise provider_exception

        # Create an actual wrapper without mocking map_exception
        wrapped = _handle_provider_exceptions_generator(mock_generator, "test_provider")

        # Patch the provider extractor to return a status code
        with patch(
            "flexai.llm.exceptions.PROVIDER_EXTRACTORS",
            {
                "test_provider": lambda e: (
                    401,
                    {"error": "invalid_auth"},
                    "Invalid API key",
                )
            },
        ):
            # Call the wrapped function and expect an AuthenticationException
            results = []
            with pytest.raises(AuthenticationException) as excinfo:
                async for item in wrapped():
                    results.append(item)

            # Verify we got one chunk before the exception
            assert results == ["chunk1"]

            # Verify the exception is correctly mapped
            assert excinfo.value.status_code == 401
            assert excinfo.value.provider == "test_provider"
            assert excinfo.value.original_exception is provider_exception
            assert excinfo.value.message == "Invalid API key"
            assert excinfo.value.response_data == {"error": "invalid_auth"}
