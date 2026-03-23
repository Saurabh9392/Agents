# src/config.py
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    # Azure Bot
    microsoft_app_id: str = ""
    microsoft_app_password: str = ""
    microsoft_app_type: str = "MultiTenant"

    # LLM Provider settings
    llm_provider: str = "zhipuai"  # "zhipuai" or "azure_openai"

    # ZhipuAI
    zhipuai_api_key: str = ""

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-4o"

    # Project
    project_root_path: str = ""
    max_context_tokens: int = 8000
    rate_limit_per_minute: int = 10
    rate_limit_per_day: int = 100

    def __post_init__(self):
        """Read environment variables at instance creation time."""
        # Only read from env if field was not explicitly set (empty string)
        if not self.microsoft_app_id:
            self.microsoft_app_id = os.getenv("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID", "")
        if not self.microsoft_app_password:
            self.microsoft_app_password = os.getenv("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD", "")
        if self.microsoft_app_type == "MultiTenant":  # Only override if still default
            self.microsoft_app_type = os.getenv("CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_TYPE", "MultiTenant")

        # LLM Provider
        if self.llm_provider == "zhipuai":  # Only override if still default
            self.llm_provider = os.getenv("LLM_PROVIDER", "zhipuai")

        # ZhipuAI
        if not self.zhipuai_api_key:
            self.zhipuai_api_key = os.getenv("ZHIPUAI_API_KEY", "")

        # Azure OpenAI
        if not self.azure_openai_api_key:
            self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        if not self.azure_openai_endpoint:
            self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if self.azure_openai_api_version == "2024-02-01":  # Only override if still default
            self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        if self.azure_openai_deployment_name == "gpt-4o":  # Only override if still default
            self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        # Project settings
        if not self.project_root_path:
            self.project_root_path = os.getenv("PROJECT_ROOT_PATH", os.getcwd())
        if self.max_context_tokens == 8000:  # Only override if still default
            max_tokens_env = os.getenv("MAX_CONTEXT_TOKENS")
            if max_tokens_env:
                try:
                    self.max_context_tokens = int(max_tokens_env)
                except ValueError:
                    self.max_context_tokens = 8000
        if self.rate_limit_per_minute == 10:  # Only override if still default
            rate_limit_env = os.getenv("RATE_LIMIT_PER_MINUTE")
            if rate_limit_env:
                try:
                    self.rate_limit_per_minute = int(rate_limit_env)
                except ValueError:
                    self.rate_limit_per_minute = 10
        if self.rate_limit_per_day == 100:  # Only override if still default
            rate_limit_day_env = os.getenv("RATE_LIMIT_PER_DAY")
            if rate_limit_day_env:
                try:
                    self.rate_limit_per_day = int(rate_limit_day_env)
                except ValueError:
                    self.rate_limit_per_day = 100

    def validate(self) -> None:
        """Validate required configuration based on selected LLM provider."""
        # Always validate Azure Bot settings
        if not self.microsoft_app_id:
            raise ValueError("Missing required environment variable: CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID")
        if not self.microsoft_app_password:
            raise ValueError("Missing required environment variable: CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD")

        # Validate LLM provider specific settings
        if self.llm_provider == "zhipuai":
            if not self.zhipuai_api_key:
                raise ValueError("Missing required environment variable: ZHIPUAI_API_KEY")
        elif self.llm_provider == "azure_openai":
            if not self.azure_openai_api_key:
                raise ValueError("Missing required environment variable: AZURE_OPENAI_API_KEY")
            if not self.azure_openai_endpoint:
                raise ValueError("Missing required environment variable: AZURE_OPENAI_ENDPOINT")
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}. Supported: 'zhipuai', 'azure_openai'")
