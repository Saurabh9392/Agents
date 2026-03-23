import os
import requests
from unittest.mock import patch, MagicMock

def test_llm_handler_initializes():
    """Test LLM handler initializes with config."""
    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        from src.llm_handler import LLMHandler
        handler = LLMHandler()
        assert handler.api_key == "test-key"

def test_llm_handler_builds_messages():
    """Test message building with system prompt."""
    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        from src.llm_handler import LLMHandler
        handler = LLMHandler()
        messages = handler.build_messages(
            user_query="What does main.py do?",
            context="def main(): print('hello')"
        )
        assert len(messages) == 2  # system + user
        assert "main.py" in messages[1]["content"]

def test_llm_handler_returns_text_on_success():
    """Test successful API call returns text."""
    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        with patch("src.llm_handler.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"messages": [{"role": "assistant", "content": "Hello!"}]}]
            }
            mock_post.return_value = mock_response

            from src.llm_handler import LLMHandler
            handler = LLMHandler()
            result = handler.generate("Hello?")

            assert result.text == "Hello!"
            assert result.success == True

def test_llm_handler_missing_api_key():
    """Test generate returns error when API key is missing."""
    from src.llm_handler import LLMHandler
    handler = LLMHandler(api_key="")
    result = handler.generate("Hello?")

    assert result.success is False
    assert result.error == "Missing API key"
    assert "MINIMAX_API_KEY" in result.text

def test_llm_handler_timeout_handling():
    """Test generate handles timeout errors."""
    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        with patch("src.llm_handler.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

            from src.llm_handler import LLMHandler
            handler = LLMHandler()
            result = handler.generate("Hello?")

            assert result.success is False
            assert result.error == "Timeout"
            assert "timed out" in result.text.lower()

def test_llm_handler_rate_limit_handling():
    """Test generate handles 429 rate limit errors."""
    with patch.dict(os.environ, {"MINIMAX_API_KEY": "test-key"}):
        with patch("src.llm_handler.requests.post") as mock_post:
            with patch("src.llm_handler.time.sleep"):
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_post.return_value = mock_response

                from src.llm_handler import LLMHandler
                handler = LLMHandler()
                result = handler.generate("Hello?")

                assert result.success is False
                assert result.error == "Max retries"