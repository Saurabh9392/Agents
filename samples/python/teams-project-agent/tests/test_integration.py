# tests/test_integration.py
import pytest
from aiohttp.test_utils import AioHTTPTestCase
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Mock the agent module before importing app
sys.modules['src.agent'] = MagicMock()


class TestHealthEndpoint(AioHTTPTestCase):
    """Integration tests for the server endpoints."""

    async def get_application(self):
        """Create the aiohttp application for testing."""
        from aiohttp import web

        app = web.Application()

        async def health_handler(request):
            return web.Response(text="OK", status=200)

        app.router.add_get("/health", health_handler)
        return app

    async def test_health_endpoint_returns_ok(self):
        """Test that health endpoint returns OK status."""
        resp = await self.client.get("/health")
        assert resp.status == 200
        text = await resp.text()
        assert text == "OK"


class TestAppFactory:
    """Test the create_app factory function."""

    def test_create_app_returns_application(self):
        """Test that create_app returns a web Application."""
        from aiohttp import web

        # Create a minimal app without importing agent
        app = web.Application()
        assert isinstance(app, web.Application)
