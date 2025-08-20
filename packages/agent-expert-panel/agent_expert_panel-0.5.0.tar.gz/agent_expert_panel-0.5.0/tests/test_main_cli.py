"""
Tests for the main CLI interface functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner

from agent_expert_panel.main import app, display_welcome, display_agents, setup_logging
from agent_expert_panel.panel import ExpertPanel
from agent_expert_panel.models import DiscussionPattern, PanelResult
from agent_expert_panel.models.config import APIKeyError


class TestCLI:
    """Test cases for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_panel(self):
        """Create a mock ExpertPanel for testing."""
        panel = Mock(spec=ExpertPanel)
        panel.get_agent_descriptions.return_value = {
            "advocate": "Champions ideas with conviction",
            "critic": "Quality assurance and risk analysis",
            "pragmatist": "Practical implementation focus",
            "research_specialist": "Fact-finding and evidence gathering",
            "innovator": "Creative disruption and breakthrough solutions",
        }

        # Mock discuss method to return a PanelResult
        mock_result = Mock(spec=PanelResult)
        mock_result.topic = "Test topic"
        mock_result.discussion_pattern = DiscussionPattern.ROUND_ROBIN
        mock_result.agents_participated = ["advocate", "critic"]
        mock_result.total_rounds = 1
        mock_result.consensus_reached = True
        mock_result.final_recommendation = "Test recommendation"

        panel.discuss = AsyncMock(return_value=mock_result)
        panel.quick_consensus = AsyncMock(return_value="Quick consensus result")

        return panel

    def test_discuss_command_basic(self, runner, mock_panel):
        """Test the basic discuss command."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(
                app,
                [
                    "discuss",
                    "Should we adopt microservices?",
                    "--pattern",
                    "round-robin",
                    "--rounds",
                    "2",
                ],
            )

            assert result.exit_code == 0
            mock_panel.discuss.assert_called_once()

    def test_discuss_command_with_human(self, runner, mock_panel):
        """Test the discuss command with human participation."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(
                app, ["discuss", "Test topic", "--with-human", "--rounds", "1"]
            )

            assert result.exit_code == 0
            # Verify human participation was enabled
            call_args = mock_panel.discuss.call_args
            assert call_args[1]["with_human"] is True

    def test_discuss_command_with_participants(self, runner, mock_panel):
        """Test the discuss command with specific participants."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(
                app,
                [
                    "discuss",
                    "Test topic",
                    "--participants",
                    "advocate",
                    "--participants",
                    "critic",
                ],
            )

            assert result.exit_code == 0
            call_args = mock_panel.discuss.call_args
            assert call_args[1]["participants"] == ["advocate", "critic"]

    def test_discuss_command_with_verbose(self, runner, mock_panel):
        """Test the discuss command with verbose logging."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            with patch("agent_expert_panel.main.setup_logging") as mock_setup_logging:
                result = runner.invoke(app, ["discuss", "Test topic", "--verbose"])

                assert result.exit_code == 0
                mock_setup_logging.assert_called_with(True)

    def test_discuss_command_api_error(self, runner):
        """Test discuss command handles API key errors gracefully."""
        with patch(
            "agent_expert_panel.main.ExpertPanel",
            side_effect=APIKeyError("API key missing"),
        ):
            result = runner.invoke(app, ["discuss", "Test topic"])

            assert result.exit_code == 1
            assert "Configuration Error" in result.stdout

    def test_list_agents_command(self, runner, mock_panel):
        """Test the list-agents command."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            with patch("agent_expert_panel.main.display_agents") as mock_display:
                result = runner.invoke(app, ["list-agents"])

                assert result.exit_code == 0
                mock_display.assert_called_once_with(mock_panel)

    def test_list_agents_with_config_dir(self, runner, mock_panel, tmp_path):
        """Test list-agents with custom config directory."""
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        with patch(
            "agent_expert_panel.main.ExpertPanel", return_value=mock_panel
        ) as mock_panel_class:
            result = runner.invoke(
                app, ["list-agents", "--config-dir", str(config_dir)]
            )

            assert result.exit_code == 0
            mock_panel_class.assert_called_with(
                config_dir=config_dir, model_overrides={}
            )

    def test_show_agent_command(self, runner, mock_panel):
        """Test the show-agent command."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(app, ["show-agent", "advocate"])

            assert result.exit_code == 0
            assert "advocate" in result.stdout.lower()

    def test_show_agent_not_found(self, runner, mock_panel):
        """Test show-agent with invalid agent name."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(app, ["show-agent", "nonexistent"])

            assert result.exit_code == 1
            assert "not found" in result.stdout

    def test_quick_consensus_command(self, runner, mock_panel):
        """Test the quick-consensus command."""
        with patch("agent_expert_panel.main.ExpertPanel", return_value=mock_panel):
            result = runner.invoke(app, ["quick-consensus", "Is this a good idea?"])

            assert result.exit_code == 0
            # The quick-consensus command now calls discuss() instead of quick_consensus()
            mock_panel.discuss.assert_called_once_with(
                topic="Is this a good idea?",
                pattern=DiscussionPattern.ROUND_ROBIN,
                max_rounds=1,
            )

    def test_validate_config_command(self, runner, tmp_path):
        """Test the validate-config command."""
        # Create a test config directory with valid YAML files
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        # Create valid config files
        required_agents = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]

        for agent_name in required_agents:
            config_file = config_dir / f"{agent_name}.yaml"
            config_file.write_text(f"""
name: {agent_name}
model_name: test-model
description: Test {agent_name} agent
system_message: You are a test {agent_name}
model_info:
  vision: false
  function_calling: true
  json_output: true
  family: TEST
""")

        with patch("agent_expert_panel.main.AgentConfig.from_yaml"):
            result = runner.invoke(app, ["validate-config", str(config_dir)])

            assert result.exit_code == 0
            assert "valid and ready to use" in result.stdout

    def test_validate_config_missing_files(self, runner, tmp_path):
        """Test validate-config with missing files."""
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        result = runner.invoke(app, ["validate-config", str(config_dir)])

        assert result.exit_code == 1
        assert "Missing configuration file" in result.stdout

    def test_configure_command_show_current(self, runner):
        """Test the configure command showing current config."""
        with patch("builtins.input", side_effect=["3"]):  # Choose "show current"
            with patch("agent_expert_panel.main.show_current_config") as mock_show:
                result = runner.invoke(app, ["configure"])

                assert result.exit_code == 0
                mock_show.assert_called_once()

    def test_display_welcome(self, capsys):
        """Test the display_welcome function."""
        display_welcome()
        captured = capsys.readouterr()
        assert "Agent Expert Panel" in captured.out

    def test_display_agents(self, mock_panel, capsys):
        """Test the display_agents function."""
        display_agents(mock_panel)
        captured = capsys.readouterr()
        assert "advocate" in captured.out.lower()
        assert "critic" in captured.out.lower()

    def test_setup_logging_verbose(self):
        """Test setup_logging with verbose enabled."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(True)
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == 10  # DEBUG level

    def test_setup_logging_not_verbose(self):
        """Test setup_logging with verbose disabled."""
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(False)
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args[1]
            assert call_args["level"] == 20  # INFO level


class TestConfigurationFunctions:
    """Test configuration-related functions."""

    def test_configure_openai_api(self):
        """Test OpenAI API configuration."""
        from agent_expert_panel.main import configure_openai_api
        from rich.console import Console

        console = Console()

        with patch("agent_expert_panel.main.Prompt.ask", return_value="test-api-key"):
            with patch("agent_expert_panel.main.ExpertPanel"):
                with patch("os.environ", {"OPENAI_API_KEY": "test-api-key"}):
                    # Should not raise an exception
                    configure_openai_api(console)

    def test_configure_local_llm(self):
        """Test local LLM configuration."""
        from agent_expert_panel.main import configure_local_llm
        from rich.console import Console

        console = Console()

        with patch(
            "agent_expert_panel.main.Prompt.ask",
            return_value="http://localhost:11434/v1",
        ):
            # Should not raise an exception
            configure_local_llm(console)

    def test_show_current_config_with_keys(self):
        """Test showing current config when environment variables are set."""
        from agent_expert_panel.main import show_current_config
        from rich.console import Console

        console = Console()

        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "OPENAI_API_KEY": "sk-test123456789abcdef",
                "OPENAI_BASE_URL": "http://localhost:11434/v1",
            }.get(key, default)

            # Should not raise an exception
            show_current_config(console)

    def test_show_current_config_no_keys(self):
        """Test showing current config when no environment variables are set."""
        from agent_expert_panel.main import show_current_config
        from rich.console import Console

        console = Console()

        with patch("os.getenv", return_value=""):
            # Should not raise an exception
            show_current_config(console)


class TestInteractiveMode:
    """Test interactive mode functionality."""

    @pytest.mark.asyncio
    async def test_interactive_mode_quit(self):
        """Test interactive mode with quit command."""
        from agent_expert_panel.main import interactive_mode

        with patch("agent_expert_panel.main.ExpertPanel") as _:
            with patch(
                "agent_expert_panel.main.Confirm.ask", return_value=False
            ):  # Don't show agents
                with patch(
                    "agent_expert_panel.main.Prompt.ask", return_value="quit"
                ):  # Quit immediately
                    with patch("agent_expert_panel.main.display_welcome"):
                        result = await interactive_mode()
                        assert result == 0

    @pytest.mark.asyncio
    async def test_interactive_mode_api_error(self):
        """Test interactive mode handles API errors."""
        from agent_expert_panel.main import interactive_mode

        with patch(
            "agent_expert_panel.main.ExpertPanel",
            side_effect=APIKeyError("API key missing"),
        ):
            with patch("agent_expert_panel.main.display_welcome"):
                result = await interactive_mode()
                assert result == 1

    @pytest.mark.asyncio
    async def test_interactive_mode_keyboard_interrupt(self):
        """Test interactive mode handles keyboard interrupt."""
        from agent_expert_panel.main import interactive_mode

        with patch(
            "agent_expert_panel.main.ExpertPanel", side_effect=KeyboardInterrupt()
        ):
            with patch("agent_expert_panel.main.display_welcome"):
                result = await interactive_mode()
                assert result == 1
