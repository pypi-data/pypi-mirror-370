from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptTemplate:
    """A configurable prompt template."""

    name: str
    template: str
    variables: list[str]

    def render(self, **kwargs: str) -> str:
        """Render the template with provided variables."""
        missing = [var for var in self.variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing template variables: {missing}")

        return self.template.format(**kwargs)


class PromptManager:
    """Manages and loads prompt templates from files or environment."""

    def __init__(self, prompts_dir: Path | None = None):
        self.prompts_dir = prompts_dir or Path(__file__).parent
        self._templates: dict[str, PromptTemplate] = {}

    def load_template(self, name: str, template: str, variables: list[str]) -> PromptTemplate:
        """Load a template and store it."""
        prompt_template = PromptTemplate(name, template, variables)
        self._templates[name] = prompt_template
        return prompt_template

    def get_template(self, name: str) -> PromptTemplate:
        """Get a stored template."""
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found")
        return self._templates[name]

    def render(self, name: str, **kwargs: str) -> str:
        """Render a template with variables."""
        return self.get_template(name).render(**kwargs)

    def load_from_env(self, name: str, default: str, variables: list[str]) -> PromptTemplate:
        """Load template from environment variable with fallback."""
        env_key = f"OBSIDIAN_AI_PROMPT_{name.upper()}"
        template_text = os.getenv(env_key, default)
        return self.load_template(name, template_text, variables)

    def load_from_file(self, name: str, filename: str, variables: list[str]) -> PromptTemplate:
        """Load template from file."""
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        template_text = file_path.read_text(encoding="utf-8")
        return self.load_template(name, template_text, variables)


# Global prompt manager instance
prompt_manager = PromptManager()
