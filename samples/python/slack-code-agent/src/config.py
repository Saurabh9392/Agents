# src/config.py
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    minimax_api_key: str = ""
    minimax_base_url: Optional[str] = None
    project_root_path: str = ""
    kuzu_db_path: Optional[str] = None
    ngrok_port: Optional[int] = None
    max_context_tokens: int = 10000
    rate_limit_per_minute: int = 20

    def __post_init__(self):
        if not self.slack_bot_token:
            self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN", "")
        if not self.slack_signing_secret:
            self.slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET", "")
        if not self.minimax_api_key:
            self.minimax_api_key = os.getenv("MINIMAX_API_KEY", "")
        if self.minimax_base_url is None:
            self.minimax_base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat")
        if not self.project_root_path:
            self.project_root_path = os.getenv("PROJECT_ROOT_PATH", "")
        if self.kuzu_db_path is None:
            self.kuzu_db_path = os.getenv("KUZU_DB_PATH")
        if self.ngrok_port is None:
            self.ngrok_port = int(os.getenv("NGROK_PORT", "3000"))

    def is_project_configured(self) -> bool:
        return bool(self.project_root_path)
