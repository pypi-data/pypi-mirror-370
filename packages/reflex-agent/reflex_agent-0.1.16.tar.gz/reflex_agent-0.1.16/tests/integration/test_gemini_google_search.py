"""Integration tests for Google Search grounding functionality.

These tests verify the Google Search grounding feature works correctly
with different models and configurations.
"""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from flexai.llm.gemini import GeminiClient
from flexai.message import GroundingBlock, UserMessage


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
class TestGeminiGoogleSearchIntegration:
    """Integration tests for Google Search grounding with Gemini."""

    @pytest.mark.asyncio
    async def test_google_search_integration_gemini_25(self):
        """Integration test for Google Search with Gemini 2.5."""
        client = GeminiClient(
            model="gemini-2.5-flash-lite-preview-06-17",
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with a query that should trigger a search
        response = await client.get_chat_response(
            messages=[
                UserMessage(content="What are the latest developments in AI in 2024?")
            ],
            use_google_search=True,
        )

        # Verify response structure
        assert response.content
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0

        # Check for grounding metadata (may or may not be present depending on model's decision)
        grounding_blocks = [
            content
            for content in response.content
            if isinstance(content, GroundingBlock)
        ]

        # If grounding occurred, verify structure
        if grounding_blocks:
            grounding = grounding_blocks[0]
            assert isinstance(grounding.search_queries, list)
            assert isinstance(grounding.grounding_chunks, list)
            assert isinstance(grounding.grounding_supports, list)
            assert isinstance(grounding.search_entry_point, dict)
            assert isinstance(grounding.metadata, dict)

            # If chunks exist, verify structure
            for chunk in grounding.grounding_chunks:
                assert "web" in chunk
                assert "uri" in chunk["web"]
                assert "title" in chunk["web"]

    @pytest.mark.asyncio
    async def test_google_search_integration_gemini_15(self):
        """Integration test for Google Search with Gemini 1.5."""
        client = GeminiClient(
            model="gemini-2.5-flash-lite-preview-06-17",
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with dynamic threshold
        response = await client.get_chat_response(
            messages=[
                UserMessage(content="Who won the Nobel Prize in Physics in 2024?")
            ],
            use_google_search=True,
            google_search_dynamic_threshold=0.8,
        )

        # Verify basic response structure
        assert response.content
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0

        # Grounding may or may not occur depending on threshold and model confidence
        grounding_blocks = [
            content
            for content in response.content
            if isinstance(content, GroundingBlock)
        ]

        # If grounding occurred, verify structure
        if grounding_blocks:
            grounding = grounding_blocks[0]
            assert isinstance(grounding.search_queries, list)
            assert len(grounding.search_queries) > 0

    @pytest.mark.asyncio
    async def test_google_search_streaming_integration(self):
        """Integration test for streaming with Google Search."""
        client = GeminiClient(
            model="gemini-2.5-flash-lite-preview-06-17",
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        content_chunks = []
        final_message = None

        async for chunk in client.stream_chat_response(
            messages=[UserMessage(content="What happened in the 2024 Olympics?")],
            use_google_search=True,
        ):
            content_chunks.append(chunk)
            if hasattr(chunk, "usage"):  # Final AIMessage
                final_message = chunk

        # Verify we got streaming content
        assert len(content_chunks) > 0
        assert final_message is not None

        # Check for grounding in final message
        if final_message:
            grounding_blocks = [
                content
                for content in final_message.content
                if isinstance(content, GroundingBlock)
            ]

            # If grounding occurred, verify it was collected properly
            if grounding_blocks:
                grounding = grounding_blocks[0]
                assert isinstance(grounding.search_queries, list)

    @pytest.mark.asyncio
    async def test_google_search_disabled_integration(self):
        """Integration test verifying Google Search can be disabled."""
        client = GeminiClient(
            model="gemini-2.5-flash-lite-preview-06-17",
            project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
            location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
            use_vertex=True,
        )

        # Test with search explicitly disabled
        response = await client.get_chat_response(
            messages=[UserMessage(content="What is the capital of France?")],
            use_google_search=False,
        )

        # Verify normal response without grounding
        assert response.content
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0

        # Should have no grounding blocks
        grounding_blocks = [
            content
            for content in response.content
            if isinstance(content, GroundingBlock)
        ]
        assert len(grounding_blocks) == 0


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
class TestGeminiGoogleSearchMocked:
    """Mocked integration tests for comprehensive coverage."""

    @pytest.mark.asyncio
    async def test_google_search_with_vertex_ai(self):
        """Test Google Search grounding with Vertex AI configuration."""
        with patch("flexai.llm.gemini.BaseApiClient") as mock_api_client:
            mock_api_client.return_value = Mock()

            client = GeminiClient(
                project_id="test-project",
                location="us-central1",
                use_vertex=True,
                model="gemini-2.5-flash",
            )

            # Mock the client creation
            with patch.object(client, "client") as mock_client:
                # Setup mock response with grounding
                mock_response = Mock()
                mock_response.candidates = [Mock()]
                mock_response.candidates[0].content = Mock()
                mock_response.candidates[0].content.parts = [
                    Mock(
                        __dict__={
                            "text": "Vertex AI search result",
                            "thought": None,
                            "function_call": None,
                        }
                    )
                ]
                mock_response.candidates[0].grounding_metadata = Mock()
                mock_response.candidates[0].grounding_metadata.web_search_queries = [
                    "vertex search"
                ]
                mock_response.candidates[0].grounding_metadata.grounding_chunks = []
                mock_response.candidates[0].grounding_metadata.grounding_supports = []
                mock_response.candidates[
                    0
                ].grounding_metadata.search_entry_point = Mock(rendered_content="")
                mock_response.usage_metadata = Mock(
                    prompt_token_count=10,
                    total_token_count=20,
                    cached_content_token_count=0,
                )

                mock_client.models.generate_content = AsyncMock(
                    return_value=mock_response
                )

                response = await client.get_chat_response(
                    messages=[UserMessage(content="Test vertex search")],
                    use_google_search=True,
                )

                # Verify grounding block was created
                grounding_blocks = [
                    content
                    for content in response.content
                    if isinstance(content, GroundingBlock)
                ]
                assert len(grounding_blocks) == 1
                assert grounding_blocks[0].search_queries == ["vertex search"]

    @pytest.mark.asyncio
    async def test_google_search_error_handling(self):
        """Test error handling when Google Search fails."""
        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )

            # Mock client that throws an error
            mock_client = Mock()
            mock_client.models.generate_content = AsyncMock(
                side_effect=Exception("Search service unavailable")
            )
            object.__setattr__(client, "client", mock_client)

            # Should raise the exception
            with pytest.raises(Exception, match="Search service unavailable"):
                await client.get_chat_response(
                    messages=[UserMessage(content="Test search")],
                    use_google_search=True,
                )

    @pytest.mark.asyncio
    async def test_google_search_with_complex_metadata(self):
        """Test handling of complex grounding metadata."""
        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )

            # Mock complex grounding metadata
            mock_client = Mock()
            mock_response = Mock()
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content = Mock()
            mock_response.candidates[0].content.parts = [
                Mock(
                    __dict__={
                        "text": "Complex search result",
                        "thought": None,
                        "function_call": None,
                    }
                )
            ]

            # Complex grounding metadata
            mock_grounding = Mock()
            mock_grounding.web_search_queries = ["query1", "query2", "query3"]
            mock_grounding.grounding_chunks = [
                Mock(web=Mock(uri="https://site1.com", title="Site 1")),
                Mock(web=Mock(uri="https://site2.com", title="Site 2")),
                Mock(web=Mock(uri="https://site3.com", title="Site 3")),
            ]
            mock_grounding.grounding_supports = [
                Mock(
                    segment=Mock(start_index=0, end_index=20, text="First segment"),
                    grounding_chunk_indices=[0, 1],
                ),
                Mock(
                    segment=Mock(start_index=21, end_index=40, text="Second segment"),
                    grounding_chunk_indices=[2],
                ),
            ]
            mock_grounding.search_entry_point = Mock(
                rendered_content="<complex-widget>"
            )

            mock_response.candidates[0].grounding_metadata = mock_grounding
            mock_response.usage_metadata = Mock(
                prompt_token_count=15,
                total_token_count=35,
                cached_content_token_count=0,
            )

            mock_client.models.generate_content = AsyncMock(return_value=mock_response)
            object.__setattr__(client, "client", mock_client)

            response = await client.get_chat_response(
                messages=[UserMessage(content="Complex search query")],
                use_google_search=True,
            )

            # Verify complex grounding data is properly extracted
            grounding_blocks = [
                content
                for content in response.content
                if isinstance(content, GroundingBlock)
            ]
            assert len(grounding_blocks) == 1
            grounding = grounding_blocks[0]

            assert len(grounding.search_queries) == 3
            assert len(grounding.grounding_chunks) == 3
            assert len(grounding.grounding_supports) == 2

            # Verify chunk structure
            assert grounding.grounding_chunks[0]["web"]["title"] == "Site 1"
            assert grounding.grounding_chunks[1]["web"]["title"] == "Site 2"
            assert grounding.grounding_chunks[2]["web"]["title"] == "Site 3"

            # Verify support structure
            assert grounding.grounding_supports[0]["segment"]["text"] == "First segment"
            assert grounding.grounding_supports[0]["grounding_chunk_indices"] == [0, 1]
            assert grounding.grounding_supports[1]["grounding_chunk_indices"] == [2]

            # Verify search entry point
            assert (
                grounding.search_entry_point["rendered_content"] == "<complex-widget>"
            )

    @pytest.mark.asyncio
    async def test_google_search_model_detection(self):
        """Test that the correct tool is used based on model version."""
        # Test cases for different model versions
        test_cases = [
            ("gemini-2.5-flash", "google_search"),
            ("gemini-2.0-flash", "google_search"),
            ("gemini-1.5-flash", "google_search_retrieval"),
            ("gemini-1.5-pro", "google_search_retrieval"),
        ]

        for model_name, expected_tool in test_cases:
            with patch.object(GeminiClient, "__post_init__"):
                client = GeminiClient(
                    model=model_name,
                    project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                    location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                    use_vertex=True,
                )

                mock_client = Mock()
                mock_response = Mock()
                mock_response.candidates = [Mock()]
                mock_response.candidates[0].content = Mock()
                mock_response.candidates[0].content.parts = [
                    Mock(
                        __dict__={
                            "text": f"Response from {model_name}",
                            "thought": None,
                            "function_call": None,
                        }
                    )
                ]
                mock_response.candidates[0].grounding_metadata = None
                mock_response.usage_metadata = Mock(
                    prompt_token_count=10,
                    total_token_count=20,
                    cached_content_token_count=0,
                )

                mock_client.models.generate_content = AsyncMock(
                    return_value=mock_response
                )
                object.__setattr__(client, "client", mock_client)

                await client.get_chat_response(
                    messages=[UserMessage(content="Test model detection")],
                    use_google_search=True,
                )

                # Verify the correct tool was configured
                call_args = mock_client.models.generate_content.call_args[1]
                config = call_args["config"]
                assert hasattr(config, "tools")
                assert len(config.tools) == 1
                assert hasattr(config.tools[0], expected_tool), (
                    f"Expected {expected_tool} for model {model_name}"
                )
