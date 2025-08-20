# Caching Tests

This directory contains tests for caching functionality across different LLM providers in the flexai library.

## Overview

The caching tests are designed to verify that caching mechanisms work correctly and efficiently across different providers. Currently, the tests focus on **implicit caching** - automatic caching behavior that happens behind the scenes.

## Types of Caching

### Implicit Caching (Currently Tested)
- Automatic caching enabled by default on supported models
- No explicit cache management required
- Tracks cache metrics via `cache_read_tokens` and `cache_write_tokens` in usage metadata
- Relies on provider's internal optimization for similar content

### Explicit Caching (Future Enhancement)
- Manual cache creation and management using provider APIs
- Requires explicit cache creation with TTL settings
- Direct control over what content gets cached
- Significant cost savings for large repeated contexts
- Supported by Google's Gemini API via `cachedContents` endpoints

## Current Test Structure

```
tests/caching/
├── __init__.py              # Package initialization
├── README.md                # This documentation
├── utils.py                 # Shared caching test utilities
├── test_gemini_caching.py   # Gemini-specific caching tests
└── test_anthropic_caching.py (planned)
└── test_openai_caching.py  (planned)
```

## Test Categories

### Basic Caching (`TestGeminiBasicCaching`)
- Cache metrics validation
- Streaming response cache tracking
- Tool usage with caching
- Repeated request behavior

### Advanced Caching (`TestGeminiAdvancedCaching`) 
- Cache efficiency analysis
- Long context scenarios
- Repeated context patterns
- Incremental context building

### Model-Specific Tests (`TestGeminiModelSpecificCaching`)
- Cross-model cache behavior
- Client consistency testing

### Feature Integration (`TestGeminiCachingWithFeatures`)
- Caching with thinking capabilities
- Temperature variation effects
- Gemini-specific features

### Performance Tests (`TestGeminiCachingPerformance`)
- Cache performance measurement
- Streaming cache efficiency
- Tool usage impact

## Shared Utilities (`utils.py`)

### Core Classes
- `CacheMetrics`: Track cache performance metrics
- `CacheTestResult`: Results from efficiency tests
- `CachingTestHelpers`: Collection of helper methods
- `CacheTestScenarios`: Pre-defined test scenarios
- `CacheTestMessages`: Common test messages

### Test Templates
Generic test templates that can be reused across providers:
- `basic_cache_tracking_template()`: Basic cache metric validation
- `cache_streaming_template()`: Streaming response cache tracking
- `cache_with_tools_template()`: Tool usage with caching
- `repeated_requests_cache_template()`: Repeated request testing

## Running Tests

### All Caching Tests
```bash
pytest tests/caching/ -v
```

### Specific Provider
```bash
pytest tests/caching/test_gemini_caching.py -v
```

### Specific Test Class
```bash
pytest tests/caching/test_gemini_caching.py::TestGeminiBasicCaching -v
```

### Single Test
```bash
pytest tests/caching/test_gemini_caching.py::TestGeminiBasicCaching::test_cache_metrics_validation -v
```

## Environment Setup

### Required Environment Variables
```bash
# For Gemini tests
export GEMINI_API_KEY="your_gemini_api_key"

# For Anthropic tests (planned)
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# For OpenAI tests (planned)  
export OPENAI_API_KEY="your_openai_api_key"
```

### .env File Support
Tests automatically load environment variables from a `.env` file if present in the project root.

## Important Notes

### Current Limitations
1. **Implicit Caching Only**: Current tests focus on implicit caching behavior and metrics tracking
2. **No Explicit Cache Management**: Tests don't create or manage explicit cache objects
3. **Provider-Dependent**: Cache behavior varies significantly between providers
4. **Minimum Token Requirements**: Some providers require minimum token counts for caching to activate

### Test Reliability
- Tests use real API calls and may be affected by network conditions
- Cache behavior can be non-deterministic and provider-dependent
- Some cache benefits may not be immediately observable in test scenarios

### Future Enhancements
1. **Explicit Caching Support**: Add tests for manual cache creation and management
2. **Cross-Provider Comparison**: Compare caching efficiency across providers
3. **Cost Analysis**: Add cost-benefit analysis for caching scenarios
4. **Cache Persistence Testing**: Test cache expiration and refresh behavior

## Adding New Providers

To add caching tests for a new provider:

1. Create `test_{provider}_caching.py` in this directory
2. Define provider-specific configuration class
3. Create provider-specific fixtures
4. Implement provider-specific test classes using shared templates
5. Add any provider-specific test scenarios

Follow the pattern established in `test_gemini_caching.py` for consistency.

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure all required dependencies are installed
- **API Key Errors**: Verify environment variables are set correctly
- **Cache Miss Expected**: Implicit caching is not guaranteed and may not always show benefits
- **Minimum Token Requirements**: Some tests may not trigger caching due to insufficient context size

### Debugging Tips
- Run tests with `-s` flag to see print output
- Check usage metadata in responses for cache metrics
- Verify that test scenarios meet minimum token requirements for caching
- Consider provider-specific caching limitations and requirements

## Cache Testing Best Practices

1. **Test Basic Tracking**: Ensure cache metrics are properly tracked
2. **Test Streaming**: Verify cache behavior in streaming mode
3. **Test with Tools**: Check cache behavior when using tools
4. **Test Consistency**: Verify consistent behavior across client instances
5. **Test Efficiency**: Measure cache efficiency over multiple requests
6. **Test Provider Features**: Test caching with provider-specific features

## Metrics Validation

All cache metrics should be:
- Non-negative integers for token counts
- Positive floats for generation time
- Properly calculated total tokens (input + output)

## Performance Considerations

Cache tests may take longer to run due to:
- Multiple API requests for efficiency testing
- Deliberate delays between requests for cache processing
- Large context messages for testing cache benefits 