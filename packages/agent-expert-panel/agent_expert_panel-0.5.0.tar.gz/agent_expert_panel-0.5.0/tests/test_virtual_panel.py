"""
Tests for the Virtual Expert Panel functionality.

This test suite validates the Virtual Expert Panel implementation,
inspired by Microsoft's MAI-DxO pattern but generalized for any domain.
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from agent_expert_panel.virtual_panel import VirtualExpertPanel
from agent_expert_panel.models.virtual_panel import (
    VirtualPanelAction,
    ConversationState,
    VirtualPanelResult,
    OrchestratorDecision,
    PanelAction,
    ResearchTask,
)


@pytest.fixture
def virtual_panel():
    """Create a VirtualExpertPanel instance for testing."""
    return VirtualExpertPanel(enable_memory=False)


@pytest.fixture
def virtual_panel_with_memory():
    """Create a VirtualExpertPanel instance with memory enabled."""
    return VirtualExpertPanel(enable_memory=True, memory_type="simple")


@pytest.fixture
def mock_user_input():
    """Mock user input function for testing."""

    async def _mock_input(question: str) -> str:
        if "budget" in question.lower():
            return "Our budget is $10,000"
        elif "timeline" in question.lower():
            return "We need to complete this in 3 months"
        else:
            return "No additional information available"

    return _mock_input


class TestVirtualExpertPanel:
    """Test cases for VirtualExpertPanel class."""

    def test_initialization_basic(self, virtual_panel):
        """Test basic initialization of VirtualExpertPanel."""
        assert virtual_panel is not None
        assert virtual_panel.enable_memory is False
        assert virtual_panel.expert_panel is not None
        assert virtual_panel.orchestrator is not None
        assert (
            len(virtual_panel.expert_panel.agents) == 6
        )  # 5 original + web_research_specialist

    def test_initialization_with_memory(self, virtual_panel_with_memory):
        """Test initialization with memory enabled."""
        assert virtual_panel_with_memory.enable_memory is True
        assert virtual_panel_with_memory.memory is not None
        assert virtual_panel_with_memory.memory_type == "simple"

    def test_orchestrator_creation(self, virtual_panel):
        """Test that orchestrator agent is created correctly."""
        orchestrator = virtual_panel.orchestrator
        assert orchestrator.name == "VirtualPanelOrchestrator"
        # Check that the orchestrator was created with a system message
        assert hasattr(orchestrator, "_system_messages") or hasattr(
            orchestrator, "system_message"
        )
        # Test passes if the orchestrator is properly created

    @pytest.mark.asyncio
    async def test_solve_problem_basic(self, virtual_panel):
        """Test basic problem solving workflow."""
        query = "What is the best approach for cloud migration?"

        # Mock the panel discussion to return a solution
        with patch.object(
            virtual_panel, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.return_value = (
                OrchestratorDecision(
                    decision=VirtualPanelAction.PROVIDE_SOLUTION,
                    rationale="Based on analysis, recommend AWS migration with lift-and-shift approach.",
                    confidence=0.9,
                    panel_consensus=True,
                ),
                [],
            )

            result = await virtual_panel.solve_problem(
                query=query, domain="technology", max_iterations=1, user_input_func=None
            )

            assert isinstance(result, VirtualPanelResult)
            assert result.original_query == query
            assert result.final_solution is not None
            assert result.total_rounds == 1
            assert "orchestrator" in result.participants

    @pytest.mark.asyncio
    async def test_ask_question_action(self, virtual_panel, mock_user_input):
        """Test ASK_QUESTION action handling."""
        query = "How should we approach this project?"

        # Mock decisions: first ask question, then provide solution
        decisions = [
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.ASK_QUESTION,
                    rationale="Need more information about budget and timeline",
                    confidence=0.8,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.PROVIDE_SOLUTION,
                    rationale="Based on budget and timeline constraints, recommend agile approach",
                    confidence=0.9,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
        ]

        with patch.object(
            virtual_panel, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.side_effect = decisions

            result = await virtual_panel.solve_problem(
                query=query,
                domain="business",
                max_iterations=3,
                user_input_func=mock_user_input,
            )

            assert len(result.actions_taken) == 2
            assert (
                result.actions_taken[0].action_type == VirtualPanelAction.ASK_QUESTION
            )
            assert (
                result.actions_taken[1].action_type
                == VirtualPanelAction.PROVIDE_SOLUTION
            )

    @pytest.mark.asyncio
    async def test_request_test_action(self, virtual_panel):
        """Test REQUEST_TEST action handling."""
        query = "Should we adopt microservices architecture?"

        decisions = [
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.REQUEST_TEST,
                    rationale="Need to research current microservices best practices",
                    confidence=0.8,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.PROVIDE_SOLUTION,
                    rationale="Based on research, microservices recommended for scalable applications",
                    confidence=0.9,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
        ]

        with patch.object(
            virtual_panel, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.side_effect = decisions

            with patch.object(virtual_panel, "_conduct_web_research") as mock_research:
                mock_research.return_value = {
                    "status": "completed",
                    "summary": "Research completed on microservices architecture",
                }

                result = await virtual_panel.solve_problem(
                    query=query,
                    domain="technology",
                    max_iterations=3,
                    user_input_func=None,
                )

                assert len(result.actions_taken) == 2
                assert (
                    result.actions_taken[0].action_type
                    == VirtualPanelAction.REQUEST_TEST
                )
                assert len(result.research_tasks) >= 1
                assert result.research_tasks[0].status == "completed"

    @pytest.mark.asyncio
    async def test_max_iterations_limit(self, virtual_panel):
        """Test that max iterations limit is respected."""
        query = "Complex problem requiring multiple iterations"

        # Always return REQUEST_TEST to force hitting iteration limit
        with patch.object(
            virtual_panel, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.return_value = (
                OrchestratorDecision(
                    decision=VirtualPanelAction.REQUEST_TEST,
                    rationale="Need more research",
                    confidence=0.7,
                    panel_consensus=True,
                ),
                [],
            )

            with patch.object(virtual_panel, "_conduct_web_research") as mock_research:
                mock_research.return_value = {
                    "status": "completed",
                    "summary": "Research done",
                }

                result = await virtual_panel.solve_problem(
                    query=query, max_iterations=2, user_input_func=None
                )

                assert result.total_rounds == 2
                assert "Unable to reach a definitive solution" in result.final_solution

    def test_knowledge_base_functionality(self, virtual_panel):
        """Test KnowledgeBase operations."""
        kb = virtual_panel.knowledge_base

        # Test document addition
        kb.add_document("Test Document", "Test content", "test_source")
        assert len(kb.documents) == 1
        assert kb.documents[0]["title"] == "Test Document"

        # Test web result addition
        kb.add_web_result("test query", [{"result": "test"}])
        assert len(kb.web_research) == 1
        assert kb.web_research[0]["query"] == "test query"

        # Test fact extraction
        kb.extract_fact("Test fact", "test_source", 0.9)
        assert len(kb.facts) == 1
        assert kb.facts[0]["fact"] == "Test fact"
        assert kb.facts[0]["confidence"] == 0.9


class TestVirtualPanelModels:
    """Test cases for Virtual Panel data models."""

    def test_panel_action_creation(self):
        """Test PanelAction model creation."""
        action = PanelAction(
            action_type=VirtualPanelAction.ASK_QUESTION,
            content="Need more information",
            reasoning="Insufficient data for decision",
            timestamp=datetime.now(),
        )

        assert action.action_type == VirtualPanelAction.ASK_QUESTION
        assert action.content == "Need more information"
        assert action.metadata == {}

    def test_research_task_creation(self):
        """Test ResearchTask model creation."""
        task = ResearchTask(
            task_id="test_task_1",
            description="Research market trends",
            agent_assigned="research_specialist",
        )

        assert task.task_id == "test_task_1"
        assert task.status == "pending"
        assert task.results == {}
        assert task.timestamp is not None

    def test_virtual_panel_result_creation(self):
        """Test VirtualPanelResult model creation."""
        result = VirtualPanelResult(
            original_query="Test query",
            final_solution="Test solution",
            conversation_history=[],
            actions_taken=[],
            research_tasks=[],
            knowledge_artifacts=[],
            session_state=ConversationState.CONCLUDING,
            total_rounds=1,
            participants=["agent1", "agent2"],
        )

        assert result.original_query == "Test query"
        assert result.session_state == ConversationState.CONCLUDING
        assert result.start_time is not None

    def test_orchestrator_decision_creation(self):
        """Test OrchestratorDecision model creation."""
        decision = OrchestratorDecision(
            decision=VirtualPanelAction.PROVIDE_SOLUTION,
            rationale="All information available",
            confidence=0.95,
            panel_consensus=True,
        )

        assert decision.decision == VirtualPanelAction.PROVIDE_SOLUTION
        assert decision.confidence == 0.95
        assert decision.dissenting_opinions == []


class TestResearchTools:
    """Test cases for research tools integration."""

    # TODO: Add tests for real research tools when implemented
    # Research functionality should be tested via web research agents using:
    # - Playwright MCP Server: https://github.com/microsoft/playwright-mcp
    # - autogen_ext.agents.web_surfer.playwright_controller


class TestGraphRAGEnhancedKnowledge:
    """Test cases for GraphRAG enhanced knowledge functionality."""

    @pytest.fixture
    def virtual_panel_with_graphrag(self):
        """Create a VirtualExpertPanel instance with GraphRAG enabled."""
        return VirtualExpertPanel(enable_graphrag=True, enable_memory=False)

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_success(self, virtual_panel_with_graphrag):
        """Test successful enhanced knowledge query."""
        # Mock the GraphRAG adapter
        from unittest.mock import AsyncMock, MagicMock

        mock_adapter = MagicMock()
        mock_adapter.query_knowledge = AsyncMock(
            return_value="GraphRAG enhanced knowledge response"
        )
        virtual_panel_with_graphrag.graphrag_adapter = mock_adapter

        # Mock the knowledge base summary
        virtual_panel_with_graphrag.knowledge_base.summary = "Legacy knowledge summary"

        result = await virtual_panel_with_graphrag._query_enhanced_knowledge(
            "test query"
        )

        # Should return enhanced summary combining both sources
        assert "Legacy Knowledge Base Summary:" in result
        assert "GraphRAG Knowledge Analysis:" in result
        assert "GraphRAG enhanced knowledge response" in result
        assert "Combined Knowledge Confidence: High (GraphRAG Enhanced)" in result

        # Verify GraphRAG adapter was called
        mock_adapter.query_knowledge.assert_called_once_with(
            "test query", search_type="global"
        )

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_error_response(
        self, virtual_panel_with_graphrag
    ):
        """Test enhanced knowledge query with error response."""
        from unittest.mock import AsyncMock, MagicMock

        mock_adapter = MagicMock()
        mock_adapter.query_knowledge = AsyncMock(
            return_value="Knowledge query failed: Connection error"
        )
        virtual_panel_with_graphrag.graphrag_adapter = mock_adapter

        # Mock the knowledge base summary
        virtual_panel_with_graphrag.knowledge_base.summary = "Legacy knowledge summary"

        result = await virtual_panel_with_graphrag._query_enhanced_knowledge(
            "test query"
        )

        # Should fallback to legacy knowledge base summary
        assert result == "Legacy knowledge summary"

        # Verify GraphRAG adapter was called
        mock_adapter.query_knowledge.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_exception_handling(
        self, virtual_panel_with_graphrag
    ):
        """Test enhanced knowledge query with exception."""
        from unittest.mock import AsyncMock, MagicMock

        mock_adapter = MagicMock()
        mock_adapter.query_knowledge = AsyncMock(
            side_effect=Exception("GraphRAG connection failed")
        )
        virtual_panel_with_graphrag.graphrag_adapter = mock_adapter

        # Mock the knowledge base summary
        virtual_panel_with_graphrag.knowledge_base.summary = "Legacy knowledge summary"

        result = await virtual_panel_with_graphrag._query_enhanced_knowledge(
            "test query"
        )

        # Should fallback to legacy knowledge base summary
        assert result == "Legacy knowledge summary"

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_no_graphrag_adapter(self, virtual_panel):
        """Test enhanced knowledge query without GraphRAG adapter."""
        # Regular panel without GraphRAG
        virtual_panel.knowledge_base.summary = "Legacy knowledge summary"

        result = await virtual_panel._query_enhanced_knowledge("test query")

        # Should return legacy knowledge base summary
        assert result == "Legacy knowledge summary"

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_error_patterns(
        self, virtual_panel_with_graphrag
    ):
        """Test enhanced knowledge query with various error patterns."""
        from unittest.mock import AsyncMock, MagicMock

        error_responses = [
            "Error: Database connection failed",
            "Exception: Invalid query format",
            "Service not available",
            "Search failed: Timeout occurred",
            "Query error: Invalid parameters",
        ]

        for error_response in error_responses:
            mock_adapter = MagicMock()
            mock_adapter.query_knowledge = AsyncMock(return_value=error_response)
            virtual_panel_with_graphrag.graphrag_adapter = mock_adapter
            virtual_panel_with_graphrag.knowledge_base.summary = (
                "Legacy knowledge summary"
            )

            result = await virtual_panel_with_graphrag._query_enhanced_knowledge(
                "test query"
            )

            # Should fallback to legacy knowledge for any error pattern
            assert result == "Legacy knowledge summary", (
                f"Failed for error: {error_response}"
            )

    @pytest.mark.asyncio
    async def test_query_enhanced_knowledge_empty_response(
        self, virtual_panel_with_graphrag
    ):
        """Test enhanced knowledge query with empty response."""
        from unittest.mock import AsyncMock, MagicMock

        mock_adapter = MagicMock()
        mock_adapter.query_knowledge = AsyncMock(return_value="")
        virtual_panel_with_graphrag.graphrag_adapter = mock_adapter

        virtual_panel_with_graphrag.knowledge_base.summary = "Legacy knowledge summary"

        result = await virtual_panel_with_graphrag._query_enhanced_knowledge(
            "test query"
        )

        # Should fallback to legacy knowledge for empty response
        assert result == "Legacy knowledge summary"


class TestIntegrationScenarios:
    """Integration test scenarios for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_technology_workflow(self, virtual_panel):
        """Test complete workflow for a technology problem."""
        query = "Should we migrate our database to the cloud?"

        # Simulate a realistic decision sequence
        decisions = [
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.REQUEST_TEST,
                    rationale="Need to research cloud database options and migration strategies",
                    confidence=0.8,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
            (
                OrchestratorDecision(
                    decision=VirtualPanelAction.PROVIDE_SOLUTION,
                    rationale="Based on research, recommend gradual migration to AWS RDS with proper backup strategy",
                    confidence=0.9,
                    panel_consensus=True,
                ),
                [],  # Empty discussion messages
            ),
        ]

        with patch.object(
            virtual_panel, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.side_effect = decisions

            with patch.object(virtual_panel, "_conduct_web_research") as mock_research:
                mock_research.return_value = {
                    "status": "completed",
                    "summary": "Comprehensive research on cloud database migration completed",
                }

                result = await virtual_panel.solve_problem(
                    query=query,
                    domain="technology",
                    max_iterations=5,
                    user_input_func=None,
                )

                # Validate complete workflow
                assert result.final_solution is not None
                assert "AWS RDS" in result.final_solution
                assert len(result.actions_taken) == 2
                assert len(result.research_tasks) >= 1
                assert result.session_state == ConversationState.CONCLUDING

    @pytest.mark.asyncio
    async def test_memory_persistence(self, virtual_panel_with_memory):
        """Test that memory persists information across operations."""
        query = "How can we improve team productivity?"

        with patch.object(
            virtual_panel_with_memory, "_orchestrate_panel_decision"
        ) as mock_decision:
            mock_decision.return_value = (
                OrchestratorDecision(
                    decision=VirtualPanelAction.PROVIDE_SOLUTION,
                    rationale="Based on available knowledge and agile practices, recommend implementing daily standups",
                    confidence=0.85,
                    panel_consensus=True,
                ),
                [],
            )

            result = await virtual_panel_with_memory.solve_problem(
                query=query, domain="business", max_iterations=1, user_input_func=None
            )

            # Check that knowledge base was initialized with the correct domain
            assert virtual_panel_with_memory.knowledge_base.domain == "business"

            # Test adding a document after solve_problem
            virtual_panel_with_memory.knowledge_base.add_document(
                "Productivity Guide",
                "Agile methodologies improve team productivity",
                "internal_doc",
            )
            assert len(virtual_panel_with_memory.knowledge_base.documents) == 1
            assert "agile" in result.final_solution.lower()


if __name__ == "__main__":
    pytest.main([__file__])
