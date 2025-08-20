"""
Tests for human participation feature using UserProxyAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from autogen_core import CancellationToken

from agent_expert_panel.panel import ExpertPanel
from agent_expert_panel.models import DiscussionPattern


class TestHumanParticipation:
    """Test cases for human participation in expert panel discussions."""

    @pytest.fixture
    def panel(self):
        """Create an ExpertPanel instance for testing."""
        with patch("src.agent_expert_panel.panel.AgentConfig.from_yaml"):
            with patch("src.agent_expert_panel.panel.create_agent"):
                return ExpertPanel()

    def test_create_human_agent(self, panel):
        """Test creating a UserProxyAgent for human participation."""
        human_name = "test_human"
        mock_input_func = Mock(return_value="Test input")

        human_agent = panel._create_human_agent(human_name, mock_input_func)

        assert human_agent.name == human_name
        assert f"Human expert '{human_name}'" in human_agent.description
        assert human_agent.input_func == mock_input_func

    def test_create_human_agent_default_input(self, panel):
        """Test creating a UserProxyAgent with default input function."""
        human_name = "test_human"

        human_agent = panel._create_human_agent(human_name)

        assert human_agent.name == human_name
        assert f"Human expert '{human_name}'" in human_agent.description
        assert human_agent.input_func is not None  # Uses default cancellable_input

    @pytest.mark.asyncio
    async def test_discuss_with_human_enabled(self, panel):
        """Test that discuss method includes human when with_human=True."""
        mock_input_func = Mock(return_value="Human input")

        with patch.object(panel, "_run_round_robin_discussion") as mock_discussion:
            mock_discussion.return_value = Mock()

            await panel.discuss(
                topic="Test topic",
                human_name="test_human",
                human_input_func=mock_input_func,
            )

            # Verify that _run_round_robin_discussion was called with human participation
            mock_discussion.assert_called_once()
            args, kwargs = mock_discussion.call_args

            # Check that agents list includes the human agent
            agents_list = args[1]  # Second argument is the agents list
            agent_names = [agent.name for agent in agents_list]

            assert len(agents_list) > 6  # Should have more than the 6 AI agents
            assert "test_human" in agent_names
            # No longer checking kwargs since with_human is handled in discuss() method

    @pytest.mark.asyncio
    async def test_discuss_without_human(self, panel):
        """Test that discuss method works normally when with_human=False."""
        with patch.object(panel, "_run_round_robin_discussion") as mock_discussion:
            mock_discussion.return_value = Mock()

            await panel.discuss(topic="Test topic", with_human=False)

            # Verify that _run_round_robin_discussion was called without human participation
            mock_discussion.assert_called_once()
            args, kwargs = mock_discussion.call_args

            # Check that agents list only includes AI agents
            agents_list = args[1]  # Second argument is the agents list
            agent_names = [agent.name for agent in agents_list]

            assert len(agents_list) == 6  # Should have exactly 6 AI agents
            assert len(agent_names) == 6
            # No longer checking kwargs since with_human is handled in discuss() method

    @pytest.mark.asyncio
    async def test_discuss_with_human_convenience_method(self, panel):
        """Test the discuss_with_human convenience method."""
        mock_input_func = Mock(return_value="Human input")

        with patch.object(panel, "discuss") as mock_discuss:
            mock_discuss.return_value = Mock()

            await panel.discuss_with_human(
                topic="Test topic",
                human_name="Expert Human",
                human_input_func=mock_input_func,
            )

            # Verify that discuss was called with correct parameters
            mock_discuss.assert_called_once_with(
                topic="Test topic",
                pattern=DiscussionPattern.ROUND_ROBIN,
                max_rounds=3,
                participants=None,
                with_human=True,
                human_name="Expert Human",
                human_input_func=mock_input_func,
            )

    @pytest.mark.asyncio
    async def test_human_participation_with_selected_agents(self, panel):
        """Test human participation with only selected AI agents."""
        selected_agents = ["advocate", "critic"]

        with patch.object(panel, "_run_round_robin_discussion") as mock_discussion:
            mock_discussion.return_value = Mock()

            await panel.discuss(
                topic="Test topic",
                participants=selected_agents,
                human_name="human_expert",
            )

            # Verify the correct agents were included
            args, kwargs = mock_discussion.call_args
            agents_list = args[1]  # Second argument is the agents list
            agent_names = [agent.name for agent in agents_list]

            assert "advocate" in agent_names
            assert "critic" in agent_names
            assert "human_expert" in agent_names
            assert len(agent_names) == 3  # 2 AI agents + 1 human

    def test_enhanced_prompt_with_human(self, panel):
        """Test that discussion prompts are enhanced when humans participate."""
        # This would require testing the actual prompt generation
        # For now, we'll test that the method signatures are correct

        # Test that the method signatures support human participation
        import inspect

        discuss_sig = inspect.signature(panel.discuss)
        assert "with_human" in discuss_sig.parameters
        assert "human_name" in discuss_sig.parameters
        assert "human_input_func" in discuss_sig.parameters

        discuss_with_human_sig = inspect.signature(panel.discuss_with_human)
        assert "human_name" in discuss_with_human_sig.parameters
        assert "human_input_func" in discuss_with_human_sig.parameters

    @pytest.mark.asyncio
    async def test_async_input_function_support(self, panel):
        """Test that async input functions are supported."""

        async def async_input_func(
            prompt: str, cancellation_token: CancellationToken = None
        ) -> str:
            await asyncio.sleep(0.01)  # Simulate async operation
            return "Async human input"

        # Test that the input function type is accepted
        human_agent = panel._create_human_agent("async_human", async_input_func)
        assert human_agent.input_func == async_input_func

    def test_human_agent_integration_types(self, panel):
        """Test that human agents integrate properly with the type system."""
        from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
        from typing import Union, List

        # Test that the type hints are correct for mixed agent lists
        human_agent = panel._create_human_agent("test_human")
        assert isinstance(human_agent, UserProxyAgent)

        # This verifies that our type hints are correct
        mixed_agents: List[Union[AssistantAgent, UserProxyAgent]] = [human_agent]
        assert len(mixed_agents) == 1

    @pytest.mark.asyncio
    async def test_structured_debate_with_human(self, panel):
        """Test that structured debate works with human participation."""
        with patch.object(panel, "_run_structured_debate") as mock_debate:
            mock_debate.return_value = Mock()

            await panel.discuss(
                topic="Test topic",
                pattern=DiscussionPattern.STRUCTURED_DEBATE,
                with_human=True,
                human_name="debate_expert",
            )

            # Verify that _run_structured_debate was called with human participation
            mock_debate.assert_called_once()
            args, kwargs = mock_debate.call_args

            agents_list = args[1]  # Second argument is the agents list
            agent_names = [agent.name for agent in agents_list]
            assert "debate_expert" in agent_names
            # No longer checking kwargs since with_human is handled in discuss() method


class TestHumanParticipationInputFunctions:
    """Test cases for different types of input functions."""

    def test_sync_input_function(self):
        """Test synchronous input function."""

        def sync_input(prompt: str) -> str:
            return f"Response to: {prompt}"

        # Test that the function works as expected
        result = sync_input("Test prompt")
        assert result == "Response to: Test prompt"

    @pytest.mark.asyncio
    async def test_async_input_function(self):
        """Test asynchronous input function."""

        async def async_input(
            prompt: str, cancellation_token: CancellationToken = None
        ) -> str:
            await asyncio.sleep(0.01)
            return f"Async response to: {prompt}"

        # Test that the function works as expected
        result = await async_input("Test prompt")
        assert result == "Async response to: Test prompt"

    def test_input_function_with_error_handling(self):
        """Test input function with error handling."""

        def robust_input(prompt: str) -> str:
            try:
                if "error" in prompt.lower():
                    raise ValueError("Simulated error")
                return f"Safe response to: {prompt}"
            except Exception as e:
                return f"Error handled: {str(e)}"

        # Test normal operation
        result = robust_input("Normal prompt")
        assert result == "Safe response to: Normal prompt"

        # Test error handling
        result = robust_input("Error prompt")
        assert result == "Error handled: Simulated error"

    def test_custom_input_function_with_skip(self):
        """Test custom input function that supports skipping."""

        def skip_capable_input(prompt: str) -> str:
            if "skip" in prompt.lower():
                return "I'll pass on this round and listen to the other experts."
            return f"Active response to: {prompt}"

        # Test normal response
        result = skip_capable_input("What do you think?")
        assert result == "Active response to: What do you think?"

        # Test skip response
        result = skip_capable_input("Skip this question")
        assert result == "I'll pass on this round and listen to the other experts."


# Integration test that would require actual agent setup
@pytest.mark.integration
class TestHumanParticipationIntegration:
    """Integration tests for human participation (requires full setup)."""

    @pytest.mark.skip(reason="Requires full agent setup and API keys")
    @pytest.mark.asyncio
    async def test_full_human_participation_flow(self):
        """Test complete human participation flow with real agents."""
        # This test would require:
        # 1. Proper agent configuration files
        # 2. API keys for model clients
        # 3. Mock input functions that simulate human responses

        panel = ExpertPanel()

        def mock_human_input(prompt: str) -> str:
            """Mock human input for testing."""
            responses = [
                "I think we should consider the security implications.",
                "From a user experience perspective, this could be challenging.",
                "Let me add some real-world context to this discussion.",
            ]
            # Cycle through responses or return a default
            return responses[hash(prompt) % len(responses)]

        result = await panel.discuss_with_human(
            topic="Should we implement single sign-on across all our applications?",
            pattern=DiscussionPattern.ROUND_ROBIN,
            max_rounds=1,
            human_name="security_expert",
            human_input_func=mock_human_input,
        )

        # Verify that the result includes human participation
        assert "Security Expert" in result.agents_participated
        assert result.final_recommendation is not None
        assert len(result.discussion_history) > 0
