# import pytest
# from flexai.llm.anthropic import AnthropicClient

# # from flexai.llm.gemini import GeminiClient
# from flexai.llm.openai import OpenAIClient
# from flexai.message import AIMessage, DataBlock, TextBlock, SystemMessage, UserMessage

# clients = {
#     "anthropic": AnthropicClient(),
#     "gemini": GeminiClient(
#         model="gemini-2.5-flash-lite-preview-06-17",
#         project_id=os.environ.get("GOOGLE_PROJECT_ID", "test-project"),
#         location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
#         use_vertex=True,
#     "openai": OpenAIClient(),
# }


# @pytest.fixture
# def system_prompt():
#     return "You are an AI agent."


# @pytest.fixture
# def starter_python_code():
#     return """
# def starter_reflex_code():
#     # This is a starter reflex code.
#     pass
#     """


# @pytest.mark.parametrize("client", clients.values(), ids=clients.keys())
# @pytest.mark.asyncio
# async def test_no_tools_provided(client, system_prompt):
#     messages = [
#         UserMessage(
#             content="What is the capital of France?",
#         )
#     ]
#     message = await client.get_chat_response(
#         messages=messages,
#         system=system_prompt,
#         tools=[],
#     )
#     assert isinstance(message, AIMessage)


# @pytest.mark.parametrize("client", clients.values(), ids=clients.keys())
# @pytest.mark.asyncio
# async def test_standard_cot_workflow(client, system_prompt, starter_python_code):
#     messages = [
#         UserMessage(
#             content=[
#                 DataBlock(
#                     data={
#                         "request": "Build a simple counter app.",
#                         "lint_errors": {},
#                         "error_logs": "",
#                         "available_env_vars": [],
#                     },
#                     cache=False,
#                 ),
#                 TextBlock(
#                     text=f"<current_app_code>\n{starter_python_code}\n</current_app_code>",
#                     cache=False,
#                 ),
#             ],
#         ),
#     ]
#     system_message = SystemMessage(
#         content=[
#             TextBlock(
#                 text=system_prompt,
#                 cache=False,
#             ),
#         ],
#     )
#     response_message = await client.get_chat_response(
#         messages=messages,
#         system=system_message,
#         tools=[],
#     )
#     assert isinstance(response_message, AIMessage)


# @pytest.mark.parametrize("client", clients.values(), ids=clients.keys())
# @pytest.mark.asyncio
# async def test_standard_codewrite_workflow(client, system_prompt):
#     messages = [
#         UserMessage(
#             content=[
#                 DataBlock(
#                     data={
#                         "request": "Build a simple counter app.",
#                         "lint_errors": {},
#                         "error_logs": "",
#                         "available_env_vars": [],
#                     },
#                     cache=False,
#                 ),
#                 TextBlock(
#                     text=f"<current_app_code>\n{starter_python_code}\n</current_app_code>",
#                     cache=False,
#                 ),
#             ],
#         ),
#         AIMessage(
#             content=[
#                 DataBlock(
#                     data={
#                         "plan": "Here is a plan",
#                     },
#                     cache=False,
#                 )
#             ]
#         ),
#         UserMessage(
#             content=[
#                 DataBlock(
#                     data={
#                         "type": "memory",
#                         "memories": "here are memories",
#                         "error_memories": "here are error memories",
#                     },
#                     cache=False,
#                 ),
#             ],
#         ),
#     ]
#     message = await client.get_chat_response(
#         messages=messages,
#         system=system_prompt,
#         tools=[],
#     )
#     assert isinstance(message, AIMessage)


# @pytest.mark.parametrize("client", clients.values(), ids=clients.keys())
# @pytest.mark.asyncio
# async def test_call_tool_when_forced(client, system_prompt):
#     messages = [
#         UserMessage(
#             content="What is the capital of France?",
#         )
#     ]
#     await client.get_chat_response(
#         messages=messages,
#         system=system_prompt,
#         tools=[],
#     )
