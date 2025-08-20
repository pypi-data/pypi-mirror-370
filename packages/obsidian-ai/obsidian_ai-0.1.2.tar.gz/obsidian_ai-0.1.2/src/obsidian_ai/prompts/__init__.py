"""Configurable prompt templates."""

from .base import PromptManager
from .chat import ChatPrompts
from .research import ResearchPrompts

__all__ = ["ChatPrompts", "PromptManager", "ResearchPrompts"]
