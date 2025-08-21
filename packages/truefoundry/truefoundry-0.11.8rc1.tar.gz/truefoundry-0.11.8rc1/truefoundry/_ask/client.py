try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.types import GetPromptResult, TextContent
except ImportError:
    import sys

    message_parts = [
        r'This feature requires the `ai` extra. Please install it using `pip install -U "truefoundry\[ai]"`.',
        "Note: This feature requires Python 3.10 or higher.",
    ]
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 10:
        message_parts.append(
            f"Your current Python version is '{python_version.major}.{python_version.minor}'."
        )
    raise ImportError("\n".join(message_parts)) from None

import json
import uuid
from contextlib import AsyncExitStack
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import rich_click as click
import yaml
from openai import NOT_GIVEN, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel
from rich.console import Console
from rich.status import Status

from truefoundry._ask.llm_utils import (
    log_chat_completion_message,
    translate_tools_for_gemini,
)
from truefoundry.common.constants import ENV_VARS, TFY_CONFIG_DIR
from truefoundry.logger import logger

console = Console(soft_wrap=False)


def _get_content(data: Any) -> Optional[Any]:
    content = None
    if isinstance(data, dict):
        content = (
            data.get("content", {}).get("text")
            if isinstance(data.get("content"), dict)
            else data.get("content")
        )
    else:
        content = data
    return content


class AskClient:
    """Handles the chat session lifecycle between the user and the assistant via OpenAI and MCP."""

    def __init__(
        self,
        cluster: str,
        token: str,
        openai_model: str,
        debug: bool = False,
        openai_client: Optional[AsyncOpenAI] = None,
    ):
        self.cluster = cluster
        self.token = token
        self.debug = debug

        self.async_openai_client = openai_client or AsyncOpenAI()
        self.openai_model = openai_model
        self.generation_params: Dict[str, Any] = dict(
            ENV_VARS.TFY_ASK_GENERATION_PARAMS
        )
        self._log_message(
            f"\nInitialized with model: {self.openai_model!r}, "
            f"generation_params: {self.generation_params!r}, "
            f"base_url: {str(self.async_openai_client.base_url)!r}\n",
        )
        self.history: List[ChatCompletionMessageParam] = []
        self._cached_tools: Optional[List[ChatCompletionToolParam]] = None
        self._session_id = str(uuid.uuid4())
        self._prompt_length = 0

    def _auth_headers(self):
        """Generate authorization headers for connecting to the SSE server."""
        return {
            "Authorization": f"Bearer {self.token}",
            "X-TFY-Session-Id": self._session_id,
        }

    def _format_tool_result(self, content) -> str:
        """Format tool result into a readable string or JSON block."""
        if isinstance(content, list):
            content = (
                content[0].text
                if len(content) == 1 and isinstance(content[0], TextContent)
                else content
            )
            if isinstance(content, list):
                return (
                    "```\n"
                    + "\n".join(
                        (
                            item.model_dump_json(indent=2)
                            if isinstance(item, BaseModel)
                            else str(item)
                        )
                        for item in content
                    )
                    + "\n```"
                )

        if isinstance(content, (BaseModel, dict)):
            return (
                "```\n"
                + json.dumps(
                    content.model_dump() if isinstance(content, BaseModel) else content,
                    indent=2,
                )
                + "\n```"
            )

        if isinstance(content, str):
            try:
                return "```\n" + json.dumps(json.loads(content), indent=2) + "\n```"
            except Exception:
                return content

        return str(content)

    def _append_message(self, message: ChatCompletionMessageParam, log: bool = True):
        """Append a message to history and optionally log it."""
        self._log_message(message, log)
        self.history.append(message)

    def _log_message(
        self,
        message: Union[str, ChatCompletionMessageParam],
        log: bool = False,
    ):
        """Display a message using Rich console, conditionally based on debug settings."""
        if not self.debug and not log:
            return
        if isinstance(message, str):
            console.print(message)
        else:
            log_chat_completion_message(message, console=console)

    def _maybe_save_transcript(self):
        """Save the transcript to a file."""
        if not click.confirm("Save the chat transcript to a file?", default=True):
            return
        transcripts_dir = TFY_CONFIG_DIR / "tfy-ask-transcripts"
        transcripts_dir.mkdir(parents=True, exist_ok=True)
        transcript_file = (
            transcripts_dir
            / f"chat-{self._session_id}-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.json"
        )

        def _custom_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, BaseModel):
                return obj.model_dump()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        data = {
            "cluster": self.cluster,
            "model": self.openai_model,
            "messages": self.history,
        }
        try:
            with open(transcript_file, "w") as f:
                json.dump(data, f, indent=2, default=_custom_encoder)
            console.print(f"Chat transcript saved to {transcript_file}")
        except (IOError, PermissionError) as e:
            console.print(f"[red]Failed to save transcript: {e}[/red]")

    def _load_config_from_file(
        self, filepath: str
    ) -> Tuple[Optional[GetPromptResult], str, Dict[str, Any]]:
        self._log_message(
            f"Loading initial prompt and params from file {filepath}.", log=True
        )
        with open(filepath, "r") as f:
            content = yaml.safe_load(f)
        if "prompt" in content:
            prompt_result = GetPromptResult.model_validate(content["prompt"])
        else:
            prompt_result = None
        model = content.get("model") or self.openai_model
        generation_params = (
            content.get("generation_params", {}) or self.generation_params
        )
        return prompt_result, model, generation_params

    def _maybe_reload_prompt_and_params(self):
        if ENV_VARS.TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE:
            prompt_result, model, generation_params = self._load_config_from_file(
                filepath=ENV_VARS.TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE
            )
            self.openai_model = model
            self.generation_params = generation_params
            if prompt_result:
                message_index = 0
                for message in prompt_result.messages:
                    data = (
                        message.model_dump()
                        if isinstance(message, BaseModel)
                        else message
                    )
                    content = _get_content(data)
                    # First message is system prompt?
                    if content:
                        if message_index < self._prompt_length:
                            self.history[message_index] = (
                                ChatCompletionSystemMessageParam(
                                    role="system", content=content
                                )
                            )
                        else:
                            # insert just before self._prompt_length
                            self.history.insert(
                                self._prompt_length,
                                ChatCompletionSystemMessageParam(
                                    role="system", content=content
                                ),
                            )
                        message_index += 1
                # Remove any leftover old prompt lines
                del self.history[message_index : self._prompt_length]
                self._prompt_length = message_index
            self._log_message(
                f"Reloaded initial prompt and params from {ENV_VARS.TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE}.",
                log=True,
            )

    async def _call_openai(self, tools: Optional[List[ChatCompletionToolParam]]):
        """Make a chat completion request to OpenAI with optional tool support."""
        return await self.async_openai_client.chat.completions.create(
            model=self.openai_model,
            messages=self.history,
            tools=tools or NOT_GIVEN,
            extra_headers={
                "X-TFY-METADATA": json.dumps(
                    {
                        "tfy_log_request": "true",
                        "session_id": self._session_id,
                    }
                )
            },
            **self.generation_params,
        )

    async def _handle_tool_calls(self, message, spinner: Status):
        """Execute tool calls returned by the assistant and return the results."""
        for tool_call in message.tool_calls:
            try:
                spinner.update(
                    f"Executing tool: {tool_call.function.name}", spinner="aesthetic"
                )
                args = json.loads(tool_call.function.arguments)
                result = await self.session.call_tool(tool_call.function.name, args)
                content = getattr(result, "content", result)
                result_content = self._format_tool_result(content)
            except Exception as e:
                result_content = f"Tool `{tool_call.function.name}` call failed: {e}"

            # Log assistant's tool call
            self._append_message(
                ChatCompletionAssistantMessageParam(
                    role="assistant", content=None, tool_calls=[tool_call]
                ),
                log=self.debug,
            )

            # Log tool response
            self._append_message(
                ChatCompletionToolMessageParam(
                    role="tool", tool_call_id=tool_call.id, content=result_content
                ),
                log=self.debug,
            )

    async def process_query(self, query: Optional[str] = None, max_turns: int = 50):
        """Handles sending user input to the assistant and processing the assistant’s reply."""
        if query:
            self._append_message(
                ChatCompletionUserMessageParam(role="user", content=query),
                log=self.debug,
            )

        tools = await self._list_tools()  # Fetch or use cached tool list

        turn: int = 0
        # Backup history to revert if OpenAI call fails
        _checkpoint_idx = len(self.history)

        with console.status(status="Thinking...", spinner="dots") as spinner:
            while True:
                try:
                    if turn >= max_turns:
                        self._log_message("Max turns reached. Exiting.", log=True)
                        break
                    spinner.update("Thinking...", spinner="dots")
                    response = await self._call_openai(tools=tools)
                    turn += 1
                    message = response.choices[0].message

                    if not message.content and not message.tool_calls:
                        self._log_message("No assistant response. Try again.", log=True)
                        break

                    if message.content:
                        self._append_message(
                            ChatCompletionAssistantMessageParam(
                                role="assistant", content=message.content
                            )
                        )

                    if message.tool_calls:
                        await self._handle_tool_calls(message, spinner)

                    if message.content and not message.tool_calls:
                        break
                except Exception as e:
                    self._log_message(f"OpenAI call failed: {e}", log=True)
                    console.print(
                        "Something went wrong. Please try rephrasing your query."
                    )
                    # Revert to safe state
                    self.history = self.history[:_checkpoint_idx]
                    turn = 0
                    break

    async def _list_tools(self) -> Optional[List[ChatCompletionToolParam]]:
        """Fetch and cache the list of available tools from the MCP session."""
        if self._cached_tools:
            return self._cached_tools

        tools: List[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema,
                },
            }
            for t in (await self.session.list_tools()).tools
        ]

        if "gemini" in self.openai_model.lower():
            tools = translate_tools_for_gemini(tools) or []

        self._cached_tools = tools

        self._log_message("\nAvailable tools:")
        for tool in self._cached_tools or []:
            self._log_message(
                f"  - {tool['function']['name']}: {tool['function']['description'] or ''}"
            )
        return self._cached_tools

    async def _load_initial_prompt(self, prompt_name: Optional[str]) -> None:
        """Load a system prompt to set assistant behavior at session start."""
        if not (self.session and prompt_name):
            return

        prompt_result = None
        if ENV_VARS.TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE:
            prompt_result, model, generation_params = self._load_config_from_file(
                filepath=ENV_VARS.TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE
            )
            self.openai_model = model
            self.generation_params = generation_params

        if not prompt_result:
            prompt_result = await self.session.get_prompt(name=prompt_name)

        if not prompt_result:
            self._log_message("Failed to get initial system prompt.")
            return

        for message in prompt_result.messages:
            data = message.model_dump() if isinstance(message, BaseModel) else message
            content = _get_content(data)
            # First message is system prompt?
            if content:
                self._append_message(
                    ChatCompletionSystemMessageParam(role="system", content=content),
                    log=self.debug,
                )
        self._prompt_length = len(self.history)

    async def chat_loop(self):
        """Interactive loop: accepts user queries and returns responses until interrupted or 'exit' is typed."""
        self._append_message(
            ChatCompletionUserMessageParam(
                role="user",
                content=f"Selected cluster: {self.cluster}",
            )
        )
        self._append_message(
            ChatCompletionAssistantMessageParam(
                role="assistant",
                content="Hello! How can I help you with this Kubernetes cluster?",
            )
        )

        while True:
            try:
                query = click.prompt(click.style("User", fg="yellow"), type=str)
                if not query:
                    self._log_message("Empty query. Type 'exit' to quit.", log=True)
                    continue

                if query.lower() in ("exit", "quit"):
                    self._log_message("Exiting chat...")
                    self._maybe_save_transcript()
                    break

                self._maybe_reload_prompt_and_params()
                await self.process_query(query)

            except (KeyboardInterrupt, EOFError, click.Abort):
                self._log_message("\nChat interrupted. Exiting chat...")
                self._maybe_save_transcript()
                break

    async def start_session(self, server_url: str, prompt_name: Optional[str] = None):
        """Initialize connection to the Streamable HTTP MCP server and prepare the chat session."""
        logger.debug(f"Starting a new client for {server_url}")
        async with AsyncExitStack() as exit_stack:
            try:
                read_stream, write_stream, _ = await exit_stack.enter_async_context(
                    streamablehttp_client(url=server_url, headers=self._auth_headers())
                )
                self.session = await exit_stack.enter_async_context(
                    ClientSession(read_stream=read_stream, write_stream=write_stream)
                )
                await self.session.initialize()
            except Exception as e:
                self._log_message(f"❌ Connection error: {e}", log=True)
                raise
            else:
                self._log_message(f"✅ Connected to {server_url}")
                await self._list_tools()
                await self._load_initial_prompt(prompt_name)
                self._log_message(
                    "\n[dim]Tip: Type 'exit' to quit chat.[/dim]", log=True
                )
                await self.chat_loop()


async def ask_client(
    cluster: str,
    server_url: str,
    token: str,
    openai_model: str,
    debug: bool = False,
    openai_client: Optional[AsyncOpenAI] = None,
):
    """Main entrypoint for launching the AskClient chat loop."""
    ask_client = AskClient(
        cluster=cluster,
        token=token,
        debug=debug,
        openai_client=openai_client,
        openai_model=openai_model,
    )
    try:
        await ask_client.start_session(
            server_url=server_url, prompt_name=ENV_VARS.TFY_ASK_SYSTEM_PROMPT_NAME
        )
    except KeyboardInterrupt:
        console.print("[yellow]Chat interrupted.[/yellow]")
    except Exception as e:
        console.print(
            f"[red]An unexpected error occurred while running the assistant: {e}[/red]\nCheck with TrueFoundry support for more details."
        )
