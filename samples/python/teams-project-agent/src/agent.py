# src/agent.py
import re
import logging
from typing import Optional, List, Dict

from microsoft_agents.hosting.aiohttp import CloudAdapter
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
    Authorization,
)
from microsoft_agents.authentication.msal import MsalConnectionManager
from microsoft_agents.activity import load_configuration_from_env
from os import environ

from src.config import Config
from src.project_analyzer import ProjectAnalyzer
from src.glm4_handler import GLM4Handler

logger = logging.getLogger(__name__)

# Load configuration
config = Config.from_env()

# Load SDK configuration from environment
agents_sdk_config = load_configuration_from_env(environ)

# Initialize SDK components
STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

# Initialize handlers
PROJECT_ANALYZER = ProjectAnalyzer(
    project_root=config.project_root_path,
    max_context_tokens=config.max_context_tokens
)
GLM_HANDLER = GLM4Handler(
    api_key=config.zhipuai_api_key,
    rate_limit_per_minute=config.rate_limit_per_minute,
    rate_limit_per_day=config.rate_limit_per_day,
)

# Create agent application
AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE,
    adapter=ADAPTER,
    authorization=AUTHORIZATION,
    **agents_sdk_config
)


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, state: TurnState) -> bool:
    """Send welcome message when user adds the bot."""
    welcome_message = """Welcome to the MS365 Agents Project Assistant!

I can help you understand this codebase. Try asking me:

- "What files are in this project?"
- "Explain the quickstart agent"
- "How does authentication work?"
- "What plugins are available?"

Just type your question and I'll analyze the project for you!"""

    await context.send_activity(welcome_message)
    return True


@AGENT_APP.message(re.compile(r".+"))
async def on_message(context: TurnContext, state: TurnState) -> bool:
    """Handle incoming messages."""
    try:
        user_message = context.activity.text
        logger.info(f"Received message: {user_message}")

        # Get project context
        project_context = PROJECT_ANALYZER.get_context_for_query(
            user_message, max_tokens=config.max_context_tokens
        )

        # Get conversation history from state
        history: List[Dict] = []
        if state and hasattr(state, "conversation_history"):
            history = state.conversation_history or []

        # Query GLM-4
        response = await GLM_HANDLER.query_async(
            user_question=user_message,
            project_context=project_context,
            conversation_history=history,
        )

        # Update history (keep last 20 messages)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": response})
        if state and hasattr(state, "conversation_history"):
            state.conversation_history = history[-20:]

        # Send response
        await context.send_activity(response)
        return True

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await context.send_activity(
            "Sorry, I encountered an error processing your request. Please try again."
        )
        return False


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    """Handle errors."""
    logger.error(f"Unhandled error: {error}", exc_info=True)
    await context.send_activity("The bot encountered an error. Please try again.")


# Export for use in app.py
AGENT_AUTH_CONFIGURATION = CONNECTION_MANAGER.get_default_connection_configuration()
