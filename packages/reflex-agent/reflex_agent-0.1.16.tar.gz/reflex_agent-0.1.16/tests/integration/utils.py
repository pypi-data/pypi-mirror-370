"""Shared utilities for integration tests.

Common models, fixtures, and test helpers used across integration test files.
This module contains only generic utilities that don't depend on specific providers.
"""

import pytest
from pydantic import BaseModel

from flexai import UserMessage
from flexai.tool import Tool

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv not available, skip loading


# =============================================================================
# COMMON PYDANTIC MODELS
# =============================================================================


class Person(BaseModel):
    """A person with basic information."""

    name: str
    age: int
    occupation: str


class MathResult(BaseModel):
    """Result of a mathematical calculation."""

    problem: str
    answer: int
    explanation: str


class WeatherInfo(BaseModel):
    """Weather information for a location."""

    location: str
    temperature: float
    condition: str
    humidity: int


class BookReview(BaseModel):
    """A book review with rating and details."""

    title: str
    author: str
    rating: int  # 1-5 stars
    review: str
    recommended: bool


# =============================================================================
# COMMON TEST TOOLS
# =============================================================================


def create_math_tool():
    """Create a simple math tool for testing."""

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together.

        Args:
            a: The first number
            b: The second number

        Returns:
            The sum of a and b
        """
        return a + b

    return Tool.from_function(add_numbers)


def create_calculator_tool():
    """Create a more complex calculator tool."""

    def calculate(operation: str, a: float, b: float) -> float:
        """Perform basic arithmetic operations.

        Args:
            operation: The operation to perform (add, subtract, multiply, divide)
            a: The first number
            b: The second number

        Returns:
            The result of the calculation
        """
        if operation == "add":
            return a + b
        if operation == "subtract":
            return a - b
        if operation == "multiply":
            return a * b
        if operation == "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        raise ValueError(f"Unknown operation: {operation}")

    return Tool.from_function(calculate)


def create_weather_tool():
    """Create a mock weather tool for testing."""

    def get_weather(location: str) -> str:
        """Get weather information for a location.

        Args:
            location: The location to get weather for

        Returns:
            Weather information as a string
        """
        # Mock weather data
        weather_data = {
            "new york": "Sunny, 72°F, 65% humidity",
            "london": "Cloudy, 18°C, 80% humidity",
            "tokyo": "Rainy, 22°C, 90% humidity",
            "default": f"Weather data not available for {location}",
        }
        return weather_data.get(location.lower(), weather_data["default"])

    return Tool.from_function(get_weather)


# =============================================================================
# COMMON TOOL FIXTURES
# =============================================================================


@pytest.fixture
def math_tool():
    """Fixture providing a simple math tool."""
    return create_math_tool()


@pytest.fixture
def calculator_tool():
    """Fixture providing a calculator tool."""
    return create_calculator_tool()


@pytest.fixture
def weather_tool():
    """Fixture providing a weather tool."""
    return create_weather_tool()


@pytest.fixture
def multiple_tools():
    """Fixture providing multiple tools for complex testing."""
    return [create_math_tool(), create_calculator_tool(), create_weather_tool()]


# =============================================================================
# COMMON TEST DATA
# =============================================================================


class TestMessages:
    """Common test messages for various scenarios."""

    # Simple queries
    SIMPLE_MATH = [UserMessage("What is 2 + 2? Give a short answer.")]
    GREETING = [UserMessage("Hello! How are you today?")]

    # Structured output requests
    PERSON_REQUEST = [UserMessage("Generate a fictional person who is a teacher")]
    MATH_PROBLEM = [UserMessage("Solve this math problem: 15 + 27")]
    WEATHER_REQUEST = [UserMessage("Create weather info for Paris")]

    # Tool usage requests
    TOOL_MATH = [UserMessage("Use the add_numbers tool to calculate 15 + 23")]
    TOOL_WEATHER = [UserMessage("Get the weather for New York")]
    TOOL_CALCULATOR = [UserMessage("Use the calculator to multiply 7 by 9")]

    # Multi-turn conversation starters
    CONVERSATION_START = [UserMessage("My name is Alice and I'm a software engineer.")]
    CONVERSATION_FOLLOWUP = [UserMessage("What's my profession?")]

    # Streaming test messages
    STREAMING_COUNT = [UserMessage("Count from 1 to 5, one number per line.")]
    STREAMING_STORY = [UserMessage("Tell a 2-sentence story about a cat.")]

    # Edge cases
    EMPTY_MESSAGE = [UserMessage("")]
    VERY_SHORT = [UserMessage("Hi")]
    PIRATE_SYSTEM = "You are a pirate. Respond in pirate speak but keep it short."


# =============================================================================
# COMMON SKIP CONDITIONS
# =============================================================================

# NOTE: Provider-specific skip conditions should be in their respective test files


# =============================================================================
# PROVIDER CONFIGURATIONS
# =============================================================================


class ProviderConfig:
    """Base class for provider-specific configurations."""

    # Basic chat model
    BASIC_MODEL: str = None

    # Model that supports structured output
    STRUCTURED_MODEL: str = None

    # List of models to test for multi-model tests
    MODELS_TO_TEST: list = []

    # Provider-specific capabilities
    SUPPORTS_STREAMING: bool = True
    SUPPORTS_TOOLS: bool = True
    SUPPORTS_STRUCTURED_OUTPUT: bool = True


# NOTE: Provider-specific configs should be in their respective test files


# =============================================================================
# COMMON ASSERTIONS
# =============================================================================


class CommonAssertions:
    """Common assertion helpers for integration tests."""

    @staticmethod
    def assert_valid_response(response):
        """Assert that a response is valid."""
        from flexai.message import AIMessage

        assert isinstance(response, AIMessage)
        assert response.content is not None
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0
        assert response.usage.generation_time > 0

    @staticmethod
    def assert_contains_tool_calls(response):
        """Assert that response contains tool calls."""
        assert isinstance(response.content, list)
        tool_calls = [item for item in response.content if hasattr(item, "name")]
        assert len(tool_calls) > 0
        return tool_calls

    @staticmethod
    def assert_streaming_chunks(chunks):
        """Assert that streaming chunks are valid."""
        from flexai.message import AIMessage, TextBlock

        assert len(chunks) > 1

        # Should have received text chunks
        text_chunks = [chunk for chunk in chunks if isinstance(chunk, TextBlock)]
        assert len(text_chunks) > 0

        # Should have final AI message
        final_messages = [chunk for chunk in chunks if isinstance(chunk, AIMessage)]
        assert len(final_messages) > 0

    @staticmethod
    def assert_person_valid(person: Person):
        """Assert that a Person model is valid."""
        assert isinstance(person, Person)
        assert isinstance(person.name, str)
        assert len(person.name) > 0
        assert isinstance(person.age, int)
        assert 0 < person.age <= 150  # Reasonable age range
        assert isinstance(person.occupation, str)
        assert len(person.occupation) > 0

    @staticmethod
    def assert_math_result_valid(
        result: MathResult, expected_answer: int | None = None
    ):
        """Assert that a MathResult model is valid."""
        assert isinstance(result, MathResult)
        assert isinstance(result.problem, str)
        assert len(result.problem) > 0
        assert isinstance(result.answer, int)
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 5

        if expected_answer is not None:
            assert result.answer == expected_answer


# =============================================================================
# COMMON TEST HELPERS
# =============================================================================


async def run_multi_turn_conversation(client, initial_message, followup_message):
    """Helper for testing multi-turn conversations."""
    messages = [initial_message]

    # First turn
    response1 = await client.get_chat_response(messages)
    messages.append(response1)

    # Second turn
    messages.append(followup_message)
    response2 = await client.get_chat_response(messages)

    return response1, response2, messages


async def multiple_models_helper(client_factory, models, test_message, assertion_func):
    """Helper for testing multiple models with the same input.

    Args:
        client_factory: Function that takes a model name and returns a client
        models: List of model names to test
        test_message: Message to send to each model
        assertion_func: Function to validate the response
    """
    results = {}

    for model in models:
        try:
            client = client_factory(model)
            response = await client.get_chat_response([test_message])
            assertion_func(response)
            results[model] = "passed"
        except Exception as e:
            results[model] = f"failed: {e}"

    return results


# =============================================================================
# GENERIC TEST TEMPLATES
# =============================================================================


async def basic_chat_template(client):
    """Generic template for testing basic chat functionality."""
    # Don't pass system parameter to avoid provider differences with empty system messages
    response = await client.get_chat_response(TestMessages.SIMPLE_MATH)
    CommonAssertions.assert_valid_response(response)
    assert "4" in str(response.content)


async def system_message_template(client):
    """Generic template for testing system message functionality."""
    response = await client.get_chat_response(
        TestMessages.GREETING, system=TestMessages.PIRATE_SYSTEM
    )
    CommonAssertions.assert_valid_response(response)
    # Should contain pirate-like language
    content_str = str(response.content).lower()
    pirate_words = ["ahoy", "mate", "arr", "ye", "aye"]
    assert any(word in content_str for word in pirate_words)


async def structured_output_template(client, model_class, expected_field_value=None):
    """Generic template for testing structured output."""
    if model_class == Person:
        messages = TestMessages.PERSON_REQUEST
        result = await client.get_structured_response(messages, Person)
        CommonAssertions.assert_person_valid(result)
        if expected_field_value:
            assert expected_field_value in result.occupation.lower()
    elif model_class == MathResult:
        messages = TestMessages.MATH_PROBLEM
        result = await client.get_structured_response(messages, MathResult)
        CommonAssertions.assert_math_result_valid(result, expected_answer=42)
        assert "15" in result.problem
        assert "27" in result.problem

    return result


async def tool_calling_template(client, tool):
    """Generic template for testing tool calling functionality."""
    response = await client.get_chat_response(
        TestMessages.TOOL_MATH, tools=[tool], allow_tool=True
    )
    CommonAssertions.assert_valid_response(response)
    # Response should contain tool calls
    if isinstance(response.content, list):
        tool_calls = CommonAssertions.assert_contains_tool_calls(response)
        assert tool_calls[0].name == "add_numbers"


async def streaming_template(client):
    """Generic template for testing streaming responses."""
    from flexai.message import AIMessage

    chunks = []
    final_message = None
    async for chunk in client.stream_chat_response(TestMessages.STREAMING_COUNT):
        chunks.append(chunk)
        # Store final message for verification
        if isinstance(chunk, AIMessage):
            final_message = chunk

    CommonAssertions.assert_streaming_chunks(chunks)
    # Verify we received a final message
    assert final_message is not None


async def agent_integration_template(client):
    """Generic template for testing agent integration."""
    from flexai import Agent
    from flexai.message import AIMessage

    agent = Agent(
        llm=client,
        prompt="You are a helpful math tutor. Keep explanations concise.",
    )

    messages = [UserMessage("What is 12 * 8?")]

    # agent.step() returns an AsyncGenerator, so we iterate through it
    final_response = None
    async for response in agent.step(messages):
        if isinstance(response, AIMessage):
            final_response = response

    assert final_response is not None
    CommonAssertions.assert_valid_response(final_response)
    assert "96" in str(final_response.content)


async def multi_turn_template(client):
    """Generic template for testing multi-turn conversations."""
    response1, response2, messages = await run_multi_turn_conversation(
        client,
        TestMessages.CONVERSATION_START[0],
        TestMessages.CONVERSATION_FOLLOWUP[0],
    )

    CommonAssertions.assert_valid_response(response1)
    CommonAssertions.assert_valid_response(response2)

    # Should remember that Alice is a software engineer
    assert (
        "software" in str(response2.content).lower()
        or "engineer" in str(response2.content).lower()
    )


async def temperature_control_template(client):
    """Generic template for testing temperature control."""
    messages = TestMessages.SIMPLE_MATH

    # Get multiple responses with different temperatures
    low_temp_responses = []
    high_temp_responses = []

    for _ in range(2):
        response = await client.get_chat_response(messages, temperature=0.1)
        low_temp_responses.append(str(response.content))

        response = await client.get_chat_response(messages, temperature=0.9)
        high_temp_responses.append(str(response.content))

    # All responses should be valid
    assert all(len(r) > 0 for r in low_temp_responses)
    assert all(len(r) > 0 for r in high_temp_responses)


# NOTE: Caching test templates have been moved to tests/caching/utils.py
