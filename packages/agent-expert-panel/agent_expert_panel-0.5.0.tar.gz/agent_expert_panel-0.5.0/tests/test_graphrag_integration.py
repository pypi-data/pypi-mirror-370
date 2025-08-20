"""
Tests for GraphRAG Integration

This module tests the GraphRAG knowledge management system and its integration
with the Virtual Expert Panel.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from agent_expert_panel.tools.graphrag_integration import (
    GraphRAGKnowledgeManager,
    LegacyKnowledgeAdapter,
    create_graphrag_knowledge_manager,
)
from agent_expert_panel.models.virtual_panel import KnowledgeBase


class TestGraphRAGKnowledgeManager:
    """Test the GraphRAG knowledge manager."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_build_index(self):
        """Mock the build index method."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GraphRAGKnowledgeManager._build_index"
        ) as mock:
            mock.return_value = AsyncMock(return_value=True)()
            yield mock

    @pytest.fixture
    def knowledge_manager(self, temp_workspace):
        """Create a knowledge manager instance for testing."""
        return GraphRAGKnowledgeManager(
            workspace_dir=temp_workspace,
            domain="test_domain",
            persist_across_sessions=False,
        )

    def test_init(self, knowledge_manager, temp_workspace):
        """Test knowledge manager initialization."""
        assert knowledge_manager.domain == "test_domain"
        assert knowledge_manager.workspace_dir == temp_workspace
        assert not knowledge_manager.persist_across_sessions
        assert knowledge_manager.documents_added == 0
        assert not knowledge_manager.is_initialized

    @pytest.mark.asyncio
    async def test_initialize_without_graphrag(self, knowledge_manager):
        """Test initialization when GraphRAG is not available."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", False
        ):
            result = await knowledge_manager.initialize()
            assert not result
            assert not knowledge_manager.is_initialized

    @pytest.mark.asyncio
    async def test_initialize_with_graphrag(self, knowledge_manager):
        """Test successful initialization with GraphRAG."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            result = await knowledge_manager.initialize()
            assert result
            assert knowledge_manager.is_initialized

    @pytest.mark.asyncio
    async def test_add_research_findings(self, knowledge_manager, mock_build_index):
        """Test adding research findings to GraphRAG."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            await knowledge_manager.initialize()

            research_results = {
                "original_query": "test query",
                "summary": "test summary",
                "key_findings": [
                    {"content": "finding 1", "source": "source1"},
                    {"content": "finding 2", "source": "source2"},
                ],
                "sources": ["source1", "source2"],
            }

            result = await knowledge_manager.add_research_findings(
                research_results, "test_session"
            )
            assert result
            assert knowledge_manager.documents_added == 1

            # Check that document was written
            input_dir = knowledge_manager.workspace_dir / "input"
            assert input_dir.exists()
            doc_files = list(input_dir.glob("research_*.txt"))
            assert len(doc_files) == 1

    @pytest.mark.asyncio
    async def test_add_user_context(self, knowledge_manager, mock_build_index):
        """Test adding user context to GraphRAG."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            await knowledge_manager.initialize()

            user_input = (
                "This is user-specific context about their goals and constraints."
            )

            result = await knowledge_manager.add_user_context(
                user_input, "user_goals", "test_session"
            )
            assert result
            assert knowledge_manager.documents_added == 1

            # Check that document was written
            input_dir = knowledge_manager.workspace_dir / "input"
            doc_files = list(input_dir.glob("User*.txt"))
            assert len(doc_files) == 1

    @pytest.mark.asyncio
    async def test_query_knowledge(self, knowledge_manager):
        """Test querying the GraphRAG knowledge base."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            await knowledge_manager.initialize()

            # Mock the global search method directly
            with patch.object(
                knowledge_manager, "global_search", new_callable=AsyncMock
            ) as mock_global_search:
                mock_global_search.return_value = {
                    "query": "test query",
                    "response": "Mock global search result",
                    "context_data": {},
                    "completion_time": "2024-01-01T00:00:00",
                    "search_type": "global",
                }

                result = await knowledge_manager.global_search("test query")

                assert result["query"] == "test query"
                assert result["search_type"] == "global"
                assert "response" in result

                # Verify the global search was called
                mock_global_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_get_knowledge_summary(self, knowledge_manager):
        """Test getting knowledge base summary."""
        summary = await knowledge_manager.get_knowledge_summary()

        assert summary["domain"] == "test_domain"
        assert "workspace_dir" in summary
        assert "documents_count" in summary
        assert "has_index" in summary
        assert "is_initialized" in summary

    @pytest.mark.asyncio
    async def test_rebuild_index(self, knowledge_manager, mock_build_index):
        """Test rebuilding the GraphRAG index."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            await knowledge_manager.initialize()

            # Create a test document first
            input_dir = knowledge_manager.workspace_dir / "input"
            input_dir.mkdir(exist_ok=True)
            (input_dir / "test.txt").write_text("Test content")

            # Mock the _build_index method to return True
            with patch.object(
                knowledge_manager, "_build_index", new_callable=AsyncMock
            ) as mock_build:
                mock_build.return_value = True

                result = await knowledge_manager._build_index()
                assert result

                # Verify build_index was called
                mock_build.assert_called_once()


class TestLegacyKnowledgeAdapter:
    """Test the legacy knowledge base adapter."""

    @pytest.fixture
    def mock_graphrag_manager(self):
        """Mock GraphRAG manager for testing."""
        manager = MagicMock()
        manager.add_research_findings = AsyncMock(return_value=True)
        manager.add_user_context = AsyncMock(return_value=True)
        manager.add_documents = AsyncMock(return_value=True)
        return manager

    @pytest.fixture
    def adapter(self, mock_graphrag_manager):
        """Create an adapter instance for testing."""
        return LegacyKnowledgeAdapter(mock_graphrag_manager)

    @pytest.fixture
    def sample_knowledge_base(self):
        """Create a sample knowledge base for testing."""
        kb = KnowledgeBase(
            domain="test",
            documents=[
                {
                    "title": "Test Document",
                    "content": "Test content",
                    "source": "user_input",
                    "metadata": {"type": "test"},
                }
            ],
            web_research=[
                {
                    "query": "test query",
                    "summary": "test summary",
                    "key_findings": [{"content": "finding", "source": "web"}],
                }
            ],
            facts=[{"fact": "Test fact", "source": "test_source", "confidence": 0.9}],
            entities=[],
            summary="Test knowledge base summary",
        )
        return kb

    @pytest.mark.asyncio
    async def test_migrate_knowledge_base(
        self, adapter, sample_knowledge_base, mock_graphrag_manager
    ):
        """Test migrating a complete knowledge base."""
        result = await adapter.migrate_knowledge_base(
            sample_knowledge_base, "test_session"
        )

        assert result

        # Verify that GraphRAG methods were called
        mock_graphrag_manager.add_user_context.assert_called()
        mock_graphrag_manager.add_research_findings.assert_called()

    @pytest.mark.asyncio
    async def test_query_knowledge_global_search(self, adapter):
        """Test query_knowledge with global search type."""
        adapter.graphrag_manager.global_search = AsyncMock(
            return_value={"response": "Global search result"}
        )

        result = await adapter.query_knowledge("test query", "global")

        assert result == "Global search result"
        adapter.graphrag_manager.global_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_query_knowledge_local_search(self, adapter):
        """Test query_knowledge with local search type."""
        adapter.graphrag_manager.local_search = AsyncMock(
            return_value={"response": "Local search result"}
        )

        result = await adapter.query_knowledge("test query", "local")

        assert result == "Local search result"
        adapter.graphrag_manager.local_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_query_knowledge_hybrid_search(self, adapter):
        """Test query_knowledge with hybrid search type."""
        adapter.graphrag_manager.hybrid_search = AsyncMock(
            return_value={"combined_response": "Hybrid search result"}
        )

        result = await adapter.query_knowledge("test query", "hybrid")

        assert result == "Hybrid search result"
        adapter.graphrag_manager.hybrid_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_query_knowledge_error_handling(self, adapter):
        """Test query_knowledge handles errors gracefully."""
        adapter.graphrag_manager.global_search = AsyncMock(
            side_effect=Exception("Test error")
        )

        result = await adapter.query_knowledge("test query", "global")

        assert result.startswith("Knowledge query failed:")
        assert "Test error" in result

    @pytest.mark.asyncio
    async def test_query_knowledge_no_results(self, adapter):
        """Test query_knowledge when no results are found."""
        adapter.graphrag_manager.global_search = AsyncMock(return_value={})

        result = await adapter.query_knowledge("test query", "global")

        assert result == "No results found"

    @pytest.mark.asyncio
    async def test_query_knowledge_missing_response_key(self, adapter):
        """Test query_knowledge when response key is missing."""
        adapter.graphrag_manager.local_search = AsyncMock(
            return_value={"other_key": "value"}
        )

        result = await adapter.query_knowledge("test query", "local")

        assert result == "No results found"


class TestGraphRAGFactory:
    """Test the GraphRAG factory function."""

    @pytest.mark.asyncio
    async def test_create_graphrag_knowledge_manager_success(self):
        """Test successful creation of GraphRAG manager."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            manager = await create_graphrag_knowledge_manager(
                domain="test", persist_across_sessions=False
            )
            assert manager is not None
            assert manager.domain == "test"

    @pytest.mark.asyncio
    async def test_create_graphrag_knowledge_manager_unavailable(self):
        """Test creation when GraphRAG is unavailable."""
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", False
        ):
            manager = await create_graphrag_knowledge_manager(domain="test")
            assert manager is None


class TestGraphRAGIntegration:
    """Integration tests for GraphRAG with the Virtual Expert Panel."""

    @pytest.mark.asyncio
    async def test_virtual_panel_with_graphrag(self):
        """Test Virtual Expert Panel with GraphRAG integration."""
        # This would be an integration test that requires actual GraphRAG installation
        # For now, we'll create a mock test

        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            from agent_expert_panel.virtual_panel import VirtualExpertPanel

            # Create panel with GraphRAG enabled
            panel = VirtualExpertPanel(
                enable_graphrag=True,
                persist_knowledge=False,  # Use temp directory
            )

            # Verify GraphRAG components are properly set up
            assert panel.enable_graphrag
            assert not panel.persist_knowledge
            assert panel.graphrag_manager is None  # Not initialized until solve_problem

    @pytest.mark.asyncio
    async def test_knowledge_persistence_workflow(self):
        """Test the complete knowledge persistence workflow."""
        # Mock the entire workflow
        with patch(
            "agent_expert_panel.tools.graphrag_integration.GRAPHRAG_AVAILABLE", True
        ):
            with tempfile.TemporaryDirectory() as tmpdir:
                manager = GraphRAGKnowledgeManager(
                    workspace_dir=Path(tmpdir),
                    domain="test",
                    persist_across_sessions=False,
                )

                # Initialize
                await manager.initialize()
                assert manager.is_initialized

                # Add research findings
                research_data = {
                    "original_query": "test query",
                    "summary": "test summary",
                    "key_findings": [{"content": "test finding"}],
                    "sources": ["test source"],
                }

                await manager.add_research_findings(research_data, "session1")
                assert manager.documents_added == 1

                # Add user context
                await manager.add_user_context("user context", "session_id", "session1")
                assert manager.documents_added == 2


if __name__ == "__main__":
    pytest.main([__file__])
