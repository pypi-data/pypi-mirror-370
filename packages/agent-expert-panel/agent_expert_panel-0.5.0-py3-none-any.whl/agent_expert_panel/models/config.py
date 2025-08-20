from pydantic_settings import YamlConfigSettingsSource, BaseSettings, SettingsConfigDict
from pydantic import model_validator, Field
from typing import Type, Union
from pathlib import Path
import os
from .model_info import ModelInfo


class APIKeyError(Exception):
    """Raised when API key configuration is missing or invalid."""

    pass


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="model_config.yaml",
        yaml_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",  # Allow OPENAI_API_KEY and OPENAI_BASE_URL without prefix
    )

    name: str
    model_name: str
    description: str
    system_message: str
    openai_base_url: str | None = Field(
        default=None,
        description="OpenAI API base URL. Can be set via OPENAI_BASE_URL environment variable.",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key. Can be set via OPENAI_API_KEY environment variable.",
    )
    timeout: float = 30.0
    model_info: ModelInfo | None = None
    reflect_on_tool_use: bool = False
    tools: list[Union[str, dict]] = []  # Tool names or tool configurations

    @model_validator(mode="after")
    def validate_api_configuration(self):
        """Validate API configuration and provide helpful error messages."""
        # Handle empty strings as missing values - fall back to environment variables
        # This is needed because pydantic-settings treats "" as a valid value
        if not self.openai_api_key:  # Catches both None and empty string ""
            env_api_key = os.getenv("OPENAI_API_KEY", "").strip()
            if env_api_key:
                self.openai_api_key = env_api_key

        if not self.openai_base_url:  # Catches both None and empty string ""
            env_base_url = os.getenv("OPENAI_BASE_URL", "").strip()
            if env_base_url:
                self.openai_base_url = env_base_url

        # If we still don't have an API key, check if we're using a local LLM server
        if not self.openai_api_key:
            # Check if we're using a local LLM server that doesn't need a real API key
            if self.openai_base_url and self._is_local_llm_server(self.openai_base_url):
                # Use a dummy API key for local LLM servers
                self.openai_api_key = "dummy-local-key"
            else:
                raise APIKeyError(
                    "OpenAI API key is required but not configured. Please set it using one of these methods:\n\n"
                    "1. Environment variable: export OPENAI_API_KEY='your-api-key-here'\n"
                    "2. Set up local configuration: agent-panel configure\n"
                    "3. Use a local LLM server: export OPENAI_BASE_URL='http://localhost:11434/v1'\n\n"
                    "For more setup instructions, visit: https://github.com/zbloss/agent-expert-panel#setup"
                )

        return self

    def _is_local_llm_server(self, base_url: str) -> bool:
        """
        Check if the base URL points to a local LLM server that doesn't need a real API key.

        Args:
            base_url: The base URL to check

        Returns:
            True if this appears to be a local LLM server
        """
        if not base_url:
            return False

        # Normalize the URL
        url_lower = base_url.lower()

        # Check for common local server patterns
        local_patterns = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "192.168.",  # Local network
            "10.",  # Private network
            "172.16.",  # Private network
            "172.17.",  # Docker default
            "172.18.",  # Docker networks
            "172.19.",  # Docker networks
            "172.20.",  # Docker networks
            "172.21.",  # Docker networks
            "172.22.",  # Docker networks
            "172.23.",  # Docker networks
            "172.24.",  # Docker networks
            "172.25.",  # Docker networks
            "172.26.",  # Docker networks
            "172.27.",  # Docker networks
            "172.28.",  # Docker networks
            "172.29.",  # Docker networks
            "172.30.",  # Docker networks
            "172.31.",  # Private network end
        ]

        return any(pattern in url_lower for pattern in local_patterns)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple:
        """
        Define the order and sources for loading settings.
        Priority order: init > yaml > env > dotenv > file_secret
        """
        yaml_settings = YamlConfigSettingsSource(
            settings_cls,
            yaml_file=settings_cls.model_config.get("yaml_file", "model_config.yaml"),
            yaml_file_encoding=settings_cls.model_config.get(
                "yaml_file_encoding", "utf-8"
            ),
        )

        return (
            init_settings,
            yaml_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @classmethod
    def from_yaml(cls, yaml_file: str | Path, **kwargs) -> "AgentConfig":
        """
        Create a AgentConfig instance from a specific YAML file.

        Args:
            yaml_file: Path to the YAML configuration file
            **kwargs: Additional keyword arguments to override

        Returns:
            AgentConfig instance loaded from the YAML file
        """
        # Create YAML source manually
        yaml_source = YamlConfigSettingsSource(
            cls, yaml_file=str(yaml_file), yaml_file_encoding="utf-8"
        )

        # Load data from YAML
        yaml_data = yaml_source()

        # Merge with any provided kwargs (kwargs take precedence)
        final_data = {**yaml_data, **kwargs}

        # Create instance with the loaded data
        return cls(**final_data)
