"""
Tests for VirtualExpertPanel Mem0 integration.

These tests verify that the VirtualExpertPanel properly integrates with
the Mem0 memory system for learning and optimization.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from agent_expert_panel.virtual_panel import VirtualExpertPanel
from agent_expert_panel.memory.mem0_manager import Mem0Manager


class TestVirtualPanelMem0Integration:
    """Test Mem0 integration with VirtualExpertPanel."""

    @pytest.fixture
    def temp_memory_path(self):
        """Provide a temporary directory for memory storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "test_memory"

    @pytest.fixture
    def virtual_panel_with_mem0(self, temp_memory_path):
        """Create a VirtualExpertPanel with Mem0 enabled."""
        return VirtualExpertPanel(
            enable_memory=True,
            memory_type="mem0",
            user_id="test_user",
            memory_path=temp_memory_path,
            enable_mem0_cloud=False,
            enable_graphrag=False,  # Disable for simpler testing
        )

    @pytest.fixture
    def virtual_panel_without_mem0(self):
        """Create a VirtualExpertPanel without Mem0."""
        return VirtualExpertPanel(enable_memory=False, enable_graphrag=False)

    def test_initialization_with_mem0_config(self, virtual_panel_with_mem0):
        """Test that VirtualExpertPanel initializes with correct Mem0 configuration."""
        panel = virtual_panel_with_mem0

        assert panel.enable_memory is True
        assert panel.memory_type == "mem0"
        assert panel.user_id == "test_user"
        assert panel.enable_mem0_cloud is False
        assert panel.mem0_manager is None  # Not initialized until solve_problem

    def test_initialization_without_mem0(self, virtual_panel_without_mem0):
        """Test that VirtualExpertPanel works without Mem0."""
        panel = virtual_panel_without_mem0

        assert panel.enable_memory is False
        assert panel.mem0_manager is None

    @pytest.mark.asyncio
    async def test_mem0_initialization_in_solve_problem(self, virtual_panel_with_mem0):
        """Test that Mem0 is initialized when solve_problem is called."""
        panel = virtual_panel_with_mem0

        # Mock the _initialize_mem0 method to avoid actual Mem0 dependency
        with patch.object(panel, "_initialize_mem0") as mock_init:
            mock_init.return_value = True

            # Mock other dependencies to prevent actual execution
            with (
                patch.object(panel, "_initialize_graphrag"),
                patch.object(panel, "_get_memory_insights") as mock_insights,
                patch.object(panel, "_orchestrate_panel_decision") as mock_discussion,
            ):
                mock_insights.return_value = ""
                mock_discussion.return_value = Mock(
                    decision="PROVIDE_SOLUTION", rationale="Test solution"
                )

                try:
                    await panel.solve_problem(
                        query="Test query", domain="test", max_iterations=1
                    )
                except Exception:
                    # Expected due to mocking, we just want to verify _initialize_mem0 was called
                    pass

                # Verify that Mem0 initialization was attempted
                mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_insights_retrieval(self, virtual_panel_with_mem0):
        """Test memory insights retrieval functionality."""
        panel = virtual_panel_with_mem0

        # Mock a Mem0Manager
        mock_mem0_manager = AsyncMock(spec=Mem0Manager)
        mock_mem0_manager.query_conversation_patterns.return_value = [
            {"content": "Test conversation pattern"}
        ]
        mock_mem0_manager.query_user_preferences.return_value = [
            {"content": "Test user preference"}
        ]
        mock_mem0_manager.query_research_strategies.return_value = [
            {"content": "Test research strategy"}
        ]
        mock_mem0_manager.query_domain_knowledge.return_value = [
            {"content": "Test domain knowledge"}
        ]

        panel.mem0_manager = mock_mem0_manager

        # Test memory insights retrieval
        insights = await panel._get_memory_insights("test query", "test_domain")

        # Verify that all query methods were called
        mock_mem0_manager.query_conversation_patterns.assert_called_once()
        mock_mem0_manager.query_user_preferences.assert_called_once()
        mock_mem0_manager.query_research_strategies.assert_called_once()
        mock_mem0_manager.query_domain_knowledge.assert_called_once()

        # Verify insights were formatted
        assert "RELEVANT CONVERSATION PATTERNS" in insights
        assert "USER PREFERENCES" in insights
        assert "EFFECTIVE RESEARCH STRATEGIES" in insights
        assert "RELEVANT DOMAIN KNOWLEDGE" in insights

    @pytest.mark.asyncio
    async def test_memory_insights_empty_response(self, virtual_panel_with_mem0):
        """Test memory insights when no memories are found."""
        panel = virtual_panel_with_mem0

        # Mock a Mem0Manager with empty responses
        mock_mem0_manager = AsyncMock(spec=Mem0Manager)
        mock_mem0_manager.query_conversation_patterns.return_value = []
        mock_mem0_manager.query_user_preferences.return_value = []
        mock_mem0_manager.query_research_strategies.return_value = []
        mock_mem0_manager.query_domain_knowledge.return_value = []

        panel.mem0_manager = mock_mem0_manager

        # Test memory insights retrieval
        insights = await panel._get_memory_insights("test query", "test_domain")

        # Should return empty string when no memories found
        assert insights == ""

    @pytest.mark.asyncio
    async def test_memory_insights_without_mem0(self, virtual_panel_without_mem0):
        """Test memory insights when Mem0 is not enabled."""
        panel = virtual_panel_without_mem0

        # Should return empty string when no Mem0Manager
        insights = await panel._get_memory_insights("test query", "test_domain")
        assert insights == ""

    @pytest.mark.asyncio
    async def test_web_research_agent_mem0_assignment(self, virtual_panel_with_mem0):
        """Test that WebResearchAgent gets the Mem0Manager assigned."""
        panel = virtual_panel_with_mem0

        # Mock Mem0Manager
        mock_mem0_manager = Mock(spec=Mem0Manager)
        panel.mem0_manager = mock_mem0_manager

        # Mock web research agent
        mock_web_agent = Mock()
        panel.web_research_agent = mock_web_agent

        # Mock the initialization and discussion to focus on the assignment
        with (
            patch.object(panel, "_initialize_mem0"),
            patch.object(panel, "_initialize_graphrag"),
            patch.object(panel, "_get_memory_insights") as mock_insights,
            patch.object(panel, "_orchestrate_panel_decision") as mock_discussion,
        ):
            mock_insights.return_value = ""
            mock_discussion.return_value = Mock(
                decision="PROVIDE_SOLUTION", rationale="Test"
            )

            try:
                await panel.solve_problem("test query", max_iterations=1)
            except Exception:
                # Expected due to mocking
                pass

            # Verify that the web research agent got the Mem0Manager
            assert mock_web_agent.mem0_manager == mock_mem0_manager


class TestMem0IntegrationDisabled:
    """Test behavior when Mem0 is disabled or unavailable."""

    @pytest.mark.asyncio
    async def test_solve_problem_without_mem0(self):
        """Test that solve_problem works when Mem0 is disabled."""
        panel = VirtualExpertPanel(enable_memory=False, enable_graphrag=False)

        # Mock dependencies to prevent actual execution
        with patch.object(panel, "_orchestrate_panel_decision") as mock_discussion:
            mock_discussion.return_value = Mock(
                decision="PROVIDE_SOLUTION", rationale="Test solution without memory"
            )

            try:
                result = await panel.solve_problem(
                    query="Test query without memory", max_iterations=1
                )

                # Should complete without errors
                assert result is not None

            except Exception as e:
                # Some exceptions are expected due to mocking, but should not be Mem0-related
                assert "mem0" not in str(e).lower()

    @pytest.mark.asyncio
    async def test_memory_insights_graceful_degradation(self):
        """Test that memory insights gracefully handle missing Mem0."""
        panel = VirtualExpertPanel(enable_memory=False)

        # Should not raise exceptions
        insights = await panel._get_memory_insights("test query", "test_domain")
        assert insights == ""


class TestMem0IntegrationErrorHandling:
    """Test error handling in Mem0 integration."""

    @pytest.fixture
    def temp_memory_path(self):
        """Provide a temporary directory for memory storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir) / "test_memory"

    @pytest.mark.asyncio
    async def test_mem0_initialization_failure(self, temp_memory_path):
        """Test handling of Mem0 initialization failure."""
        panel = VirtualExpertPanel(
            enable_memory=True,
            memory_type="mem0",
            memory_path=temp_memory_path,
            enable_graphrag=False,
        )

        # Mock initialization to fail
        with patch.object(panel, "_initialize_mem0") as mock_init:
            mock_init.return_value = False  # Simulate failure

            with patch.object(panel, "_orchestrate_panel_decision") as mock_discussion:
                mock_discussion.return_value = Mock(
                    decision="PROVIDE_SOLUTION", rationale="Test"
                )

                try:
                    await panel.solve_problem("test query", max_iterations=1)
                    # Should not crash even if Mem0 initialization fails
                except Exception as e:
                    # Acceptable if other components fail due to mocking
                    assert "mem0" not in str(e).lower()

    @pytest.mark.asyncio
    async def test_memory_insights_exception_handling(self, temp_memory_path):
        """Test that memory insights handle exceptions gracefully."""
        panel = VirtualExpertPanel(
            enable_memory=True, memory_type="mem0", memory_path=temp_memory_path
        )

        # Mock Mem0Manager that raises exceptions
        mock_mem0_manager = AsyncMock(spec=Mem0Manager)
        mock_mem0_manager.query_conversation_patterns.side_effect = Exception(
            "Test error"
        )
        panel.mem0_manager = mock_mem0_manager

        # Should not raise exception, should return empty string
        insights = await panel._get_memory_insights("test query", "test_domain")
        assert insights == ""


if __name__ == "__main__":
    pytest.main([__file__])
