# src/app.py
import logging
from aiohttp import web
from microsoft_agents.hosting.aiohttp import start_agent_process

from src.agent import AGENT_APP, ADAPTER, AGENT_AUTH_CONFIGURATION

logger = logging.getLogger(__name__)


class MessagesEndpoint(web.View):
    async def post(self) -> web.Response:
        return await start_agent_process(
            self.request, AGENT_APP, ADAPTER, AGENT_AUTH_CONFIGURATION
        )


class HealthEndpoint(web.View):
    async def get(self) -> web.Response:
        return web.Response(text="OK", status=200)


def create_app() -> web.Application:
    """Create the aiohttp application."""
    app = web.Application()

    # Add routes
    app.router.add_post("/api/messages", MessagesEndpoint)
    app.router.add_get("/health", HealthEndpoint)

    # Store agent references
    app["agent_app"] = AGENT_APP
    app["adapter"] = ADAPTER

    return app
