# src/config.py
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class Config:
    # Azure Bot
    microsoft_app_id: str
    microsoft_app_password: str
    microsoft_app_type: str = "MultiTenant"

    # ZhipuAI
    zhipuai_api_key: str = ""

    # Project
    project_root_path: str = ""
    max_context_tokens: int = 8000
    rate_limit_per_minute: int = 10
    rate_limit_per_day: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            microsoft_app_id=os.getenv("MicrosoftAppId", ""),
            microsoft_app_password=os.getenv("MicrosoftAppPassword", ""),
            microsoft_app_type=os.getenv("MicrosoftAppType", "MultiTenant"),
            zhipuai_api_key=os.getenv("ZHIPUAI_API_KEY", ""),
            project_root_path=os.getenv("PROJECT_ROOT_PATH", os.getcwd()),
            max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "8000")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "10")),
            rate_limit_per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "100")),
        )

    def validate(self) -> None:
        required = [
            ("MicrosoftAppId", self.microsoft_app_id),
            ("MicrosoftAppPassword", self.microsoft_app_password),
            ("ZHIPUAI_API_KEY", self.zhipuai_api_key),
        ]
        for name, value in required:
            if not value:
                raise ValueError(f"Missing required environment variable: {name}")
