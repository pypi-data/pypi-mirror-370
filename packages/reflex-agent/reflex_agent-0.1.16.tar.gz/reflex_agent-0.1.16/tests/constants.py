"""Constants for testing across all LLM providers.

This file centralizes model names, API configurations, and test parameters
to avoid hard-coding values throughout the test suite.
"""


class OpenAIModels:
    """OpenAI model configurations for testing."""

    BASIC_MODEL = "gpt-4.1-2025-04-14"
    STRUCTURED_MODEL = (
        "gpt-4.1-2025-04-14"  # gpt-3.5-turbo doesn't support structured output
    )
    MODELS_TO_TEST = [BASIC_MODEL, STRUCTURED_MODEL]


class AnthropicModels:
    """Anthropic model configurations for testing."""

    BASIC_MODEL = "claude-sonnet-4-20250514"
    STRUCTURED_MODEL = "claude-sonnet-4-20250514"  # Claude supports structured output
    MODELS_TO_TEST = [BASIC_MODEL, "claude-sonnet-4-20250514"]


class GeminiModels:
    """Gemini model configurations for testing."""

    # Primary models for testing
    PRO_MODEL = "gemini-2.5-pro-preview-06-05"  # Latest Pro model
    FLASH_MODEL = (
        "gemini-2.5-flash-lite-preview-06-17"  # Use Flash Lite for all flash tests
    )
    FLASH_LITE_MODEL = (
        "gemini-2.5-flash-lite-preview-06-17"  # Flash Lite model for testing
    )

    # Model aliases for different test purposes
    BASIC_MODEL = FLASH_LITE_MODEL  # Use Flash Lite for testing function calling
    STRUCTURED_MODEL = PRO_MODEL  # Gemini supports structured output
    CACHING_MODEL = FLASH_LITE_MODEL  # Use Flash Lite for caching tests

    # Thinking budget requirements
    PRO_MIN_THINKING_BUDGET = 128  # Pro models minimum thinking budget
    FLASH_MIN_THINKING_BUDGET = 0  # Flash models can disable thinking

    # Test model sets
    MODELS_TO_TEST = [PRO_MODEL, FLASH_MODEL]


class TestDefaults:
    """Default test configuration values."""

    # Timeouts
    BASIC_TIMEOUT_SECONDS = 30
    STREAMING_TIMEOUT_SECONDS = 60
    THINKING_TIMEOUT_SECONDS = 120

    # Test parameters
    DEFAULT_THINKING_BUDGET = 256
    TEMPERATURE_LOW = 0.1
    TEMPERATURE_HIGH = 0.9

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1


class ProviderConfigs:
    """Provider-specific configurations."""

    OPENAI = {
        "basic_model": OpenAIModels.BASIC_MODEL,
        "structured_model": OpenAIModels.STRUCTURED_MODEL,
        "models_to_test": OpenAIModels.MODELS_TO_TEST,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_structured_output": True,
        "supports_thinking": False,
    }

    ANTHROPIC = {
        "basic_model": AnthropicModels.BASIC_MODEL,
        "structured_model": AnthropicModels.STRUCTURED_MODEL,
        "models_to_test": AnthropicModels.MODELS_TO_TEST,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_structured_output": True,
        "supports_thinking": False,
    }

    GEMINI = {
        "basic_model": GeminiModels.BASIC_MODEL,
        "structured_model": GeminiModels.STRUCTURED_MODEL,
        "models_to_test": GeminiModels.MODELS_TO_TEST,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_structured_output": True,
        "supports_thinking": True,
        "thinking_models": {
            "pro": {
                "model": GeminiModels.PRO_MODEL,
                "min_budget": GeminiModels.PRO_MIN_THINKING_BUDGET,
                "can_disable": False,
            },
            "flash": {
                "model": GeminiModels.FLASH_MODEL,
                "min_budget": GeminiModels.FLASH_MIN_THINKING_BUDGET,
                "can_disable": True,
            },
        },
    }


# Quick access constants for backwards compatibility
GEMINI_PRO_MODEL = GeminiModels.PRO_MODEL
GEMINI_FLASH_MODEL = GeminiModels.FLASH_MODEL
OPENAI_BASIC_MODEL = OpenAIModels.BASIC_MODEL
ANTHROPIC_BASIC_MODEL = AnthropicModels.BASIC_MODEL
