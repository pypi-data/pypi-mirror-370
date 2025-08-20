"""Unit tests for GroundingBlock message content and cross-client compatibility.

Tests the GroundingBlock implementation and how it's handled across different LLM clients.
"""

import os
from unittest.mock import Mock

from flexai.llm.anthropic import AnthropicClient
from flexai.llm.gemini import GeminiClient
from flexai.message import AIMessage, GroundingBlock, TextBlock


class TestGroundingBlock:
    """Test the GroundingBlock message content type."""

    def test_grounding_block_creation(self):
        """Test creating a GroundingBlock with all fields."""
        grounding = GroundingBlock(
            search_queries=["test query", "another query"],
            grounding_chunks=[
                {"web": {"uri": "https://example.com", "title": "Example"}},
                {"web": {"uri": "https://test.com", "title": "Test"}},
            ],
            grounding_supports=[
                {
                    "segment": {"start_index": 0, "end_index": 10, "text": "test text"},
                    "grounding_chunk_indices": [0, 1],
                }
            ],
            search_entry_point={"rendered_content": "<widget>"},
            metadata={"source": "google_search"},
        )

        assert grounding.search_queries == ["test query", "another query"]
        assert len(grounding.grounding_chunks) == 2
        assert grounding.grounding_chunks[0]["web"]["title"] == "Example"
        assert len(grounding.grounding_supports) == 1
        assert grounding.search_entry_point["rendered_content"] == "<widget>"
        assert grounding.metadata["source"] == "google_search"

    def test_grounding_block_minimal(self):
        """Test creating a GroundingBlock with minimal fields."""
        grounding = GroundingBlock(
            search_queries=["minimal query"],
            grounding_chunks=[],
            grounding_supports=[],
            search_entry_point={},
            metadata={},
        )

        assert grounding.search_queries == ["minimal query"]
        assert grounding.grounding_chunks == []
        assert grounding.grounding_supports == []
        assert grounding.search_entry_point == {}
        assert grounding.metadata == {}

    def test_grounding_block_serialization(self):
        """Test that GroundingBlock can be serialized/deserialized."""
        original = GroundingBlock(
            search_queries=["serialization test"],
            grounding_chunks=[{"web": {"uri": "https://test.com", "title": "Test"}}],
            grounding_supports=[],
            search_entry_point={},
            metadata={"test": True},
        )

        # Convert to dict and back (simulating JSON serialization)
        data = {
            "search_queries": original.search_queries,
            "grounding_chunks": original.grounding_chunks,
            "grounding_supports": original.grounding_supports,
            "search_entry_point": original.search_entry_point,
            "metadata": original.metadata,
        }

        reconstructed = GroundingBlock(**data)

        assert reconstructed.search_queries == original.search_queries
        assert reconstructed.grounding_chunks == original.grounding_chunks
        assert reconstructed.grounding_supports == original.grounding_supports
        assert reconstructed.search_entry_point == original.search_entry_point
        assert reconstructed.metadata == original.metadata


class TestGroundingBlockExtraction:
    """Test the _extract_grounding_block method in GeminiClient."""

    def test_extract_grounding_block_complete(self):
        """Test extracting complete grounding metadata."""
        # Mock complete grounding metadata
        mock_metadata = Mock()
        mock_metadata.web_search_queries = ["query1", "query2"]
        mock_metadata.grounding_chunks = [
            Mock(web=Mock(uri="https://site1.com", title="Site 1")),
            Mock(web=Mock(uri="https://site2.com", title="Site 2")),
        ]
        mock_metadata.grounding_supports = [
            Mock(
                segment=Mock(start_index=0, end_index=20, text="test segment"),
                grounding_chunk_indices=[0, 1],
            )
        ]
        mock_metadata.search_entry_point = Mock(rendered_content="<search-widget>")

        # Create client instance to access the method
        from unittest.mock import patch

        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )

            # Call the extraction method
            grounding = client._extract_grounding_block(mock_metadata)

        assert isinstance(grounding, GroundingBlock)
        assert grounding.search_queries == ["query1", "query2"]
        assert len(grounding.grounding_chunks) == 2
        assert grounding.grounding_chunks[0]["web"]["title"] == "Site 1"
        assert grounding.grounding_chunks[1]["web"]["title"] == "Site 2"
        assert len(grounding.grounding_supports) == 1
        assert grounding.grounding_supports[0]["segment"]["text"] == "test segment"
        assert grounding.search_entry_point["rendered_content"] == "<search-widget>"

    def test_extract_grounding_block_partial(self):
        """Test extracting partial grounding metadata."""
        # Mock partial grounding metadata
        mock_metadata = Mock()
        mock_metadata.web_search_queries = ["single query"]
        mock_metadata.grounding_chunks = []
        mock_metadata.grounding_supports = []
        mock_metadata.search_entry_point = None

        from unittest.mock import patch

        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )
            grounding = client._extract_grounding_block(mock_metadata)

        assert isinstance(grounding, GroundingBlock)
        assert grounding.search_queries == ["single query"]
        assert grounding.grounding_chunks == []
        assert grounding.grounding_supports == []
        assert grounding.search_entry_point == {}

    def test_extract_grounding_block_missing_attributes(self):
        """Test extracting grounding when some attributes are missing."""
        # Mock metadata with missing attributes (set to empty lists to avoid iteration errors)
        mock_metadata = Mock()
        mock_metadata.web_search_queries = ["test"]
        mock_metadata.grounding_chunks = []  # Empty list instead of missing
        mock_metadata.grounding_supports = []  # Empty list instead of missing

        # Explicitly delete search_entry_point to simulate missing attribute
        if hasattr(mock_metadata, "search_entry_point"):
            delattr(mock_metadata, "search_entry_point")

        from unittest.mock import patch

        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )
            grounding = client._extract_grounding_block(mock_metadata)

        assert isinstance(grounding, GroundingBlock)
        assert grounding.search_queries == ["test"]
        assert grounding.grounding_chunks == []
        assert grounding.grounding_supports == []
        assert grounding.search_entry_point == {}

    def test_extract_grounding_block_none(self):
        """Test that None is returned when no metadata provided."""
        from unittest.mock import patch

        with patch.object(GeminiClient, "__post_init__"):
            client = GeminiClient(
                model="gemini-2.5-flash-lite-preview-06-17",
                project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                use_vertex=True,
            )
            result = client._extract_grounding_block(None)

        assert result is None


class TestCrossClientCompatibility:
    """Test how GroundingBlock is handled across different LLM clients."""

    def test_anthropic_filters_grounding_blocks(self):
        """Test that AnthropicClient filters out GroundingBlock content."""
        # Create content with mixed types including GroundingBlock
        mixed_content = [
            TextBlock(text="This is a text response."),
            GroundingBlock(
                search_queries=["test query"],
                grounding_chunks=[],
                grounding_supports=[],
                search_entry_point={},
                metadata={},
            ),
            TextBlock(text="More text after grounding."),
        ]

        # Test the _format_message_content method directly
        formatted = AnthropicClient._format_message_content(mixed_content)

        # Should only have text content, no grounding
        assert len(formatted) == 2  # Only the two text blocks
        assert all(item["type"] == "text" for item in formatted)
        assert formatted[0]["text"] == "This is a text response."
        assert formatted[1]["text"] == "More text after grounding."

    def test_gemini_grounding_block_integration(self):
        """Test that GeminiClient properly integrates GroundingBlock in responses."""
        # This test verifies that GroundingBlock works as MessageContent
        # The actual integration is tested in the main Gemini tests

        # Create a response with GroundingBlock (simulating what GeminiClient creates)
        grounding = GroundingBlock(
            search_queries=["test query"],
            grounding_chunks=[{"web": {"uri": "https://test.com", "title": "Test"}}],
            grounding_supports=[],
            search_entry_point={},
            metadata={},
        )

        ai_message = AIMessage(
            content=[TextBlock(text="Response with grounding."), grounding]
        )

        # Verify the message contains both content types
        assert len(ai_message.content) == 2
        assert isinstance(ai_message.content[0], TextBlock)
        assert isinstance(ai_message.content[1], GroundingBlock)
        assert ai_message.content[1].search_queries == ["test query"]

    def test_message_content_type_checking(self):
        """Test that GroundingBlock is properly recognized as MessageContent."""
        from flexai.message import MessageContent

        grounding = GroundingBlock(
            search_queries=["test"],
            grounding_chunks=[],
            grounding_supports=[],
            search_entry_point={},
            metadata={},
        )

        # Should be recognized as MessageContent
        assert isinstance(grounding, MessageContent)

        # Should work in message creation
        message = AIMessage(content=[grounding])
        assert len(message.content) == 1
        assert isinstance(message.content[0], GroundingBlock)

    def test_grounding_block_in_mixed_content(self):
        """Test GroundingBlock mixed with other content types."""
        from flexai.message import ToolCall

        mixed_content = [
            TextBlock(text="Here's what I found:"),
            GroundingBlock(
                search_queries=["mixed content test"],
                grounding_chunks=[
                    {"web": {"uri": "https://example.com", "title": "Example"}}
                ],
                grounding_supports=[],
                search_entry_point={},
                metadata={},
            ),
            ToolCall(id="tool_1", name="test_tool", input={"param": "value"}),
            TextBlock(text="Additional information."),
        ]

        message = AIMessage(content=mixed_content)

        # Verify all content types are preserved
        assert len(message.content) == 4
        assert isinstance(message.content[0], TextBlock)
        assert isinstance(message.content[1], GroundingBlock)
        assert isinstance(message.content[2], ToolCall)
        assert isinstance(message.content[3], TextBlock)

        # Verify grounding data is intact
        grounding = message.content[1]
        assert grounding.search_queries == ["mixed content test"]
        assert len(grounding.grounding_chunks) == 1
        assert grounding.grounding_chunks[0]["web"]["title"] == "Example"
