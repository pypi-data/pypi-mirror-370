import pytest
import os
from unittest.mock import Mock, patch

# Prevent OpenAI client initialization during import
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
    from obsidian_ai.services.openai_client import OpenAIClient, OpenAIError
    from obsidian_ai.services.embedding_service import EmbeddingService


class TestOpenAIClient:
    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_init_with_api_key(self, mock_openai):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            mock_openai.assert_called_once()

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_chat_completion_success(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock successful response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client_instance.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            result = client.chat_completion([{"role": "user", "content": "test"}])

        assert result == mock_response
        mock_client_instance.chat.completions.create.assert_called_once()

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_chat_completion_error(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()

            with pytest.raises(OpenAIError, match="Failed to get OpenAI response"):
                client.chat_completion([{"role": "user", "content": "test"}])

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_simple_completion(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Simple response"
        mock_client_instance.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            result = client.simple_completion("test prompt")

        assert result == "Simple response"

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_simple_completion_error_handling(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            result = client.simple_completion("test prompt")

        assert "Error:" in result
        assert "Failed to get OpenAI response" in result

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_structured_completion(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock tool calls
        mock_tool_call = Mock()
        mock_tool_call.model_dump.return_value = {"id": "call_123", "function": {"name": "test"}}

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Structured response"
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_client_instance.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            content, tool_calls = client.structured_completion("system", "user", [])

        assert content == "Structured response"
        assert tool_calls is not None
        assert len(tool_calls) == 1

    @patch("obsidian_ai.services.openai_client.OpenAI")
    def test_continue_conversation(self, mock_openai):
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Continued response"
        mock_client_instance.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            client = OpenAIClient()
            result = client.continue_conversation([{"role": "user", "content": "continue"}])

        assert result == "Continued response"


class TestEmbeddingService:
    def test_semantic_search_basic(self, temp_brain):
        service = EmbeddingService()
        result = service.semantic_search("test query", k=5)

        assert "query" in result
        assert "results" in result
        assert result["query"] == "test query"

    def test_semantic_search_json(self, temp_brain):
        service = EmbeddingService()
        result_json = service.semantic_search_json("machine learning", k=3)

        import json

        result = json.loads(result_json)

        assert "query" in result
        assert "results" in result
        assert result["query"] == "machine learning"

    def test_semantic_search_error_handling(self, temp_brain):
        service = EmbeddingService()

        # Test with potentially problematic query
        result = service.semantic_search("", k=5)

        # Should handle gracefully
        assert "query" in result
        assert "results" in result

    def test_semantic_search_with_k_param(self, temp_brain):
        service = EmbeddingService()

        # Test with different k values
        result1 = service.semantic_search("test", k=1)
        result2 = service.semantic_search("test", k=10)

        assert result1["query"] == "test"
        assert result2["query"] == "test"

    def test_global_service_instance(self, temp_brain):
        from obsidian_ai.services.embedding_service import embedding_service

        # Should be able to use global instance
        result = embedding_service.semantic_search("global test")
        assert "query" in result
        assert result["query"] == "global test"

    def test_service_initialization(self, temp_brain):
        service = EmbeddingService()

        # Should initialize without parameters
        assert service is not None

    def test_multiple_service_instances(self, temp_brain):
        service1 = EmbeddingService()
        service2 = EmbeddingService()

        # Both should work independently
        result1 = service1.semantic_search("test1")
        result2 = service2.semantic_search("test2")

        assert result1["query"] == "test1"
        assert result2["query"] == "test2"

    def test_semantic_search_complex_query(self, temp_brain):
        service = EmbeddingService()

        # Test with complex query
        complex_query = "machine learning algorithms for natural language processing"
        result = service.semantic_search(complex_query, k=8)

        assert result["query"] == complex_query
        assert "results" in result

    def test_semantic_search_unicode_query(self, temp_brain):
        service = EmbeddingService()

        # Test with unicode characters
        unicode_query = "café résumé naïve"
        result = service.semantic_search(unicode_query, k=3)

        assert result["query"] == unicode_query
        assert "results" in result

    def test_semantic_search_special_chars(self, temp_brain):
        service = EmbeddingService()

        # Test with special characters
        special_query = "AI/ML & NLP research @#$%"
        result = service.semantic_search(special_query, k=2)

        assert result["query"] == special_query
        assert "results" in result
