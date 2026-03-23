import os
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