"""Tests for the map_exception function and related exception handling functionality."""

from unittest.mock import MagicMock, patch

from flexai.llm.exceptions import (
    AuthenticationException,
    BadRequestException,
    LLMClientException,
    LLMException,
    LLMServerException,
    NotFoundException,
    PermissionDeniedException,
    RateLimitException,
    ServerException,
    extract_anthropic_details,
    extract_gemini_details,
    extract_openai_details,
    map_exception,
)


class TestMapException:
    """Tests for map_exception function."""

    def test_map_exception_with_status_code(self):
        """Test map_exception maps to correct exception types based on status code."""
        # Create a mock exception with a status code
        original_exception = Exception("Test exception")

        # Test common status codes
        test_cases = [
            (400, BadRequestException),
            (401, AuthenticationException),
            (403, PermissionDeniedException),
            (404, NotFoundException),
            (429, RateLimitException),
            (500, ServerException),
        ]

        for status_code, expected_class in test_cases:
            # Create a mock extractor that returns the status code
            with patch(
                "flexai.llm.exceptions.PROVIDER_EXTRACTORS",
                {
                    "test_provider": lambda e, status_code=status_code: (
                        status_code,
                        None,
                        "Error message",
                    )
                },
            ):
                result = map_exception(original_exception, "test_provider")

            # Verify the exception is mapped correctly
            assert isinstance(result, expected_class)
            assert result.status_code == status_code
            assert result.provider == "test_provider"
            assert result.original_exception == original_exception

    def test_map_exception_without_status_code(self):
        """Test map_exception returns generic LLMException when no status code is available."""
        original_exception = Exception("Test exception with no status")

        # Create a mock extractor that returns no status code
        with patch(
            "flexai.llm.exceptions.PROVIDER_EXTRACTORS",
            {"test_provider": lambda e: (None, None, "Error message")},
        ):
            result = map_exception(original_exception, "test_provider")

        # Should return a generic LLMException
        assert isinstance(result, LLMException)
        assert not isinstance(result, LLMClientException)
        assert not isinstance(result, LLMServerException)
        assert result.status_code is None
        assert result.provider == "test_provider"
        assert result.original_exception == original_exception

    def test_map_exception_unknown_provider(self):
        """Test map_exception with an unknown provider falls back to default behavior."""
        original_exception = Exception("Test exception")

        # Use an unknown provider
        result = map_exception(original_exception, "unknown_provider")

        # Should use a default extractor and return a generic LLMException
        assert isinstance(result, LLMException)
        assert result.provider == "unknown_provider"
        assert result.original_exception == original_exception
        assert str(original_exception) in result.message

    def test_map_exception_preserves_message_and_data(self):
        """Test that map_exception preserves the error message and response data."""
        original_exception = Exception("Original error message")
        response_data = {"error": {"message": "API error", "code": "invalid_request"}}

        # Create a mock extractor that returns custom message and response data
        with patch(
            "flexai.llm.exceptions.PROVIDER_EXTRACTORS",
            {"test_provider": lambda e: (400, response_data, "Custom error message")},
        ):
            result = map_exception(original_exception, "test_provider")

        # Should use the message from the extractor and preserve response data
        assert isinstance(result, BadRequestException)
        assert result.message == "Custom error message"
        assert result.response_data == response_data


class TestExceptionExtractors:
    """Tests for provider-specific exception extractors."""

    def test_extract_openai_details_with_api_error(self):
        """Test extract_openai_details with an OpenAI APIError."""
        # Create a mock APIError instance
        mock_error = MagicMock()
        mock_error.status_code = 429
        mock_error.message = "Rate limit exceeded"
        mock_error.body = MagicMock()
        mock_error.body.__dict__ = {"error": {"type": "rate_limit_exceeded"}}

        # Patch the isinstance check to return True
        with patch("flexai.llm.exceptions.isinstance", return_value=True):
            # Test the extractor
            status_code, response_data, message = extract_openai_details(mock_error)

            # Verify the extracted details
            assert status_code == 429
            assert response_data == {"error": {"type": "rate_limit_exceeded"}}
            assert message == "Rate limit exceeded"

    def test_extract_openai_details_with_other_exception(self):
        """Test extract_openai_details with a non-OpenAI exception."""
        # Create a generic exception
        exception = ValueError("Generic error")
        exception.__dict__ = {"attr": "value"}

        # Mock the imports
        with patch("flexai.llm.exceptions.isinstance", return_value=False):
            # Test the extractor
            status_code, response_data, message = extract_openai_details(exception)

            # Verify the extracted details
            assert status_code is None
            assert response_data == {"attr": "value"}
            assert message == "Generic error"

    def test_extract_anthropic_details_with_api_error(self):
        """Test extract_anthropic_details with an Anthropic APIError."""
        # Create a mock APIError instance
        mock_error = MagicMock()
        mock_error.status_code = 401
        mock_error.message = "Invalid API key"
        mock_error.body = MagicMock()
        mock_error.body.__dict__ = {"error": {"type": "authentication_error"}}

        # Patch the isinstance check to return True
        with patch("flexai.llm.exceptions.isinstance", return_value=True):
            # Test the extractor
            status_code, response_data, message = extract_anthropic_details(mock_error)

            # Verify the extracted details
            assert status_code == 401
            assert response_data == {"error": {"type": "authentication_error"}}
            assert message == "Invalid API key"

    def test_extract_gemini_details_with_api_error(self):
        """Test extract_gemini_details with a Gemini APIError."""
        # Create a mock APIError instance
        mock_error = MagicMock()
        mock_error._get_code = MagicMock(return_value=403)
        mock_error._get_message = MagicMock(return_value="Permission denied")
        mock_error.details = {
            "error": {"message": "Permission denied", "status": "PERMISSION_DENIED"}
        }

        # Patch the isinstance check to return True
        with patch("flexai.llm.exceptions.isinstance", return_value=True):
            # Test the extractor
            status_code, response_data, message = extract_gemini_details(mock_error)

            # Verify the extracted details
            assert status_code == 403
            assert response_data == {
                "error": {"message": "Permission denied", "status": "PERMISSION_DENIED"}
            }
            assert message == "Permission denied"

    def test_extract_gemini_details_with_httpx_error(self):
        """Test extract_gemini_details with an HTTPX HTTPStatusError."""
        # Import httpx inside the test to avoid import errors
        import httpx

        # Create a mock HTTPStatusError
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json = MagicMock(return_value={"error": "Rate limit exceeded"})

        mock_error = MagicMock(spec=httpx.HTTPStatusError)
        mock_error.response = mock_response
        mock_error.__str__ = MagicMock(
            return_value="429 Client Error: Too Many Requests"
        )

        # Setup the isinstance checks
        def isinstance_side_effect(obj, class_type):
            if class_type == httpx.HTTPStatusError:
                return obj is mock_error
            return False

        with patch(
            "flexai.llm.exceptions.isinstance", side_effect=isinstance_side_effect
        ):
            # Test the extractor
            status_code, response_data, message = extract_gemini_details(mock_error)

            # Verify the extracted details
            assert status_code == 429
            assert response_data == {"error": "Rate limit exceeded"}
            assert message == "429 Client Error: Too Many Requests"

    def test_extract_gemini_details_with_httpx_error_json_error(self):
        """Test extract_gemini_details with an HTTPX HTTPStatusError that fails to parse JSON."""
        # Import httpx inside the test to avoid import errors
        import httpx

        # Create a mock HTTPStatusError with a response that raises on json()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json = MagicMock(side_effect=ValueError("Invalid JSON"))
        mock_response.__str__ = MagicMock(
            return_value="<Response [500 Internal Server Error]>"
        )

        mock_error = MagicMock(spec=httpx.HTTPStatusError)
        mock_error.response = mock_response
        mock_error.__str__ = MagicMock(
            return_value="500 Server Error: Internal Server Error"
        )

        # Setup the isinstance checks
        def isinstance_side_effect(obj, class_type):
            if class_type == httpx.HTTPStatusError:
                return obj is mock_error
            return False

        with patch(
            "flexai.llm.exceptions.isinstance", side_effect=isinstance_side_effect
        ):
            # Test the extractor
            status_code, response_data, message = extract_gemini_details(mock_error)

            # Verify the extracted details
            assert status_code == 500
            assert response_data == {"error": "<Response [500 Internal Server Error]>"}
            assert message == "500 Server Error: Internal Server Error"


class TestExceptionBehavior:
    """Tests for exception behavior and formatting."""

    def test_llm_exception_str_method(self):
        """Test the __str__ method of LLMException."""
        # Test without status code
        exception = LLMException(
            message="Test error", provider="test_provider", original_exception=None
        )
        assert str(exception) == "[test_provider] Test error"

        # Test with status code
        exception = LLMException(
            message="Test error",
            provider="test_provider",
            status_code=429,
            original_exception=None,
        )
        assert str(exception) == "[test_provider] Test error (Status: 429)"

    def test_exception_chaining(self):
        """Test that exceptions are properly chained."""
        original_exception = ValueError("Original error")

        # Create a mapped exception that chains the original
        mapped_exception = map_exception(original_exception, "test_provider")

        # Verify the original exception is set correctly
        assert mapped_exception.original_exception is original_exception

        # Raise and catch to verify exception chaining works as expected
        try:
            raise mapped_exception from original_exception
        except LLMException as e:
            assert e.__cause__ is original_exception  # noqa: PT017
