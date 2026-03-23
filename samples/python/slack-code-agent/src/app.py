# src/app.py
import os
import logging
from typing import Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .config import Config
from .agent import CodeAgent, AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config: Optional[Config] = None) -> tuple[App, SocketModeHandler]:
    """Create and configure the Slack Bolt app.

    Signature verification is handled automatically by Bolt framework
    when signing_secret is provided to App constructor.
    """
    config = config or Config()

    # Initialize Bolt app (signing_secret enables request signature verification)
    app = App(
        token=config.slack_bot_token,
        signing_secret=config.slack_signing_secret,
    )

    # Initialize agent
    agent = CodeAgent(config)

    # Message handler for DMs and mentions
    @app.message()
    def handle_message(message, say, logger):
        """Handle incoming messages."""
        logger.info(f"Received message: {message}")

        try:
            response = agent.process_message(message)

            if response.success:
                say(text=response.text)
            else:
                say(text=f"I couldn't process that: {response.text}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            say(text="Sorry, I encountered an error processing your message.")

    # App mention handler
    @app.event("app_mention")
    def handle_app_mention(event, say, logger):
        """Handle @mention events."""
        logger.info(f"Received app mention: {event}")

        try:
            text = event.get("text", "")
            message = text.replace("<@BOT_USER_ID>", "").strip()

            response = agent.process_message(message)

            if response.success:
                say(text=response.text)
            else:
                say(text=f"I couldn't process that: {response.text}")

        except Exception as e:
            logger.error(f"Error handling app mention: {e}")
            say(text="Sorry, I encountered an error processing your message.")

    # Slash command handler
    @app.command("/claude-agent")
    def handle_slash_command(ack, respond, command, logger):
        """Handle /claude-agent slash command."""
        logger.info(f"Received slash command: {command}")

        ack()  # Acknowledge immediately

        try:
            message = command["text"]
            response = agent.process_message(message)

            if response.success:
                respond(text=response.text)
            else:
                respond(text=f"I couldn't process that: {response.text}")

        except Exception as e:
            logger.error(f"Error handling slash command: {e}")
            respond(text="Sorry, I encountered an error processing your command.")

    # Help command
    @app.command("/claude-agent-help")
    def handle_help_command(ack, respond, logger):
        """Handle /claude-agent-help command."""
        ack()

        help_text = """*Claude Code Agent*

Ask me questions about your code projects and documents!

*Commands:*
• `/claude-agent <question>` - Ask anything
• DM me directly - Same as using /claude-agent
• @mention me in a channel - I'll respond in that channel

*Example questions:*
• "What files are in the project?"
• "Explain the main.py file"
• "Find functions related to authentication"
• "What does the Q3 report say about revenue?"

*Note:* Works best with single, specific questions."""

        respond(text=help_text)

    # Create Socket Mode handler
    handler = SocketModeHandler(app)

    return app, handler

def run_app():
    """Run the app with ngrok tunnel."""
    config = Config()

    # Check required env vars
    if not config.slack_bot_token:
        raise ValueError("SLACK_BOT_TOKEN is required")
    if not config.slack_signing_secret:
        raise ValueError("SLACK_SIGNING_SECRET is required")

    app, handler = create_app(config)

    # Run with Socket Mode
    handler.start()

if __name__ == "__main__":
    run_app()
