import functools
import json
import logging
import operator
import os
import time
import uuid
from collections.abc import AsyncGenerator, Sequence
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any

import google.auth.transport.requests  # noqa: F401
from google import genai
from google.auth import default  # noqa: F401
from google.genai import types
from google.genai._api_client import BaseApiClient
from google.genai.types import FunctionDeclaration, Schema
from google.genai.types import Type as DataType
from google.oauth2 import service_account
from pydantic import BaseModel

from flexai.llm.client import Client
from flexai.message import (
    AIMessage,
    DataBlock,
    GroundingBlock,
    ImageBlock,
    Message,
    MessageContent,
    SystemMessage,
    TextBlock,
    ThoughtBlock,
    ToolCall,
    ToolResult,
    URLContextBlock,
    Usage,
)
from flexai.tool import Tool


def get_tool_call(function_call) -> ToolCall:
    return ToolCall(
        id=function_call.id or str(uuid.uuid4()),
        name=function_call.name,
        input=function_call.args,
    )


@dataclass(frozen=True)
class GeminiClient(Client):
    """Client for the Gemini API with support for both direct API and Vertex AI endpoints.

    This client supports:
    - Direct Gemini API access using API keys
    - Vertex AI regional endpoints with Google Cloud authentication
    - Global endpoints for higher availability and reliability

    Global Endpoint:
    The global endpoint provides higher availability and reliability than single regions.
    It's supported for Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash, and 2.0 Flash-Lite models.

    Usage Examples:

    # Direct API access (default)
    client = GeminiClient(api_key="your-api-key")

    # Vertex AI regional endpoint
    client = GeminiClient(
        project_id="your-project",
        location="us-central1",
        use_vertex=True
    )

    # Global endpoint (recommended for production)
    client = GeminiClient(
        project_id="your-project",
        location="global",
        use_vertex=True
    )

    Environment Variables:
    - GEMINI_API_KEY: API key for direct access
    - GOOGLE_PROJECT_ID: Default project ID for Vertex AI
    - VERTEX_AI_LOCATION: Default location (defaults to us-central1)
    - GEMINI_MODEL: Default model name

    Note: Global endpoint has some limitations:
    - No tuning support
    - No batch prediction
    - No context caching
    - No RAG corpus (RAG requests are supported)
    """

    # The provider name.
    provider: str = "gemini"

    # The API key to use for interacting with the model.
    api_key: InitVar[str] = field(default=os.environ.get("GEMINI_API_KEY", ""))

    # The client to use for interacting with the model.
    client: genai.client.AsyncClient | None = None

    # The base URL for the Gemini API.
    base_url: InitVar[str] = field(
        default=os.environ.get(
            "GEMINI_BASE_URL",
            "https://www.googleapis.com/auth/generative-language",
        )
    )

    # The model to use for the client.
    model: str = os.getenv("GEMINI_MODEL") or "gemini-2.5-pro-preview-06-05"

    # Default thinking budget for LLM calls
    default_thinking_budget: int | None = None

    # Project ID for Vertex AI (required when using Vertex AI or global endpoint)
    project_id: str | None = field(default=os.environ.get("GOOGLE_PROJECT_ID"))

    # Location for Vertex AI endpoints (use 'global' for global endpoint)
    location: str = field(default=os.environ.get("VERTEX_AI_LOCATION", "us-central1"))

    # Whether to use Vertex AI instead of direct API
    use_vertex: bool = False

    def __post_init__(self, api_key, base_url, **kwargs):
        use_vertex = kwargs.get("use_vertex", self.use_vertex)
        credential_file_path = kwargs.get("credential_file_path", "")

        if use_vertex or self.location == "global":
            # Using Vertex AI or global endpoint
            if not self.project_id:
                raise ValueError(
                    "project_id is required when using Vertex AI or global endpoint. "
                    "Set GOOGLE_PROJECT_ID environment variable or pass project_id parameter."
                )

            scopes = [
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language",
            ]

            # Handle authentication
            if credential_file_path and Path(credential_file_path).exists():
                # Use service account file
                creds = service_account.Credentials.from_service_account_file(
                    credential_file_path, scopes=scopes
                )
            else:
                # Use default credentials (ADC)
                try:
                    from google.auth import default

                    creds, _ = default(scopes=scopes)
                except Exception as e:
                    raise ValueError(
                        "Failed to load default credentials. Either set up Application Default Credentials "
                        "or provide credential_file_path."
                    ) from e

            object.__setattr__(
                self,
                "client",
                genai.client.AsyncClient(
                    api_client=BaseApiClient(
                        vertexai=True,
                        credentials=creds,
                        location=self.location,
                        project=self.project_id,
                    )
                ),
            )
        else:
            # Using direct API
            object.__setattr__(
                self,
                "client",
                genai.client.AsyncClient(api_client=BaseApiClient(api_key=api_key)),
            )

    @staticmethod
    def format_tool(tool: Tool) -> FunctionDeclaration:
        return FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=Schema(
                type=DataType.OBJECT,
                properties={
                    param_name: Schema(type=DataType(param_type))
                    for param_name, param_type in tool.params
                },
            ),
        )

    @staticmethod
    def _extract_content_from_part_object(part_object: types.Part):
        value = next(
            ((k, v) for k, v in vars(part_object).items() if v is not None), None
        )
        if not value:
            return None
        if value[0] == "text":
            return TextBlock(
                text=value[1],
            )
        if value[0] == "thought":
            return ThoughtBlock(
                text=part_object.text or "",
            )
        if value[0] == "function_call":
            return get_tool_call(value[1])

        return None

    @classmethod
    def _format_message_content(
        cls,
        content: str | MessageContent | Sequence[MessageContent],
        name_context: dict,
    ):
        if isinstance(content, str):
            return [{"text": content}]

        if isinstance(content, Sequence):
            formatted_contents = [
                cls._format_message_content(item, name_context=name_context)
                for item in content
            ]
            # Just a list flatten. I don't like itertools.chain.from_iterable personally
            formatted_contents = [
                [item] if not isinstance(item, list) else item
                for item in formatted_contents
            ]
            return functools.reduce(operator.iadd, formatted_contents, [])

        if isinstance(content, ImageBlock):
            return {
                "inlineData": {
                    "mimeType": content.mime_type,
                    "data": content.image,
                }
            }
        if isinstance(content, TextBlock):
            return {
                "text": content.text,
            }
        if isinstance(content, DataBlock):
            return [
                cls._format_message_content(item, name_context=name_context)
                for item in content.into_text_and_image_blocks()
            ]
        if isinstance(content, ToolCall):
            name_context[content.id] = content.name
            return {
                "functionCall": {
                    "id": content.id,
                    "name": content.name,
                    "args": content.input,
                }
            }
        if isinstance(content, ToolResult):
            formatted_result = content.result
            if isinstance(formatted_result, str):
                formatted_result = {
                    "result": formatted_result,
                }
            if not isinstance(formatted_result, dict):
                raise TypeError(
                    f"Expected tool reuslt to be of type str or dict, instead got {type(formatted_result)}"
                )
            if content.tool_call_id not in name_context:
                raise ValueError(
                    f"Tool call {content.tool_call_id} not found in context, but a result for it was found."
                )
            return {
                "functionResponse": {
                    "id": content.tool_call_id,
                    "name": name_context[content.tool_call_id],
                    "response": formatted_result,
                }
            }
        raise ValueError(f"Unsupported content type: {type(content)}")

    def _get_params(
        self,
        messages: list[Message],
        system: str | SystemMessage,
        tools: list[Tool] | None,
        force_tool: bool,
        include_thoughts: bool,
        disable_thinking: bool,
        thinking_budget: int | None,
        use_url_context: bool = False,
        use_google_search: bool = False,
        google_search_dynamic_threshold: float | None = None,
        **kwargs,
    ):
        name_context = {}

        formatted_messages = [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": self._format_message_content(
                    message.content, name_context=name_context
                ),
            }
            for message in messages
        ]

        if isinstance(system, str):
            system = SystemMessage(content=system)

        formatted_system = json.dumps(
            self._format_message_content(
                system.normalize().content, name_context=name_context
            )
        )

        config_args: dict[str, Any] = {
            "system_instruction": formatted_system,
        }

        thinking_args = {}

        if disable_thinking:
            thinking_budget = 0

        if thinking_budget is not None:
            thinking_args["thinking_budget"] = thinking_budget

        if include_thoughts:
            thinking_args["include_thoughts"] = True

        if thinking_args:
            config_args["thinking_config"] = types.ThinkingConfig(**thinking_args)

        gemini_tools = []
        if use_url_context:
            gemini_tools.append(types.Tool(url_context=types.UrlContext()))

        if use_google_search:
            # Check if we're using Gemini 2.0+ models (recommended google_search tool)
            # or Gemini 1.5 models (legacy google_search_retrieval tool)
            model_version = self.model.lower()
            if any(ver in model_version for ver in ["2.0", "2.5"]):
                # Use the new google_search tool for Gemini 2.0+ models
                gemini_tools.append(types.Tool(google_search=types.GoogleSearch()))
            # Use the legacy google_search_retrieval tool for Gemini 1.5 models
            elif google_search_dynamic_threshold is not None:
                # Dynamic mode with threshold
                retrieval_config = types.DynamicRetrievalConfig(
                    mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
                    dynamic_threshold=google_search_dynamic_threshold,
                )
                gemini_tools.append(
                    types.Tool(
                        google_search_retrieval=types.GoogleSearchRetrieval(
                            dynamic_retrieval_config=retrieval_config
                        )
                    )
                )
            else:
                # Default mode (always search)
                gemini_tools.append(
                    types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())
                )

        if tools:
            # Create a formatted tool list
            formatted_tool_list = types.Tool(
                function_declarations=[self.format_tool(tool) for tool in tools]
            )
            gemini_tools.append(formatted_tool_list)

        if gemini_tools:
            # Create a tool config object
            tool_config = None
            if force_tool and tools:
                tool_config = types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=types.FunctionCallingConfigMode.ANY,
                    ),
                )
            config_args.update(
                {
                    "tools": gemini_tools,
                    "tool_config": tool_config,
                }
            )

        if "model" in kwargs:
            config_args.update(
                {
                    "response_mime_type": "application/json",
                    "response_schema": kwargs["model"],
                }
            )

        config = types.GenerateContentConfig(
            **config_args,
        )
        return {
            "model": self.model,
            "contents": formatted_messages,
            "config": config,
        }

    async def get_chat_response(
        self,
        messages: list[Message],
        *,
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        force_tool: bool = True,
        disable_thinking: bool = False,
        thinking_budget: int | None = None,
        include_thoughts: bool = False,
        use_url_context: bool = False,
        use_google_search: bool = False,
        google_search_dynamic_threshold: float | None = None,
        **kwargs,
    ) -> AIMessage:
        if not self.client:
            raise ValueError("GeminiClient is not initialized.")
        extra_param_args = {}
        if "model" in kwargs:
            extra_param_args["model"] = kwargs["model"]

        # If this client has a default thinking budget set, use that if one wasn't specified here
        thinking_budget = thinking_budget or self.default_thinking_budget
        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            force_tool=force_tool,
            disable_thinking=disable_thinking,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts,
            use_url_context=use_url_context,
            use_google_search=use_google_search,
            google_search_dynamic_threshold=google_search_dynamic_threshold,
            **extra_param_args,
        )
        start = time.time()
        response_object = await self.client.models.generate_content(
            **params,
        )
        usage_metadata = response_object.usage_metadata
        if not usage_metadata:
            raise ValueError("Gemini did not respond with any usage metadata.")
        input_tokens = usage_metadata.prompt_token_count or 0
        output_tokens = (usage_metadata.total_token_count or 0) - input_tokens
        cache_read = usage_metadata.cached_content_token_count or 0
        usage = Usage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read,
            cache_write_tokens=0,  # Currently not accounted for
            generation_time=time.time() - start,
        )
        # Handle this case
        if not response_object.candidates or not response_object.candidates[0].content:
            raise ValueError(
                "Gemini did not respond with any content, and candidates is null."
            )
        response_content_parts = response_object.candidates[0].content.parts
        if not response_content_parts:
            raise ValueError("Gemini did not respond with any content.")
        formatted_content_parts: list[
            TextBlock | ThoughtBlock | ToolCall | URLContextBlock | GroundingBlock
        ] = list(
            filter(
                None,
                [
                    self._extract_content_from_part_object(part)
                    for part in response_content_parts
                ],
            )
        )

        # Add URL context block if metadata is present
        if response_object.candidates and len(response_object.candidates) > 0:
            url_context_metadata = getattr(
                response_object.candidates[0], "url_context_metadata", None
            )
            if url_context_block := self._extract_url_context_block(
                url_context_metadata
            ):
                formatted_content_parts.append(url_context_block)

            # Add grounding block if metadata is present
            grounding_metadata = getattr(
                response_object.candidates[0], "grounding_metadata", None
            )
            if grounding_block := self._extract_grounding_block(grounding_metadata):
                formatted_content_parts.append(grounding_block)

        return AIMessage(
            content=formatted_content_parts,
            usage=usage,
        )

    async def stream_chat_response(
        self,
        messages: list[Message],
        *,
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        allow_tool: bool = True,
        force_tool: bool = True,
        disable_thinking: bool = False,
        thinking_budget: int | None = None,
        include_thoughts: bool = False,
        use_url_context: bool = False,
        use_google_search: bool = False,
        google_search_dynamic_threshold: float | None = None,
        **kwargs,
    ) -> AsyncGenerator[MessageContent | AIMessage, None]:
        if not self.client:
            raise ValueError("GeminiClient is not initialized.")

        extra_param_args = {}
        if "model" in kwargs:
            extra_param_args["model"] = kwargs["model"]

        # If this client has a default thinking budget set, use that if one wasn't specified here
        thinking_budget = thinking_budget or self.default_thinking_budget
        usage = Usage(
            input_tokens=0,
            output_tokens=0,
            cache_read_tokens=0,
            cache_write_tokens=0,
            generation_time=0,
        )
        params = self._get_params(
            messages=messages,
            system=system,
            tools=tools,
            force_tool=force_tool,
            disable_thinking=disable_thinking,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts,
            use_url_context=use_url_context,
            use_google_search=use_google_search,
            google_search_dynamic_threshold=google_search_dynamic_threshold,
            **extra_param_args,
        )
        start = time.time()
        response_object = await self.client.models.generate_content_stream(
            **params,
        )
        text_buffer = None
        total_content_list: list[
            TextBlock | ThoughtBlock | ToolCall | URLContextBlock | GroundingBlock
        ] = []
        url_context_metadata = None
        grounding_metadata = None

        async for chunk in response_object:
            # Handle this case
            if not chunk.candidates or not chunk.candidates[0].content:
                continue

            chunk_parts = chunk.candidates[0].content.parts

            if chunk.candidates and len(chunk.candidates) > 0:
                chunk_url_context_metadata = getattr(
                    chunk.candidates[0], "url_context_metadata", None
                )
                if chunk_url_context_block := self._extract_url_context_block(
                    chunk_url_context_metadata
                ):
                    yield chunk_url_context_block
                chunk_grounding_metadata = getattr(
                    chunk.candidates[0], "grounding_metadata", None
                )
                if chunk_grounding_block := self._extract_grounding_block(
                    chunk_grounding_metadata
                ):
                    yield chunk_grounding_block

            usage_metadata = chunk.usage_metadata
            if not usage_metadata:
                raise ValueError("Gemini did not respond with any usage metadata.")
            input_tokens = usage_metadata.prompt_token_count or 0
            output_tokens = (usage_metadata.total_token_count or 0) - input_tokens
            cache_read = usage_metadata.cached_content_token_count or 0
            usage.input_tokens += input_tokens
            usage.output_tokens += output_tokens
            usage.cache_read_tokens += cache_read
            if isinstance(chunk_parts, list):
                for part in chunk_parts:
                    to_yield = self._extract_content_from_part_object(part)
                    if isinstance(to_yield, TextBlock):
                        # We don't need to keep thoughts in the final message
                        if not isinstance(to_yield, ThoughtBlock):
                            if not text_buffer:
                                text_buffer = TextBlock(text="")
                            text_buffer = text_buffer.append(to_yield.text)
                        yield to_yield
                    elif isinstance(to_yield, ToolCall):
                        total_content_list.append(to_yield)
                        yield to_yield

        usage.generation_time = time.time() - start
        if text_buffer:
            total_content_list.append(text_buffer)

        # Add URL context block if metadata is present
        if url_context_block := self._extract_url_context_block(url_context_metadata):
            total_content_list.append(url_context_block)

        # Add grounding block if metadata is present
        if grounding_block := self._extract_grounding_block(grounding_metadata):
            total_content_list.append(grounding_block)

        yield AIMessage(
            content=total_content_list,
            usage=usage,
        )

    def _extract_url_context_block(
        self, url_context_metadata
    ) -> URLContextBlock | None:
        """Extract URLContextBlock from URL context metadata.

        Args:
            url_context_metadata: The URL context metadata from Gemini response.

        Returns:
            URLContextBlock if metadata is present, None otherwise.
        """
        if not url_context_metadata:
            return None

        # Extract URLs and metadata from the URL context
        urls_accessed = []
        metadata_dict = {}

        if hasattr(url_context_metadata, "__iter__"):
            # Handle list of URL metadata objects
            for url_meta in url_context_metadata:
                if hasattr(url_meta[1][0], "retrieved_url"):
                    urls_accessed.append(url_meta[1][0].retrieved_url)
                # Store the complete metadata object
                metadata_dict = {"url_metadata": url_context_metadata}
        else:
            # Handle single metadata object or dict
            if hasattr(url_context_metadata, "retrieved_url"):
                urls_accessed.append(url_context_metadata.retrieved_url)
            metadata_dict = {"url_metadata": url_context_metadata}

        return URLContextBlock(urls_accessed=urls_accessed, metadata=metadata_dict)

    def _extract_grounding_block(self, grounding_metadata) -> GroundingBlock | None:
        """Extract GroundingBlock from Google Search grounding metadata.

        Args:
            grounding_metadata: The grounding metadata from Gemini response.

        Returns:
            GroundingBlock if metadata is present, None otherwise.
        """
        if not grounding_metadata:
            return None

        # Extract search queries
        search_queries = []
        if getattr(grounding_metadata, "web_search_queries", None):
            search_queries = list(grounding_metadata.web_search_queries or [])

        # Extract grounding chunks
        grounding_chunks = []
        if getattr(grounding_metadata, "grounding_chunks", None):
            grounding_chunks = [
                {
                    "web": {
                        "uri": chunk.web.uri
                        if hasattr(chunk, "web") and hasattr(chunk.web, "uri")
                        else "",
                        "title": chunk.web.title
                        if hasattr(chunk, "web") and hasattr(chunk.web, "title")
                        else "",
                    }
                }
                for chunk in grounding_metadata.grounding_chunks
                if hasattr(chunk, "web")
            ]

        # Extract grounding supports
        grounding_supports = []
        if getattr(grounding_metadata, "grounding_supports", None):
            grounding_supports = [
                {
                    "segment": {
                        "start_index": support.segment.start_index
                        if hasattr(support, "segment")
                        and hasattr(support.segment, "start_index")
                        else 0,
                        "end_index": support.segment.end_index
                        if hasattr(support, "segment")
                        and hasattr(support.segment, "end_index")
                        else 0,
                        "text": support.segment.text
                        if hasattr(support, "segment")
                        and hasattr(support.segment, "text")
                        else "",
                    },
                    "grounding_chunk_indices": list(
                        support.grounding_chunk_indices or []
                    ),
                }
                for support in grounding_metadata.grounding_supports
                if hasattr(support, "segment")
            ]

        # Extract search entry point
        search_entry_point = {}
        if getattr(grounding_metadata, "search_entry_point", None):
            entry_point = grounding_metadata.search_entry_point
            if hasattr(entry_point, "rendered_content"):
                search_entry_point = {"rendered_content": entry_point.rendered_content}

        return GroundingBlock(
            search_queries=search_queries,
            grounding_chunks=grounding_chunks,
            grounding_supports=grounding_supports,
            search_entry_point=search_entry_point,
            metadata={"grounding_metadata": grounding_metadata},
        )

    def _extract_text_content(self, content: Any) -> str:
        """Extract text content from response, handling various formats.

        Args:
            content: The response content to extract text from.

        Returns:
            The extracted text content.

        Raises:
            TypeError: If the response is not a string.
            ValueError: If no text content found in response.
        """
        if isinstance(content, list):
            # Filter to only TextBlock content, ignoring GroundingBlock and other types
            text_blocks = [item for item in content if isinstance(item, TextBlock)]
            if len(text_blocks) == 1:
                content = text_blocks[0]
            elif len(text_blocks) > 1:
                # Concatenate multiple text blocks
                content = "".join(block.text for block in text_blocks)
            elif len(content) == 1:
                # Fallback for single non-TextBlock item
                content = content[0]
            else:
                raise ValueError("No text content found in response.")

        if isinstance(content, TextBlock):
            content = content.text

        if not isinstance(content, str):
            raise TypeError("The response is not a string.")

        return content

    def _accumulate_usage(self, base_usage: Usage, additional_usage: Usage) -> Usage:
        """Combine two Usage objects by accumulating their values.

        Args:
            base_usage: The base usage to add to.
            additional_usage: The additional usage to accumulate.

        Returns:
            A new Usage object with accumulated values.
        """
        return Usage(
            input_tokens=base_usage.input_tokens + additional_usage.input_tokens,
            output_tokens=base_usage.output_tokens + additional_usage.output_tokens,
            cache_read_tokens=base_usage.cache_read_tokens
            + additional_usage.cache_read_tokens,
            cache_write_tokens=base_usage.cache_write_tokens
            + additional_usage.cache_write_tokens,
            generation_time=base_usage.generation_time
            + additional_usage.generation_time,
        )

    async def _get_structured_response_with_usage(
        self,
        messages: list[Message],
        model: type[BaseModel],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        disable_thinking: bool = False,
        thinking_budget: int | None = None,
        include_thoughts: bool = False,
        use_url_context: bool = False,
        use_google_search: bool = False,
        google_search_dynamic_threshold: float | None = None,
        **kwargs,
    ) -> tuple[BaseModel, Usage]:
        """Get the structured response from the chat model with usage tracking.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: Tools to use in the response.
            disable_thinking: Whether to disable thinking for this request.
            thinking_budget: The thinking budget for this request.
            include_thoughts: Whether to include thoughts in the response.
            use_url_context: Whether to enable URL context for accessing web content.
            use_google_search: Whether to enable Google Search for grounding.
            google_search_dynamic_threshold: Dynamic threshold for Google Search.
            kwargs: Additional keyword arguments to pass to the model.

        Returns:
            A tuple of (structured response, accumulated usage information).

        Raises:
            ValueError: If the response is not valid JSON or doesn't match the model schema.
        """
        logger = logging.getLogger(__name__)

        # Initial attempt with native structured output support
        response = await self.get_chat_response(
            messages,
            system=system,
            tools=tools,
            force_tool=False,
            disable_thinking=disable_thinking,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts,
            use_url_context=use_url_context,
            use_google_search=use_google_search,
            google_search_dynamic_threshold=google_search_dynamic_threshold,
            model=model.model_json_schema(),
            **kwargs,
        )

        try:
            content = self._extract_text_content(response.content)
            parsed_model = model.model_validate_json(content)
            return parsed_model, response.usage
        except Exception as initial_error:
            logger.warning(
                f"Structured response parsing failed, retrying with clearer instructions. "
                f"This will result in additional API usage. Error: {initial_error}"
            )

            # Retry with more explicit instructions
            retry_system = f"""{system}

Return your answer as a valid JSON object according to this schema:
{model.model_json_schema()}

Return only the JSON object. Do not include any explanations or markdown formatting."""

            retry_response = await self.get_chat_response(
                messages,
                system=retry_system,
                tools=tools,
                force_tool=False,
                disable_thinking=disable_thinking,
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts,
                use_url_context=use_url_context,
                use_google_search=use_google_search,
                google_search_dynamic_threshold=google_search_dynamic_threshold,
                **kwargs,
            )

            # Accumulate usage from both attempts
            total_usage = self._accumulate_usage(response.usage, retry_response.usage)

            try:
                retry_content = self._extract_text_content(retry_response.content)
                parsed_model = model.model_validate_json(retry_content)

                logger.info(
                    f"Structured response retry successful. Total usage: "
                    f"{total_usage.input_tokens} input tokens, "
                    f"{total_usage.output_tokens} output tokens, "
                    f"{total_usage.generation_time:.2f}s generation time"
                )

                return parsed_model, total_usage
            except Exception as retry_error:
                logger.exception(
                    f"Structured response failed after retry. Total usage: "
                    f"{total_usage.input_tokens} input tokens, "
                    f"{total_usage.output_tokens} output tokens, "
                    f"{total_usage.generation_time:.2f}s generation time. "
                )
                raise ValueError(
                    "Failed to parse structured response after retry"
                ) from retry_error

    async def get_structured_response(
        self,
        messages: list[Message],
        model: type[BaseModel],
        system: str | SystemMessage = "",
        tools: list[Tool] | None = None,
        disable_thinking: bool = False,
        thinking_budget: int | None = None,
        include_thoughts: bool = False,
        use_url_context: bool = False,
        use_google_search: bool = False,
        google_search_dynamic_threshold: float | None = None,
        **kwargs,
    ) -> BaseModel:
        """Get the structured response from the chat model.

        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
            system: Optional system message to set the behavior of the AI.
            tools: Tools to use in the response.
            disable_thinking: Whether to disable thinking for this request.
            thinking_budget: The thinking budget for this request.
            include_thoughts: Whether to include thoughts in the response.
            use_url_context: Whether to enable URL context for accessing web content.
            use_google_search: Whether to enable Google Search for grounding.
            google_search_dynamic_threshold: Dynamic threshold for Google Search.
            kwargs: Additional keyword arguments to pass to the model.

        Returns:
            The structured response from the model.
        """
        structured_response, _ = await self._get_structured_response_with_usage(
            messages=messages,
            model=model,
            system=system,
            tools=tools,
            disable_thinking=disable_thinking,
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts,
            use_url_context=use_url_context,
            use_google_search=use_google_search,
            google_search_dynamic_threshold=google_search_dynamic_threshold,
            **kwargs,
        )
        return structured_response

    def get_endpoint_info(self) -> dict[str, str | bool]:
        """Get information about the current endpoint configuration.

        Returns:
            Dictionary with endpoint information
        """
        return {
            "location": self.location,
            "project_id": self.project_id or "",
            "is_global": self.location == "global",
            "use_vertex": self.use_vertex or self.location == "global",
            "model": self.model,
        }
