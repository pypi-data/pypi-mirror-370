"""Integration test package for the FlexAI framework.

This package contains integration tests that make real API calls to various
LLM providers. These tests require valid API keys to be set in environment
variables.

Test files:
- test_openai_integration.py: Tests for OpenAI client integration
- utils.py: Shared utilities, models, and fixtures

To run integration tests:
    pytest tests/integration/ -v

To run specific provider tests:
    pytest tests/integration/test_openai_integration.py -v

Required environment variables:
- OPENAI_API_KEY: For OpenAI integration tests
- ANTHROPIC_API_KEY: For Anthropic integration tests
- GEMINI_API_KEY: For Gemini integration tests
"""
