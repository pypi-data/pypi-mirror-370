"""Exception classes for LLM client errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMException(Exception):  # noqa: N818
    """Base exception class for all LLM-related errors."""

    message: str
    provider: str
    original_exception: Exception | None = None
    status_code: int | None = None
    response_data: dict[str, Any] | None = None

    def __str__(self) -> str:
        result = f"[{self.provider}] {self.message}"
        if self.status_code:
            result += f" (Status: {self.status_code})"
        return result


@dataclass
class LLMClientException(LLMException):
    """Base exception class for 4XX client errors."""


@dataclass
class LLMServerException(LLMException):
    """Base exception class for 5XX server errors."""


@dataclass
class BadRequestException(LLMClientException):
    """Exception raised when the request is malformed (400)."""


@dataclass
class AuthenticationException(LLMClientException):
    """Exception raised when authentication fails (401)."""


@dataclass
class PermissionDeniedException(LLMClientException):
    """Exception raised when permission is denied (403)."""


@dataclass
class NotFoundException(LLMClientException):
    """Exception raised when a resource is not found (404)."""


@dataclass
class MethodNotAllowedException(LLMClientException):
    """Exception raised when the HTTP method is not allowed (405)."""


@dataclass
class RequestTimeoutException(LLMClientException):
    """Exception raised when a request times out (408)."""


@dataclass
class ConflictException(LLMClientException):
    """Exception raised when there's a conflict with the resource state (409)."""


@dataclass
class ValidationException(LLMClientException):
    """Exception raised when the request validation fails (422)."""


@dataclass
class RateLimitException(LLMClientException):
    """Exception raised when a rate limit is hit (429)."""


@dataclass
class ServerException(LLMServerException):
    """Exception raised when the server encounters an error (500)."""


@dataclass
class BadGatewayException(LLMServerException):
    """Exception raised when the server acts as a gateway and gets an invalid response (502)."""


@dataclass
class ServiceUnavailableException(LLMServerException):
    """Exception raised when the service is unavailable (503)."""


@dataclass
class GatewayTimeoutException(LLMServerException):
    """Exception raised when the gateway times out (504)."""


@dataclass
class ServerOverloadException(LLMServerException):
    """Exception raised when the server is overloaded and cannot handle the request (529)."""


# Mapping of HTTP status codes to our generic exceptions
STATUS_CODE_MAPPINGS: dict[int, type[LLMException]] = {
    400: BadRequestException,
    401: AuthenticationException,
    403: PermissionDeniedException,
    404: NotFoundException,
    405: MethodNotAllowedException,
    408: RequestTimeoutException,
    409: ConflictException,
    422: ValidationException,
    429: RateLimitException,
    500: ServerException,
    502: BadGatewayException,
    503: ServiceUnavailableException,
    504: GatewayTimeoutException,
    529: ServerOverloadException,
}


# Provider-specific exception extractors
def extract_openai_details(
    exception: Exception,
) -> tuple[int | None, dict[str, Any] | None, str]:
    """Extract status code, response data and message from OpenAI exceptions.

    Args:
        exception: The exception raised by the OpenAI API.

    Returns:
        A tuple containing:
            - status_code: The HTTP status code if available, otherwise None.
            - response_data: The response data as a dictionary if available, otherwise None.
            - message: A string message describing the error.
    """
    from openai import APIError

    if isinstance(exception, APIError):
        body = getattr(exception, "body", None)
        return (
            getattr(exception, "status_code", None),
            getattr(body, "__dict__", None),
            exception.message,
        )

    return None, exception.__dict__, str(exception)


def extract_anthropic_details(
    exception: Exception,
) -> tuple[int | None, dict[str, Any] | None, str]:
    """Extract status code, response data and message from Anthropic exceptions.

    Args:
        exception: The exception raised by the Anthropic API.

    Returns:
        A tuple containing:
            - status_code: The HTTP status code if available, otherwise None.
            - response_data: The response data as a dictionary if available, otherwise None.
            - message: A string message describing the error.
    """
    from anthropic import APIError

    if isinstance(exception, APIError):
        body = getattr(exception, "body", None)
        return (
            getattr(exception, "status_code", None),
            getattr(body, "__dict__", None),
            exception.message,
        )

    return None, exception.__dict__, str(exception)


def extract_gemini_details(
    exception: Exception,
) -> tuple[int | None, dict[str, Any] | None, str]:
    """Extract status code, response data and message from Gemini exceptions.

    Args:
        exception: The exception raised by the Gemini API.

    Returns:
        A tuple containing:
            - status_code: The HTTP status code if available, otherwise None.
            - response_data: The response data as a dictionary if available, otherwise None.
            - message: A string message describing the error.
    """
    import httpx
    from google.genai.errors import APIError

    if isinstance(exception, APIError):
        response_json = exception.details
        return (
            exception._get_code(response_json),
            response_json,
            exception._get_message(response_json),
        )

    # Handle HTTPX errors which Gemini sometimes raises directly
    if isinstance(exception, httpx.HTTPStatusError):
        try:
            response_data = exception.response.json()
        except Exception:
            response_data = {"error": str(exception.response)}
        return exception.response.status_code, response_data, str(exception)

    return None, exception.__dict__, str(exception)


# Map of provider to extraction function
PROVIDER_EXTRACTORS = {
    "openai": extract_openai_details,
    "anthropic": extract_anthropic_details,
    "gemini": extract_gemini_details,
}


def map_exception(exception: Exception, provider: str) -> Exception:
    """Map a provider-specific exception to our generic exception types.

    Args:
        exception: The original exception from the provider
        provider: The provider name ("openai", "anthropic", "gemini", etc.)

    Returns:
        A generic LLMException subclass instance
    """
    # Extract details using provider-specific extractor
    extractor = PROVIDER_EXTRACTORS.get(provider, lambda e: (None, None, str(e)))
    status_code, response_data, message = extractor(exception)

    # Get the appropriate exception class based on status code
    exception_class = STATUS_CODE_MAPPINGS.get(status_code) if status_code else None

    # If we couldn't determine the exception type, return a wrapped version of the original
    if not exception_class:
        return LLMException(
            message=str(exception),
            provider=provider,
            original_exception=exception,
        )

    # Create and return the appropriate exception
    return exception_class(
        message=message,
        provider=provider,
        original_exception=exception,
        status_code=status_code,
        response_data=response_data,
    )
