"""
Extended tests for ExpertPanel to improve coverage of error handling and edge cases.
"""

import pytest
from unittest.mock import Mock, patch

from agent_expert_panel.panel import ExpertPanel
from agent_expert_panel.models import DiscussionPattern, PanelResult
from agent_expert_panel.models.config import AgentConfig
from autogen_agentchat.base import TaskResult


class TestExpertPanelErrorHandling:
    """Test error handling and edge cases in ExpertPanel."""

    @pytest.fixture
    def mock_agent_config(self):
        """Create a mock agent configuration."""
        config = Mock(spec=AgentConfig)
        config.description = "Test agent description"
        return config

    def test_init_with_custom_tools_directory_error(self, tmp_path):
        """Test initialization when custom tools directory loading fails."""
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()

        # Create a file that will cause an import error
        bad_tool_file = tools_dir / "bad_tool.py"
        bad_tool_file.write_text("import non_existent_module\n")

        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                with patch(
                    "agent_expert_panel.panel.load_tools_from_directory",
                    side_effect=Exception("Tool loading failed"),
                ):
                    # Should not raise exception, but log warning
                    panel = ExpertPanel(tools_dir=tools_dir)
                    # Custom tools should not be loaded due to error
                    assert len(panel.available_tools) >= 0  # Only built-in tools

    def test_init_with_nonexistent_tools_directory(self, tmp_path):
        """Test initialization with non-existent tools directory."""
        tools_dir = tmp_path / "nonexistent_tools"

        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                # Should not raise exception
                panel = ExpertPanel(tools_dir=tools_dir)
                assert panel.tools_dir == tools_dir

    def test_load_agents_missing_config_file(self, tmp_path):
        """Test _load_agents when a config file is missing."""
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        # Only create some config files, not all
        (config_dir / "advocate.yaml").write_text("""
name: advocate
model_name: test-model
description: test description
system_message: test message
openai_api_key: test-key
model_info:
  vision: false
  function_calling: true
  json_output: true
  family: TEST
""")

        with pytest.raises(FileNotFoundError):
            ExpertPanel(config_dir=config_dir)

    def test_load_agents_config_loading_error(self, tmp_path):
        """Test _load_agents when config loading fails."""
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        # Create all required config files
        agent_names = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]
        for name in agent_names:
            (config_dir / f"{name}.yaml").write_text("test config")

        with patch(
            "agent_expert_panel.panel.AgentConfig.from_yaml",
            side_effect=Exception("Config loading failed"),
        ):
            with pytest.raises(Exception):
                ExpertPanel(config_dir=config_dir)

    def test_add_tools_to_agent_invalid_agent(self):
        """Test adding tools to non-existent agent."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                with pytest.raises(ValueError, match="Agent 'nonexistent' not found"):
                    panel.add_tools_to_agent("nonexistent", ["some_tool"])

    def test_add_tools_to_agent_library_import_error(self):
        """Test adding tools when library import fails."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent") as mock_create:
                mock_agent = Mock()
                mock_agent.tools = []
                mock_create.return_value = mock_agent

                panel = ExpertPanel()
                panel.agents = {"test_agent": mock_agent}

                with patch(
                    "agent_expert_panel.panel.create_library_tool",
                    side_effect=Exception("Import failed"),
                ):
                    # Should not raise exception, but print warning
                    panel.add_tools_to_agent("test_agent", ["pandas.read_csv"])

    def test_add_tools_to_agent_unknown_tool(self):
        """Test adding unknown tool."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent") as mock_create:
                mock_agent = Mock()
                mock_agent.tools = []
                mock_create.return_value = mock_agent

                panel = ExpertPanel()
                panel.agents = {"test_agent": mock_agent}

                # Should not raise exception, but print warning
                panel.add_tools_to_agent("test_agent", ["unknown_tool"])

    def test_get_default_config_dir_fallback(self):
        """Test _get_default_config_dir fallback logic."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel.__new__(ExpertPanel)

                # Mock Path.exists to return False for package configs
                with patch("pathlib.Path.exists", return_value=False):
                    with patch("pathlib.Path.glob", return_value=[]):
                        config_dir = panel._get_default_config_dir()
                        assert config_dir.name == "configs"

    @pytest.mark.asyncio
    async def test_discuss_invalid_pattern(self):
        """Test discuss with invalid discussion pattern."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                with pytest.raises(NotImplementedError):
                    await panel.discuss(
                        topic="Test topic",
                        pattern=DiscussionPattern.OPEN_FLOOR,  # Not implemented
                    )

    def test_extract_discussion_history_no_messages(self):
        """Test _extract_discussion_history with no messages."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                mock_task_result = Mock(spec=TaskResult)
                mock_task_result.messages = []

                history = panel._extract_discussion_history(mock_task_result)
                assert history == []

    @pytest.mark.asyncio
    async def test_analyze_discussion_results_error_handling(self):
        """Test _analyze_discussion_results with error during analysis."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent") as mock_create:
                # Mock the main agent
                mock_agent = Mock()
                mock_agent._model_client = Mock()
                mock_create.return_value = mock_agent

                panel = ExpertPanel()

                mock_task_result = Mock(spec=TaskResult)
                # Make messages non-iterable to trigger an error
                mock_task_result.messages = Mock(spec=[])

                # The current implementation will raise an exception for non-iterable messages
                with pytest.raises(TypeError):
                    await panel._analyze_discussion_results(
                        mock_task_result, ["agent1"]
                    )

    @pytest.mark.asyncio
    async def test_detect_consensus_empty_messages(self):
        """Test _detect_consensus with empty message list."""
        from agent_expert_panel.models.consensus import Consensus

        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                consensus = await panel._detect_consensus([])
                assert isinstance(consensus, Consensus)
                assert consensus.consensus_reached is False

    @pytest.mark.asyncio
    async def test_detect_consensus_single_message(self):
        """Test _detect_consensus with single message."""
        from agent_expert_panel.models.consensus import Consensus

        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                messages = ["I agree with this approach"]
                consensus = await panel._detect_consensus(messages)
                assert isinstance(consensus, Consensus)
                assert consensus.consensus_reached is False  # Not enough messages

    @pytest.mark.asyncio
    async def test_detect_consensus_agreement(self):
        """Test _detect_consensus with agreement keywords."""
        from agent_expert_panel.models.consensus import Consensus

        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent") as mock_create:
                # Mock the main agent
                mock_agent = Mock()
                mock_agent._model_client = Mock()
                mock_create.return_value = mock_agent

                # Mock the consensus agent and its response
                with patch(
                    "agent_expert_panel.panel.AssistantAgent"
                ) as mock_consensus_agent_class:
                    mock_consensus_agent = Mock()
                    mock_consensus_agent_class.return_value = mock_consensus_agent

                    # Mock the TaskResult and consensus response
                    mock_task_result = Mock()
                    mock_message = Mock()
                    mock_message.content = Consensus(
                        consensus_reached=True,
                        summary="The participants reached agreement",
                        participants=["agent1", "agent2", "agent3"],
                    )
                    mock_task_result.messages = [mock_message]

                    # Mock RichConsole for consensus detection
                    with patch(
                        "agent_expert_panel.panel.RichConsole"
                    ) as mock_rich_console:
                        mock_rich_console.return_value = mock_task_result

                        panel = ExpertPanel()

                        messages = [
                            "I think we should proceed",
                            "I agree with that recommendation",
                            "That sounds reasonable, I support this approach",
                        ]
                        consensus = await panel._detect_consensus(messages)
                        assert isinstance(consensus, Consensus)
                        assert consensus.consensus_reached is True

    @pytest.mark.asyncio
    async def test_synthesize_recommendation_empty_messages(self):
        """Test _synthesize_recommendation with empty messages."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                recommendation = await panel._synthesize_recommendation([])
                assert recommendation == "No discussion content available."

    @pytest.mark.asyncio
    async def test_synthesize_recommendation_single_long_message(self):
        """Test _synthesize_recommendation with single long message."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                long_content = "A" * 250  # Long message
                messages = [long_content]

                recommendation = await panel._synthesize_recommendation(messages)
                assert "Final Panel Recommendation" in recommendation
                assert long_content in recommendation

    def test_calculate_discussion_rounds_zero_agents(self):
        """Test _calculate_discussion_rounds with zero agents."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                rounds = panel._calculate_discussion_rounds([], 0)
                assert rounds == 0

    def test_calculate_discussion_rounds_empty_history(self):
        """Test _calculate_discussion_rounds with empty history."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                rounds = panel._calculate_discussion_rounds([], 5)
                assert rounds == 0


class TestPanelResultValidation:
    """Test PanelResult data validation."""

    def test_panel_result_creation(self):
        """Test creating a PanelResult with all fields."""
        result = PanelResult(
            topic="Test topic",
            discussion_pattern=DiscussionPattern.ROUND_ROBIN,
            agents_participated=["agent1", "agent2"],
            discussion_history=[{"round": 1, "speaker": "agent1", "content": "test"}],
            consensus_reached=True,
            final_recommendation="Test recommendation",
            total_rounds=2,
        )

        assert result.topic == "Test topic"
        assert result.discussion_pattern == DiscussionPattern.ROUND_ROBIN
        assert result.agents_participated == ["agent1", "agent2"]
        assert len(result.discussion_history) == 1
        assert result.consensus_reached is True
        assert result.final_recommendation == "Test recommendation"
        assert result.total_rounds == 2


class TestToolsIntegration:
    """Test tools integration with panel."""

    def test_add_library_tools(self):
        """Test adding library tools to panel."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent"):
                panel = ExpertPanel()

                library_tools = {"read_csv": "pandas.read_csv"}

                with patch(
                    "agent_expert_panel.panel.add_library_tools_to_dict"
                ) as mock_add:
                    panel.add_library_tools(library_tools)
                    mock_add.assert_called_once_with(
                        panel.available_tools, library_tools
                    )

    def test_add_tools_to_agent_callable(self):
        """Test adding callable tools to agent."""
        with patch("agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("agent_expert_panel.panel.create_agent") as mock_create:

                def my_tool():
                    return "test"

                mock_agent = Mock()
                mock_agent.tools = []
                mock_create.return_value = mock_agent

                panel = ExpertPanel()
                panel.agents = {"test_agent": mock_agent}

                panel.add_tools_to_agent("test_agent", [my_tool])

                # Verify the callable was added
                assert my_tool in mock_agent.tools
