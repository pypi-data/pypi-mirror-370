import pytest
import os
from unittest.mock import patch

from obsidian_ai.prompts.base import PromptTemplate, PromptManager
from obsidian_ai.prompts.chat import ChatPrompts
from obsidian_ai.prompts.research import ResearchPrompts


class TestPromptTemplate:
    def test_basic_template_rendering(self):
        template = PromptTemplate(name="test", template="Hello {name}, welcome to {place}!", variables=["name", "place"])

        result = template.render(name="Alice", place="Wonderland")
        assert result == "Hello Alice, welcome to Wonderland!"

    def test_missing_variables_error(self):
        template = PromptTemplate(name="test", template="Hello {name}!", variables=["name"])

        with pytest.raises(ValueError, match="Missing template variables"):
            template.render()

    def test_extra_variables_ignored(self):
        template = PromptTemplate(name="test", template="Hello {name}!", variables=["name"])

        result = template.render(name="Alice", extra="ignored")
        assert result == "Hello Alice!"


class TestPromptManager:
    def test_load_and_get_template(self):
        manager = PromptManager()
        template = manager.load_template("greeting", "Hello {name}!", ["name"])

        retrieved = manager.get_template("greeting")
        assert retrieved == template
        assert retrieved.name == "greeting"

    def test_get_nonexistent_template(self):
        manager = PromptManager()

        with pytest.raises(KeyError, match="Template 'nonexistent' not found"):
            manager.get_template("nonexistent")

    def test_render_template(self):
        manager = PromptManager()
        manager.load_template("test", "Hello {username}!", ["username"])

        result = manager.render("test", username="World")
        assert result == "Hello World!"

    def test_load_from_env_with_default(self):
        manager = PromptManager()

        with patch.dict(os.environ, {}, clear=True):
            template = manager.load_from_env("test_prompt", "Default: {value}", ["value"])

            result = template.render(value="test")
            assert result == "Default: test"

    def test_load_from_env_with_override(self):
        manager = PromptManager()

        with patch.dict(os.environ, {"OBSIDIAN_AI_PROMPT_TEST_PROMPT": "Override: {value}"}):
            template = manager.load_from_env("test_prompt", "Default: {value}", ["value"])

            result = template.render(value="test")
            assert result == "Override: test"

    def test_load_from_file_not_found(self):
        manager = PromptManager()

        with pytest.raises(FileNotFoundError):
            manager.load_from_file("test", "nonexistent.txt", ["var"])


class TestChatPrompts:
    def test_default_system_prompt(self):
        chat_prompts = ChatPrompts()
        prompt = chat_prompts.system_prompt

        assert "Obsidian-AI" in prompt
        assert "search(" in prompt
        assert "deep_research(" in prompt
        assert "wikilinks" in prompt

    def test_update_system_prompt(self):
        chat_prompts = ChatPrompts()
        original = chat_prompts.system_prompt

        new_prompt = "This is a custom system prompt."
        chat_prompts.update_system_prompt(new_prompt)

        assert chat_prompts.system_prompt == new_prompt
        assert chat_prompts.system_prompt != original

    def test_env_override_system_prompt(self):
        custom_prompt = "Custom prompt from environment"

        with patch.dict(os.environ, {"OBSIDIAN_AI_PROMPT_CHAT_SYSTEM": custom_prompt}):
            chat_prompts = ChatPrompts()
            assert chat_prompts.system_prompt == custom_prompt


class TestResearchPrompts:
    def test_research_reasoning_prompt(self):
        research_prompts = ResearchPrompts()

        prompt = research_prompts.get_research_reasoning_prompt(
            original_topic="Test Topic", current_focus="Focus Area", previous_context="Previous findings", discovered_context="Discovered entities"
        )

        assert "Test Topic" in prompt
        assert "Focus Area" in prompt
        assert "Previous findings" in prompt
        assert "Discovered entities" in prompt
        assert "REASONING:" in prompt
        assert "ACTION:" in prompt
        assert "QUERY:" in prompt

    def test_content_analysis_prompt(self):
        research_prompts = ResearchPrompts()

        prompt = research_prompts.get_content_analysis_prompt(topic="AI Research", file_path="/path/to/file.md", content="Sample content about AI")

        assert "AI Research" in prompt
        assert "/path/to/file.md" in prompt
        assert "Sample content about AI" in prompt

    def test_step_synthesis_prompt(self):
        research_prompts = ResearchPrompts()

        prompt = research_prompts.get_step_synthesis_prompt(
            topic="Research Topic",
            reasoning="Step reasoning",
            results_summary="Results found",
            wikilinks_summary="Links discovered",
            content_analysis="Analysis results",
            previous_context="Previous context",
        )

        assert "Research Topic" in prompt
        assert "Step reasoning" in prompt
        assert "Results found" in prompt
        assert "Links discovered" in prompt

    def test_final_report_prompt(self):
        research_prompts = ResearchPrompts()

        prompt = research_prompts.get_final_report_prompt(
            topic="Final Topic", all_syntheses="All findings", discovered_entities="Entity1, Entity2", unique_wikilinks="Link1, Link2"
        )

        assert "Final Topic" in prompt
        assert "All findings" in prompt
        assert "Entity1, Entity2" in prompt
        assert "Link1, Link2" in prompt
        assert "Executive Summary" in prompt
        assert "Key Findings" in prompt

    def test_env_override_research_prompts(self):
        custom_reasoning = "Custom reasoning prompt for {original_topic}"

        with patch.dict(os.environ, {"OBSIDIAN_AI_PROMPT_RESEARCH_REASONING": custom_reasoning}):
            research_prompts = ResearchPrompts()

            prompt = research_prompts.get_research_reasoning_prompt(
                original_topic="Test", current_focus="Focus", previous_context="", discovered_context=""
            )

            assert "Custom reasoning prompt for Test" in prompt
