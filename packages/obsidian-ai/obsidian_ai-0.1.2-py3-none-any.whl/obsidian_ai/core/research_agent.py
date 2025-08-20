from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger

from ..core.search_engine import search_engine
from ..core.wikilink_parser import WikiLinkParser
from ..infrastructure.file_system import read_file_safe
from ..services.openai_client import get_openai_client, OpenAIError
from ..services.embedding_service import embedding_service
from ..prompts.research import ResearchPrompts


@dataclass
class ResearchStep:
    """Represents a single step in the research process."""

    step_number: int
    reasoning: str
    action: str
    query: str
    results: list[dict[str, Any]]
    wikilinks_found: list[str]
    synthesis: str
    next_actions: list[str]


class ResearchAgent:
    """Autonomous research agent that follows wikilinks and builds understanding iteratively."""

    def __init__(self) -> None:
        self.prompts = ResearchPrompts()

    def conduct_research(self, topic: str, max_iterations: int = 4) -> dict[str, Any]:
        """
        Conduct comprehensive research on a topic.

        Returns:
            Structured research results with steps, findings, and final report.
        """
        try:
            return self._execute_research(topic, max_iterations)
        except Exception as e:
            logger.error(f"Research failed for topic '{topic}': {e}")
            return self._create_error_response(topic, str(e))

    def _execute_research(self, topic: str, max_iterations: int) -> dict[str, Any]:
        """Execute the research process."""
        research_steps: list[ResearchStep] = []
        discovered_entities: set[str] = set()
        explored_queries: set[str] = set()

        current_focus = topic

        for iteration in range(max_iterations):
            logger.info(f"Research iteration {iteration + 1} for topic: {topic}")

            try:
                # Plan the next step
                action_plan = self._plan_research_step(topic, current_focus, research_steps, discovered_entities)

                # Avoid repeating queries
                if action_plan["query"] in explored_queries:
                    action_plan["query"] = self._generate_alternative_query(topic, explored_queries, research_steps)

                explored_queries.add(action_plan["query"])

                # Execute the search
                search_results, wikilinks_found = self._execute_search(action_plan)

                # Update discovered entities
                discovered_entities.update(wikilinks_found)

                # Analyze relevant files
                content_analysis = self._analyze_relevant_files(topic, search_results)

                # Synthesize findings
                synthesis = self._synthesize_findings(topic, action_plan, search_results, wikilinks_found, content_analysis, research_steps)

                # Determine next actions
                next_actions = self._determine_next_actions(topic, synthesis, discovered_entities, explored_queries)

                # Create research step
                step = ResearchStep(
                    step_number=iteration + 1,
                    reasoning=action_plan["reasoning"],
                    action=action_plan["action"],
                    query=action_plan["query"],
                    results=search_results,
                    wikilinks_found=list(set(wikilinks_found)),
                    synthesis=synthesis,
                    next_actions=next_actions,
                )

                research_steps.append(step)

                # Update focus for next iteration
                if next_actions and iteration < max_iterations - 1:
                    current_focus = next_actions[0]

                # Check if research is complete
                if self._is_research_complete(synthesis, next_actions):
                    logger.info(f"Research completed early at iteration {iteration + 1}")
                    break

            except Exception as e:
                logger.error(f"Error in research iteration {iteration + 1}: {e}")
                # Continue with next iteration rather than failing completely
                continue

        # Generate final report
        final_report = self._generate_final_report(topic, research_steps, discovered_entities)

        return {
            "topic": topic,
            "total_iterations": len(research_steps),
            "discovered_entities": sorted(discovered_entities),
            "research_steps": [
                {
                    "step": step.step_number,
                    "reasoning": step.reasoning,
                    "action": f"{step.action}({step.query})",
                    "results_found": len(step.results),
                    "wikilinks_discovered": step.wikilinks_found,
                    "synthesis": step.synthesis,
                    "next_planned_actions": step.next_actions,
                }
                for step in research_steps
            ],
            "final_comprehensive_report": final_report,
            "research_quality_metrics": {
                "total_sources_examined": sum(len(step.results) for step in research_steps),
                "unique_wikilinks_discovered": len(discovered_entities),
                "research_depth_score": len(research_steps) * len(discovered_entities),
            },
        }

    def _plan_research_step(
        self, topic: str, current_focus: str, previous_steps: list[ResearchStep], discovered_entities: set[str]
    ) -> dict[str, str]:
        """Plan the next research step using AI reasoning."""
        previous_context = ""
        if previous_steps:
            previous_context = "\n\n**Previous Research Steps:**\n"
            for step in previous_steps[-2:]:  # Last 2 steps for context
                previous_context += f"Step {step.step_number}: {step.action}('{step.query}') → {step.synthesis[:200]}...\n"

        discovered_context = ""
        if discovered_entities:
            discovered_context = f"\n\n**Entities Discovered So Far:** {', '.join(sorted(discovered_entities)[:10])}"

        try:
            prompt = self.prompts.get_research_reasoning_prompt(
                original_topic=topic, current_focus=current_focus, previous_context=previous_context, discovered_context=discovered_context
            )

            response = get_openai_client().simple_completion(prompt, max_tokens=400)
            return self._parse_reasoning_response(response)

        except OpenAIError as e:
            logger.error(f"Failed to plan research step: {e}")
            return {"reasoning": f"Continue investigating {current_focus} to gather more information.", "action": "search", "query": current_focus}

    def _parse_reasoning_response(self, response: str) -> dict[str, str]:
        """Parse the AI's reasoning response."""
        lines = response.split("\n")
        result = {"reasoning": "", "action": "search", "query": ""}

        for line in lines:
            if line.startswith("REASONING:"):
                result["reasoning"] = line.replace("REASONING:", "").strip()
            elif line.startswith("ACTION:"):
                result["action"] = line.replace("ACTION:", "").strip()
            elif line.startswith("QUERY:"):
                result["query"] = line.replace("QUERY:", "").strip()

        return result

    def _execute_search(self, action_plan: dict[str, str]) -> tuple[list[dict], list[str]]:
        """Execute the planned search and extract wikilinks."""
        search_results = []
        wikilinks_found = []

        try:
            if action_plan["action"] == "search":
                results = search_engine.search(action_plan["query"], max_results=12)
                search_results = [
                    {"path": result.relative_path, "line": result.line, "text": result.text, "score": result.score} for result in results
                ]

            elif action_plan["action"] == "semantic_search":
                semantic_data = embedding_service.semantic_search(action_plan["query"], k=8)
                search_results = semantic_data.get("results", [])

            # Extract wikilinks from all found content
            for result in search_results:
                content = result.get("text", result.get("preview", ""))
                links = WikiLinkParser.extract_unique_targets(str(content))
                wikilinks_found.extend(links)

        except Exception as e:
            logger.error(f"Search execution failed: {e}")

        return search_results, wikilinks_found

    def _analyze_relevant_files(self, topic: str, search_results: list[dict]) -> str:
        """Analyze the most relevant files for deeper insights."""
        relevant_files = self._identify_relevant_files(search_results)
        analysis_parts = []

        for file_path in relevant_files[:3]:  # Limit to top 3 files
            try:
                content = read_file_safe(file_path, max_bytes=16384)
                analysis = self._analyze_file_content(topic, file_path, content[:2000])
                analysis_parts.append(f"**Analysis of {file_path}:**\n{analysis}")

            except Exception as e:
                logger.warning(f"Could not analyze file {file_path}: {e}")
                continue

        return "\n\n".join(analysis_parts)

    def _identify_relevant_files(self, search_results: list[dict]) -> list[str]:
        """Identify files most relevant for deeper analysis."""
        file_scores = {}

        for result in search_results:
            path = result.get("path", "")
            if path:
                text = result.get("text", result.get("preview", ""))
                # Score based on content length and wikilink density
                score = len(text) + text.lower().count("[[") * 10
                score += result.get("score", 1.0) * 5  # Boost by search relevance

                if path not in file_scores:
                    file_scores[path] = 0
                file_scores[path] += score

        # Return files sorted by relevance score
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        return [path for path, _ in sorted_files]

    def _analyze_file_content(self, topic: str, file_path: str, content: str) -> str:
        """Analyze how relevant a file's content is to the research topic."""
        try:
            prompt = self.prompts.get_content_analysis_prompt(topic=topic, file_path=file_path, content=content)

            return get_openai_client().simple_completion(prompt, max_tokens=200)

        except OpenAIError as e:
            logger.error(f"Content analysis failed for {file_path}: {e}")
            return f"File {file_path} contains content related to {topic}."

    def _synthesize_findings(
        self, topic: str, action_plan: dict, search_results: list, wikilinks: list, content_analysis: str, previous_steps: list[ResearchStep]
    ) -> str:
        """Synthesize findings from this research step."""
        results_summary = f"Found {len(search_results)} results from {action_plan['action']}('{action_plan['query']}')"
        if search_results:
            results_summary += ":\n" + "\n".join(
                [f"- {result.get('path', 'Unknown')}: {result.get('text', result.get('preview', ''))[:100]}..." for result in search_results[:5]]
            )

        wikilinks_summary = f"Discovered wikilinks: {', '.join(wikilinks[:10])}" if wikilinks else "No new wikilinks found."

        previous_context = ""
        if previous_steps:
            previous_context = f"\n\nBuilding on previous findings:\n{previous_steps[-1].synthesis}"

        try:
            prompt = self.prompts.get_step_synthesis_prompt(
                topic=topic,
                reasoning=action_plan["reasoning"],
                results_summary=results_summary,
                wikilinks_summary=wikilinks_summary,
                content_analysis=content_analysis,
                previous_context=previous_context,
            )

            return get_openai_client().simple_completion(prompt, max_tokens=400)

        except OpenAIError as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Step completed: {action_plan['action']} for '{action_plan['query']}' found {len(search_results)} results."

    def _determine_next_actions(self, topic: str, synthesis: str, discovered_entities: set[str], explored_queries: set[str]) -> list[str]:
        """Determine next research actions based on findings."""
        unexplored_entities = [entity for entity in discovered_entities if entity.lower() not in explored_queries and len(entity) > 2]

        try:
            prompt = f"""Research Topic: "{topic}"

**Current Synthesis:**
{synthesis}

**Unexplored Entities:** {", ".join(unexplored_entities[:15])}
**Already Explored:** {", ".join(list(explored_queries)[-5:])}

Based on the current synthesis, what are the 2-3 most important next research directions?

Consider:
- Which unexplored entities are most relevant to the topic?
- What information gaps need to be filled?
- Which connections should be explored deeper?

Return 2-3 specific research directions, each as a short phrase or entity name."""

            response = get_openai_client().simple_completion(prompt, max_tokens=200)
            next_actions = [action.strip("- ").strip() for action in response.strip().split("\n") if action.strip()]
            return next_actions[:3]

        except OpenAIError:
            return unexplored_entities[:2] if unexplored_entities else []

    def _generate_alternative_query(self, topic: str, explored_queries: set[str], previous_steps: list[ResearchStep]) -> str:
        """Generate alternative query when the planned one was already explored."""
        recent_findings = ""
        if previous_steps:
            recent_findings = previous_steps[-1].synthesis

        try:
            prompt = f"""Research Topic: "{topic}"

**Already Explored:** {", ".join(list(explored_queries))}
**Recent Findings:** {recent_findings}

Generate a new, unexplored search query that would advance our understanding of this topic.
Focus on a different angle or aspect that hasn't been covered yet.

Return only the search query:"""

            return get_openai_client().simple_completion(prompt, max_tokens=50).strip()

        except OpenAIError:
            return f"information about {topic}"

    def _is_research_complete(self, synthesis: str, next_actions: list[str]) -> bool:
        """Determine if research has sufficient depth to conclude."""
        if len(synthesis) < 100:
            return False

        if not next_actions:
            return True

        completion_indicators = ["comprehensive understanding", "thorough investigation", "all major aspects covered", "no significant gaps"]

        return any(indicator in synthesis.lower() for indicator in completion_indicators)

    def _generate_final_report(self, topic: str, research_steps: list[ResearchStep], discovered_entities: set[str]) -> str:
        """Generate comprehensive final research report."""
        all_syntheses = "\n\n".join([f"**Step {step.step_number}:** {step.synthesis}" for step in research_steps])

        all_wikilinks = []
        for step in research_steps:
            all_wikilinks.extend(step.wikilinks_found)
        unique_wikilinks = list(set(all_wikilinks))

        try:
            prompt = self.prompts.get_final_report_prompt(
                topic=topic,
                all_syntheses=all_syntheses,
                discovered_entities=", ".join(sorted(discovered_entities)),
                unique_wikilinks=", ".join(unique_wikilinks[:20]),
            )

            return get_openai_client().simple_completion(prompt, max_tokens=1000)

        except OpenAIError as e:
            logger.error(f"Final report generation failed: {e}")
            return f"Research completed on '{topic}' with {len(research_steps)} iterations, discovering {len(discovered_entities)} related entities."

    def _create_error_response(self, topic: str, error_msg: str) -> dict[str, Any]:
        """Create an error response when research fails."""
        return {
            "topic": topic,
            "total_iterations": 0,
            "discovered_entities": [],
            "research_steps": [],
            "final_comprehensive_report": f"Research failed: {error_msg}",
            "research_quality_metrics": {"total_sources_examined": 0, "unique_wikilinks_discovered": 0, "research_depth_score": 0},
            "error": error_msg,
        }


# Global research agent instance
research_agent = ResearchAgent()
