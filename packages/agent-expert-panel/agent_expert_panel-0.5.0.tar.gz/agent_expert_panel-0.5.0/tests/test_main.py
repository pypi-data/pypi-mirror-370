"""
Tests for the main CLI functionality.

Note: The main.py module now uses Typer CLI framework. These tests focus on
testing the utility functions that are still directly testable.
For testing CLI commands, consider using Typer's testing utilities.
"""

from unittest.mock import Mock, patch

from agent_expert_panel.main import (
    main,
    setup_logging,
    display_welcome,
    display_agents,
)
from agent_expert_panel.panel import ExpertPanel


class TestMain:
    """Test cases for main CLI functionality."""

    def test_setup_logging_default(self):
        """Test logging setup with default verbosity."""
        with patch("agent_expert_panel.main.logging.basicConfig") as mock_config:
            setup_logging(verbose=False)

            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert "level" in kwargs

    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode."""
        with patch("agent_expert_panel.main.logging.basicConfig") as mock_config:
            setup_logging(verbose=True)

            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert "level" in kwargs

    @patch("agent_expert_panel.main.Console")
    def test_display_welcome(self, mock_console):
        """Test welcome message display."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        display_welcome()

        # Should create console and print welcome message
        mock_console.assert_called_once()
        mock_console_instance.print.assert_called()

    @patch("agent_expert_panel.main.Console")
    def test_display_agents(self, mock_console):
        """Test agent display functionality."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        # Create a mock panel with agent descriptions
        mock_panel = Mock(spec=ExpertPanel)
        mock_panel.get_agent_descriptions.return_value = {
            "advocate": "Test advocate description",
            "critic": "Test critic description",
        }

        display_agents(mock_panel)

        # Should create console and display agents table
        mock_console.assert_called_once()
        mock_console_instance.print.assert_called()

    def test_main_exists(self):
        """Test that main function exists and can be imported."""
        # The main function now uses Typer CLI
        assert callable(main)

    def test_imports_work(self):
        """Test that all expected functions can be imported."""
        # This ensures the module structure is correct
        from agent_expert_panel.main import (
            setup_logging,
            display_welcome,
            display_agents,
            main,
        )

        assert callable(setup_logging)
        assert callable(display_welcome)
        assert callable(display_agents)
        assert callable(main)

    def test_typer_app_exists(self):
        """Test that the Typer app is properly configured."""
        from agent_expert_panel.main import app
        import typer

        assert isinstance(app, typer.Typer)
        assert app.info.name == "agent-panel"
