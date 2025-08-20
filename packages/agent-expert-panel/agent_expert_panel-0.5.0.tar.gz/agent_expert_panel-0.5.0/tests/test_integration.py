"""
Integration tests for the Agent Expert Panel system.

These tests verify that all components work together correctly,
using mocks to avoid actually calling LLM APIs.
"""

import pytest
import yaml
from unittest.mock import Mock, patch, AsyncMock

from agent_expert_panel.panel import ExpertPanel
from agent_expert_panel.models import DiscussionPattern
from agent_expert_panel.utils.export import save_discussion
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent


class TestFullSystemIntegration:
    """Integration tests for the complete expert panel system."""

    @pytest.fixture
    def test_configs(self, tmp_path):
        """Create test configuration files."""
        config_dir = tmp_path / "test_configs"
        config_dir.mkdir()

        # Define configurations for all 5 agents
        configs = {
            "advocate": {
                "name": "advocate",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test advocate agent",
                "system_message": "You are an advocate who champions ideas with conviction.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "critic": {
                "name": "critic",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test critic agent",
                "system_message": "You are a critic who identifies risks and challenges.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "pragmatist": {
                "name": "pragmatist",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test pragmatist agent",
                "system_message": "You are a pragmatist focused on practical solutions.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "research_specialist": {
                "name": "research_specialist",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test research specialist agent",
                "system_message": "You are a research specialist who provides evidence-based insights.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "innovator": {
                "name": "innovator",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test innovator agent",
                "system_message": "You are an innovator who thinks outside conventional boundaries.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
        }

        # Write YAML files
        for name, config in configs.items():
            config_file = config_dir / f"{name}.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config, f)

        return config_dir

    @pytest.fixture
    def realistic_task_result(self):
        """Create a realistic TaskResult for testing."""
        mock_result = Mock(spec=TaskResult)

        # Create realistic agent conversation
        messages = []

        # Advocate's message
        msg1 = Mock()
        msg1.source = "advocate"
        msg1.content = """I strongly advocate for implementing remote work policies. The evidence is compelling:

1. Productivity studies show 13-50% improvement in remote workers
2. Cost savings of $11,000 per remote employee annually
3. Access to global talent pool increases by 300%
4. Employee satisfaction increases by 87%

The benefits clearly outweigh any perceived risks. This is a strategic advantage we cannot ignore."""
        msg1.timestamp = None
        messages.append(msg1)

        # Critic's message
        msg2 = Mock()
        msg2.source = "critic"
        msg2.content = """While I acknowledge the potential benefits, we must address several critical concerns:

1. Security risks increase by 40% with remote access
2. Team cohesion and collaboration suffer - 60% of managers report decreased team effectiveness
3. Onboarding new employees becomes 3x more difficult
4. Company culture erosion is a documented risk
5. Not all roles are suitable for remote work

We need robust mitigation strategies before implementation."""
        msg2.timestamp = None
        messages.append(msg2)

        # Pragmatist's message
        msg3 = Mock()
        msg3.source = "pragmatist"
        msg3.content = """Building on both perspectives, I recommend a phased hybrid approach:

Phase 1 (3 months): Pilot with 25% of workforce, roles suited for remote work
Phase 2 (6 months): Implement security protocols and collaboration tools
Phase 3 (12 months): Full rollout with 60/40 office/remote split

This approach captures the benefits while mitigating the risks through controlled implementation."""
        msg3.timestamp = None
        messages.append(msg3)

        # Research Specialist's message
        msg4 = Mock()
        msg4.source = "research_specialist"
        msg4.content = """Based on current research data:

- GitLab's 2023 Remote Work Report: 82% of remote workers report better work-life balance
- Stanford study: 16% productivity increase in hybrid models
- Gartner research: 47% of organizations will allow full-time remote work post-2024
- McKinsey analysis: $2.4 trillion potential economic impact from remote work

The data supports a hybrid model as optimal for most organizations."""
        msg4.timestamp = None
        messages.append(msg4)

        # Innovator's message
        msg5 = Mock()
        msg5.source = "innovator"
        msg5.content = """Let's think beyond traditional remote work models:

1. Asynchronous-first design - optimize for global collaboration
2. Virtual reality meeting spaces for immersive collaboration
3. AI-powered productivity tracking and optimization
4. Outcome-based performance metrics rather than time-based
5. Digital nomad programs to attract top talent

This positions us as an innovation leader while solving traditional remote work challenges."""
        msg5.timestamp = None
        messages.append(msg5)

        mock_result.messages = messages
        return mock_result

    @pytest.mark.asyncio
    @patch("agent_expert_panel.agents.create_agent.create_agent")
    @patch("agent_expert_panel.panel.RichConsole")
    @patch("agent_expert_panel.panel.RoundRobinGroupChat")
    @patch("agent_expert_panel.panel.AssistantAgent")
    async def test_full_discussion_workflow(
        self,
        mock_assistant_agent,
        mock_group_chat,
        mock_rich_console,
        mock_create_agent,
        test_configs,
        realistic_task_result,
    ):
        """Test complete discussion workflow with all components."""
        from agent_expert_panel.models.consensus import Consensus

        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_agent.description = "Test agent"
        mock_agent._model_client = Mock()
        mock_create_agent.return_value = mock_agent

        # Mock the consensus and summary agents
        mock_consensus_agent = Mock()
        mock_summary_agent = Mock()
        mock_assistant_agent.side_effect = [mock_consensus_agent, mock_summary_agent]

        # Mock consensus agent response
        mock_consensus_result = Mock()
        mock_consensus_message = Mock()
        mock_consensus_message.content = Consensus(
            consensus_reached=False,  # Mixed opinions = no consensus
            summary="Mixed perspectives on remote work policy",
            participants=["advocate", "critic", "pragmatist"],
        )
        mock_consensus_result.messages = [mock_consensus_message]

        # Mock summary agent response
        mock_summary_result = Mock()
        mock_summary_message = Mock()
        mock_summary_message.content = "The panel discussed implementing a comprehensive remote work policy with mixed perspectives. The advocate highlighted productivity benefits and cost savings, while the critic raised security and team cohesion concerns. The pragmatist proposed a phased hybrid approach to balance benefits and risks."
        mock_summary_result.messages = [mock_summary_message]

        mock_group_chat_instance = Mock()
        mock_group_chat.return_value = mock_group_chat_instance
        mock_group_chat_instance.run_stream.return_value = AsyncMock()

        # Update realistic_task_result messages to have to_model_text and to_text methods
        for i, msg in enumerate(realistic_task_result.messages):
            msg.to_model_text = Mock(return_value=msg.content)
            msg.to_text = Mock(return_value=msg.content)
            msg.created_at = f"2024-01-01T00:0{i}:00Z"

        # Mock RichConsole to return the appropriate results for different calls
        mock_rich_console.side_effect = [
            realistic_task_result,  # First call for main discussion
            mock_consensus_result,  # Second call for consensus
            mock_summary_result,  # Third call for summary
        ]

        # Initialize panel and run full discussion
        panel = ExpertPanel(config_dir=test_configs)

        result = await panel.discuss(
            topic="Should our company implement a comprehensive remote work policy?",
            pattern=DiscussionPattern.ROUND_ROBIN,
            max_rounds=3,
        )

        # Verify complete result structure
        assert (
            result.topic
            == "Should our company implement a comprehensive remote work policy?"
        )
        assert result.discussion_pattern == DiscussionPattern.ROUND_ROBIN
        assert len(result.agents_participated) == 5  # All agents
        assert len(result.discussion_history) == 5  # All messages parsed
        assert isinstance(result.consensus_reached, bool)  # Should be a boolean
        assert result.consensus_reached is False  # Mixed opinions = no consensus
        assert len(result.final_recommendation) > 50  # Should have substantial content
        assert result.total_rounds == 1  # 5 messages / 5 agents = 1 round

        # Verify discussion history parsing
        history = result.discussion_history
        assert history[0]["speaker"] == "advocate"
        assert "productivity studies" in history[0]["content"].lower()
        assert history[1]["speaker"] == "critic"
        assert "security risks" in history[1]["content"].lower()
        assert history[2]["speaker"] == "pragmatist"
        assert "phased hybrid approach" in history[2]["content"].lower()

        # Verify recommendation synthesis contains actual content
        recommendation = result.final_recommendation
        assert isinstance(recommendation, str)
        assert len(recommendation) > 50  # Should have substantial content
        # The new logic uses the summary agent's response

    @pytest.mark.asyncio
    @patch("agent_expert_panel.agents.create_agent.create_agent")
    @patch("agent_expert_panel.panel.RichConsole")
    @patch("agent_expert_panel.panel.RoundRobinGroupChat")
    @patch("agent_expert_panel.panel.AssistantAgent")
    async def test_discussion_with_export(
        self,
        mock_assistant_agent,
        mock_group_chat,
        mock_rich_console,
        mock_create_agent,
        test_configs,
        realistic_task_result,
        tmp_path,
    ):
        """Test complete workflow including discussion and export."""
        from agent_expert_panel.models.consensus import Consensus

        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_agent.description = "Test agent"
        mock_agent._model_client = Mock()
        mock_create_agent.return_value = mock_agent

        # Mock the consensus and summary agents
        mock_consensus_agent = Mock()
        mock_summary_agent = Mock()
        mock_assistant_agent.side_effect = [mock_consensus_agent, mock_summary_agent]

        # Mock consensus agent response
        mock_consensus_result = Mock()
        mock_consensus_message = Mock()
        mock_consensus_message.content = Consensus(
            consensus_reached=True,
            summary="Consensus reached on technology adoption strategy",
            participants=[
                "advocate",
                "critic",
                "pragmatist",
                "research_specialist",
                "innovator",
            ],
        )
        mock_consensus_result.messages = [mock_consensus_message]

        # Mock summary agent response
        mock_summary_result = Mock()
        mock_summary_message = Mock()
        mock_summary_message.content = "The panel reached consensus on implementing a comprehensive technology adoption strategy with phased rollout and risk mitigation."
        mock_summary_result.messages = [mock_summary_message]

        mock_group_chat_instance = Mock()
        mock_group_chat.return_value = mock_group_chat_instance
        mock_group_chat_instance.run_stream.return_value = AsyncMock()

        # Update realistic_task_result messages to have to_model_text and to_text methods
        for i, msg in enumerate(realistic_task_result.messages):
            msg.to_model_text = Mock(return_value=msg.content)
            msg.to_text = Mock(return_value=msg.content)
            msg.created_at = f"2024-01-01T00:0{i}:00Z"

        # Mock RichConsole to return the appropriate results for different calls
        mock_rich_console.side_effect = [
            realistic_task_result,  # First call for main discussion
            mock_consensus_result,  # Second call for consensus
            mock_summary_result,  # Third call for summary
        ]

        # Run discussion
        panel = ExpertPanel(config_dir=test_configs)
        result = await panel.discuss(
            topic="Technology adoption strategy",
            pattern=DiscussionPattern.ROUND_ROBIN,
            max_rounds=2,
        )

        # Export results
        export_dir = tmp_path / "test_exports"
        saved_files = save_discussion(
            result=result, output_dir=export_dir, formats=["json", "markdown", "csv"]
        )

        # Verify exports
        assert len(saved_files) == 3
        assert "json" in saved_files
        assert "markdown" in saved_files
        assert "csv" in saved_files

        # Verify files exist and have content
        for format_name, file_path in saved_files.items():
            assert file_path.exists()
            assert file_path.stat().st_size > 0

        # Verify JSON content
        import json

        with open(saved_files["json"], "r") as f:
            json_data = json.load(f)
        assert json_data["topic"] == result.topic
        assert len(json_data["discussion_history"]) == 5

        # Verify Markdown content
        md_content = saved_files["markdown"].read_text()
        assert "# Expert Panel Discussion Report" in md_content
        assert result.topic in md_content
        assert "Round 1 - Advocate" in md_content

    @pytest.mark.asyncio
    @patch("agent_expert_panel.agents.create_agent.create_agent")
    @patch("agent_expert_panel.panel.RichConsole")
    @patch("agent_expert_panel.panel.RoundRobinGroupChat")
    @patch("agent_expert_panel.panel.AssistantAgent")
    async def test_partial_agent_participation(
        self,
        mock_assistant_agent,
        mock_group_chat,
        mock_rich_console,
        mock_create_agent,
        test_configs,
    ):
        """Test discussion with only subset of agents participating."""
        from agent_expert_panel.models.consensus import Consensus

        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_agent.description = "Test agent"
        mock_agent._model_client = Mock()
        mock_create_agent.return_value = mock_agent

        # Mock the consensus and summary agents
        mock_consensus_agent = Mock()
        mock_summary_agent = Mock()
        mock_assistant_agent.side_effect = [mock_consensus_agent, mock_summary_agent]

        # Mock consensus agent response
        mock_consensus_result = Mock()
        mock_consensus_message = Mock()
        mock_consensus_message.content = Consensus(
            consensus_reached=False,  # Two opposing views = no consensus
            summary="Mixed perspectives between advocate and critic",
            participants=["advocate", "critic"],
        )
        mock_consensus_result.messages = [mock_consensus_message]

        # Mock summary agent response
        mock_summary_result = Mock()
        mock_summary_message = Mock()
        mock_summary_message.content = "The advocate recommended implementation while the critic raised implementation risks."
        mock_summary_result.messages = [mock_summary_message]

        mock_group_chat_instance = Mock()
        mock_group_chat.return_value = mock_group_chat_instance
        mock_group_chat_instance.run_stream.return_value = AsyncMock()

        # Create task result with only 2 agents
        task_result = Mock(spec=TaskResult)
        messages = []

        msg1 = Mock()
        msg1.source = "advocate"
        msg1.content = "I recommend implementing this solution for maximum benefit."
        msg1.to_model_text = Mock(return_value=msg1.content)
        msg1.to_text = Mock(return_value=msg1.content)
        msg1.created_at = "2024-01-01T00:00:00Z"
        messages.append(msg1)

        msg2 = Mock()
        msg2.source = "critic"
        msg2.content = "However, we must carefully consider the implementation risks."
        msg2.to_model_text = Mock(return_value=msg2.content)
        msg2.to_text = Mock(return_value=msg2.content)
        msg2.created_at = "2024-01-01T00:01:00Z"
        messages.append(msg2)

        task_result.messages = messages

        # Mock RichConsole to return the appropriate results for different calls
        mock_rich_console.side_effect = [
            task_result,  # First call for main discussion
            mock_consensus_result,  # Second call for consensus
            mock_summary_result,  # Third call for summary
        ]

        # Run discussion with subset of agents
        panel = ExpertPanel(config_dir=test_configs)
        result = await panel.discuss(
            topic="Limited discussion test",
            pattern=DiscussionPattern.ROUND_ROBIN,
            max_rounds=2,
            participants=["advocate", "critic"],
        )

        # Verify results reflect partial participation
        assert result.agents_participated == ["advocate", "critic"]
        assert len(result.discussion_history) == 2
        assert result.discussion_history[0]["speaker"] == "advocate"
        assert result.discussion_history[1]["speaker"] == "critic"

    @pytest.mark.asyncio
    @patch("agent_expert_panel.agents.create_agent.create_agent")
    async def test_quick_consensus_integration(self, mock_create_agent, test_configs):
        """Test quick consensus feature integration."""
        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_create_agent.return_value = mock_agent

        panel = ExpertPanel(config_dir=test_configs)

        # Mock the discuss method to return a simple result
        with patch.object(panel, "discuss") as mock_discuss:
            from agent_expert_panel.models import PanelResult, DiscussionPattern

            mock_result = PanelResult(
                topic="Quick test question",
                discussion_pattern=DiscussionPattern.ROUND_ROBIN,
                agents_participated=["advocate", "critic", "pragmatist"],
                discussion_history=[],
                consensus_reached=True,
                final_recommendation="Yes, this is a good approach based on our analysis.",
                total_rounds=1,
            )
            mock_discuss.return_value = mock_result

            result = await panel.quick_consensus("Is this a good approach?")

            assert result == "Yes, this is a good approach based on our analysis."
            mock_discuss.assert_called_once_with(
                topic="Is this a good approach?",
                pattern=DiscussionPattern.ROUND_ROBIN,
                max_rounds=1,
            )

    @pytest.mark.asyncio
    @patch("agent_expert_panel.agents.create_agent.create_agent")
    async def test_error_handling_integration(self, mock_create_agent, test_configs):
        """Test error handling throughout the system."""
        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_create_agent.return_value = mock_agent

        panel = ExpertPanel(config_dir=test_configs)

        # Test with empty/malformed TaskResult
        with patch("agent_expert_panel.panel.RichConsole") as mock_console:
            with patch("agent_expert_panel.panel.RoundRobinGroupChat"):
                # Return a TaskResult with no messages
                empty_result = Mock(spec=TaskResult)
                empty_result.messages = []
                mock_console.return_value = empty_result

                result = await panel.discuss(
                    topic="Error handling test",
                    pattern=DiscussionPattern.ROUND_ROBIN,
                    max_rounds=1,
                )

                # Should still return a valid result with defaults
                assert isinstance(result.final_recommendation, str)
                assert isinstance(result.consensus_reached, bool)
                assert isinstance(result.discussion_history, list)
                assert result.total_rounds >= 0

    def test_config_loading_integration(self, test_configs):
        """Test that all agent configurations load correctly."""
        with patch("agent_expert_panel.panel.create_agent") as mock_create:
            mock_create.return_value = Mock(spec=AssistantAgent)

            panel = ExpertPanel(config_dir=test_configs)

            # Verify all 5 agents were loaded
            assert len(panel.agents) == 5
            expected_agents = [
                "advocate",
                "critic",
                "pragmatist",
                "research_specialist",
                "innovator",
            ]
            for agent_name in expected_agents:
                assert agent_name in panel.agents

            # Verify create_agent was called for each
            assert mock_create.call_count == 5

            # Verify descriptions are accessible
            descriptions = panel.get_agent_descriptions()
            assert len(descriptions) == 5
            for agent_name in expected_agents:
                assert agent_name in descriptions
                assert len(descriptions[agent_name]) > 0
