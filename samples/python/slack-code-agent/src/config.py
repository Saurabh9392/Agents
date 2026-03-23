# src/config.py
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimax.chat"
    project_root_path: str = ""
    kuzu_db_path: Optional[str] = None
    ngrok_port: int = 3000
    max_context_tokens: int = 10000
    rate_limit_per_minute: int = 20

    def __post_init__(self):
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
        self.minimax_api_key = os.getenv("MINIMAX_API_KEY", "")
        self.minimax_base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat")
        self.project_root_path = os.getenv("PROJECT_ROOT_PATH", "")
        self.kuzu_db_path = os.getenv("KUZU_DB_PATH")
        self.ngrok_port = int(os.getenv("NGROK_PORT", "3000"))

    def is_project_configured(self) -> bool:
        return bool(self.project_root_path)
