from .base import prompt_manager

# Research reasoning prompt
DEFAULT_RESEARCH_REASONING_PROMPT = """
You are an expert research agent conducting deep investigation into: "{original_topic}"

**Current Research Focus:** {current_focus}

{previous_context}{discovered_context}

**Your Task:** Plan the next research step with clear reasoning.

**Available Actions:**
1. search(query) - Multi-strategy keyword search
2. semantic_search(query) - Conceptual similarity search

**Research Strategy Guidelines:**
- Look for specific people, places, events mentioned in the topic
- Follow wikilinks [[like this]] to discover connected information
- Build understanding progressively from basic facts to deeper connections
- Use different search strategies to cover all angles
- When you find relevant files, the system will analyze their full content

**Response Format:**
REASONING: [Your step-by-step thinking about what to search for and why]
ACTION: [search or semantic_search]
QUERY: [The specific search query to use]

Think carefully about what information gaps exist and how to fill them systematically.
"""

# Content analysis prompt
DEFAULT_CONTENT_ANALYSIS_PROMPT = """
Analyze this file's relevance to the research topic: "{topic}"

**File:** {file_path}
**Content Preview:**
{content}

Provide a 2-3 sentence analysis of:
1. What key information this file contains about the topic
2. What new entities or connections it reveals
3. How it advances our understanding

Be specific and cite details from the content.
"""

# Step synthesis prompt
DEFAULT_STEP_SYNTHESIS_PROMPT = """
Research Topic: "{topic}"
Current Step Reasoning: {reasoning}

**Search Results:**
{results_summary}

**Wikilinks Discovered:**
{wikilinks_summary}

**Content Analysis:**
{content_analysis}
{previous_context}

**Synthesize this step's key findings:**
1. What new information was discovered about the topic?
2. Which wikilinks/entities are most important to explore next?
3. How does this connect to or build upon previous findings?
4. What gaps in knowledge remain?

Provide a clear, concise synthesis that advances our understanding of the topic.
"""

# Final report prompt
DEFAULT_FINAL_REPORT_PROMPT = """
Research Topic: "{topic}"

**Complete Research Journey:**
{all_syntheses}

**Network of Discovered Entities:** {discovered_entities}
**Key Wikilinks Found:** {unique_wikilinks}

**Generate a comprehensive final report that:**

1. **Executive Summary:** Direct answer to the original research question
2. **Key Findings:** Most important discoveries from all research steps
3. **Entity Network:** How the discovered people/concepts connect to each other and the topic
4. **Detailed Analysis:** Deeper insights that emerged from following wikilinks and connections
5. **Knowledge Gaps:** What information is still missing or unclear
6. **Source Files:** Key files that contained the most valuable information

Structure this as a professional research report with clear sections and specific citations.
"""


class ResearchPrompts:
    """Research-related prompt templates."""

    def __init__(self) -> None:
        # Load all research prompts
        prompt_manager.load_from_env(
            "research_reasoning", DEFAULT_RESEARCH_REASONING_PROMPT, ["original_topic", "current_focus", "previous_context", "discovered_context"]
        )

        prompt_manager.load_from_env("content_analysis", DEFAULT_CONTENT_ANALYSIS_PROMPT, ["topic", "file_path", "content"])

        prompt_manager.load_from_env(
            "step_synthesis",
            DEFAULT_STEP_SYNTHESIS_PROMPT,
            ["topic", "reasoning", "results_summary", "wikilinks_summary", "content_analysis", "previous_context"],
        )

        prompt_manager.load_from_env(
            "final_report", DEFAULT_FINAL_REPORT_PROMPT, ["topic", "all_syntheses", "discovered_entities", "unique_wikilinks"]
        )

    def get_research_reasoning_prompt(self, **kwargs: str) -> str:
        return prompt_manager.render("research_reasoning", **kwargs)

    def get_content_analysis_prompt(self, **kwargs: str) -> str:
        return prompt_manager.render("content_analysis", **kwargs)

    def get_step_synthesis_prompt(self, **kwargs: str) -> str:
        return prompt_manager.render("step_synthesis", **kwargs)

    def get_final_report_prompt(self, **kwargs: str) -> str:
        return prompt_manager.render("final_report", **kwargs)
