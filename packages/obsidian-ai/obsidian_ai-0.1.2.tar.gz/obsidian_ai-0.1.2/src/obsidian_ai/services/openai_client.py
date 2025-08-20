from __future__ import annotations

from typing import Any

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..infrastructure.config import config


class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""

    pass


class OpenAIClient:
    """Wrapper for OpenAI client with error handling and retries."""

    def __init__(self) -> None:
        self.client = OpenAI()

    def chat_completion(
        self, messages: list[dict[str, str]], tools: list[dict] | None = None, max_tokens: int = 2000, temperature: float = 0.1
    ) -> ChatCompletion:
        """Create a chat completion with error handling."""
        try:
            return self.client.chat.completions.create(
                model=config.model, messages=messages, tools=tools, max_completion_tokens=max_tokens, temperature=temperature  # type: ignore[arg-type]
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIError(f"Failed to get OpenAI response: {e}") from e

    def simple_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """Get a simple text completion."""
        try:
            response = self.chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error in simple completion: {e}")
            return f"Error: Could not process request - {e}"

    def structured_completion(self, system_prompt: str, user_prompt: str, tools: list[dict] | None = None) -> tuple[str, list[dict] | None]:
        """Get a structured completion with optional tool calls."""
        try:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

            response = self.chat_completion(messages, tools=tools)
            message = response.choices[0].message

            content = message.content or ""
            tool_calls = [tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None

            return content, tool_calls

        except OpenAIError:
            raise
        except Exception as e:
            logger.error(f"Error in structured completion: {e}")
            return f"Error: {e}", None

    def continue_conversation(self, messages: list[dict[str, Any]], tools: list[dict] | None = None) -> str:
        """Continue a conversation with tool results."""
        try:
            response = self.chat_completion(messages, tools=tools)
            return response.choices[0].message.content or ""
        except OpenAIError:
            raise
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return f"Error: Could not continue conversation - {e}"


# Global client instance - lazy initialization
_openai_client = None


def get_openai_client() -> OpenAIClient:
    """Get the global OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


# For backward compatibility
openai_client = None
