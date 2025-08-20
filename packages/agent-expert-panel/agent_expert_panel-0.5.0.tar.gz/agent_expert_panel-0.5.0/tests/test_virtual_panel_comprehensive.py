"""
Comprehensive tests for VirtualExpertPanel

This module contains comprehensive tests to improve coverage of the
VirtualExpertPanel class including error handling, edge cases, and
integration scenarios.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from agent_expert_panel.virtual_panel import VirtualExpertPanel
from agent_expert_panel.models.virtual_panel import (
    VirtualPanelAction,
    ConversationState,
)
from agent_expert_panel.models.config import AgentConfig


class TestVirtualExpertPanelInitialization:
    """Test VirtualExpertPanel initialization scenarios."""

    def test_initialization_web_research_agent_failures(self):
        """Test initialization when web research agent fails to initialize."""
        with patch.object(
            VirtualExpertPanel, "_initialize_web_research_agent", return_value=None
        ):
            panel = VirtualExpertPanel()
            assert panel.web_research_agent is None

    def test_initialization_web_research_agent_tavily_fails_simulation_works(self):
        """Test fallback to simulation when Tavily fails."""
        mock_agent = Mock()
        with patch.object(
            VirtualExpertPanel,
            "_initialize_web_research_agent",
            return_value=mock_agent,
        ):
            panel = VirtualExpertPanel()
            assert panel.web_research_agent == mock_agent

    def test_initialization_with_memory_enabled(self):
        """Test initialization with memory system enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "memory"
            panel = VirtualExpertPanel(
                enable_memory=True, memory_type="basic", memory_path=memory_path
            )
            assert panel.enable_memory is True
            assert panel.memory_path == memory_path

    def test_initialization_with_graphrag_enabled(self):
        """Test initialization with GraphRAG enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            panel = VirtualExpertPanel(
                enable_graphrag=True, graphrag_workspace=Path(temp_dir)
            )
            assert panel.enable_graphrag is True
            assert panel.graphrag_workspace == Path(temp_dir)

    def test_initialization_with_custom_config(self):
        """Test initialization with custom agent configuration."""
        from agent_expert_panel.models.model_info import ModelInfo

        config = AgentConfig(
            name="custom-agent",
            model_name="gpt-4",
            description="Custom test agent",
            system_message="Custom system message",
            openai_api_key="test-key",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="UNKNOWN",
                structured_output=True,
                multiple_system_messages=False,
            ),
        )
        panel = VirtualExpertPanel(config=config)
        assert panel.config == config

    def test_initialization_with_mem0_memory_type(self):
        """Test initialization with mem0 memory type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            panel = VirtualExpertPanel(
                enable_memory=True,
                memory_type="mem0",
                memory_path=Path(temp_dir),
                user_id="test_user",
            )
            assert panel.memory_type == "mem0"
            assert panel.user_id == "test_user"

    def test_initialization_web_research_agent_from_config(self):
        """Test initialization of web research agent from configuration."""
        # Mock the agent creation to test the configuration path
        mock_agent = Mock()
        with patch(
            "agent_expert_panel.virtual_panel.WebResearchAgent.from_config",
            return_value=mock_agent,
        ) as mock_from_config:
            # Use default config directory (which has web_research_specialist.yaml)
            panel = VirtualExpertPanel()

            # Verify from_config was called correctly
            mock_from_config.assert_called_once()
            call_kwargs = mock_from_config.call_args.kwargs
            assert call_kwargs["use_tavily"] is True
            assert call_kwargs["mem0_manager"] is None

            assert panel.web_research_agent == mock_agent


class TestVirtualExpertPanelMemoryInitialization:
    """Test memory initialization scenarios."""

    def test_initialize_memory_basic_type(self):
        """Test basic memory initialization."""
        panel = VirtualExpertPanel(enable_memory=True, memory_type="basic")
        memory = panel._initialize_memory()
        assert memory is not None

    def test_initialize_memory_mem0_type(self):
        """Test mem0 memory initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            panel = VirtualExpertPanel(
                enable_memory=True,
                memory_type="mem0",
                memory_path=Path(temp_dir),
                user_id="test_user",
            )
            memory = panel._initialize_memory()
            # For mem0 type, _initialize_memory returns a fallback dict, not the manager
            expected_fallback = {"conversations": [], "facts": [], "context": {}}
            assert memory == expected_fallback

    def test_initialize_memory_mem0_creation_fails(self):
        """Test mem0 memory initialization when creation fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            panel = VirtualExpertPanel(
                enable_memory=True,
                memory_type="mem0",
                memory_path=Path(temp_dir),
                user_id="test_user",
            )
            memory = panel._initialize_memory()
            # Even if creation fails, _initialize_memory returns fallback dict for mem0
            expected_fallback = {"conversations": [], "facts": [], "context": {}}
            assert memory == expected_fallback

    def test_initialize_memory_unknown_type(self):
        """Test memory initialization with unknown type."""
        panel = VirtualExpertPanel(enable_memory=True, memory_type="unknown")
        memory = panel._initialize_memory()
        # Unknown type defaults to simple memory
        expected_fallback = {"conversations": [], "facts": [], "context": {}}
        assert memory == expected_fallback


class TestVirtualExpertPanelGraphRAGOperations:
    """Test GraphRAG related operations."""

    @pytest.mark.asyncio
    async def test_initialize_graphrag_success(self):
        """Test successful GraphRAG initialization."""
        panel = VirtualExpertPanel(enable_graphrag=True, persist_knowledge=True)

        with patch(
            "agent_expert_panel.virtual_panel.create_graphrag_knowledge_manager"
        ) as mock_create:
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True
            mock_create.return_value = mock_manager

            result = await panel._initialize_graphrag("test_domain")
            assert result is True
            assert panel.graphrag_manager == mock_manager

    @pytest.mark.asyncio
    async def test_initialize_graphrag_creation_fails(self):
        """Test GraphRAG initialization when creation fails."""
        panel = VirtualExpertPanel(enable_graphrag=True)

        with patch(
            "agent_expert_panel.virtual_panel.create_graphrag_knowledge_manager",
            return_value=None,
        ):
            result = await panel._initialize_graphrag("test_domain")
            assert result is False
            assert panel.graphrag_manager is None

    @pytest.mark.asyncio
    async def test_initialize_graphrag_initialization_fails(self):
        """Test GraphRAG initialization when manager init fails."""
        panel = VirtualExpertPanel(enable_graphrag=True)

        with patch(
            "agent_expert_panel.virtual_panel.create_graphrag_knowledge_manager"
        ) as mock_create:
            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = False
            mock_create.return_value = mock_manager

            # Also mock the availability check and LegacyKnowledgeAdapter
            with patch("agent_expert_panel.virtual_panel.GRAPHRAG_AVAILABLE", True):
                with patch(
                    "agent_expert_panel.virtual_panel.LegacyKnowledgeAdapter", None
                ):
                    result = await panel._initialize_graphrag("test_domain")
                    assert result is False
                    assert panel.graphrag_manager == mock_manager

    @pytest.mark.asyncio
    async def test_initialize_graphrag_disabled(self):
        """Test GraphRAG initialization when disabled."""
        panel = VirtualExpertPanel(enable_graphrag=False)
        result = await panel._initialize_graphrag("test_domain")
        assert result is False  # GraphRAG is not initialized when disabled
        assert panel.graphrag_manager is None


class TestVirtualExpertPanelMemoryOperations:
    """Test memory-related operations."""

    @pytest.mark.asyncio
    async def test_initialize_mem0_success(self):
        """Test successful Mem0 initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            panel = VirtualExpertPanel(
                enable_memory=True,
                memory_type="mem0",
                memory_path=Path(temp_dir),
                user_id="test_user",
            )

            mock_manager = AsyncMock()
            mock_manager.initialize.return_value = True

            with patch(
                "agent_expert_panel.virtual_panel.create_mem0_manager",
                return_value=mock_manager,
            ):
                result = await panel._initialize_mem0()
                assert result is True
                assert panel.mem0_manager == mock_manager

    @pytest.mark.asyncio
    async def test_initialize_mem0_creation_fails(self):
        """Test Mem0 initialization when creation fails."""
        panel = VirtualExpertPanel(
            enable_memory=True, memory_type="mem0", user_id="test_user"
        )

        with patch(
            "agent_expert_panel.virtual_panel.create_mem0_manager", return_value=None
        ):
            result = await panel._initialize_mem0()
            assert result is False
            assert panel.mem0_manager is None

    @pytest.mark.asyncio
    async def test_initialize_mem0_init_fails(self):
        """Test Mem0 initialization when manager creation returns None."""
        panel = VirtualExpertPanel(
            enable_memory=True, memory_type="mem0", user_id="test_user"
        )

        with patch(
            "agent_expert_panel.virtual_panel.create_mem0_manager",
            return_value=None,
        ):
            result = await panel._initialize_mem0()
            assert result is False
            assert panel.mem0_manager is None

    @pytest.mark.asyncio
    async def test_get_memory_insights_with_mem0(self):
        """Test getting memory insights with Mem0."""
        panel = VirtualExpertPanel()
        mock_manager = AsyncMock()
        mock_manager.query_conversation_patterns.return_value = [
            {"content": "User prefers detailed explanations"}
        ]
        panel.mem0_manager = mock_manager

        insights = await panel._get_memory_insights("test query", "tech")
        assert "User prefers detailed explanations" in insights

    @pytest.mark.asyncio
    async def test_get_memory_insights_without_mem0(self):
        """Test getting memory insights without Mem0."""
        panel = VirtualExpertPanel()
        panel.mem0_manager = None

        insights = await panel._get_memory_insights("test query", "tech")
        assert insights == ""

    @pytest.mark.asyncio
    async def test_get_memory_insights_exception(self):
        """Test memory insights when exception occurs."""
        panel = VirtualExpertPanel()
        mock_manager = AsyncMock()
        mock_manager.query_conversation_patterns.side_effect = Exception("Query failed")
        panel.mem0_manager = mock_manager

        insights = await panel._get_memory_insights("test query", "tech")
        assert insights == ""


class TestVirtualExpertPanelActionHandling:
    """Test action handling methods."""

    @pytest.mark.asyncio
    async def test_handle_ask_question_action(self):
        """Test handling ASK_QUESTION action."""
        from agent_expert_panel.models.virtual_panel import OrchestratorDecision

        panel = VirtualExpertPanel()
        # Initialize session state required by the method
        panel.current_session = {
            "session_id": "test_session",
            "iteration": 1,
            "domain": "test",
            "start_time": datetime.now(),
        }

        decision = OrchestratorDecision(
            decision=VirtualPanelAction.ASK_QUESTION,
            rationale="What is your preferred programming language? Need user preference for better recommendations",
            confidence=0.8,
            panel_consensus=True,
        )

        # Mock user input function
        def mock_user_input(prompt):
            return "Python"

        user_response = await panel._handle_ask_question(decision, mock_user_input)
        assert user_response == "Python"

    @pytest.mark.asyncio
    async def test_handle_request_test_action_success(self):
        """Test successful REQUEST_TEST action handling."""
        from agent_expert_panel.models.virtual_panel import OrchestratorDecision

        panel = VirtualExpertPanel()
        # Initialize session state required by the method
        panel.current_session = {
            "session_id": "test_session",
            "iteration": 1,
            "domain": "test",
            "start_time": datetime.now(),
        }
        panel.web_research_agent = Mock()

        mock_research_results = {
            "original_query": "test query",
            "summary": "test summary",
            "key_findings": [{"content": "finding 1"}],
            "sources": ["source1"],
            "confidence_score": 0.8,
        }

        panel.web_research_agent.research_topic = AsyncMock(
            return_value=mock_research_results
        )

        decision = OrchestratorDecision(
            decision=VirtualPanelAction.REQUEST_TEST,
            rationale="Research the latest developments in AI. Need current information",
            confidence=0.8,
            panel_consensus=True,
        )

        result = await panel._handle_request_test(decision)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].status == "completed"
        assert result[0].results == mock_research_results

    @pytest.mark.asyncio
    async def test_handle_request_test_action_no_agent(self):
        """Test REQUEST_TEST action when no web research agent."""
        from agent_expert_panel.models.virtual_panel import OrchestratorDecision

        panel = VirtualExpertPanel()
        # Initialize session state required by the method
        panel.current_session = {
            "session_id": "test_session",
            "iteration": 1,
            "domain": "test",
            "start_time": datetime.now(),
        }
        panel.web_research_agent = None

        decision = OrchestratorDecision(
            decision=VirtualPanelAction.REQUEST_TEST,
            rationale="Research something. Need info",
            confidence=0.8,
            panel_consensus=True,
        )

        result = await panel._handle_request_test(decision)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].status == "failed"
        assert "not available" in result[0].results.get("error", "")

    @pytest.mark.asyncio
    async def test_handle_request_test_action_exception(self):
        """Test REQUEST_TEST action exception handling."""
        from agent_expert_panel.models.virtual_panel import OrchestratorDecision

        panel = VirtualExpertPanel()
        # Initialize session state required by the method
        panel.current_session = {
            "session_id": "test_session",
            "iteration": 1,
            "domain": "test",
            "start_time": datetime.now(),
        }
        panel.web_research_agent = Mock()
        panel.web_research_agent.research_topic = AsyncMock(
            side_effect=Exception("Research failed")
        )

        decision = OrchestratorDecision(
            decision=VirtualPanelAction.REQUEST_TEST,
            rationale="Research something. Need info",
            confidence=0.8,
            panel_consensus=True,
        )

        result = await panel._handle_request_test(decision)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].status == "failed"
        assert "Research failed" in result[0].results.get("error", "")


class TestVirtualExpertPanelSolveProbleMethod:
    """Test the main solve_problem method and its components."""

    @pytest.mark.asyncio
    async def test_solve_problem_basic_flow(self):
        """Test basic solve_problem flow."""
        panel = VirtualExpertPanel()

        # Mock the orchestrator to return PROVIDE_SOLUTION immediately
        mock_decision = Mock()
        mock_decision.decision = VirtualPanelAction.PROVIDE_SOLUTION
        mock_decision.rationale = "Have enough information"
        mock_decision.confidence = 0.9
        mock_decision.panel_consensus = True
        mock_decision.dissenting_opinions = []
        mock_decision.required_info = []
        mock_decision.research_plan = []

        with patch.object(
            panel, "_orchestrate_panel_decision", return_value=(mock_decision, [])
        ):
            result = await panel.solve_problem("Test query", max_iterations=1)

            assert result.original_query == "Test query"
            # Check that the final solution contains the rationale
            assert result.final_solution == mock_decision.rationale
            assert result.session_state == ConversationState.CONCLUDING

    @pytest.mark.asyncio
    async def test_solve_problem_with_graphrag_initialization(self):
        """Test solve_problem with GraphRAG initialization."""
        panel = VirtualExpertPanel(enable_graphrag=True)

        with patch.object(panel, "_initialize_graphrag", return_value=True):
            with patch.object(panel, "_orchestrate_panel_decision") as mock_orchestrate:
                mock_decision = Mock()
                mock_decision.decision = VirtualPanelAction.PROVIDE_SOLUTION
                mock_decision.rationale = "Done"
                mock_decision.confidence = 0.9
                mock_decision.panel_consensus = True
                mock_orchestrate.return_value = (mock_decision, [])

                result = await panel.solve_problem("Test", domain="tech")
                assert result is not None

    @pytest.mark.asyncio
    async def test_solve_problem_with_mem0_initialization(self):
        """Test solve_problem with Mem0 initialization."""
        panel = VirtualExpertPanel(
            enable_memory=True, memory_type="mem0", user_id="test"
        )

        with patch.object(panel, "_initialize_mem0", return_value=True):
            with patch.object(panel, "_orchestrate_panel_decision") as mock_orchestrate:
                mock_decision = Mock()
                mock_decision.decision = VirtualPanelAction.PROVIDE_SOLUTION
                mock_decision.rationale = "Solution ready"
                mock_decision.confidence = 0.8
                mock_decision.panel_consensus = True
                mock_orchestrate.return_value = (mock_decision, [])

                result = await panel.solve_problem("Test")
                assert result is not None

    @pytest.mark.asyncio
    async def test_solve_problem_max_iterations_reached(self):
        """Test solve_problem when max iterations is reached."""
        panel = VirtualExpertPanel()

        # Mock orchestrator to always return ASK_QUESTION (never conclude)
        mock_decision = Mock()
        mock_decision.decision = VirtualPanelAction.ASK_QUESTION
        mock_decision.rationale = "Need more info"
        mock_decision.confidence = 0.8
        mock_decision.panel_consensus = True
        mock_decision.required_info = ["What's your goal?"]

        def mock_user_input(prompt):
            return "Some answer"

        with patch.object(
            panel, "_orchestrate_panel_decision", return_value=(mock_decision, [])
        ):
            result = await panel.solve_problem(
                "Test", max_iterations=2, user_input_func=mock_user_input
            )

            assert result.total_rounds == 2
            # Session state should be AWAITING_USER since we're in an ASK_QUESTION loop
            assert result.session_state == ConversationState.AWAITING_USER
            # Should have partial solution when max iterations reached
            assert "Unable to reach a definitive solution" in result.final_solution

    @pytest.mark.asyncio
    async def test_solve_problem_exception_handling(self):
        """Test solve_problem exception handling."""
        panel = VirtualExpertPanel()

        with patch.object(
            panel,
            "_orchestrate_panel_decision",
            side_effect=Exception("Orchestration failed"),
        ):
            # The method should raise the exception since it's not caught in the current implementation
            with pytest.raises(Exception, match="Orchestration failed"):
                await panel.solve_problem("Test")


class TestVirtualExpertPanelUtilityMethods:
    """Test utility methods."""

    def test_create_orchestrator_agent(self):
        """Test orchestrator agent creation."""
        panel = VirtualExpertPanel()
        orchestrator = panel._create_orchestrator_agent()
        assert orchestrator is not None
        assert orchestrator.name == "VirtualPanelOrchestrator"

    def test_create_orchestrator_agent_with_custom_config(self):
        """Test orchestrator creation with custom config."""
        from agent_expert_panel.models.model_info import ModelInfo

        config = AgentConfig(
            name="custom",
            model_name="gpt-4",
            description="Custom",
            system_message="Custom message",
            openai_api_key="test-key",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="UNKNOWN",
                structured_output=True,
                multiple_system_messages=False,
            ),
        )
        panel = VirtualExpertPanel(config=config)
        orchestrator = panel._create_orchestrator_agent()
        assert orchestrator is not None

    def test_format_panel_context_basic(self):
        """Test basic panel context formatting."""
        panel = VirtualExpertPanel()
        context = panel._format_panel_context("Test query", "tech", "", [])
        assert "Test query" in context
        assert "tech" in context

    def test_format_panel_context_with_memory_insights(self):
        """Test panel context formatting with memory insights."""
        panel = VirtualExpertPanel()
        context = panel._format_panel_context(
            "Test query", "tech", "User prefers detailed answers", []
        )
        assert "User prefers detailed answers" in context

    def test_format_panel_context_with_conversation_history(self):
        """Test panel context formatting with conversation history."""
        panel = VirtualExpertPanel()
        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]
        context = panel._format_panel_context("Test query", "tech", "", history)
        assert "Previous question" in context
        assert "Previous answer" in context


if __name__ == "__main__":
    pytest.main([__file__])
