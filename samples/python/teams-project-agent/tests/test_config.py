# tests/test_config.py
import os
import pytest
from unittest.mock import patch
from src.config import Config


class TestConfig:
    """Unit tests for Config class."""

    def test_config_from_env_with_defaults(self):
        """Test that config loads from environment with default values."""
        with patch.dict(os.environ, {
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID": "test_app_id",
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD": "test_password",
            "ZHIPUAI_API_KEY": "test_zhipuai_key",
        }, clear=False):
            config = Config()

            assert config.microsoft_app_id == "test_app_id"
            assert config.microsoft_app_password == "test_password"
            assert config.microsoft_app_type == "MultiTenant"
            assert config.zhipuai_api_key == "test_zhipuai_key"
            assert config.max_context_tokens == 8000
            assert config.rate_limit_per_minute == 10
            assert config.rate_limit_per_day == 100

    def test_config_from_env_with_custom_values(self):
        """Test that config loads custom values from environment."""
        with patch.dict(os.environ, {
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID": "custom_app_id",
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD": "custom_password",
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_TYPE": "SingleTenant",
            "ZHIPUAI_API_KEY": "custom_zhipuai_key",
            "PROJECT_ROOT_PATH": "/custom/path",
            "MAX_CONTEXT_TOKENS": "16000",
            "RATE_LIMIT_PER_MINUTE": "20",
            "RATE_LIMIT_PER_DAY": "200",
        }, clear=False):
            config = Config()

            assert config.microsoft_app_id == "custom_app_id"
            assert config.microsoft_app_password == "custom_password"
            assert config.microsoft_app_type == "SingleTenant"
            assert config.zhipuai_api_key == "custom_zhipuai_key"
            assert config.project_root_path == "/custom/path"
            assert config.max_context_tokens == 16000
            assert config.rate_limit_per_minute == 20
            assert config.rate_limit_per_day == 200

    def test_config_explicit_values_override_env(self):
        """Test that explicitly passed values override environment variables."""
        with patch.dict(os.environ, {
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID": "env_app_id",
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD": "env_password",
            "ZHIPUAI_API_KEY": "env_zhipuai_key",
        }, clear=False):
            config = Config(
                microsoft_app_id="explicit_app_id",
                microsoft_app_password="explicit_password",
                zhipuai_api_key="explicit_zhipuai_key",
                project_root_path="/explicit/path"
            )

            # Explicit values should be used, not env values
            assert config.microsoft_app_id == "explicit_app_id"
            assert config.microsoft_app_password == "explicit_password"
            assert config.zhipuai_api_key == "explicit_zhipuai_key"
            assert config.project_root_path == "/explicit/path"

    def test_config_validate_success(self):
        """Test that validation passes when required fields are present."""
        config = Config(
            microsoft_app_id="test_app_id",
            microsoft_app_password="test_password",
            zhipuai_api_key="test_zhipuai_key",
            project_root_path="/test/path"
        )

        # Should not raise any exception
        config.validate()

    def test_config_validate_missing_app_id(self):
        """Test that validation fails when MicrosoftAppId is missing."""
        config = Config(
            microsoft_app_id="",
            microsoft_app_password="test_password",
            zhipuai_api_key="test_zhipuai_key",
            project_root_path="/test/path"
        )

        with pytest.raises(ValueError, match="Missing required environment variable: CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_ID"):
            config.validate()

    def test_config_validate_missing_app_password(self):
        """Test that validation fails when MicrosoftAppPassword is missing."""
        config = Config(
            microsoft_app_id="test_app_id",
            microsoft_app_password="",
            zhipuai_api_key="test_zhipuai_key",
            project_root_path="/test/path"
        )

        with pytest.raises(ValueError, match="Missing required environment variable: CONNECTIONS__SERVICE_CONNECTION__SETTINGS__MICROSOFT_APP_PASSWORD"):
            config.validate()

    def test_config_validate_missing_zhipuai_key(self):
        """Test that validation fails when ZHIPUAI_API_KEY is missing."""
        config = Config(
            microsoft_app_id="test_app_id",
            microsoft_app_password="test_password",
            zhipuai_api_key="",
            project_root_path="/test/path"
        )

        with pytest.raises(ValueError, match="Missing required environment variable: ZHIPUAI_API_KEY"):
            config.validate()
