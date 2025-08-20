from obsidian_ai.core.wikilink_parser import WikiLink, WikiLinkParser, extract_key_terms


class TestWikiLink:
    def test_simple_wikilink_str(self):
        link = WikiLink("Person")
        assert str(link) == "[[Person]]"

    def test_wikilink_with_display_str(self):
        link = WikiLink("Person", "John Doe")
        assert str(link) == "[[Person|John Doe]]"


class TestWikiLinkParser:
    def test_extract_simple_wikilinks(self):
        text = "I met [[Tara]] and [[Steve Baker]] yesterday."
        links = WikiLinkParser.extract_wikilinks(text)

        assert len(links) == 2
        assert links[0] == WikiLink("Tara")
        assert links[1] == WikiLink("Steve Baker")

    def test_extract_wikilinks_with_display_text(self):
        text = "See [[Person|John Doe]] and [[Project|AI Research]]."
        links = WikiLinkParser.extract_wikilinks(text)

        assert len(links) == 2
        assert links[0] == WikiLink("Person", "John Doe")
        assert links[1] == WikiLink("Project", "AI Research")

    def test_extract_mixed_wikilinks(self):
        text = "[[Simple Link]] and [[Complex|Display Text]] here."
        links = WikiLinkParser.extract_wikilinks(text)

        assert len(links) == 2
        assert links[0] == WikiLink("Simple Link")
        assert links[1] == WikiLink("Complex", "Display Text")

    def test_extract_link_targets(self):
        text = "[[Tara]] met [[Steve Baker|Steve]] about [[AI Research]]."
        targets = WikiLinkParser.extract_link_targets(text)

        assert targets == ["Tara", "Steve Baker", "AI Research"]

    def test_extract_unique_targets(self):
        text = "[[Tara]] and [[Tara]] met [[Steve]] and [[Steve|Steven]]."
        targets = WikiLinkParser.extract_unique_targets(text)

        assert targets == ["Tara", "Steve"]  # Should preserve order and remove duplicates

    def test_replace_wikilinks(self):
        text = "I met [[Tara]] and [[Steve|Steven]] yesterday."

        def replacement_func(wikilink, full_link):
            return f"@{wikilink.target}"

        result = WikiLinkParser.replace_wikilinks(text, replacement_func)
        assert result == "I met @Tara and @Steve yesterday."

    def test_validate_wikilink(self):
        assert WikiLinkParser.validate_wikilink("[[Valid Link]]")
        assert WikiLinkParser.validate_wikilink("Text with [[Link]] inside")
        assert not WikiLinkParser.validate_wikilink("No links here")
        assert not WikiLinkParser.validate_wikilink("[Single bracket]")

    def test_count_wikilinks(self):
        text = "[[First]] link and [[Second]] link and [[Third|Display]]."
        count = WikiLinkParser.count_wikilinks(text)
        assert count == 3

    def test_empty_text(self):
        links = WikiLinkParser.extract_wikilinks("")
        assert links == []

        targets = WikiLinkParser.extract_link_targets("")
        assert targets == []

        assert WikiLinkParser.count_wikilinks("") == 0
        assert not WikiLinkParser.validate_wikilink("")

    def test_malformed_links(self):
        # Should not extract malformed links
        text = "[[Incomplete and [single] bracket"
        links = WikiLinkParser.extract_wikilinks(text)
        assert links == []

    def test_nested_brackets(self):
        # Should handle nested brackets correctly
        text = "[[Link with [nested] brackets]]"
        links = WikiLinkParser.extract_wikilinks(text)
        assert len(links) == 1
        assert links[0].target == "Link with [nested] brackets"


class TestExtractKeyTerms:
    def test_extract_basic_terms(self):
        content = "I met Tara and Steve Baker yesterday at the conference."
        terms = extract_key_terms(content)

        assert "Tara" in terms
        assert "Steve" in terms or "Steve Baker" in terms
        assert "conference" in terms

        # Should not include common words
        assert "the" not in terms
        assert "and" not in terms

    def test_extract_from_wikilinks(self):
        content = "I met [[Tara]] and [[Steve Baker]] at [[AI Conference]]."
        terms = extract_key_terms(content)

        assert "Tara" in terms
        assert "Steve Baker" in terms
        assert "AI Conference" in terms

    def test_filter_common_words(self):
        content = "The quick brown fox jumps over the lazy dog."
        terms = extract_key_terms(content)

        # Should include meaningful words
        assert "quick" in terms
        assert "brown" in terms

        # Should exclude common words
        common_words = ["the", "over", "and", "for", "are"]
        for word in common_words:
            assert word not in terms

    def test_length_sorted_terms(self):
        content = "AI and Artificial Intelligence and Machine Learning"
        terms = extract_key_terms(content)

        # Longer terms should come first (they're more specific)
        longer_terms = [term for term in terms if len(term) > 10]
        shorter_terms = [term for term in terms if len(term) <= 10]

        if longer_terms and shorter_terms:
            # Check that longer terms appear before shorter ones
            first_long_index = terms.index(longer_terms[0])
            first_short_index = terms.index(shorter_terms[0])
            assert first_long_index < first_short_index

    def test_extract_capitalized_names(self):
        content = "John Doe and Jane Smith attended the meeting."
        terms = extract_key_terms(content)

        assert "John Doe" in terms or ("John" in terms and "Doe" in terms)
        assert "Jane Smith" in terms or ("Jane" in terms and "Smith" in terms)

    def test_remove_markdown_formatting(self):
        content = "# Heading\n**Bold** and *italic* and `code` and [[link]]"
        terms = extract_key_terms(content)

        # Should extract content words, not formatting
        assert "Heading" in terms
        assert "Bold" in terms
        assert "italic" in terms
        assert "code" in terms
        assert "link" in terms

        # Should not include markdown syntax
        for term in terms:
            assert "#" not in term
            assert "*" not in term
            assert "`" not in term

    def test_max_terms_limit(self):
        # Create content with many potential terms
        content = " ".join([f"Term{i}" for i in range(50)])
        terms = extract_key_terms(content)

        # Should limit to 20 terms
        assert len(terms) <= 20
