# src/start_server.py
import os
import logging
from aiohttp import web

from src.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Start the server."""
    app = create_app()
    port = int(os.getenv("PORT", "3978"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
