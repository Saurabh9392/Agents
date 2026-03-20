# tests/test_glm4_handler.py
import pytest
import time
from unittest.mock import patch, MagicMock
from src.glm4_handler import GLM4Handler, RateLimiter

class TestGLM4HandlerInit:
    def test_init_with_api_key(self):
        handler = GLM4Handler(api_key="test-key")
        assert handler.api_key == "test-key"

    def test_init_without_api_key_raises(self):
        with pytest.raises(ValueError):
            GLM4Handler(api_key="")


class TestRateLimiter:
    def test_can_make_request_within_limits(self):
        limiter = RateLimiter(max_per_minute=10, max_per_day=100)
        assert limiter.can_make_request() is True

    def test_can_make_request_exceeds_minute_limit(self):
        limiter = RateLimiter(max_per_minute=2, max_per_day=100)
        limiter.record_request()
        limiter.record_request()
        assert limiter.can_make_request() is False

    def test_can_make_request_exceeds_day_limit(self):
        limiter = RateLimiter(max_per_minute=10, max_per_day=2)
        limiter.record_request()
        limiter.record_request()
        assert limiter.can_make_request() is False


class TestGLM4HandlerQuery:
    def test_query_returns_response(self):
        handler = GLM4Handler(api_key="test-key")

        # Mock the client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        handler.client.chat.completions.create = MagicMock(return_value=mock_response)

        response = handler.query(
            user_question="What is this project?",
            project_context="Some context"
        )
        assert "Test response" in response

    def test_query_rate_limited_raises(self):
        handler = GLM4Handler(api_key="test-key", rate_limit_per_minute=1)
        handler.rate_limiter.record_request()  # Use up the limit

        with pytest.raises(Exception, match="Rate limit"):
            handler.query("test", "context")

    def test_query_async_returns_response(self):
        import asyncio
        handler = GLM4Handler(api_key="test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Async response"))]
        handler.client.chat.completions.create = MagicMock(return_value=mock_response)

        async def run_test():
            response = await handler.query_async(
                user_question="Test question",
                project_context="Test context"
            )
            assert "Async response" in response

        asyncio.run(run_test())
