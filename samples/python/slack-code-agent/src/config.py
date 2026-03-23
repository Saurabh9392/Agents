# src/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
    minimax_base_url: str = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat")
    project_root_path: str = os.getenv("PROJECT_ROOT_PATH", "")
    kuzu_db_path: Optional[str] = os.getenv("KUZU_DB_PATH")
    ngrok_port: int = int(os.getenv("NGROK_PORT", "3000"))
    max_context_tokens: int = 10000
    rate_limit_per_minute: int = 20

    def is_project_configured(self) -> bool:
        return bool(self.project_root_path)