from __future__ import annotations

import re
from typing import NamedTuple
from collections.abc import Callable


class WikiLink(NamedTuple):
    """Represents a parsed wikilink."""

    target: str
    display_text: str | None = None

    def __str__(self) -> str:
        if self.display_text:
            return f"[[{self.target}|{self.display_text}]]"
        return f"[[{self.target}]]"


class WikiLinkParser:
    """Parser for extracting and processing wikilinks."""

    @staticmethod
    def extract_wikilinks(text: str) -> list[WikiLink]:
        """Extract all wikilinks from text."""
        # Pattern to match [[content]] - handles nested brackets
        pattern = r"\[\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]\]"
        matches = re.findall(pattern, text)

        wikilinks = []
        for match in matches:
            if "|" in match:
                target, display = match.split("|", 1)
                wikilinks.append(WikiLink(target.strip(), display.strip()))
            else:
                wikilinks.append(WikiLink(match.strip()))

        return wikilinks

    @staticmethod
    def extract_link_targets(text: str) -> list[str]:
        """Extract just the target names from wikilinks."""
        wikilinks = WikiLinkParser.extract_wikilinks(text)
        return [link.target for link in wikilinks]

    @staticmethod
    def extract_unique_targets(text: str) -> list[str]:
        """Extract unique target names from wikilinks."""
        targets = WikiLinkParser.extract_link_targets(text)
        return list(dict.fromkeys(targets))  # Preserve order while removing duplicates

    @staticmethod
    def replace_wikilinks(text: str, replacement_func: Callable[[WikiLink, str], str]) -> str:
        """Replace wikilinks in text using a replacement function."""

        def replace_match(match: re.Match[str]) -> str:
            full_link = match.group(0)
            link_content = match.group(1)

            if "|" in link_content:
                target, display = link_content.split("|", 1)
                wikilink = WikiLink(target.strip(), display.strip())
            else:
                wikilink = WikiLink(link_content.strip())

            return replacement_func(wikilink, full_link)

        pattern = r"\[\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]\]"
        return re.sub(pattern, replace_match, text)

    @staticmethod
    def validate_wikilink(text: str) -> bool:
        """Check if text contains valid wikilink syntax."""
        pattern = r"\[\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]\]"
        return bool(re.search(pattern, text))

    @staticmethod
    def count_wikilinks(text: str) -> int:
        """Count the number of wikilinks in text."""
        return len(WikiLinkParser.extract_wikilinks(text))


def extract_key_terms(content: str) -> list[str]:
    """Extract key terms from content for finding related notes."""
    # Extract wiki-style links first (before removing brackets)
    wiki_targets = WikiLinkParser.extract_unique_targets(content)

    # Remove markdown formatting
    content = re.sub(r"[#*`\[\]]+", "", content)

    # Extract potential names (capitalized words including multi-word phrases)
    names = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)

    # Extract important phrases (3+ character words)
    words = re.findall(r"\b[a-zA-Z]{3,}\b", content)

    # Combine and deduplicate
    key_terms = list(dict.fromkeys(wiki_targets + names + words))

    # Filter out common words
    common_words = {
        "the",
        "and",
        "for",
        "are",
        "but",
        "not",
        "you",
        "all",
        "can",
        "had",
        "her",
        "was",
        "one",
        "our",
        "out",
        "day",
        "get",
        "has",
        "him",
        "his",
        "how",
        "its",
        "new",
        "now",
        "old",
        "see",
        "two",
        "way",
        "who",
        "boy",
        "did",
        "may",
        "say",
        "she",
        "use",
        "your",
        "each",
        "make",
        "most",
        "over",
        "said",
        "some",
        "time",
        "very",
        "what",
        "with",
        "have",
        "from",
        "they",
        "know",
        "want",
        "been",
        "good",
        "much",
        "more",
        "will",
        "well",
        "where",
        "come",
        "could",
        "should",
        "would",
        "there",
        "their",
        "which",
        "about",
        "after",
        "first",
        "never",
        "these",
        "think",
        "other",
        "many",
        "than",
        "then",
        "them",
        "before",
        "here",
        "this",
    }

    filtered_terms = [term for term in key_terms if term.lower() not in common_words and len(term) > 2]

    # Sort by length (longer terms first, as they're likely more specific)
    filtered_terms.sort(key=len, reverse=True)

    return filtered_terms[:20]  # Return top 20 terms
