"""
Tests for the Web Research Agent configuration-based functionality.

This test suite validates the WebResearchAgent.from_config implementation
and its ability to create agents from configuration files.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from agent_expert_panel.agents.web_research_agent import WebResearchAgent
from agent_expert_panel.models.config import AgentConfig, ModelInfo


class TestWebResearchAgentFromConfig:
    """Test suite for WebResearchAgent.from_config class method."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample agent configuration for testing."""
        return AgentConfig(
            name="web_research_specialist",
            model_name="qwen3:4b",
            openai_base_url="http://localhost:11434/v1",
            openai_api_key="test-key",
            timeout=30.0,
            description="Test web research specialist",
            system_message="Test system message for web research",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="UNKNOWN",
                structured_output=True,
                multiple_system_messages=False,
            ),
            reflect_on_tool_use=True,
            tools=["tavily_search"],
        )

    @pytest.fixture
    def config_yaml_content(self):
        """YAML content for configuration testing."""
        return """
# Default Model Configuration
name: "web_research_specialist"
model_name: "qwen3:4b"
openai_base_url: "http://localhost:11434/v1"
openai_api_key: "test-key"
timeout: 30.0
description: "Test web research specialist"
system_message: |
  The Web Research Specialist is a test agent for configuration-based creation.
model_info:
  vision: false
  function_calling: true
  json_output: true
  family: "UNKNOWN"
  structured_output: true
  multiple_system_messages: false
reflect_on_tool_use: true
tools:
  - tavily_search
"""

    def test_from_config_success(self, sample_config):
        """Test successful WebResearchAgent creation from config."""
        with patch(
            "autogen_ext.models.openai.OpenAIChatCompletionClient"
        ) as mock_client:
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance

            with patch(
                "agent_expert_panel.agents.web_research_agent.TavilyWebSearchTool"
            ):
                result = WebResearchAgent.from_config(
                    config=sample_config,
                    use_tavily=True,
                    max_pages_per_search=3,
                )

                # Verify model client creation
                mock_client.assert_called_once()
                call_kwargs = mock_client.call_args.kwargs
                assert call_kwargs["model"] == "qwen3:4b"
                assert call_kwargs["base_url"] == "http://localhost:11434/v1"
                assert call_kwargs["api_key"] == "test-key"

                # Verify WebResearchAgent creation
                assert isinstance(result, WebResearchAgent)
                assert result.max_pages_per_search == 3
                assert result.use_tavily is True

    def test_from_config_with_mem0(self, sample_config):
        """Test WebResearchAgent creation with Mem0 manager."""
        mock_mem0_manager = Mock()

        with patch("autogen_ext.models.openai.OpenAIChatCompletionClient"):
            with patch(
                "agent_expert_panel.agents.web_research_agent.TavilyWebSearchTool"
            ):
                result = WebResearchAgent.from_config(
                    config=sample_config,
                    mem0_manager=mock_mem0_manager,
                )

                # Verify Mem0 manager is passed
                assert result.mem0_manager == mock_mem0_manager

    def test_from_config_no_tavily(self, sample_config):
        """Test WebResearchAgent creation without Tavily."""
        with patch("autogen_ext.models.openai.OpenAIChatCompletionClient"):
            result = WebResearchAgent.from_config(
                config=sample_config,
                use_tavily=False,
                tavily_api_key="custom-key",
            )

            # Verify Tavily settings
            assert result.use_tavily is False
            assert result.tavily_tool is None  # Should be None when Tavily is disabled

    def test_from_config_failure(self, sample_config):
        """Test WebResearchAgent creation failure handling."""
        with patch(
            "autogen_ext.models.openai.OpenAIChatCompletionClient",
            side_effect=Exception("Model client creation failed"),
        ):
            with pytest.raises(Exception, match="Model client creation failed"):
                WebResearchAgent.from_config(config=sample_config)

    def test_from_yaml_success(self, config_yaml_content):
        """Test successful WebResearchAgent creation from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_yaml_content)
            f.flush()
            config_path = Path(f.name)

        try:
            with patch("autogen_ext.models.openai.OpenAIChatCompletionClient"):
                with patch(
                    "agent_expert_panel.agents.web_research_agent.TavilyWebSearchTool"
                ):
                    config = AgentConfig.from_yaml(config_path)
                    result = WebResearchAgent.from_config(
                        config=config,
                        use_tavily=True,
                        max_pages_per_search=5,
                    )

                    # Verify agent creation
                    assert isinstance(result, WebResearchAgent)
                    assert result.max_pages_per_search == 5
                    assert result.use_tavily is True

        finally:
            # Clean up temporary file
            config_path.unlink()

    def test_from_yaml_file_not_found(self):
        """Test WebResearchAgent creation with non-existent YAML file."""
        non_existent_path = Path("/non/existent/config.yaml")

        with pytest.raises((FileNotFoundError, ValueError)):
            config = AgentConfig.from_yaml(non_existent_path)
            WebResearchAgent.from_config(config=config)

    def test_from_yaml_invalid_yaml(self):
        """Test WebResearchAgent creation with invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: [unclosed"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            config_path = Path(f.name)

        try:
            with pytest.raises(Exception):  # YAML parsing error
                config = AgentConfig.from_yaml(config_path)
                WebResearchAgent.from_config(config=config)

        finally:
            config_path.unlink()

    def test_from_yaml_with_all_parameters(self, config_yaml_content):
        """Test WebResearchAgent creation from YAML with all parameters."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_yaml_content)
            f.flush()
            config_path = Path(f.name)

        mock_mem0_manager = Mock()

        try:
            with patch("autogen_ext.models.openai.OpenAIChatCompletionClient"):
                config = AgentConfig.from_yaml(config_path)
                result = WebResearchAgent.from_config(
                    config=config,
                    use_tavily=False,
                    tavily_api_key="test-tavily-key",
                    mem0_manager=mock_mem0_manager,
                    max_pages_per_search=8,
                )

                # Verify all parameters are passed correctly
                assert result.use_tavily is False
                assert result.mem0_manager == mock_mem0_manager
                assert result.max_pages_per_search == 8

        finally:
            config_path.unlink()


class TestWebResearchAgentConfigIntegration:
    """Integration tests for WebResearchAgent.from_config."""

    def test_real_config_loading(self):
        """Test loading a real configuration file from the project."""
        config_path = (
            Path(__file__).parent.parent
            / "src"
            / "agent_expert_panel"
            / "configs"
            / "web_research_specialist.yaml"
        )

        if not config_path.exists():
            pytest.skip("Web research specialist config file not found")

        # Test that the config can be loaded without errors
        config = AgentConfig.from_yaml(config_path)
        assert config.name == "web_research_specialist"
        assert "tavily_search" in config.tools
        assert config.model_info.function_calling is True

        # Test that from_config can create agent from the real config
        with patch("autogen_ext.models.openai.OpenAIChatCompletionClient"):
            with patch(
                "agent_expert_panel.agents.web_research_agent.TavilyWebSearchTool"
            ):
                result = WebResearchAgent.from_config(config=config)

                assert isinstance(result, WebResearchAgent)
                assert result.use_tavily is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
