import os
from unittest.mock import patch

from src.config import Config


def test_config_loads_environment_variables():
    """Test that config reads from environment variables."""
    with patch.dict(os.environ, {
        "SLACK_BOT_TOKEN": "xoxb-test-token",
        "SLACK_SIGNING_SECRET": "test-secret",
        "MINIMAX_API_KEY": "test-minimax-key",
        "PROJECT_ROOT_PATH": "/test/path",
        "KUZU_DB_PATH": "/test/db",
        "MINIMAX_BASE_URL": "https://custom.api.example.com",
    }):
        config = Config()
        assert config.slack_bot_token == "xoxb-test-token"
        assert config.slack_signing_secret == "test-secret"
        assert config.minimax_api_key == "test-minimax-key"
        assert config.project_root_path == "/test/path"
        assert config.kuzu_db_path == "/test/db"
        assert config.minimax_base_url == "https://custom.api.example.com"


def test_config_defaults():
    """Test default values when env vars not set."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.ngrok_port == 3000
        assert config.max_context_tokens == 10000
        assert config.kuzu_db_path is None  # Optional
        assert config.minimax_base_url == "https://api.minimax.chat"
        assert config.rate_limit_per_minute == 20
