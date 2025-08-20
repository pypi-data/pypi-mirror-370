from obsidian_ai.core.wikilink_parser import WikiLinkParser, WikiLink, extract_key_terms


class TestWikilinkParser:
    def test_extract_wikilinks_simple(self):
        text = "This mentions [[John Smith]] and [[Machine Learning]]."

        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 2
        assert links[0].target == "John Smith"
        assert links[1].target == "Machine Learning"

    def test_extract_wikilinks_with_aliases(self):
        text = "See [[John Smith|John]] and [[Machine Learning|ML]] for details."

        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 2
        assert links[0].target == "John Smith"
        assert links[0].display_text == "John"
        assert links[1].target == "Machine Learning"
        assert links[1].display_text == "ML"

    def test_extract_wikilinks_none_found(self):
        text = "This is plain text with no links."

        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 0

    def test_extract_wikilinks_nested_brackets(self):
        text = "This has [[nested [brackets] inside]] a link."

        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 1
        assert links[0].target == "nested [brackets] inside"

    def test_extract_wikilinks_multiline(self):
        text = """
    First paragraph mentions [[Person A]].

    Second paragraph discusses [[Topic B]] and [[Topic C]].
    """

        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 3
        targets = [link.target for link in links]
        assert "Person A" in targets
        assert "Topic B" in targets
        assert "Topic C" in targets

    def test_extract_link_targets(self):
        text = "Links to [[A|Display A]] and [[B]] and [[C|Display C]]."

        targets = WikiLinkParser.extract_link_targets(text)
        assert len(targets) == 3
        assert targets == ["A", "B", "C"]

    def test_extract_unique_targets(self):
        text = "Links to [[A]], [[B]], [[A]], and [[C]]."

        targets = WikiLinkParser.extract_unique_targets(text)
        assert len(targets) == 3
        assert targets == ["A", "B", "C"]  # Order preserved, duplicates removed

    def test_replace_wikilinks(self):
        text = "See [[John Smith]] and [[Machine Learning|ML]]."

        def replacement(wikilink, full_link):
            return f"LINK({wikilink.target})"

        result = WikiLinkParser.replace_wikilinks(text, replacement)
        assert result == "See LINK(John Smith) and LINK(Machine Learning)."

    def test_validate_wikilink(self):
        assert WikiLinkParser.validate_wikilink("Text with [[link]]")
        assert WikiLinkParser.validate_wikilink("[[simple link]]")
        assert not WikiLinkParser.validate_wikilink("Text with no links")
        assert not WikiLinkParser.validate_wikilink("Broken [link]")

    def test_count_wikilinks(self):
        text = "[[A]] and [[B]] plus [[C|display]]"
        assert WikiLinkParser.count_wikilinks(text) == 3

        assert WikiLinkParser.count_wikilinks("No links") == 0


class TestWikiLink:
    def test_wikilink_without_display(self):
        link = WikiLink("Target Name")
        assert link.target == "Target Name"
        assert link.display_text is None
        assert str(link) == "[[Target Name]]"

    def test_wikilink_with_display(self):
        link = WikiLink("Target Name", "Display Text")
        assert link.target == "Target Name"
        assert link.display_text == "Display Text"
        assert str(link) == "[[Target Name|Display Text]]"


class TestExtractKeyTerms:
    def test_extract_key_terms_basic(self):
        content = "This is about Machine Learning and Deep Learning algorithms."

        terms = extract_key_terms(content)
        assert "Machine Learning" in terms
        assert "Deep Learning" in terms
        assert "algorithms" in terms

        # Should not include common words
        assert "This" not in terms
        assert "about" not in terms

    def test_extract_key_terms_with_wikilinks(self):
        content = "Study [[Machine Learning]] and [[Neural Networks]] concepts."

        terms = extract_key_terms(content)
        assert "Machine Learning" in terms
        assert "Neural Networks" in terms

    def test_extract_key_terms_filters_short_words(self):
        content = "AI is a big field with ML and NLP."

        terms = extract_key_terms(content)
        assert "field" in terms
        # Short words should be filtered
        assert "AI" not in terms
        assert "ML" not in terms
        assert "is" not in terms

    def test_extract_key_terms_capitalized_names(self):
        content = "John Smith works with Sarah Wilson on Project Alpha."

        terms = extract_key_terms(content)
        assert "John Smith" in terms
        assert "Sarah Wilson" in terms
        assert "Project Alpha" in terms

    def test_extract_key_terms_removes_markdown(self):
        content = "# Title\n\n**Bold** and *italic* and `code`."

        terms = extract_key_terms(content)
        assert "Title" in terms
        assert "Bold" in terms
        assert "italic" in terms
        assert "code" in terms
        # Markdown symbols should be removed
        assert "#" not in " ".join(terms)
        assert "**" not in " ".join(terms)

    def test_extract_key_terms_length_sorting(self):
        content = "AI Machine Learning Deep Learning Networks Neural Networks"

        terms = extract_key_terms(content)
        # Longer terms should come first
        longer_terms = [term for term in terms if len(term) > 10]
        shorter_terms = [term for term in terms if len(term) <= 10]

        if longer_terms and shorter_terms:
            first_long = terms.index(longer_terms[0])
            first_short = terms.index(shorter_terms[0]) if shorter_terms[0] in terms else len(terms)
            assert first_long < first_short

    def test_extract_key_terms_max_count(self):
        # Create content with many terms
        content = " ".join([f"Term{i} Concept{i} Idea{i}" for i in range(50)])

        terms = extract_key_terms(content)
        assert len(terms) <= 20  # Should limit to 20 terms
