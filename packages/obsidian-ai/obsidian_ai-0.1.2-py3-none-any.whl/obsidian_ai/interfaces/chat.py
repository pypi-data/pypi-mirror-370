from __future__ import annotations

import json
from typing import Any

from loguru import logger
from rich.console import Console
from rich.panel import Panel

from ..services.openai_client import get_openai_client, OpenAIError
from ..prompts.chat import ChatPrompts
from .tools import TOOLS, dispatch_tool


class ChatSession:
    """Manages chat sessions with tool integration and error handling."""

    def __init__(self) -> None:
        self.console = Console()
        self.prompts = ChatPrompts()

    def chat_once(self, query: str, show_tools: bool = False) -> str:
        """Single question-answer chat with optional tool visibility."""
        try:
            return self._execute_chat(query, show_tools)
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I encountered an error while processing your request: {e}"

    def _execute_chat(self, query: str, show_tools: bool) -> str:
        """Execute a single chat interaction."""
        messages = [{"role": "system", "content": self.prompts.system_prompt}, {"role": "user", "content": query}]

        try:
            response = get_openai_client().chat_completion(messages, tools=TOOLS)
            message = response.choices[0].message

            # Handle tool calls
            if message.tool_calls:
                return self._handle_tool_calls(messages, message, show_tools)

            return message.content or "No response generated."

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm having trouble connecting to the AI service. Please try again."

    def _handle_tool_calls(self, messages: list, message: Any, show_tools: bool) -> str:
        """Handle tool calls and get final response."""
        if show_tools:
            self._display_tool_calls(message.tool_calls)

        # Add assistant message with tool calls
        messages.append({"role": "assistant", "content": message.content, "tool_calls": [tc.model_dump() for tc in message.tool_calls]})

        # Execute tools and add results
        for tool_call in message.tool_calls:
            try:
                result = dispatch_tool(tool_call.function.name, json.loads(tool_call.function.arguments))

                messages.append({"role": "tool", "content": result, "tool_call_id": tool_call.id})

                if show_tools:
                    self._display_tool_result(result)

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                messages.append({"role": "tool", "content": json.dumps({"error": str(e)}), "tool_call_id": tool_call.id})

        # Get final response
        try:
            final_response = get_openai_client().continue_conversation(messages)
            return final_response or "No final response generated."
        except OpenAIError as e:
            logger.error(f"Error getting final response: {e}")
            return "I found some information but had trouble formulating a response."

    def _display_tool_calls(self, tool_calls: list) -> None:
        """Display tool calls to user."""
        for tool_call in tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
                args_str = ", ".join(f"{k}={v}" for k, v in args.items())
                self.console.print(f"[yellow]🔧 Calling {tool_call.function.name}({args_str})[/yellow]")
            except Exception:
                self.console.print(f"[yellow]🔧 Calling {tool_call.function.name}[/yellow]")

    def _display_tool_result(self, result: str) -> None:
        """Display truncated tool results."""
        display_result = result[:200] + "..." if len(result) > 200 else result
        self.console.print(f"[dim]   → {display_result}[/dim]")

    def chat_repl(self) -> None:
        """Interactive chat loop with error handling."""
        self.console.print(Panel("Obsidian-AI Chat. Type 'quit' to exit.", title="Welcome", border_style="blue"))

        while True:
            try:
                query = self.console.input("\n[bold blue]You:[/bold blue] ")
            except (EOFError, KeyboardInterrupt):
                break

            if query.strip().lower() in ("quit", "exit", "q"):
                break

            if not query.strip():
                continue

            try:
                response = self.chat_once(query, show_tools=True)
                self.console.print(Panel(response, title="Assistant", border_style="green"))
            except Exception as e:
                logger.error(f"REPL error: {e}")
                self.console.print(f"[red]Error: {e}[/red]")

        self.console.print("Goodbye!")

    def update_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt for this session."""
        self.prompts.update_system_prompt(new_prompt)
