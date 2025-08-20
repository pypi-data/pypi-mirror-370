"""
Extended tests for config.py to improve coverage.
"""

import pytest
from pathlib import Path
import yaml
from unittest.mock import patch

from agent_expert_panel.models.config import AgentConfig, APIKeyError


class TestAgentConfigErrorHandling:
    """Test error handling in AgentConfig."""

    def test_from_yaml_file_not_found(self):
        """Test loading config from non-existent file."""
        with pytest.raises((FileNotFoundError, ValueError)):
            AgentConfig.from_yaml(Path("/nonexistent/file.yaml"))

    def test_from_yaml_invalid_yaml(self, tmp_path):
        """Test loading config from file with invalid YAML."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [unclosed")

        with pytest.raises(yaml.YAMLError):
            AgentConfig.from_yaml(config_file)

    def test_from_yaml_missing_required_fields(self, tmp_path):
        """Test loading config with missing required fields."""
        config_file = tmp_path / "incomplete.yaml"
        config_file.write_text("""
name: test
# Missing model_name, description, system_message
""")

        # Should raise validation error for missing fields
        with pytest.raises((ValueError, KeyError, TypeError)):
            AgentConfig.from_yaml(config_file)

    def test_from_yaml_invalid_field_types(self, tmp_path):
        """Test loading config with invalid field types."""
        config_file = tmp_path / "invalid_types.yaml"
        config_file.write_text("""
name: test
model_name: test-model
description: test description
system_message: test message
timeout: "not_a_number"  # Should be float
""")

        # Should handle type conversion or validation error
        with pytest.raises((ValueError, TypeError)):
            AgentConfig.from_yaml(config_file)

    def test_api_key_resolution_no_env_var(self):
        """Test API key resolution when no environment variable is set."""
        with patch.dict("os.environ", {}, clear=True):
            # Should raise APIKeyError when no API key is provided
            config_data = {
                "name": "test",
                "model_name": "test-model",
                "description": "test description",
                "system_message": "test message",
            }

            # This should raise APIKeyError for missing API key
            with pytest.raises(APIKeyError):
                AgentConfig(**config_data)

    def test_api_key_resolution_with_env_var(self):
        """Test API key resolution when environment variable is set."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key"}):
            config_data = {
                "name": "test",
                "model_name": "test-model",
                "description": "test description",
                "system_message": "test message",
            }

            config = AgentConfig(**config_data)
            assert config.openai_api_key == "test-api-key"

    def test_api_key_error_creation(self):
        """Test APIKeyError creation and message."""
        error = APIKeyError("Custom API key error message")
        assert str(error) == "Custom API key error message"
        assert isinstance(error, Exception)

    def test_config_with_all_optional_fields(self, tmp_path):
        """Test config creation with all optional fields provided."""
        config_file = tmp_path / "complete.yaml"
        config_file.write_text("""
name: test
model_name: test-model
description: test description
system_message: test message
openai_base_url: http://localhost:11434/v1
openai_api_key: test-key
timeout: 60.0
tools:
  - name: web_search
  - name: read_file
reflect_on_tool_use: true
model_info:
  vision: true
  function_calling: true
  json_output: true
  family: TEST
  structured_output: true
  multiple_system_messages: false
""")

        config = AgentConfig.from_yaml(config_file)

        assert config.name == "test"
        assert config.model_name == "test-model"
        assert config.openai_base_url == "http://localhost:11434/v1"
        assert config.openai_api_key == "test-key"
        assert config.timeout == 60.0
        assert config.reflect_on_tool_use is True
        assert len(config.tools) == 2
        assert config.model_info.vision is True

    def test_config_with_minimal_fields(self, tmp_path):
        """Test config creation with only required fields."""
        config_file = tmp_path / "minimal.yaml"
        config_file.write_text("""
name: test
model_name: test-model
description: test description
system_message: test message
openai_api_key: test-key
""")

        config = AgentConfig.from_yaml(config_file)

        assert config.name == "test"
        assert config.model_name == "test-model"
        assert config.description == "test description"
        assert config.system_message == "test message"
        # Optional fields should have defaults
        assert config.tools == []
        assert config.reflect_on_tool_use is False
